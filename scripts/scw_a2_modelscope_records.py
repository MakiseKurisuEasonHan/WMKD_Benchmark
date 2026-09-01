"""Persist verified SCW A2 ModelScope archive metadata into small project records."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

P = Path("/root/autodl-tmp/WMKD_Benchmark")
D = Path("/root/autodl-tmp/WMKD_Benchmark_data")
TRANSFER = D / "artifacts/transfers/modelscope/scw_a2_teacher_upload_20260901"
RESULT = P / "results/scw/experiment_a2"
MARKER = "SCW_A2_MODELSCOPE_ARCHIVE_20260901"


def write_json(path: Path, value):
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def append_once(path: Path, text: str):
    old = path.read_text(encoding="utf-8")
    if MARKER not in old:
        path.write_text(old.rstrip() + "\n\n" + text.strip() + "\n", encoding="utf-8")


def main():
    verification = json.loads((TRANSFER / "upload_verification_summary.json").read_text(encoding="utf-8"))
    required = {
        "overall_status": "COMPLETE", "private": True, "remote_verified_files": 9,
        "remote_verified_bytes": 6442815654, "filename_verification": "PASS",
        "size_verification": "PASS", "remote_metadata_verification": "PASS",
        "destination_verified": False,
    }
    for key, value in required.items():
        if verification.get(key) != value:
            raise RuntimeError(f"archive verification mismatch: {key}")
    archive = {
        "modelscope_repo": verification["repo"], "visibility": "private",
        "archive_status": verification["archive_status"],
        "source_manifest_sha256": verification["source_manifest_sha256"],
        "teacher_manifest_sha256": verification["teacher_manifest_sha256"],
        "source_files": 9, "source_bytes": 6442815654,
        "uploaded_files": 9, "uploaded_bytes": 6442815654,
        "remote_verified_files": 9, "remote_verified_bytes": 6442815654,
        "filename_verification": "PASS", "size_verification": "PASS",
        "remote_metadata_verification": "PASS",
        "metadata_identity_available_files": 9,
        "destination_verified": False, "retries": verification["retries"],
        "errors": verification["errors"], "preferred_teacher": "YES",
        "ba_started": False,
    }
    summary_path = RESULT / "summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    if summary.get("scientific_status") != "REPRODUCTION_SUCCESSFUL" or summary.get("preferred_teacher") != "YES":
        raise RuntimeError("scientific closure status drift")
    summary["modelscope_archive"] = archive
    write_json(summary_path, summary)

    report_path = RESULT / "final_report.md"
    section = f"""## 13. ModelScope archive

<!-- {MARKER} -->
The immutable preferred Teacher was uploaded to the private ModelScope repository `MakiseKurisuEasonHan/WMKD-SCW-A2-Teacher`. The fixed nine-file loadable scope contains 6,442,815,654 bytes. Remote filename, size, and ModelScope metadata identity checks passed for 9/9 files and all bytes. Source manifest SHA256 is `{verification['source_manifest_sha256']}`; Teacher manifest SHA256 is `{verification['teacher_manifest_sha256']}`. Archive status is `{verification['archive_status']}` and `destination_verified=false` because no full 6GB+ destination redownload and independent SHA256 pass was performed. Scientific results are unchanged and Ba remains NOT STARTED.
"""
    append_once(report_path, section)

    record = f"""## SCW A2 preferred Teacher ModelScope archive

<!-- {MARKER} -->
The immutable SCW A2 preferred Teacher was archived to private repo `MakiseKurisuEasonHan/WMKD-SCW-A2-Teacher`. Upload completed with 9 files / 6,442,815,654 bytes and zero retries. Remote filename, size, and metadata identity verification passed for 9/9 files and all bytes. Source archive manifest SHA256: `{verification['source_manifest_sha256']}`; Teacher manifest SHA256: `{verification['teacher_manifest_sha256']}`. Status: `{verification['archive_status']}` with `destination_verified=false` because a full destination redownload was intentionally not performed. Preferred Teacher remains YES; Ba remains NOT STARTED. Exact next step: design and explicitly authorize SCW Ba; do not start it automatically.
"""
    for rel in ("PROJECT_STATUS.md", "TODO.md", "DECISIONS.md", "EXPERIMENT_LOG.md", "CODEX_LOG.md",
                "docs/experiment_logs/scw_experiment_a_log.md"):
        append_once(P / rel, record)

    archive_dir = RESULT / "archive"
    archive_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(TRANSFER / "WMKD_ARTIFACT_MANIFEST.json", archive_dir / "scw_a2_teacher_modelscope_source_manifest.json")
    shutil.copy2(TRANSFER / "upload_verification_summary.json", archive_dir / "scw_a2_teacher_modelscope_verification.json")


if __name__ == "__main__":
    main()
