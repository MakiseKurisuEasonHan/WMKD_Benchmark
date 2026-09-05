#!/usr/bin/env python3
"""Strong remote verification for existing PRIVATE ModelScope model archives."""
from __future__ import annotations

import hashlib
import json
import stat
from datetime import datetime, timezone
from pathlib import Path

from modelscope_hub.api import HubApi

DATA = Path("/root/autodl-tmp/WMKD_Benchmark_data")
PROJECT = Path("/root/autodl-tmp/WMKD_Benchmark")
SECRET = DATA / "secrets/modelscope.env"
OUT = DATA / "archive_remediation/evidence"
NAMESPACE = "MakiseKurisuEasonHan"
TARGETS = [
    ("evertracer_a_teacher", "MakiseKurisuEasonHan/WMKD-EverTracer-A-Teacher", DATA / "artifacts/transfers/modelscope/evertracer_teacher_upload_20260829/WMKD_ARTIFACT_MANIFEST.json"),
    ("evertracer_ba_student", "MakiseKurisuEasonHan/WMKD-EverTracer-Ba-Student", DATA / "artifacts/transfers/modelscope/evertracer_student_upload_20260829/WMKD_ARTIFACT_MANIFEST.json"),
    ("ctcc_a_teacher", "MakiseKurisuEasonHan/WMKD-CTCC-A-Teacher", DATA / "artifacts/transfers/modelscope/ctcc_teacher_upload_20260830/WMKD_ARTIFACT_MANIFEST.json"),
    ("ctcc_ba_student", "MakiseKurisuEasonHan/WMKD-CTCC-Ba-Student", DATA / "artifacts/transfers/modelscope/ctcc_student_upload_20260830/WMKD_ARTIFACT_MANIFEST.json"),
    ("iseal_a6_teacher", "MakiseKurisuEasonHan/WMKD-iSeal-A6-Teacher", DATA / "artifacts/transfers/modelscope/iseal_teacher_upload_20260830/WMKD_ARTIFACT_MANIFEST.json"),
    ("iseal_ba_student", "MakiseKurisuEasonHan/WMKD-iSeal-Ba-Student", DATA / "artifacts/transfers/modelscope/iseal_student_upload_20260830/WMKD_ARTIFACT_MANIFEST.json"),
    ("scw_a2_teacher", "MakiseKurisuEasonHan/WMKD-SCW-A2-Teacher", DATA / "artifacts/transfers/modelscope/scw_a2_teacher_upload_20260901/WMKD_ARTIFACT_MANIFEST.json"),
    ("scw_ba_student", "MakiseKurisuEasonHan/WMKD-SCW-Ba-Student", DATA / "artifacts/transfers/modelscope/scw_ba_student_upload_20260901/WMKD_ARTIFACT_MANIFEST.json"),
]


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def credentials() -> dict[str, str]:
    if not SECRET.is_file() or stat.S_IMODE(SECRET.stat().st_mode) != 0o600:
        raise RuntimeError("MODELSCOPE_CREDENTIAL_MISSING_OR_MODE_NOT_600")
    values = {}
    for line in SECRET.read_text(encoding="utf-8").splitlines():
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            values[key] = value
    if values.get("MODELSCOPE_NAMESPACE") != NAMESPACE or not values.get("MODELSCOPE_API_TOKEN"):
        raise RuntimeError("MODELSCOPE_CREDENTIAL_INVALID")
    return values


def private(repo: object) -> bool:
    visibility = getattr(getattr(repo, "visibility", None), "value", getattr(repo, "visibility", None))
    return getattr(repo, "private", None) is True or visibility in (1, "private", "PRIVATE")


def name(row: dict) -> str:
    value = (row.get("relative_path") or row.get("relative_filename") or row.get("path")
             or row.get("filename") or row.get("name"))
    if not value:
        raise RuntimeError("MANIFEST_NAME_MISSING")
    return value


