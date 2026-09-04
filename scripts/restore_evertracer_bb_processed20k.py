#!/usr/bin/env python3
"""Fail-closed restore of the canonical EverTracer Bb processed20k archive."""
from __future__ import annotations

import argparse
import json
import os
import shutil
import stat
from datetime import datetime, timezone
from pathlib import Path

from modelscope_hub.api import HubApi
from passive5_shared_bb import adapt_student_dataset, file_sha256, read_jsonl, records_sha256

REPO = "MakiseKurisuEasonHan/WMKD_Benchmark_evertracer_bb_processed20k"
EXPECTED_FILE = "41a44ffc153c5df78485037f154c4004f1b6f04b2451deac3c1c7ca9af6e6853"
EXPECTED_CONTENT = "0f23881da975d7b8262599690c85cfb5d1a90b2c3c1976efcaa8f651aa064c55"
EXPECTED_IDS = "49d42164d0aa254385d0d9b78596d7369a50ad6070d4e47e32b3f74c73a6be73"
EXPECTED_MANIFEST = "3e25a4401e9e91c544c133db3790ed31bcf131a9a5a25b90615c259b0bef34fe"
REQUIRED = {"sample_id", "instruction", "input", "source_answer", "source_answer_sha256",
            "paraphrased_answer", "paraphrased_answer_sha256", "source_answer_token_count",
            "processing_mode"}


def token(secret: Path) -> str:
    if not secret.is_file() or stat.S_IMODE(secret.stat().st_mode) != 0o600:
        raise RuntimeError("MODELSCOPE_CREDENTIAL_MISSING_OR_MODE_NOT_600")
    values = dict(line.split("=", 1) for line in secret.read_text(encoding="utf-8").splitlines()
                  if line and not line.startswith("#") and "=" in line)
    if values.get("MODELSCOPE_NAMESPACE") != "MakiseKurisuEasonHan":
        raise RuntimeError("MODELSCOPE_NAMESPACE_MISMATCH")
    value = values.get("MODELSCOPE_API_TOKEN")
    if not value:
        raise RuntimeError("MODELSCOPE_TOKEN_UNAVAILABLE")
    return value


def validate(path: Path) -> dict:
    rows = read_jsonl(path)
    if len(rows) != 20000:
        raise RuntimeError(f"RECORD_COUNT_MISMATCH {len(rows)}")
    if any(REQUIRED - set(row) for row in rows):
        raise RuntimeError("SCHEMA_MISMATCH")
    values = {"record_count": len(rows), "frozen_jsonl_sha256": file_sha256(path),
              "dataset_sha256": records_sha256(rows),
              "sample_ids_sha256": records_sha256([{"sample_id": row["sample_id"]} for row in rows]),
              "schema": sorted(REQUIRED)}
    if (values["frozen_jsonl_sha256"], values["dataset_sha256"], values["sample_ids_sha256"]) != (
            EXPECTED_FILE, EXPECTED_CONTENT, EXPECTED_IDS):
        raise RuntimeError(f"CANONICAL_IDENTITY_MISMATCH {values}")
    return values


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--secret", type=Path, required=True)
    parser.add_argument("--restore-root", type=Path, required=True)
    parser.add_argument("--canonical-dataset", type=Path, required=True)
    parser.add_argument("--student-dataset", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    for path in (args.restore_root, args.canonical_dataset, args.student_dataset, args.output):
        if path.exists():
            raise FileExistsError(f"OUTPUT_COLLISION {path}")
    api = HubApi(token=token(args.secret))
    repo = api.get_repo(REPO, "dataset")
    visibility = getattr(getattr(repo, "visibility", None), "value", getattr(repo, "visibility", None))
    if not (getattr(repo, "private", None) is True or visibility in (1, "private", "PRIVATE")):
        raise RuntimeError("REPOSITORY_NOT_PRIVATE")
    downloaded = Path(api.download_repo(REPO, "dataset", local_dir=args.restore_root,
                                         local_files_only=False, max_workers=4))
    expected_files = {"README.md", "SHA256SUMS", "frozen_paired_qa.jsonl", "manifest.json"}
    actual_files = {str(path.relative_to(downloaded)) for path in downloaded.rglob("*") if path.is_file()}
    if not expected_files.issubset(actual_files):
        raise RuntimeError(f"ARCHIVE_FILE_SET_MISMATCH {sorted(actual_files)}")
    package_manifest = downloaded / "manifest.json"
    if file_sha256(package_manifest) != EXPECTED_MANIFEST:
        raise RuntimeError("PACKAGE_MANIFEST_SHA_MISMATCH")
    manifest = json.loads(package_manifest.read_text(encoding="utf-8"))
    source = downloaded / "frozen_paired_qa.jsonl"
    verified = validate(source)
    if manifest.get("dataset_sha256") != EXPECTED_CONTENT or manifest.get("frozen_jsonl_sha256") != EXPECTED_FILE:
        raise RuntimeError("PACKAGE_PROVENANCE_MISMATCH")
    args.canonical_dataset.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.canonical_dataset.with_suffix(args.canonical_dataset.suffix + ".tmp")
    shutil.copyfile(source, temporary)
    if validate(temporary) != verified:
        raise RuntimeError("CANONICAL_COPY_VALIDATION_FAILED")
    os.replace(temporary, args.canonical_dataset)
    student = adapt_student_dataset(read_jsonl(args.canonical_dataset), args.student_dataset)
    result = {"status": "PASS", "repository": REPO, "visibility": "PRIVATE",
              "download_directory": str(downloaded), "canonical_dataset": str(args.canonical_dataset),
              "archive_manifest_sha256": EXPECTED_MANIFEST, "archive_provenance": manifest,
              "processed20k": verified, "sft_formatter": student,
              "token_emitted": False, "completed_at": datetime.now(timezone.utc).isoformat()}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "archive_provenance"}, indent=2))


if __name__ == "__main__":
    main()
