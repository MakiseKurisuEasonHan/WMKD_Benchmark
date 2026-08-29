"""Two-step fail-closed trainability audit for pinned official iSeal semantics."""

import argparse
import hashlib
import hmac
import json
import math
import os
import random
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import yaml
from datasets import load_dataset
from torch.utils.data import DataLoader, Dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, get_linear_schedule_with_warmup


class KeyedCipher(nn.Module):
    def __init__(self, dim, n_layers, key, dtype=torch.bfloat16):
        super().__init__()
        layers = []
        for index in range(n_layers):
            seed = int(hmac.new(key, f"layer{index}".encode(), hashlib.sha256).hexdigest(), 16) % (2**31)
            torch.manual_seed(seed)
            layer = nn.Linear(dim, dim, bias=False)
            nn.init.orthogonal_(layer.weight)
            layers.append(layer.to(dtype))
        self.layers = nn.ModuleList(layers)
        for parameter in self.parameters():
            parameter.requires_grad = False

    def forward(self, value):
        for layer in self.layers:
            value = value + layer(value)
        return value


class OfficialInstructionFingerprint(nn.Module):
    """Exact zero-initialized adapter structure from pinned official superglue code."""

    def __init__(self, embedding, train_ids, inner_dim):
        super().__init__()
        vocabulary, dimension = embedding.weight.shape
        device = embedding.weight.device
        id_to_row = torch.full((vocabulary,), -1, dtype=torch.long, device=device)
        id_to_row[train_ids] = torch.arange(len(train_ids), device=device)
        self.register_buffer("id2row", id_to_row, persistent=False)
        self.delta = nn.Embedding(len(train_ids), dimension, device=device)
        nn.init.zeros_(self.delta.weight)
        self.A = nn.Linear(dimension, inner_dim, bias=False, device=device)
        self.B = nn.Linear(inner_dim, dimension, bias=False, device=device)
        nn.init.zeros_(self.A.weight)
        nn.init.zeros_(self.B.weight)
        self.orig_emb = embedding

    @property
    def weight(self):
        return self.orig_emb.weight

    def forward(self, input_ids):
        base = self.orig_emb(input_ids)
        rows = self.id2row[input_ids]
        mask = rows != -1
        if mask.any():
            delta = self.B(self.A(self.delta(rows[mask])))
            base[mask] += delta
        return base


class TextDataset(Dataset):
    def __init__(self, texts, tokenizer, max_length):
        self.texts = list(texts)
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, index):
        encoded = self.tokenizer(
            self.texts[index], truncation=True, padding="max_length",
            max_length=self.max_length, return_tensors="pt",
        )
        ids = encoded.input_ids.squeeze(0)
        return {"input_ids": ids, "attention_mask": encoded.attention_mask.squeeze(0), "labels": ids.clone()}


def tensor_hash(tensor):
    return hashlib.sha256(tensor.detach().float().cpu().numpy().tobytes()).hexdigest()


def block_stats(parameters):
    params = list(parameters)
    return {
        "parameter_count": sum(item.numel() for item in params),
        "requires_grad": any(item.requires_grad for item in params),
        "initial_norm": math.sqrt(sum(item.detach().float().pow(2).sum().item() for item in params)),
        "initial_sha256": hashlib.sha256("".join(tensor_hash(item) for item in params).encode()).hexdigest(),
    }


def grad_norm(parameters):
    return math.sqrt(sum(item.grad.detach().float().pow(2).sum().item() for item in parameters if item.grad is not None))


