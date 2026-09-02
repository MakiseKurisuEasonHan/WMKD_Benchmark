#!/usr/bin/env python3
"""Evaluation-only continuation for the immutable Passive-5 Shared Ba Student."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

EXPECTED = {
    "dataset_sha256": "eb90c3e0c95e37d07bf0f099aaeabeedf1779bae7ef8a4aacf25e3fb8bed6ab7",
    "frozen_jsonl_sha256": "408053fef5fa42b3a203e70ac049f43b73f9b0fccb06189363d0643c3633cbed",
    "manifest_sha256": "488b7b11533c12aee6f7aa0d44a53bb3acf03dc065d7a0f12c954701ee11426e",
    "sample_ids_sha256": "7cef00810ca079eaf3557bb40222314a3d9f23c1db5ee9f1f386d87845dbab93",
    "provenance_sha256": "253f18da0bec906265044bced1d9a7f22a7861a69b4ec905a2653ed4dd0b7633",
    "config_sha256": "65d4eb83fa7706a0af80adaf2664ad20600208ac964171411bd8cac002c12839",
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def atomic_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(temp, path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--parent-run-id", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--stage", choices=("reload-validation",), required=True)
    args = parser.parse_args()

    parent = args.data_root / "runs/passive5_shared_ba" / args.parent_run_id
    student = parent / "student/final_model"
    output = args.data_root / "runs/passive5_shared_ba_eval" / args.run_id
    status_path = output / "status.json"
    status = {
        "schema_version": "wmkd.passive5-shared-ba-eval.v1",
        "run_id": args.run_id,
        "parent_run_id": args.parent_run_id,
        "continuation_type": "EVALUATION_ONLY_CONTINUATION",
        "state": "RUNNING",
        "stage": "IMMUTABLE_PREFLIGHT",
        "started_at": now(),
        "auto_shutdown": False,
    }
    atomic_json(status_path, status)
    started = time.time()
    try:
        paths = {
            "frozen_jsonl_sha256": parent / "dataset/frozen_qa.jsonl",
            "manifest_sha256": parent / "dataset/manifest.json",
            "provenance_sha256": parent / "dataset/provenance.json",
            "config_sha256": args.project / "configs/distillation/passive5_shared_ba.json",
        }
        observed = {name: sha256(path) for name, path in paths.items()}
        manifest = json.loads(paths["manifest_sha256"].read_text(encoding="utf-8"))
        observed["dataset_sha256"] = manifest["dataset_sha256"]
        observed["sample_ids_sha256"] = manifest["sample_ids_sha256"]
        mismatches = {key: {"expected": EXPECTED[key], "observed": observed.get(key)}
                      for key in EXPECTED if observed.get(key) != EXPECTED[key]}
        student_manifest_path = parent / "student/student_manifest.json"
        student_manifest = json.loads(student_manifest_path.read_text(encoding="utf-8"))
        file_checks = []
        for relative, expected in student_manifest["files_sha256"].items():
            path = student / relative
            actual = sha256(path)
            file_checks.append({"path": relative, "expected": expected, "observed": actual,
                                "pass": actual == expected})
        if mismatches or not all(item["pass"] for item in file_checks):
            raise RuntimeError(f"FAIL_CLOSED_IMMUTABLE_HASH_MISMATCH: {mismatches}")
        if student_manifest.get("status") != "PASS" or student_manifest.get("dataset_sha256") != EXPECTED["dataset_sha256"]:
            raise RuntimeError("FAIL_CLOSED_STUDENT_MANIFEST_MISMATCH")

        status.update(stage="STUDENT_FRESH_RELOAD_VALIDATION", immutable_preflight="PASS", updated_at=now())
        atomic_json(status_path, status)
        torch.cuda.reset_peak_memory_stats()
        tokenizer = AutoTokenizer.from_pretrained(student, local_files_only=True, trust_remote_code=True)
        if not getattr(tokenizer, "chat_template", None):
            raise RuntimeError("STUDENT_CHAT_TEMPLATE_MISSING")
        model = AutoModelForCausalLM.from_pretrained(
            student, local_files_only=True, trust_remote_code=True,
            torch_dtype=torch.bfloat16, device_map="cuda:0",
        ).eval()
        config = model.config
        adapter_files = [str(path.relative_to(student)) for path in student.rglob("*")
                         if path.is_file() and ("adapter" in path.name.lower() or "lora" in path.name.lower())]
        if adapter_files:
            raise RuntimeError(f"UNEXPECTED_ADAPTER_FILES: {adapter_files}")
        prompt = "Reply with exactly: WMKD_RELOAD_PASS"
        rendered = tokenizer.apply_chat_template(
            [{"role": "user", "content": prompt}], tokenize=False, add_generation_prompt=True
        )
        encoded = tokenizer(rendered, return_tensors="pt").to("cuda:0")
        with torch.inference_mode():
            generated = model.generate(**encoded, max_new_tokens=16, do_sample=False)
        new_tokens = generated[0, encoded["input_ids"].shape[1]:]
        response = tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
        inference_pass = bool(response)

        parameter_count = 0
        nonfinite_count = 0
        global_min = math.inf
        global_max = -math.inf
        tensors_scanned = 0
        with torch.inference_mode():
            for parameter in model.parameters():
                value = parameter.detach()
                parameter_count += value.numel()
                tensors_scanned += 1
                finite = torch.isfinite(value)
                bad = value.numel() - int(finite.sum().item())
                nonfinite_count += bad
                if bad == 0 and value.numel():
                    global_min = min(global_min, float(value.min().item()))
                    global_max = max(global_max, float(value.max().item()))
        validation = {
            "status": "PASS" if inference_pass and nonfinite_count == 0 else "FAIL",
            "fresh_process_reload": True,
            "student_path": str(student),
            "student_manifest_path": str(student_manifest_path),
            "student_manifest_sha256": sha256(student_manifest_path),
            "immutable_hashes": observed,
            "student_file_checks": file_checks,
            "config": {
                "architecture": config.architectures,
                "model_type": config.model_type,
                "hidden_size": config.hidden_size,
                "num_hidden_layers": config.num_hidden_layers,
                "vocab_size": config.vocab_size,
                "torch_dtype": str(config.torch_dtype),
            },
            "tokenizer": {
                "class": tokenizer.__class__.__name__,
                "vocab_size": len(tokenizer),
                "chat_template_present": bool(tokenizer.chat_template),
            },
            "adapter_files": adapter_files,
            "inference_smoke": {"prompt": prompt, "response": response, "pass": inference_pass},
            "finite_weight_check": {
                "parameter_count": parameter_count,
                "tensors_scanned": tensors_scanned,
                "nonfinite_count": nonfinite_count,
                "minimum": global_min,
                "maximum": global_max,
                "pass": nonfinite_count == 0,
            },
            "peak_vram_bytes": int(torch.cuda.max_memory_allocated()),
            "runtime_seconds": time.time() - started,
            "completed_at": now(),
        }
        atomic_json(output / "student_reload_validation.json", validation)
        if validation["status"] != "PASS":
            raise RuntimeError("STUDENT_RELOAD_VALIDATION_FAILED")
        status.update(state="COMPLETED", stage="STUDENT_RELOAD_VALIDATION_COMPLETED",
                      reload_validation="PASS", terminal=True, updated_at=now())
        atomic_json(status_path, status)
        print(json.dumps({"run_id": args.run_id, "validation": validation}, ensure_ascii=False), flush=True)
    except Exception as exc:
        status.update(state="FAILED", stage="FAILED", terminal=True,
                      failure=f"{type(exc).__name__}: {exc}", updated_at=now())
        atomic_json(status_path, status)
        raise


if __name__ == "__main__":
    main()
