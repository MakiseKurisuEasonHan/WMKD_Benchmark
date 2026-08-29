"""Independent two-step trainability gate for iSeal Experiment A2."""

from iseal_trainability_audit import *  # reuse frozen cipher/data/audit helpers


class A2InstructionFingerprint(nn.Module):
    """Minimal A2 repair: model-native delta init, default Linear A, zero B."""

    def __init__(self, embedding, train_ids, inner_dim, delta_std):
        super().__init__()
        vocabulary, dimension = embedding.weight.shape
        device = embedding.weight.device
        id_to_row = torch.full((vocabulary,), -1, dtype=torch.long, device=device)
        id_to_row[train_ids] = torch.arange(len(train_ids), device=device)
        self.register_buffer("id2row", id_to_row, persistent=False)
        self.delta = nn.Embedding(len(train_ids), dimension, device=device)
        nn.init.normal_(self.delta.weight, mean=0.0, std=delta_std)
        self.A = nn.Linear(dimension, inner_dim, bias=False, device=device)
        self.B = nn.Linear(inner_dim, dimension, bias=False, device=device)
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
            base[mask] += self.B(self.A(self.delta(rows[mask])))
        return base

    def merge(self):
        """Pinned-public-code-equivalent merge for a standard reloadable checkpoint."""
        with torch.no_grad():
            residual = self.B(self.A(self.delta.weight))
            token_ids = torch.nonzero(self.id2row >= 0, as_tuple=True)[0]
            rows = self.id2row[token_ids]
            self.orig_emb.weight[token_ids] += residual[rows]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--dataset-cache", required=True)
    parser.add_argument("--optimizer-steps", type=int)
    parser.add_argument("--lineage-parent")
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
    tokenizer = AutoTokenizer.from_pretrained(config["model"]["path"], local_files_only=True, use_fast=False)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    dataset = load_dataset(config["dataset"]["id"], split="train", cache_dir=args.dataset_cache)
    dataset = dataset.shuffle(seed=config["dataset"]["shuffle_seed"]).select(range(config["dataset"]["registered_count"]))
    text_dataset = TextDataset(dataset["text"], tokenizer, config["training"]["max_sequence_length"])
    train_ids = sorted({token for row in text_dataset for token in row["input_ids"].tolist()})
    model = AutoModelForCausalLM.from_pretrained(config["model"]["path"], torch_dtype=torch.bfloat16, device_map="auto", low_cpu_mem_usage=True, local_files_only=True)
    original_embedding = model.get_input_embeddings()
    repair = config["training"]["initialization_repair"]
    adapter = A2InstructionFingerprint(original_embedding, train_ids, config["training"]["adapter_inner_dim"], repair["delta"]["std"])
    model.set_input_embeddings(adapter)
    for parameter in model.parameters(): parameter.requires_grad = False
    for parameter in adapter.parameters():
        if parameter is not adapter.orig_emb.weight: parameter.requires_grad = True
    model.lm_head.weight.requires_grad = True
    blocks = {
        "base_transformer": [p for name, p in model.named_parameters() if not name.startswith("model.embed_tokens") and name != "lm_head.weight"],
        "original_embeddings": [adapter.orig_emb.weight], "iseal_delta": [adapter.delta.weight],
        "iseal_A": [adapter.A.weight], "iseal_B": [adapter.B.weight], "lm_head": [model.lm_head.weight],
    }
    initial = {name: block_stats(params) for name, params in blocks.items()}
    snapshots = {name: [p.detach().float().cpu().clone() for p in params] for name, params in blocks.items()}
    cipher = KeyedCipher(model.config.hidden_size, config["training"]["cipher_layers"], secret_key, torch.bfloat16)
    loader = DataLoader(text_dataset, batch_size=config["training"]["per_device_batch_size"], shuffle=True)
    optimizer = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=config["training"]["learning_rate"], weight_decay=config["training"]["weight_decay"], eps=config["training"]["adam_epsilon"])
    steps = args.optimizer_steps or config["trainability_audit"]["optimizer_steps"]
    scheduler = get_linear_schedule_with_warmup(optimizer, max(1, int(config["training"]["warmup_ratio"] * steps)), steps)
    records=[]; iterator=iter(loader)
    for step in range(steps):
        batch=next(iterator); device=next(model.parameters()).device
        ids=batch["input_ids"].to(device); mask=batch["attention_mask"].to(device); labels=batch["labels"].to(device)
        output=model(inputs_embeds=cipher.to(device)(model.get_input_embeddings()(ids)), attention_mask=mask, labels=labels)
        effective_lr=optimizer.param_groups[0]["lr"]
        output.loss.backward(); gradients={name:grad_norm(params) for name,params in blocks.items()}
        torch.nn.utils.clip_grad_norm_(model.parameters(),config["training"]["max_grad_norm"])
        optimizer.step(); scheduler.step(); optimizer.zero_grad()
        cumulative_deltas={name:delta_norm(params,snapshots[name]) for name,params in blocks.items()}
        records.append({"step":step+1,"effective_learning_rate":effective_lr,"loss":output.loss.item(),"gradient_norms_before_clip":gradients,"cumulative_parameter_delta_norms_after_step":cumulative_deltas,"task_gradient_nonzero":{name:gradients[name]>0 for name in blocks}})
    deltas={name:delta_norm(params,snapshots[name]) for name,params in blocks.items()}
    b_started=records[0]["gradient_norms_before_clip"]["iseal_B"]>0 and deltas["iseal_B"]>0
    downstream=any(record["effective_learning_rate"]>0 and record["gradient_norms_before_clip"][name]>0 for record in records[2:] for name in ("iseal_delta","iseal_A")) if len(records)>2 else False
    transformer_frozen=deltas["base_transformer"]==0
    gate=b_started and downstream and transformer_frozen
    result={"project":config["project"],"method":"iSeal","experiment":"A2","audit":"a2_initialization_repair_trainability","lineage_parent":args.lineage_parent,"diagnostic_duration_extension_only":args.optimizer_steps is not None,"optimizer_steps":steps,"official_commit":config["official_source"]["commit"],"model_revision":config["model"]["revision"],"initialization_repair":repair,"registered_count":len(dataset),"trainable_token_count":len(train_ids),"blocks":initial,"steps":records,"parameter_delta_norms":deltas,"update_interpretation":{"nonzero_task_gradient_with_positive_lr":"task-gradient-driven update present","zero_task_gradient_with_nonzero_delta":"weight-decay-only movement; not adapter progression"},"checks":{"B_started_step1":b_started,"A_or_delta_task_gradient_progression_after_B_update":downstream,"base_transformer_frozen":transformer_frozen},"gate_passed":gate,"formal_experiment_a2_allowed":gate,"terminal_state":"PASSED" if gate else "BLOCKED_SCIENTIFIC_IMPLEMENTATION_TRAINABILITY"}
    output=Path(args.output); output.parent.mkdir(parents=True,exist_ok=True); output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2)); raise SystemExit(0 if gate else 3)


if __name__ == "__main__": main()
