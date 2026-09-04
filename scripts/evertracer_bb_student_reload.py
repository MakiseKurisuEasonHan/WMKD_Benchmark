#!/usr/bin/env python3
"""Fresh-process reload and integrity validation for EverTracer Bb Student."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import time
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    os.replace(temporary, path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--student", type=Path, required=True)
    parser.add_argument("--dataset-sha", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()

    files = {
        str(path.relative_to(args.student)): sha256(path)
        for path in sorted(args.student.rglob("*"))
        if path.is_file()
    }
    adapters = [
        name
        for name in files
        if "adapter" in name.casefold() or "lora" in name.casefold()
    ]
    if adapters:
        raise RuntimeError(f"UNEXPECTED_ADAPTER_FILES {adapters}")

    manifest = {
        "schema_version": "wmkd.evertracer-bb-student.v1",
        "status": "PASS",
        "run_id": args.run_id,
        "artifact": str(args.student),
        "dataset_sha256": args.dataset_sha,
        "files_sha256": files,
        "file_count": len(files),
        "full_parameter": True,
        "resume": False,
        "base_model": "meta-llama/Llama-3.2-3B-Instruct",
        "base_revision": "0cb88a4f764b7a12671c53f0838cd831a0843b95",
    }
    atomic_json(args.manifest, manifest)

    started = time.time()
    torch.cuda.reset_peak_memory_stats()
    tokenizer = AutoTokenizer.from_pretrained(
        args.student, local_files_only=True, trust_remote_code=True
    )
    model = AutoModelForCausalLM.from_pretrained(
        args.student,
        local_files_only=True,
        trust_remote_code=True,
        torch_dtype=torch.bfloat16,
        device_map="cuda:0",
    ).eval()

    prompt = "Reply briefly with the name of Earth's natural satellite."
    rendered = tokenizer.apply_chat_template(
        [{"role": "user", "content": prompt}],
        tokenize=False,
        add_generation_prompt=True,
    )
    encoded = tokenizer(rendered, return_tensors="pt").to("cuda:0")
    with torch.inference_mode():
        generated = model.generate(**encoded, max_new_tokens=16, do_sample=False)
    response = tokenizer.decode(
        generated[0, encoded["input_ids"].shape[1] :], skip_special_tokens=True
    ).strip()

    parameter_count = 0
    nonfinite_count = 0
    minimum = math.inf
    maximum = -math.inf
    with torch.inference_mode():
        for parameter in model.parameters():
            value = parameter.detach()
            parameter_count += value.numel()
            finite = torch.isfinite(value)
            current_bad = value.numel() - int(finite.sum())
            nonfinite_count += current_bad
            if current_bad == 0 and value.numel():
                minimum = min(minimum, float(value.min()))
                maximum = max(maximum, float(value.max()))

    result = {
        "schema_version": "wmkd.evertracer-bb-student-reload.v1",
        "status": "PASS" if response and nonfinite_count == 0 else "FAIL",
        "run_id": args.run_id,
        "fresh_process_reload": True,
        "student_path": str(args.student),
        "student_manifest_sha256": sha256(args.manifest),
        "tokenizer": {
            "class": tokenizer.__class__.__name__,
            "vocab_size": len(tokenizer),
            "chat_template_present": bool(tokenizer.chat_template),
        },
        "inference_smoke": {
            "prompt": prompt,
            "response": response,
            "pass": bool(response),
        },
        "finite_weight_check": {
            "parameter_count": parameter_count,
            "nonfinite_count": nonfinite_count,
            "minimum": minimum,
            "maximum": maximum,
            "pass": nonfinite_count == 0,
        },
        "adapter_files": adapters,
        "peak_vram_bytes": torch.cuda.max_memory_allocated(),
        "runtime_seconds": time.time() - started,
    }
    atomic_json(args.output, result)
    print(json.dumps(result, ensure_ascii=False))
    if result["status"] != "PASS":
        raise RuntimeError("EVERTRACER_BB_STUDENT_RELOAD_VALIDATION_FAILED")


if __name__ == "__main__":
    main()
