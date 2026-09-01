"""Construct recoverable LLMPrint fingerprints with pinned upstream GCG semantics."""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import os
import sys
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
    # Python 3.12 dataclasses resolve annotations through sys.modules while
    # the class decorators execute, so register the dynamic module first.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    # The release pins transformers 4.51.3, whose DynamicCache is mutated in
    # place.  The upstream optimizer reuses one prefix cache as if it were an
    # immutable legacy tuple and therefore fails when a candidate batch has
    # more than one row.  Keep prefix caching enabled and preserve identical
    # logits by cloning the fixed prefix for every forward and repeating only
    # its batch dimension for the current candidate chunk.
    original_gradient = module.GCG.compute_token_gradient

    def compatible_gradient(self, optim_ids):
        original_cache = self.prefix_cache
        if original_cache is None or not hasattr(original_cache, "batch_repeat_interleave"):
            return original_gradient(self, optim_ids)
        self.prefix_cache = copy.deepcopy(original_cache)
        try:
            return original_gradient(self, optim_ids)
        finally:
            self.prefix_cache = original_cache

    def compatible_candidate_loss(self, search_batch_size, input_embeds):
        import torch

        all_loss = []
        for index in range(0, input_embeds.shape[0], search_batch_size):
            with torch.no_grad():
                batch_embeds = input_embeds[index : index + search_batch_size]
                current_batch_size = batch_embeds.shape[0]
                if self.prefix_cache is not None:
                    cache = copy.deepcopy(self.prefix_cache)
                    if hasattr(cache, "batch_repeat_interleave") and current_batch_size > 1:
                        cache.batch_repeat_interleave(current_batch_size)
                    outputs = self.model(
                        inputs_embeds=batch_embeds,
                        past_key_values=cache,
                        use_cache=True,
                    )
                else:
                    outputs = self.model(inputs_embeds=batch_embeds)
                first_token_logits = outputs.logits[:, -1, :]
                loss = module.custom_loss(
                    first_token_logits,
                    self.target_token_ids[0],
                    self.target_token_ids[1],
                    alpha=self.config.alpha,
                    beta=self.config.beta,
                    margin=self.config.margin,
                )
                loss = loss * torch.ones(current_batch_size, device=loss.device)
                all_loss.append(loss)
                del outputs
                module.gc.collect()
                module._empty_cuda_cache()
        return torch.cat(all_loss, dim=0)

    module.GCG.compute_token_gradient = compatible_gradient
    module.GCG._compute_candidates_loss = compatible_candidate_loss
    return module


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--pairs", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--max-pairs", type=int, default=None)
    parser.add_argument("--scientific-config-sha256")
    parser.add_argument("--experiment-label", default="A")
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
            "runtime_compatibility": "immutable_dynamic_prefix_cache_batch_repeat",
            "experiment_label": args.experiment_label,
            "scientific_config_sha256": args.scientific_config_sha256,
            "warnings": [],
            "error": None,
        }
        atomic_json(output, record)
        print(json.dumps({"pair_id": pair["pair_id"], "runtime_seconds": runtime, "best_loss": result.best_loss}))


if __name__ == "__main__":
    main()
