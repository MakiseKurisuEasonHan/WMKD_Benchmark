#!/usr/bin/env python3
"""Deterministic resumable teacher-generated QA for formal PN-FP Ba."""

import argparse
import json
import random
import re
import time
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from distillation_data import enforce_generation_progress_limits

CATEGORIES = ("general knowledge", "reasoning", "writing", "summarization or editing",
              "classification", "mathematics", "coding", "reading comprehension")


def extract_records(text):
    records = []
    for match in re.finditer(r"\{[^{}]+\}", text, re.DOTALL):
        try:
            item = json.loads(match.group(0))
        except json.JSONDecodeError:
            continue
        if all(key in item for key in ("instruction", "input", "answer")):
            records.append(item)
    return records


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-path", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--errors", required=True)
    parser.add_argument("--target-candidates", type=int, default=24000)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--records-per-prompt", type=int, default=4)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max-total-calls", type=int, default=12000)
    parser.add_argument("--max-consecutive-zero-calls", type=int, default=64)
    parser.add_argument("--max-wall-seconds", type=int, default=43200)
    parser.add_argument("--acceptance-warmup-calls", type=int, default=200)
    parser.add_argument("--minimum-records-per-call", type=float, default=0.5)
    args = parser.parse_args()
    random.seed(args.seed); torch.manual_seed(args.seed); torch.cuda.manual_seed_all(args.seed)
    output = Path(args.output); output.parent.mkdir(parents=True, exist_ok=True)
    existing = sum(1 for line in output.open(encoding="utf-8")) if output.exists() else 0
    tokenizer = AutoTokenizer.from_pretrained(args.model_path, local_files_only=True)
    tokenizer.pad_token = tokenizer.pad_token or tokenizer.eos_token
    tokenizer.padding_side = "left"
    model = AutoModelForCausalLM.from_pretrained(
        args.model_path, local_files_only=True, torch_dtype=torch.bfloat16, device_map="cuda"
    ).eval()
    prompt_index = existing // args.records_per_prompt
    started = time.monotonic(); total_calls = 0; accepted_this_run = 0; consecutive_zero_calls = 0
    with output.open("a", encoding="utf-8", buffering=1) as sink, Path(args.errors).open("a", encoding="utf-8", buffering=1) as errors:
        while existing < args.target_candidates:
            prompts = []
            indices = []
            for offset in range(args.batch_size):
                idx = prompt_index + offset
                category = CATEGORIES[idx % len(CATEGORIES)]
                content = (
                    f"Create exactly {args.records_per_prompt} diverse, self-contained training examples in the category {category}. "
                    "Return JSON objects, one per line, with exactly the string fields instruction, input, answer. "
                    "Use an empty input when no context is needed. Answers must be correct, useful, and non-empty. "
                    f"Generation seed index: {idx}. Do not use markdown fences or commentary."
                )
                prompts.append(tokenizer.apply_chat_template([{"role":"user","content":content}], tokenize=False, add_generation_prompt=True))
                indices.append(idx)
            encoded = tokenizer(prompts, return_tensors="pt", padding=True, add_special_tokens=False).to("cuda")
            with torch.inference_mode():
                generated = model.generate(**encoded, max_new_tokens=768, do_sample=True, temperature=0.8,
                                           top_p=0.95, generator=None, pad_token_id=tokenizer.pad_token_id)
            for row, idx in zip(generated, indices):
                total_calls += 1
                text = tokenizer.decode(row[encoded["input_ids"].shape[1]:], skip_special_tokens=True)
                records = extract_records(text)
                if not records:
                    errors.write(json.dumps({"prompt_index": idx, "reason": "parse_failure", "raw": text}, ensure_ascii=False) + "\n")
                    consecutive_zero_calls += 1
                    continue
                consecutive_zero_calls = 0
                for item in records:
                    sink.write(json.dumps({"candidate_index": existing, "prompt_index": idx, "category": CATEGORIES[idx % len(CATEGORIES)],
                                           "instruction": item["instruction"], "input": item["input"],
                                           "teacher_raw_answer": item["answer"]}, ensure_ascii=False) + "\n")
                    existing += 1
                    accepted_this_run += 1
                    if existing >= args.target_candidates: break
            prompt_index += args.batch_size
            print(json.dumps({"candidate_count": existing, "target": args.target_candidates}), flush=True)
            elapsed = time.monotonic() - started
            enforce_generation_progress_limits(total_calls=total_calls, accepted=accepted_this_run,
                consecutive_zero=consecutive_zero_calls, elapsed=elapsed,
                max_total_calls=args.max_total_calls, max_consecutive_zero=args.max_consecutive_zero_calls,
                max_wall_seconds=args.max_wall_seconds, warmup_calls=args.acceptance_warmup_calls,
                minimum_records_per_call=args.minimum_records_per_call)

if __name__ == "__main__": main()