def delta_norm(parameters, before):
    return math.sqrt(sum((item.detach().float().cpu() - old).pow(2).sum().item() for item, old in zip(parameters, before)))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--dataset-cache", required=True)
    args = parser.parse_args()
    config = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    secret_hex = os.environ.get("ISEAL_SECRET_KEY_HEX")
    if not secret_hex:
        raise SystemExit("ISEAL_SECRET_KEY_HEX must be provided outside Git")
    secret_key = bytes.fromhex(secret_hex)
    if hashlib.sha256(secret_key).hexdigest() != config["training"]["secret_key_sha256"]:
        raise SystemExit("iSeal external secret key hash does not match pinned config")
    seed = config["seed"]
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed); torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True; torch.backends.cudnn.benchmark = False
    model_path = config["model"]["path"]
    tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True, use_fast=False)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    dataset = load_dataset(config["dataset"]["id"], split="train", cache_dir=args.dataset_cache)
    dataset = dataset.shuffle(seed=config["dataset"]["shuffle_seed"]).select(range(config["dataset"]["registered_count"]))
    texts = dataset["text"]
    text_dataset = TextDataset(texts, tokenizer, config["training"]["max_sequence_length"])
    train_ids = sorted({token for row in text_dataset for token in row["input_ids"].tolist()})
    model = AutoModelForCausalLM.from_pretrained(
        model_path, torch_dtype=torch.bfloat16, device_map="auto", low_cpu_mem_usage=True, local_files_only=True,
    )
    original_embedding = model.get_input_embeddings()
    adapter = OfficialInstructionFingerprint(original_embedding, train_ids, config["training"]["adapter_inner_dim"])
    model.set_input_embeddings(adapter)
    for parameter in model.parameters():
        parameter.requires_grad = False
    for parameter in adapter.parameters():
        if parameter is not adapter.orig_emb.weight:
            parameter.requires_grad = True
    model.lm_head.weight.requires_grad = True
    blocks = {
        "base_transformer": [p for name, p in model.named_parameters() if not name.startswith("model.embed_tokens") and name != "lm_head.weight"],
        "original_embeddings": [adapter.orig_emb.weight],
        "iseal_delta": [adapter.delta.weight],
        "iseal_A": [adapter.A.weight],
        "iseal_B": [adapter.B.weight],
        "lm_head": [model.lm_head.weight],
    }
    initial = {name: block_stats(params) for name, params in blocks.items()}
    snapshots = {name: [p.detach().float().cpu().clone() for p in params] for name, params in blocks.items()}
    cipher = KeyedCipher(
        model.config.hidden_size, config["training"]["cipher_layers"],
        secret_key, torch.bfloat16,
    )
    loader = DataLoader(text_dataset, batch_size=config["training"]["per_device_batch_size"], shuffle=True)
    optimizer = torch.optim.AdamW(
        [p for p in model.parameters() if p.requires_grad], lr=config["training"]["learning_rate"],
        weight_decay=config["training"]["weight_decay"], eps=config["training"]["adam_epsilon"],
    )
    steps = config["trainability_audit"]["optimizer_steps"]
    scheduler = get_linear_schedule_with_warmup(optimizer, max(1, int(0.1 * steps)), steps)
    step_records = []
    iterator = iter(loader)
    for step in range(steps):
        batch = next(iterator)
        device = next(model.parameters()).device
        ids = batch["input_ids"].to(device); mask = batch["attention_mask"].to(device); labels = batch["labels"].to(device)
        encrypted = cipher.to(device)(model.get_input_embeddings()(ids))
        output = model(inputs_embeds=encrypted, attention_mask=mask, labels=labels)
        output.loss.backward()
        gradients = {name: grad_norm(params) for name, params in blocks.items()}
        torch.nn.utils.clip_grad_norm_(model.parameters(), config["training"]["max_grad_norm"])
        optimizer.step(); scheduler.step(); optimizer.zero_grad()
        step_records.append({"step": step + 1, "loss": output.loss.item(), "gradient_norms_before_clip": gradients})
    deltas = {name: delta_norm(params, snapshots[name]) for name, params in blocks.items()}
    adapter_updated = any(deltas[name] > 0 for name in ("iseal_delta", "iseal_A", "iseal_B"))
    lm_head_updated = deltas["lm_head"] > 0
    gate_passed = adapter_updated and not (lm_head_updated and not adapter_updated)
    result = {
        "project": config["project"], "method": "iSeal", "audit": "official_semantics_two_step_trainability",
        "official_commit": config["official_source"]["commit"], "model_revision": config["model"]["revision"],
        "registered_count": len(texts), "trainable_token_count": len(train_ids), "blocks": initial,
        "steps": step_records, "parameter_delta_norms": deltas, "adapter_updated": adapter_updated,
        "lm_head_updated": lm_head_updated, "formal_experiment_a_allowed": gate_passed,
        "terminal_state": "PASSED" if gate_passed else "BLOCKED_SCIENTIFIC_IMPLEMENTATION_TRAINABILITY",
    }
    output_path = Path(args.output); output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if gate_passed else 3)


if __name__ == "__main__":
    main()
