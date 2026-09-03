#!/usr/bin/env python3
"""Prepare one method-specific proactive Bb config without changing Bb3 science."""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

try:
    from scripts.passive5_shared_bb import file_sha256, read_jsonl, records_sha256
except ModuleNotFoundError:
    from passive5_shared_bb import file_sha256, read_jsonl, records_sha256


METHODS = {
    "pnfp": "PN-FP",
    "evertracer": "EverTracer",
    "ctcc": "CTCC",
    "iseal": "iSeal",
    "scw": "SCW",
}
FROZEN_PROMPT_SHA256 = "7f4284788b5147bca7f444db989eab6f2f9f3a10eb06fddb309fc06748414495"
SCIENTIFIC_SECTIONS = ("paraphraser", "paraphrase", "quality", "student", "training")


def assert_frozen_reference(reference: dict) -> None:
    p = reference["paraphrase"]
    atomic = p["atomic_identity_preservation"]
    assert reference["paraphraser"]["canonical_upstream"] == "Qwen/Qwen2.5-3B-Instruct"
    assert p["prompt_sha256"] == FROZEN_PROMPT_SHA256
    assert p["do_sample"] is True and p["temperature"] == 0.7 and p["top_p"] == 0.9 and p["seed"] == 42
    assert atomic["enabled"] is True and atomic["qwen_non_special_token_threshold"] == 1
    assert atomic["add_special_tokens"] is False


def inspect_parent(path: Path) -> dict:
    rows = read_jsonl(path)
    if len(rows) != 20_000:
        raise ValueError(f"PARENT_COUNT_MISMATCH observed={len(rows)}")
    required = {"sample_id", "instruction", "input", "teacher_raw_answer"}
    if any(not required.issubset(row) for row in rows):
        raise ValueError("PARENT_SCHEMA_MISMATCH")
    ids = [{"sample_id": row["sample_id"]} for row in rows]
    return {
        "record_count": len(rows),
        "record_schema": sorted(required),
        "dataset_sha256": records_sha256(rows),
        "frozen_jsonl_sha256": file_sha256(path),
        "sample_ids_sha256": records_sha256(ids),
    }


def build_config(reference: dict, *, method_slug: str, parent_path: Path,
                 parent_run_id: str, parent_teacher: str, run_id: str) -> dict:
    if method_slug not in METHODS:
        raise ValueError(f"UNKNOWN_METHOD {method_slug}")
    assert_frozen_reference(reference)
    identity = inspect_parent(parent_path)
    config = {key: copy.deepcopy(value) for key, value in reference.items()}
    method = METHODS[method_slug]
    config.update({
        "schema_version": "wmkd.proactive-bb-config.v1",
        "project": "WMKD_Benchmark",
        "experiment": "Bb",
        "method": method,
        "run_id": run_id,
        "status": "PREPARED_NOT_STARTED",
        "scientific_reference": "Passive Shared Bb3 frozen implementation",
        "paired_dataset_schema_version": "wmkd.proactive-bb-paired-dataset.v1",
    })
    config["source_dataset"] = {
        "parent_experiment": f"{method} Ba",
        "parent_run_id": parent_run_id,
        "parent_teacher": parent_teacher,
        "path": str(parent_path),
        "manifest_path": None,
        **identity,
    }
    root = f"/root/autodl-tmp/WMKD_Benchmark_data/runs/{method_slug}_bb/{{run_id}}"
    config["paths"] = {
        "run_root": root,
        "records_journal": "paraphrase/attempts.jsonl",
        "progress": "paraphrase/progress.json",
        "frozen_paired_dataset": "dataset/frozen_paired_qa.jsonl",
        "student_dataset": "dataset/student_qa.jsonl",
        "student_output": "student/final_model",
        "full_experiment_log": f"results/{method_slug}/experiment_bb/full_experiment_log.json",
        "provenance_manifest": f"results/{method_slug}/experiment_bb/provenance_manifest.json",
        "artifact_manifest": f"results/{method_slug}/experiment_bb/artifact_manifest.json",
        "formal_report": f"docs/reproduction_reports/{method_slug}_experiment_bb_report.md",
    }
    return config


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reference-config", type=Path, required=True)
    ap.add_argument("--method", choices=sorted(METHODS), required=True)
    ap.add_argument("--parent-frozen20k", type=Path, required=True)
    ap.add_argument("--parent-run-id", required=True)
    ap.add_argument("--parent-teacher", required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    reference = json.loads(args.reference_config.read_text(encoding="utf-8"))
    config = build_config(reference, method_slug=args.method, parent_path=args.parent_frozen20k,
                          parent_run_id=args.parent_run_id, parent_teacher=args.parent_teacher,
                          run_id=args.run_id)
    if args.output.exists():
        raise FileExistsError(args.output)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
