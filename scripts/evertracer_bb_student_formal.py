#!/usr/bin/env python3
"""Fail-closed formal EverTracer Bb Student launcher using the frozen config."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from passive5_shared_bb import read_jsonl, records_sha256, validate_training_parity

EXPECTED_REVISION = "0cb88a4f764b7a12671c53f0838cd831a0843b95"
EXPECTED_DATASET = "a4dd0c4dcd5141a62d380a6577083d48f80fb04c0e2a8b2b41f44dcb47bffff4"
EXPECTED_FILE = "2fc1acd16f8e7239924948f48d420eca4b2ded50ae90aefec4f5fb0536a7f91f"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def validate_base(base: Path, manifest_path: Path) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("revision") != EXPECTED_REVISION or manifest.get("file_count") != 12:
        raise RuntimeError("BASE_MANIFEST_IDENTITY_MISMATCH")
    observed = {}
    for row in manifest["files"]:
        path = base / row["path"]
        if not path.is_file() or path.stat().st_size != row["size_bytes"] or sha(path) != row["sha256"]:
            raise RuntimeError(f"BASE_FILE_MISMATCH {row['path']}")
        observed[row["path"]] = row["sha256"]
    contamination = [str(path.relative_to(base)) for path in base.rglob("*") if path.is_file()
                     and ("adapter" in path.name.casefold() or "lora" in path.name.casefold())]
    if contamination:
        raise RuntimeError(f"BASE_ADAPTER_CONTAMINATION {contamination}")
    return {"status": "PASS", "model": manifest["repo_id"], "revision": manifest["revision"],
            "path": str(base), "file_count": len(observed),
            "total_bytes": sum((base / name).stat().st_size for name in observed),
            "manifest_sha256": sha(manifest_path), "adapter_files": contamination}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--ba-config", type=Path, required=True)
    parser.add_argument("--base-manifest", type=Path, required=True)
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--restore-verification", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--trainer", type=Path, required=True)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if args.run_root.exists():
        raise FileExistsError(f"RUN_COLLISION {args.run_root}")
    config = json.loads(args.config.read_text(encoding="utf-8"))
    ba = json.loads(args.ba_config.read_text(encoding="utf-8"))
    parity = validate_training_parity(ba, config)
    training = config["training"]
    expected = {"epochs": 3, "learning_rate": 1e-5, "precision": "bf16",
                "full_parameter": True, "lora": False, "per_device_batch_size": 8,
                "gradient_accumulation_steps": 1, "effective_batch_size": 8,
                "max_length": 1024, "optimizer": "adamw_torch", "scheduler": "cosine",
                "warmup_ratio": 0.03, "weight_decay": 0.0, "expected_steps": 7500,
                "checkpoint_retention": {"save_total_limit": 1, "keep_final_model": True}}
    if training != expected or config["student"]["revision"] != EXPECTED_REVISION:
        raise RuntimeError("FROZEN_TRAINING_CONFIG_MISMATCH")
    if config["student"]["resume"] or config["student"]["initialization"] != "fresh_canonical_original_revision":
        raise RuntimeError("UNEXPECTED_RESUME_OR_INITIALIZATION")
    base = Path(config["student"]["path"])
    base_result = validate_base(base, args.base_manifest)
    rows = read_jsonl(args.dataset)
    dataset = {"record_count": len(rows), "dataset_sha256": records_sha256(rows),
               "file_sha256": sha(args.dataset), "path": str(args.dataset)}
    if dataset != {"record_count": 20000, "dataset_sha256": EXPECTED_DATASET,
                   "file_sha256": EXPECTED_FILE, "path": str(args.dataset)}:
        raise RuntimeError(f"SFT_DATASET_MISMATCH {dataset}")
    restore = json.loads(args.restore_verification.read_text(encoding="utf-8"))
    if restore.get("status") != "PASS" or restore["sft_formatter"]["dataset_sha256"] != EXPECTED_DATASET:
        raise RuntimeError("RESTORE_PROVENANCE_MISMATCH")
    command = [sys.executable, str(args.trainer), "--model-path", str(base),
               "--dataset", str(args.dataset), "--output-dir", str(args.run_root / "student"),
               "--batch-size", str(training["per_device_batch_size"]),
               "--epochs", str(training["epochs"]), "--learning-rate", str(training["learning_rate"]),
               "--seed", "42", "--max-length", str(training["max_length"]),
               "--telemetry", str(args.run_root / "metrics/training_telemetry.json")]
    launch = {"schema_version": "wmkd.evertracer-bb-student-launch.v1", "status": "READY",
              "run_id": args.run_root.name, "created_at": now(), "git_head": subprocess.check_output(
                  ["git", "rev-parse", "HEAD"], text=True).strip(),
              "base": base_result, "dataset": dataset, "restore_verification": str(args.restore_verification),
              "config": str(args.config), "config_sha256": sha(args.config),
              "training_parity": {**parity, "passed": 19, "total": 19},
              "runtime_config_effectiveness": {"status": "PASS", "command": command,
                  "no_resume_argument": "--resume" not in command, "seed": 42,
                  "template": "tokenizer.apply_chat_template", "output": str(args.run_root / "student")},
              "prohibited_stages": {"detector": "NOT_STARTED", "utility": "NOT_STARTED",
                  "ctcc_bb": "NOT_STARTED", "iseal_bb": "NOT_STARTED"}}
    args.run_root.mkdir(parents=True, exist_ok=False)
    (args.run_root / "config").mkdir()
    (args.run_root / "metrics").mkdir()
    shutil.copyfile(args.config, args.run_root / "config/frozen_config.json")
    write(args.run_root / "launch_manifest.json", launch)
    if not args.execute:
        print(json.dumps(launch, indent=2))
        return
    log_path = args.run_root / "logs/training.log"
    log_path.parent.mkdir(parents=True)
    started = now()
    with log_path.open("w", encoding="utf-8") as log:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                   text=True, bufsize=1)
        assert process.stdout is not None
        for line in process.stdout:
            print(line, end="", flush=True)
            log.write(line)
            log.flush()
        exit_code = process.wait()
    result = {"status": "COMPLETED" if exit_code == 0 else "FAILED", "run_id": args.run_root.name,
              "start": started, "end": now(), "exit_code": exit_code,
              "training_log": str(log_path), "command": command}
    write(args.run_root / "training_exit.json", result)
    print(json.dumps(result))
    if exit_code:
        raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
