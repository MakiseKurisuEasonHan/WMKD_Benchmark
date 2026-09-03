#!/usr/bin/env python3
"""Private ModelScope archive and independent verification for EverTracer Bb processed20k."""
from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import modelscope_passive5_bb3_dataset_archive as base

REPO_ID = "MakiseKurisuEasonHan/WMKD_Benchmark_evertracer_bb_processed20k"
RUN_ID = "evertracer_bb_20260903_130000"
SOURCE = Path(
    "/root/autodl-tmp/WMKD_Benchmark_data/runs/evertracer_bb/"
    f"{RUN_ID}/dataset/frozen_paired_qa.jsonl"
)
CONFIG = Path(
    f"/root/autodl-tmp/WMKD_Benchmark/configs/distillation/{RUN_ID}.json"
)
PRIVACY = Path(
    "/root/autodl-tmp/WMKD_Benchmark_data/tmp/"
    "evertracer_bb_processed20k_privacy_audit.json"
)
INHERITANCE = Path(
    "/root/autodl-tmp/WMKD_Benchmark_data/tmp/"
    "evertracer_bb_high_entropy_inheritance.json"
)
EXPECTED_FILE_SHA = "41a44ffc153c5df78485037f154c4004f1b6f04b2451deac3c1c7ca9af6e6853"
EXPECTED_DATASET_SHA = "0f23881da975d7b8262599690c85cfb5d1a90b2c3c1976efcaa8f651aa064c55"
EXPECTED_IDS_SHA = "49d42164d0aa254385d0d9b78596d7369a50ad6070d4e47e32b3f74c73a6be73"
OUTPUT = base.DATA_ROOT / "manifests/evertracer_bb_processed20k_modelscope_archive.json"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def validate_processed(path: Path) -> dict:
    rows = base.read_jsonl(path)
    if len(rows) != 20000:
        raise RuntimeError(f"RECORD_COUNT_MISMATCH {len(rows)}")
    if any(base.REQUIRED - set(row) for row in rows):
        raise RuntimeError("PROCESSED_SCHEMA_MISMATCH")
    dataset_sha = base.records_sha256(rows)
    ids_sha = base.records_sha256([{"sample_id": row["sample_id"]} for row in rows])
    file_sha = base.file_sha256(path)
    if (dataset_sha, ids_sha, file_sha) != (
        EXPECTED_DATASET_SHA, EXPECTED_IDS_SHA, EXPECTED_FILE_SHA
    ):
        raise RuntimeError("PROCESSED_IDENTITY_MISMATCH")
    return {"status": "PASS", "record_count": len(rows),
            "dataset_sha256": dataset_sha, "sample_ids_sha256": ids_sha,
            "frozen_jsonl_sha256": file_sha}


def source_gate() -> dict:
    validated = validate_processed(SOURCE)
    privacy = json.loads(PRIVACY.read_text(encoding="utf-8"))
    inheritance = json.loads(INHERITANCE.read_text(encoding="utf-8"))
    if privacy.get("strict_secret_total") != 0:
        raise RuntimeError("STRICT_SECRET_GATE_FAILED")
    if privacy.get("high_entropy_candidate_count") != 5:
        raise RuntimeError("HIGH_ENTROPY_COUNT_DRIFT")
    if inheritance.get("candidate_count") != 5 or not inheritance.get(
        "all_candidates_identical_in_parent_record"
    ) or inheritance.get("candidate_text_emitted"):
        raise RuntimeError("HIGH_ENTROPY_INHERITANCE_GATE_FAILED")
    return {"validation": validated,
            "privacy_audit_sha256": base.file_sha256(PRIVACY),
            "privacy_strict_secret_total": 0,
            "high_entropy_review": "PASS_ALL_5_INHERITED_FROM_ARCHIVED_BA_PARENT",
            "high_entropy_inheritance_sha256": base.file_sha256(INHERITANCE)}