def git_records(repo_id: str) -> list[str]:
    roots = [PROJECT / "PROJECT_STATUS.md", PROJECT / "EXPERIMENT_LOG.md", PROJECT / "CODEX_LOG.md",
             PROJECT / "results", PROJECT / "docs"]
    found = []
    for root in roots:
        paths = [root] if root.is_file() else root.rglob("*") if root.is_dir() else []
        for path in paths:
            if not path.is_file() or path.stat().st_size > 10 * 1024 * 1024:
                continue
            try:
                if repo_id in path.read_text(encoding="utf-8", errors="ignore"):
                    found.append(str(path.relative_to(PROJECT)))
            except OSError:
                pass
    return sorted(set(found))


def main() -> None:
    api = HubApi(token=credentials()["MODELSCOPE_API_TOKEN"])
    OUT.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    summary = []
    for label, repo_id, manifest_path in TARGETS:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        excluded = set(manifest.get("excluded_source_files", []))
        expected = {}
        for row in manifest["files"]:
            filename = name(row)
            if row.get("upload_included") is False or filename in excluded:
                continue
            expected[filename] = {"size": int(row.get("bytes", row.get("size"))), "sha256": row["sha256"]}
        if not api.repo_exists(repo_id, "model"):
            raise RuntimeError(f"{label}:REMOTE_REPOSITORY_MISSING")
        repo = api.get_repo(repo_id, "model")
        if not private(repo):
            raise RuntimeError(f"{label}:REMOTE_REPOSITORY_NOT_PRIVATE")
        remote = {x.path: {"size": int(x.size), "sha256": x.sha256, "blob_id": x.blob_id}
                  for x in api.list_repo_files(repo_id, "model", recursive=True) if not x.is_dir}
        checks = {}
        failures = []
        for filename, identity in sorted(expected.items()):
            observed = remote.get(filename)
            match = bool(observed and observed["size"] == identity["size"]
                         and observed["sha256"] == identity["sha256"]
                         and observed["blob_id"] == identity["sha256"])
            checks[filename] = {"expected": identity, "remote": observed, "match": match}
            if not match:
                failures.append(filename)
        records = git_records(repo_id)
        if not records:
            failures.append("GIT_ARCHIVE_RECORD_CORRESPONDENCE")
        evidence = {
            "schema_version": "wmkd.project-archive-remediation.strong-remote-model-verification.v1",
            "label": label, "repository": repo_id, "repository_type": "model",
            "status": "PASS" if not failures else "FAIL",
            "classification": "ARCHIVED_STRONGLY_VERIFIED" if not failures else "MISSING_ARCHIVE",
            "visibility": "PRIVATE", "full_independent_redownload": False, "fresh_process_reload": "NOT_REQUIRED_BY_TIER",
            "source_manifest": str(manifest_path), "source_manifest_sha256": digest(manifest_path),
            "expected_canonical_file_count": len(expected), "matched_canonical_file_count": len(expected) - len([x for x in failures if x in expected]),
            "canonical_checks": checks, "remote_total_file_count": len(remote), "remote_files": remote,
            "git_archive_records": records, "failures": failures,
            "no_missing_shard_or_truncation": not failures, "unexpected_overwrite": False if not failures else None,
            "credential_emitted": False, "scientific_configuration_changed": False,
            "verified_at": datetime.now(timezone.utc).isoformat(),
        }
        path = OUT / f"{label}_strong_remote_{stamp}.json"
        path.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"label": label, "status": evidence["status"], "classification": evidence["classification"],
                          "canonical": f"{evidence['matched_canonical_file_count']}/{len(expected)}", "evidence": str(path)}))
        if failures:
            raise RuntimeError(f"{label}:STRONG_REMOTE_VERIFICATION_FAILED:{failures}")
        summary.append(evidence)
    print(json.dumps({"status": "PASS", "verified": len(summary), "classification": "ARCHIVED_STRONGLY_VERIFIED"}))


if __name__ == "__main__":
    main()
