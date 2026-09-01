"""Construct recoverable LLMPrint fingerprints with pinned upstream GCG semantics."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import time
from pathlib import Path


PROMPT_TEMPLATE = "Randomly output a word from your vocabulary {optim_str}"
INIT_SUFFIX = "x x x x x x x x x x x x x x x x x x x x"


def atomic_json(path: Path, payload: dict) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def valid_success(path: Path, expected_id: str) -> bool:
    if not path.exists():
        return False
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return value.get("pair_id") == expected_id and value.get("status") == "COMPLETED"


def load_gcg(source: Path):
    module_path = source / "create_adv_prompt.py"
    spec = importlib.util.spec_from_file_location("llmprint_create_adv_prompt", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import pinned upstream optimizer: {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--pairs", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--max-pairs", type=int, default=None)
    parser.add_argument("--num-steps", type=int, default=1000)
    parser.add_argument("--dtype", choices=("float16", "bfloat16"), default="float16")
    args = parser.parse_args()

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is required")
    gcg = load_gcg(args.source)
    pair_package = json.loads(args.pairs.read_text(encoding="utf-8"))
    pairs = pair_package["pairs"][: args.max_pairs]
    args.output_dir.mkdir(parents=True, exist_ok=True)

    tokenizer = AutoTokenizer.from_pretrained(args.model, local_files_only=True)
    dtype = torch.float16 if args.dtype == "float16" else torch.bfloat16
    load_start = time.perf_counter()
    model = AutoModelForCausalLM.from_pretrained(args.model, local_files_only=True, torch_dtype=dtype)
    model.to("cuda:0").eval()
    load_seconds = time.perf_counter() - load_start

    for pair in pairs:
        output = args.output_dir / f"{pair['pair_id']}.json"
        if valid_success(output, pair["pair_id"]):
            print(f"skip validated {pair['pair_id']}")
            continue
        if output.exists():
            raise RuntimeError(f"invalid existing record; fail closed: {output}")
        config = gcg.GCGConfig_target(
            num_steps=args.num_steps,
            optim_str_init=INIT_SUFFIX,
            search_width=64,
            topk=64,
            n_replace=1,
            use_prefix_cache=True,
            allow_non_ascii=False,
            filter_ids=True,
            seed=42,
            verbosity="WARNING",
            target_word1=pair["w_plus"],
            target_word2=pair["w_minus"],
            alpha=0.5,
            beta=1.0,
            margin=0.0,
        )
        started = time.perf_counter()
        result = gcg.run(model, tokenizer, PROMPT_TEMPLATE, config)
        runtime = time.perf_counter() - started
        final_ids = [int(item) for item in result.best_ids.detach().cpu().reshape(-1).tolist()]
        final_text = tokenizer.decode(final_ids, skip_special_tokens=False)
        complete_prompt = PROMPT_TEMPLATE.format(optim_str=final_text)
        input_ids = tokenizer(complete_prompt, add_special_tokens=False, return_tensors="pt")["input_ids"].to("cuda:0")
        with torch.no_grad():
            logits = model(input_ids=input_ids).logits[0, -1].float()
            probs = torch.softmax(logits, dim=-1)
        pos_id = pair["w_plus_token_id"]
        neg_id = pair["w_minus_token_id"]
        record = {
            **pair,
            "status": "COMPLETED",
            "full_fixed_prompt": PROMPT_TEMPLATE,
            "initial_suffix_text": INIT_SUFFIX,
            "initial_suffix_token_ids": tokenizer.encode(INIT_SUFFIX, add_special_tokens=False),
            "final_suffix_text": final_text,
            "final_suffix_token_ids": final_ids,
            "complete_optimized_prompt": complete_prompt,
            "alpha": 0.5,
            "beta": 1.0,
            "margin": 0.0,
            "gcg_iterations_requested": args.num_steps,
            "gcg_iterations_completed": len(result.losses),
            "best_loss": float(result.best_loss),
            "loss_first": float(result.losses[0]),
            "loss_final_iteration": float(result.losses[-1]),
            "w_plus_logit": float(logits[pos_id]),
            "w_minus_logit": float(logits[neg_id]),
            "w_plus_probability": float(probs[pos_id]),
            "w_minus_probability": float(probs[neg_id]),
            "preference_margin": float(logits[pos_id] - logits[neg_id]),
            "reference_bit": int(logits[pos_id] >= logits[neg_id]),
            "runtime_seconds": runtime,
            "model_load_seconds": load_seconds,
            "model_path": str(args.model),
            "model_modified": False,
            "dtype": str(dtype),
            "torch_version": torch.__version__,
            "cuda_version": torch.version.cuda,
            "gpu": torch.cuda.get_device_name(0),
            "peak_vram_bytes": int(torch.cuda.max_memory_allocated(0)),
            "upstream_commit": "3e577f98b2bb64780ec2995b074c5aeec9b017e1",
        }
        atomic_json(output, record)
        print(json.dumps({"pair_id": pair["pair_id"], "runtime_seconds": runtime, "best_loss": result.best_loss}))


if __name__ == "__main__":
    main()
