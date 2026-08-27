"""Offline-only tokenizer, model-load, and short-generation smoke test."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-path", type=Path, required=True)
    parser.add_argument("--max-new-tokens", type=int, default=4)
    args = parser.parse_args()

    model_path = args.model_path.resolve(strict=True)
    tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
    print(json.dumps({"tokenizer_load": "passed", "vocab_size": len(tokenizer)}))

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is unavailable; refusing the GPU model smoke test")

    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        local_files_only=True,
        torch_dtype=torch.bfloat16,
        device_map={"": 0},
    )
    print(json.dumps({"model_load": "passed", "device": str(model.device)}))

    prompt = "Reply with one word: ready"
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.inference_mode():
        output = model.generate(
            **inputs,
            max_new_tokens=args.max_new_tokens,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
        )
    generated = tokenizer.decode(output[0][inputs["input_ids"].shape[1] :], skip_special_tokens=True)
    print(json.dumps({"generation_smoke": "passed", "text": generated}))


if __name__ == "__main__":
    main()
