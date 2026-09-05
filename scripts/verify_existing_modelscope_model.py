#!/usr/bin/env python3
"""Independently redownload and verify one existing PRIVATE ModelScope model.

This transport-only helper never uploads or mutates a repository.  On success it
persists verification evidence outside the download directory and may remove only
that newly-created temporary verification copy.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import stat
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from modelscope_hub.api import HubApi

DATA = Path("/root/autodl-tmp/WMKD_Benchmark_data")
SECRET = DATA / "secrets/modelscope.env"
NAMESPACE = "MakiseKurisuEasonHan"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def credentials() -> dict[str, str]:
    if not SECRET.is_file() or stat.S_IMODE(SECRET.stat().st_mode) != 0o600:
        raise RuntimeError("MODELSCOPE_CREDENTIAL_MISSING_OR_MODE_NOT_600")
    values = {}
    for line in SECRET.read_text(encoding="utf-8").splitlines():
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            values[key] = value
    if values.get("MODELSCOPE_NAMESPACE") != NAMESPACE or not values.get("MODELSCOPE_API_TOKEN"):
        raise RuntimeError("MODELSCOPE_NAMESPACE_OR_TOKEN_UNAVAILABLE")
    return values


def is_private(repo: object) -> bool:
    visibility = getattr(getattr(repo, "visibility", None), "value", getattr(repo, "visibility", None))
    return getattr(repo, "private", None) is True or visibility in (1, "private", "PRIVATE")


def expected_files(manifest_path: Path) -> dict[str, dict]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    rows = {}
    for item in manifest["files"]:
        name = item.get("relative_path") or item.get("path") or item.get("filename") or item.get("name")
        if not name:
            raise RuntimeError("MANIFEST_FILE_NAME_MISSING")
        rows[name] = {"size": int(item.get("bytes", item.get("size"))), "sha256": item["sha256"]}
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--label", required=True)
    parser.add_argument("--reload-python", required=True)
    parser.add_argument("--existing-verify-dir", type=Path)
    parser.add_argument("--delete-verified-copy", action="store_true")
    args = parser.parse_args()
    if not args.repo.startswith(NAMESPACE + "/"):
        raise RuntimeError("REPOSITORY_NAMESPACE_MISMATCH")

    api = HubApi(token=credentials()["MODELSCOPE_API_TOKEN"])
    if not api.repo_exists(args.repo, "model"):
        raise RuntimeError("REMOTE_REPOSITORY_MISSING")
    before = api.get_repo(args.repo, "model")
    if not is_private(before):
        raise RuntimeError("REMOTE_REPOSITORY_NOT_PRIVATE_BEFORE_DOWNLOAD")
    remote_files = sorted(x.path for x in api.list_repo_files(args.repo, "model", recursive=True) if not x.is_dir)
    expected = expected_files(args.manifest)
    missing = sorted(set(expected) - set(remote_files))
    if missing:
        raise RuntimeError(f"REMOTE_CANONICAL_FILES_MISSING:{missing}")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    if args.existing_verify_dir:
        restored = args.existing_verify_dir
        if (restored.resolve().parent != (DATA / "tmp").resolve()
                or not restored.name.startswith("modelscope_verify_remediation_")
                or restored.is_symlink() or not restored.is_dir()):
            raise RuntimeError("INVALID_EXISTING_VERIFICATION_DIRECTORY")
    else:
        verify_dir = DATA / "tmp" / f"modelscope_verify_remediation_{args.label}_{stamp}"
        if verify_dir.exists():
            raise RuntimeError("FRESH_VERIFICATION_DIRECTORY_ALREADY_EXISTS")
        restored = Path(api.download_repo(args.repo, "model", local_dir=verify_dir, local_files_only=False, max_workers=4))

    checks = {}
    failures = []
    for name, identity in sorted(expected.items()):
        path = restored / name
        observed = {"exists": path.is_file()}
        if path.is_file():
            observed.update(size=path.stat().st_size, sha256=sha256(path))
        observed["match"] = observed.get("size") == identity["size"] and observed.get("sha256") == identity["sha256"]
        checks[name] = {"expected": identity, "observed": observed}
        if not observed["match"]:
            failures.append(name)
    if failures:
        raise RuntimeError(f"INDEPENDENT_FILE_VERIFICATION_FAILED:{failures}")

    reload_code = """from transformers import AutoTokenizer,AutoModelForCausalLM\nimport sys\np=sys.argv[1]\nt=AutoTokenizer.from_pretrained(p,local_files_only=True)\nm=AutoModelForCausalLM.from_pretrained(p,local_files_only=True,device_map={'': 'cpu'},torch_dtype='auto',low_cpu_mem_usage=True)\nassert len(t)==m.get_input_embeddings().num_embeddings==m.config.vocab_size\nprint('FRESH_PROCESS_RELOAD_PASS')\n"""
    proc = subprocess.run([args.reload_python, "-c", reload_code, str(restored)], text=True, capture_output=True, timeout=1800)
    reload_pass = proc.returncode == 0 and "FRESH_PROCESS_RELOAD_PASS" in proc.stdout
    if not reload_pass:
        raise RuntimeError("FRESH_PROCESS_RELOAD_FAILED:" + (proc.stderr[-2000:] or proc.stdout[-2000:]))

    after = api.get_repo(args.repo, "model")
    if not is_private(after):
        raise RuntimeError("REMOTE_REPOSITORY_NOT_PRIVATE_AFTER_DOWNLOAD")
    evidence = {
        "schema_version": "wmkd.project-archive-remediation.model-verification.v1",
        "status": "PASS", "label": args.label, "repository": args.repo,
        "repository_type": "model", "visibility_before": "PRIVATE", "visibility_after": "PRIVATE",
        "source_manifest": str(args.manifest), "source_manifest_sha256": sha256(args.manifest),
        "canonical_file_count": len(expected), "canonical_files": checks,
        "remote_files": remote_files, "independent_verification_directory": str(restored),
        "fresh_process_reload": "PASS", "reload_python": args.reload_python,
        "credential_emitted": False, "scientific_configuration_changed": False,
        "verified_at": now(), "temporary_verification_copy_deleted": False,
    }
    evidence_dir = DATA / "archive_remediation" / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    evidence_path = evidence_dir / f"{args.label}_{stamp}.json"
    evidence_path.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    if args.delete_verified_copy:
        resolved = restored.resolve()
        allowed = (DATA / "tmp").resolve()
        if resolved.parent != allowed or not resolved.name.startswith("modelscope_verify_remediation_") or restored.is_symlink():
            raise RuntimeError("REFUSED_UNSAFE_TEMPORARY_COPY_DELETION")
        shutil.rmtree(restored)
        evidence["temporary_verification_copy_deleted"] = True
        evidence["deleted_at"] = now()
        evidence_path.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "repository": args.repo, "evidence": str(evidence_path),
                      "fresh_process_reload": "PASS", "temporary_verification_copy_deleted": evidence["temporary_verification_copy_deleted"]}))


if __name__ == "__main__":
    main()
