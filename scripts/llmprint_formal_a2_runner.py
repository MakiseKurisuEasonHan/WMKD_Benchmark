"""Detached formal runner for the frozen LLMPrint A2 200x500 construction."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


EXPECTED_SUBSET_SHA256 = "162e27bccf4be98a3e15596772490dac44503363ac5781ac5365fea2d08f4a10"
EXPECTED_SOURCE_PAIR_SHA256 = "47443733c5a85ee1bcb131144d2b55a4ecab44ae8de752d978d99b1119ba0c37"
EXPECTED_SOURCE_COMMIT = "3e577f98b2bb64780ec2995b074c5aeec9b017e1"
EXPECTED_CONFIG_SHA256 = "4325b2a518aa5080dfb5cc070d57713bf6ee84efb9d72e8e4cbc89308920613a"
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


def validate_artifacts(fingerprint_dir: Path) -> tuple[int, list[str]]:
    valid = []
    errors = []
    for index in range(200):
        pair_id = f"llmprint-pair-{index:03d}"
        path = fingerprint_dir / f"{pair_id}.json"
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            if not (
                payload.get("pair_id") == pair_id
                and payload.get("status") == "COMPLETED"
                and payload.get("gcg_iterations_requested") == 500
                and payload.get("gcg_iterations_completed") == 500
                and len(payload.get("final_suffix_token_ids", [])) == 20
                and payload.get("experiment_label") == "A2"
                and payload.get("scientific_config_sha256") == EXPECTED_CONFIG_SHA256
            ):
                errors.append(f"invalid:{pair_id}")
            else:
                valid.append(pair_id)
        except Exception as error:
            errors.append(f"{pair_id}:{type(error).__name__}")
    return len(valid), errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--source-pairs", type=Path, required=True)
    parser.add_argument("--subset-pairs", type=Path, required=True)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--git-commit", required=True)
    parser.add_argument("--panel-sha256", required=True)
    args = parser.parse_args()

    if os.environ.get("CUBLAS_WORKSPACE_CONFIG") != EXPECTED_CUBLAS:
        raise RuntimeError("A2 requires CUBLAS_WORKSPACE_CONFIG=:4096:8")
    if sha256(args.source_pairs) != EXPECTED_SOURCE_PAIR_SHA256:
        raise RuntimeError("source 300-pair artifact SHA256 mismatch")
    if sha256(args.subset_pairs) != EXPECTED_SUBSET_SHA256:
        raise RuntimeError("A2 subset SHA256 mismatch")
    subset = json.loads(args.subset_pairs.read_text(encoding="utf-8"))
    if [pair["pair_id"] for pair in subset["pairs"]] != [f"llmprint-pair-{i:03d}" for i in range(200)]:
        raise RuntimeError("A2 subset identity/order mismatch")
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
        "--pairs", str(args.subset_pairs),
        "--output-dir", str(fingerprint_dir),
        "--max-pairs", "200",
        "--num-steps", "500",
        "--dtype", "float16",
        "--experiment-label", "A2",
        "--scientific-config-sha256", EXPECTED_CONFIG_SHA256,
    ]
    state = {
        "schema_version": "wmkd.llmprint-formal-run-status.v1",
        "experiment": "A2",
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
        "config_sha256": EXPECTED_CONFIG_SHA256,
        "source_pair_sha256": EXPECTED_SOURCE_PAIR_SHA256,
        "subset_pair_sha256": EXPECTED_SUBSET_SHA256,
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
        valid_count, errors = validate_artifacts(fingerprint_dir)
        state["validated_record_count"] = valid_count
        state["validation_errors"] = errors
        state["status"] = "COMPLETED" if return_code == 0 and valid_count == 200 and not errors else "FAILED"
    except BaseException as error:
        state["status"] = "FAILED"
        state["error"] = f"{type(error).__name__}: {error}"
        raise
    finally:
        state["finished_at"] = datetime.now(timezone.utc).isoformat()
        atomic_json(status_path, state)


if __name__ == "__main__":
    main()
