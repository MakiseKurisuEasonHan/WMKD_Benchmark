"""Detached-runner payload for the frozen LLMPrint formal A construction."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


EXPECTED_PAIR_SHA256 = "47443733c5a85ee1bcb131144d2b55a4ecab44ae8de752d978d99b1119ba0c37"
EXPECTED_SOURCE_COMMIT = "3e577f98b2bb64780ec2995b074c5aeec9b017e1"
EXPECTED_CUBLAS = ":4096:8"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_json(path: Path, payload: dict) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--pairs", type=Path, required=True)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--git-commit", required=True)
    parser.add_argument("--config-sha256", required=True)
    parser.add_argument("--panel-sha256", required=True)
    args = parser.parse_args()

    if os.environ.get("CUBLAS_WORKSPACE_CONFIG") != EXPECTED_CUBLAS:
        raise RuntimeError("formal runner requires CUBLAS_WORKSPACE_CONFIG=:4096:8")
    if sha256(args.pairs) != EXPECTED_PAIR_SHA256:
        raise RuntimeError("pair artifact SHA256 mismatch")
    source_commit = subprocess.check_output(
        ["git", "-C", str(args.source), "rev-parse", "HEAD"], text=True
    ).strip()
    if source_commit != EXPECTED_SOURCE_COMMIT:
        raise RuntimeError("pinned LLMPrint source commit mismatch")

    fingerprint_dir = args.run_dir / "fingerprints"
    status_path = args.run_dir / "status.json"
    args.run_dir.mkdir(parents=True, exist_ok=False)
    fingerprint_dir.mkdir()
    command = [
        sys.executable,
        str(args.project / "scripts" / "llmprint_construct_fingerprints.py"),
        "--source", str(args.source),
        "--model", str(args.model),
        "--pairs", str(args.pairs),
        "--output-dir", str(fingerprint_dir),
        "--max-pairs", "300",
        "--num-steps", "1000",
        "--dtype", "float16",
    ]
    state = {
        "schema_version": "wmkd.llmprint-formal-run-status.v1",
        "run_id": args.run_id,
        "status": "STARTING",
        "runner_pid": os.getpid(),
        "scientific_pid": None,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "finished_at": None,
        "exit_code": None,
        "command": command,
        "cublas_workspace_config": EXPECTED_CUBLAS,
        "git_commit": args.git_commit,
        "source_commit": source_commit,
        "canonical_revision": "0cb88a4f764b7a12671c53f0838cd831a0843b95",
        "config_sha256": args.config_sha256,
        "pair_sha256": EXPECTED_PAIR_SHA256,
        "panel_sha256": args.panel_sha256,
        "fingerprint_dir": str(fingerprint_dir),
    }
    atomic_json(status_path, state)
    try:
        process = subprocess.Popen(command)
        state["status"] = "RUNNING"
        state["scientific_pid"] = process.pid
        atomic_json(status_path, state)
        return_code = process.wait()
        state["exit_code"] = return_code
        records = list(fingerprint_dir.glob("llmprint-pair-*.json"))
        state["validated_record_count"] = len(records)
        state["status"] = "COMPLETED" if return_code == 0 and len(records) == 300 else "FAILED"
    except BaseException as error:
        state["status"] = "FAILED"
        state["error"] = f"{type(error).__name__}: {error}"
        raise
    finally:
        state["finished_at"] = datetime.now(timezone.utc).isoformat()
        atomic_json(status_path, state)


if __name__ == "__main__":
    main()
