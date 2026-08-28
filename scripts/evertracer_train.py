#!/usr/bin/env python3
"""Project-owned LoRA CLM trainer matching EverTracer Experiment A settings."""

import argparse
import json
import math
from pathlib import Path
import time

import torch
from datasets import Dataset
from peft import LoraConfig, TaskType, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments, set_seed

from evertracer_common import configure_cache, load_config, write_json


def read_texts(path: Path) -> list[str]:
    return [json.loads(line)["text"] for line in path.read_text(encoding="utf-8").splitlines() if line]


def packed_dataset(texts: list[str], tokenizer, block_size: int) -> Dataset:
    tokens: list[int] = []
    for text in texts:
        tokens.extend(tokenizer(text, add_special_tokens=True, truncation=False)["input_ids"])
        if tokenizer.eos_token_id is not None and (not tokens or tokens[-1] != tokenizer.eos_token_id):
            tokens.append(tokenizer.eos_token_id)
    blocks = [tokens[i:i + block_size] for i in range(0, len(tokens) - block_size + 1, block_size)]
    if not blocks:
        raise ValueError("packing produced zero full blocks")
    return Dataset.from_dict({"input_ids": blocks, "attention_mask": [[1] * block_size for _ in blocks], "labels": blocks})


class Collator:
    def __call__(self, rows):
        return {key: torch.tensor([row[key] for row in rows], dtype=torch.long) for key in ("input_ids", "attention_mask", "labels")}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--config", required=True); p.add_argument("--role", required=True, choices=("target", "reference"))
    p.add_argument("--dataset-root", required=True); p.add_argument("--output-dir", required=True)
    p.add_argument("--max-steps", type=int, default=-1); p.add_argument("--metrics", required=True)
    args = p.parse_args(); cfg = load_config(args.config); configure_cache(cfg["runtime"]["data_root"]); set_seed(cfg["seed"])
    tc, mc = cfg["training"], cfg["model"]; subset = "dtr" if args.role == "target" else "dref"
    epochs = tc["target_epochs"] if args.role == "target" else tc["reference_epochs"]
    tokenizer = AutoTokenizer.from_pretrained(mc["path"], local_files_only=True, revision=mc["revision"])
    tokenizer.pad_token = tokenizer.pad_token or tokenizer.eos_token
    dataset = packed_dataset(read_texts(Path(args.dataset_root) / f"{subset}.jsonl"), tokenizer, tc["block_size"])
    model = AutoModelForCausalLM.from_pretrained(mc["path"], local_files_only=True, torch_dtype=torch.bfloat16)
    model.config.use_cache = False
    model = get_peft_model(model, LoraConfig(task_type=TaskType.CAUSAL_LM, r=tc["lora_rank"],
        lora_alpha=tc["lora_alpha"], lora_dropout=tc["lora_dropout"], inference_mode=False))
    trainable = sum(v.numel() for v in model.parameters() if v.requires_grad); total = sum(v.numel() for v in model.parameters())
    output = Path(args.output_dir); output.mkdir(parents=True, exist_ok=False)
    training_args = TrainingArguments(output_dir=str(output), num_train_epochs=epochs,
        per_device_train_batch_size=tc["batch_size"], gradient_accumulation_steps=tc["gradient_accumulation_steps"],
        learning_rate=tc["learning_rate"], lr_scheduler_type=tc["lr_scheduler_type"], warmup_steps=tc["warmup_steps"],
        weight_decay=tc["weight_decay"], bf16=True, fp16=False, logging_steps=1, save_strategy="no", report_to=[],
        remove_unused_columns=False, seed=cfg["seed"], data_seed=cfg["seed"], max_steps=args.max_steps)
    trainer = Trainer(model=model, args=training_args, train_dataset=dataset, data_collator=Collator())
    torch.cuda.reset_peak_memory_stats(); start = time.monotonic(); result = trainer.train(); elapsed = time.monotonic() - start
    model.save_pretrained(output / "adapter"); tokenizer.save_pretrained(output / "adapter")
    steps = int(result.global_step); samples = steps * tc["batch_size"] * tc["gradient_accumulation_steps"]
    metrics = {"role": args.role, "subset": subset, "records": len(read_texts(Path(args.dataset_root) / f"{subset}.jsonl")),
        "packed_blocks": len(dataset), "epochs": epochs, "optimizer_steps": steps, "expected_full_steps": math.ceil(len(dataset)/tc["batch_size"]) * epochs,
        "elapsed_seconds": elapsed, "seconds_per_step": elapsed / max(steps, 1), "samples_per_second": samples / max(elapsed, 1e-9),
        "peak_vram_bytes": torch.cuda.max_memory_allocated(), "trainable_parameters": trainable, "total_parameters": total,
        "train_result": result.metrics, "effective_config": {"model": mc, "training": tc, "seed": cfg["seed"]}}
    write_json(args.metrics, metrics); print(json.dumps(metrics, indent=2))


if __name__ == "__main__": main()