def prepare_package(work: Path, source: dict) -> tuple[Path, dict]:
    package = work / "package"
    package.mkdir(parents=True, exist_ok=False)
    shutil.copyfile(SOURCE, package / "frozen_paired_qa.jsonl")
    if base.file_sha256(package / "frozen_paired_qa.jsonl") != EXPECTED_FILE_SHA:
        raise RuntimeError("PACKAGE_COPY_NOT_BYTE_IDENTICAL")
    config = base.load_config(CONFIG)
    manifest = {"project": "WMKD_Benchmark",
        "object": "evertracer_bb_processed20k", "run_id": RUN_ID,
        "parent_run": config["source_dataset"]["parent_run_id"],
        "record_count": 20000, "canonical_source_path": str(SOURCE),
        "schema": sorted(base.REQUIRED), "dataset_sha256": EXPECTED_DATASET_SHA,
        "frozen_jsonl_sha256": EXPECTED_FILE_SHA,
        "sample_id_sha256": EXPECTED_IDS_SHA,
        "source_ba_dataset_sha256": config["source_dataset"]["dataset_sha256"],
        "prompt_sha256": config["paraphrase"]["prompt_sha256"],
        "processing_modes": {"atomic_identity_preserved": 4864,
            "qwen_paraphrased": 12099, "qwen_identity_output": 2959,
            "pipeline_identity_fallback": 78},
        "privacy_gate": source,
        "transport_purpose": "private ModelScope backup / cross-instance restoration",
        "scientific_semantics": "EverTracer Bb answer-only untargeted paraphrasing; no training or evaluation",
        "created_at": now()}
    base.atomic_json(package / "manifest.json", manifest)
    (package / "README.md").write_text(
        "# WMKD_Benchmark EverTracer Bb processed20k\n\n"
        "Private transport backup of the frozen EverTracer Bb processed20k. "
        "No Student training or detector/utility evaluation is included. "
        "Verify SHA256 before use.\n", encoding="utf-8", newline="\n")
    names = ("frozen_paired_qa.jsonl", "manifest.json", "README.md")
    (package / "SHA256SUMS").write_text("".join(
        f"{base.file_sha256(package / name)}  {name}\n" for name in names
    ), encoding="utf-8", newline="\n")
    return package, manifest


def verify_existing(api, gate: dict, package: Path, created: bool, upload_result=None) -> dict:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    verify_dir = base.DATA_ROOT / "tmp" / f"modelscope_verify_evertracer_bb_{stamp}"
    expected_files = {"README.md", "SHA256SUMS", "frozen_paired_qa.jsonl", "manifest.json"}
    state = base.repo_state(api)
    if not state["private"] or not expected_files.issubset(set(state["files"])):
        raise RuntimeError(f"REMOTE_FILE_OR_VISIBILITY_GATE_FAILED {state}")
    downloaded = Path(api.download_repo(REPO_ID, base.REPO_TYPE, local_dir=verify_dir,
                                        local_files_only=False, max_workers=4))
    remote_frozen = downloaded / "frozen_paired_qa.jsonl"
    verified = validate_processed(remote_frozen)
    local_manifest = json.loads((package / "manifest.json").read_text(encoding="utf-8"))
    remote_manifest = json.loads((downloaded / "manifest.json").read_text(encoding="utf-8"))
    if remote_manifest != local_manifest:
        raise RuntimeError("DOWNLOADED_MANIFEST_MISMATCH")
    result = {"status": "COMPLETED", "modelscope_backup_verified": True,
        "repository": REPO_ID, "repository_type": base.REPO_TYPE,
        "visibility": "PRIVATE", "created": created,
        "uploaded_files": sorted(expected_files),
        "source_validation": gate["source"]["validation"],
        "downloaded_copy_validation": verified,
        "byte_identical": base.file_sha256(SOURCE) == base.file_sha256(remote_frozen),
        "package_manifest_sha256": base.file_sha256(package / "manifest.json"),
        "privacy_gate": gate["source"], "verification_directory": str(verify_dir),
        "canonical_source_preserved": SOURCE.is_file(), "verified_at": now(),
        "token_emitted": False, "upload_result_available": upload_result is not None}
    base.atomic_json(OUTPUT, result)
    print(json.dumps(result, indent=2))
    return result


def configure() -> None:
    base.REPO_NAME = REPO_ID.split("/", 1)[1]
    base.REPO_ID = REPO_ID
    base.SOURCE = SOURCE
    base.CONFIG = CONFIG
    base.EXPECTED_FILE_SHA = EXPECTED_FILE_SHA
    base.EXPECTED_DATASET_SHA = EXPECTED_DATASET_SHA
    base.EXPECTED_IDS_SHA = EXPECTED_IDS_SHA
    base.validate_processed = validate_processed
    base.source_gate = source_gate
    base.prepare_package = prepare_package
    base.verify_existing = verify_existing


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("preflight", "upload", "verify"))
    args = parser.parse_args()
    configure()
    if args.command == "preflight":
        base.preflight()
    elif args.command == "upload":
        base.upload()
    else:
        base.verify()


if __name__ == "__main__":
    main()
