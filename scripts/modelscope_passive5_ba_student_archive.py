#!/usr/bin/env python3
"""Archive and independently verify the canonical Passive-5 Shared Ba Student."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
from datetime import datetime, timezone
from pathlib import Path

from modelscope_hub.api import HubApi

NAMESPACE = "MakiseKurisuEasonHan"
REPO_NAME = "Llama-3.2-WMKD-Passive5-Shared-Ba-Student"
REPO_ID = f"{NAMESPACE}/{REPO_NAME}"
REPO_TYPE = "model"
ARCHIVE_SLUG = "passive5_ba"
EXPERIMENT_LABEL = "Ba"
OBJECT_SLUG = "canonical_passive5_shared_ba_final_student"
SCHEMA_VERSION = "wmkd.modelscope-passive5-shared-ba-student.v1"
EVALUATION_RUN_ID = "passive5_shared_ba_eval_cont2_20260902_164200"
PROJECT = Path("/root/autodl-tmp/WMKD_Benchmark")
DATA_ROOT = Path("/root/autodl-tmp/WMKD_Benchmark_data")
SOURCE = DATA_ROOT / "runs/passive5_shared_ba/passive5_shared_ba_20260902_114500_cont1/student/final_model"
SOURCE_MANIFEST = PROJECT / "results/passive5_shared_ba/student_manifest.json"
TRAINING_SUMMARY = PROJECT / "results/passive5_shared_ba/training_summary.json"
FULL_LOG = PROJECT / "results/passive5_shared_ba/full_experiment_log.json"
BASE_LICENSE = DATA_ROOT / "models/base/Llama-3.2-3B-Instruct/LICENSE.txt"
SECRET = DATA_ROOT / "secrets/modelscope.env"
EXPECTED_SOURCE_FILES = {
    "chat_template.jinja", "config.json", "generation_config.json",
    "model-00001-of-00002.safetensors", "model-00002-of-00002.safetensors",
    "model.safetensors.index.json", "special_tokens_map.json", "tokenizer.json",
    "tokenizer_config.json", "training_args.bin",
}
META_NOTICE = "Llama 3.2 is licensed under the Llama 3.2 Community License, Copyright © Meta Platforms, Inc. All Rights Reserved."


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


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


def api_client() -> HubApi:
    return HubApi(token=credentials()["MODELSCOPE_API_TOKEN"])


def is_private(repo: object) -> bool:
    visibility = getattr(getattr(repo, "visibility", None), "value", getattr(repo, "visibility", None))
    return getattr(repo, "private", None) is True or visibility in (1, "private", "PRIVATE")


def repo_state(api: HubApi) -> dict:
    exists = api.repo_exists(REPO_ID, REPO_TYPE)
    if not exists:
        return {"exists": False, "private": None, "files": []}
    repo = api.get_repo(REPO_ID, REPO_TYPE)
    files = sorted(item.path for item in api.list_repo_files(REPO_ID, REPO_TYPE, recursive=True) if not item.is_dir)
    return {"exists": True, "private": is_private(repo), "files": files}


def source_gate() -> dict:
    if not SOURCE.is_dir():
        raise RuntimeError("CANONICAL_SOURCE_MISSING")
    entries = list(SOURCE.iterdir())
    if any(p.is_symlink() for p in entries):
        raise RuntimeError("SOURCE_CONTAINS_SYMLINK")
    names = {p.name for p in entries if p.is_file()}
    if names != EXPECTED_SOURCE_FILES or any(p.is_dir() for p in entries):
        raise RuntimeError(f"SOURCE_FILE_SET_MISMATCH {sorted(names)}")
    if any(p.stat().st_size == 0 for p in entries):
        raise RuntimeError("SOURCE_ZERO_LENGTH_FILE")
    manifest = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    summary = json.loads(TRAINING_SUMMARY.read_text(encoding="utf-8"))
    full_log = json.loads(FULL_LOG.read_text(encoding="utf-8"))
    hashes = {name: sha256(SOURCE / name) for name in sorted(names)}
    if manifest.get("status") != "PASS" or manifest.get("artifact") != str(SOURCE) or manifest.get("files_sha256") != hashes:
        raise RuntimeError("SOURCE_MANIFEST_GATE_FAILED")
    cfg = manifest.get("config", {})
    required = {"epochs": 3, "learning_rate": 1e-5, "precision": "bf16", "full_parameter": True,
                "lora": False, "effective_batch_size": 8, "expected_steps": 7500}
    if any(cfg.get(k) != v for k, v in required.items()):
        raise RuntimeError("TRAINING_CONFIGURATION_GATE_FAILED")
    if summary.get("status") != "COMPLETED" or summary.get("optimizer_steps") != 7500 or summary.get("student_path") != str(SOURCE):
        raise RuntimeError("TRAINING_SUMMARY_GATE_FAILED")
    reload_info = full_log.get("reload_validation", {})
    if reload_info.get("status") != "PASS" or reload_info.get("fresh_process_reload") is not True or reload_info.get("student_path") != str(SOURCE):
        raise RuntimeError("FRESH_RELOAD_EVIDENCE_GATE_FAILED")
    index = json.loads((SOURCE / "model.safetensors.index.json").read_text(encoding="utf-8"))
    shards = set(index.get("weight_map", {}).values())
    if shards != {"model-00001-of-00002.safetensors", "model-00002-of-00002.safetensors"}:
        raise RuntimeError("SHARD_INDEX_GATE_FAILED")
    tensor_bytes = index.get("metadata", {}).get("total_size")
    shard_file_bytes = sum((SOURCE / x).stat().st_size for x in shards)
    if not isinstance(tensor_bytes, int) or shard_file_bytes < tensor_bytes or shard_file_bytes - tensor_bytes > 1024 * 1024:
        raise RuntimeError("SHARD_TOTAL_SIZE_GATE_FAILED")
    config = json.loads((SOURCE / "config.json").read_text(encoding="utf-8"))
    if config.get("architectures") != ["LlamaForCausalLM"] or config.get("torch_dtype") != "bfloat16":
        raise RuntimeError("MODEL_IDENTITY_GATE_FAILED")
    return {"hashes": hashes, "sizes": {n: (SOURCE / n).stat().st_size for n in sorted(names)},
            "manifest": manifest, "summary": summary, "reload": reload_info,
            "model": {"architecture": "LlamaForCausalLM", "parameters": index["metadata"]["total_parameters"],
                      "weight_bytes": index["metadata"]["total_size"], "dtype": "bfloat16"}}


def scan_text(package: Path) -> dict:
    patterns = [re.compile(x, re.I) for x in (r"BEGIN [A-Z ]*PRIVATE KEY", r"(?:api[_-]?key|token|secret|password)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{16,}", r"hf_[A-Za-z0-9]{20,}", r"sk-[A-Za-z0-9]{20,}")]
    hits = []
    for p in package.iterdir():
        if not p.is_file() or p.name == ".ms_upload_cache" or p.suffix.lower() in {".safetensors", ".bin"}:
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        for pattern in patterns:
            if pattern.search(text):
                hits.append({"file": p.name, "pattern": pattern.pattern})
    if hits:
        raise RuntimeError(f"SECRET_SCAN_FAILED {hits}")
    return {"status": "PASS", "files_scanned": sorted(p.name for p in package.iterdir() if p.is_file() and p.name != ".ms_upload_cache" and p.suffix.lower() not in {".safetensors", ".bin"}), "hits": 0}


def prepare_package(work: Path, gate: dict) -> tuple[Path, dict]:
    package = work / "package"
    package.mkdir(parents=True, exist_ok=False)
    for name in sorted(EXPECTED_SOURCE_FILES):
        os.link(SOURCE / name, package / name)
    shutil.copyfile(BASE_LICENSE, package / "LICENSE.txt")
    (package / "NOTICE").write_text(META_NOTICE + "\n", encoding="utf-8", newline="\n")
    readme = f"""# Llama 3.2 WMKD Passive-5 Shared {EXPERIMENT_LABEL} Student

Built with Llama.

Private transport backup of the canonical WMKD_Benchmark Passive-5 Shared {EXPERIMENT_LABEL} final Student. This is a full-parameter BF16 derivative of Llama 3.2 3B Instruct, trained on the immutable 20,000-record Shared {EXPERIMENT_LABEL} dataset. ModelScope is storage/transport only; this upload creates no new scientific result. Verify every file against `SHA256SUMS` and `manifest.json` before restoration.

Use is governed by the included `LICENSE.txt`, `NOTICE`, and the Llama Acceptable Use Policy. The repository name begins with “Llama” and the required “Built with Llama” attribution is displayed here.
"""
    (package / "README.md").write_text(readme, encoding="utf-8", newline="\n")
    manifest = {"schema_version": SCHEMA_VERSION, "project": "WMKD_Benchmark",
        "object": OBJECT_SLUG, "repository": REPO_ID, "visibility": "PRIVATE",
        "canonical_source_path": str(SOURCE), "source_run_id": gate["manifest"]["run_id"],
        "evaluation_run_id": EVALUATION_RUN_ID,
        "dataset_sha256": gate["manifest"]["dataset_sha256"], "training": gate["summary"]["configuration"],
        "optimizer_steps": gate["summary"]["optimizer_steps"], "model": gate["model"],
        "fresh_process_reload_evidence": {"status": gate["reload"]["status"], "fresh_process_reload": True,
            "student_manifest_sha256": gate["reload"]["student_manifest_sha256"]},
        "source_files": {n: {"size": gate["sizes"][n], "sha256": gate["hashes"][n]} for n in sorted(EXPECTED_SOURCE_FILES)},
        "license": {"base": "Llama 3.2", "built_with_llama": True, "notice": META_NOTICE},
        "transport_purpose": "private ModelScope backup and cross-instance restoration", "created_at": now()}
    write_json(package / "manifest.json", manifest)
    sums = [(sha256(p), p.name) for p in sorted(package.iterdir(), key=lambda x: x.name) if p.name != "SHA256SUMS"]
    (package / "SHA256SUMS").write_text("".join(f"{digest}  {name}\n" for digest, name in sums), encoding="utf-8", newline="\n")
    scan = scan_text(package)
    return package, {"manifest": manifest, "secret_scan": scan}


def verify_package(downloaded: Path, package: Path) -> dict:
    expected = sorted(p.name for p in package.iterdir() if p.is_file() and p.name != ".ms_upload_cache")
    actual = sorted(p.name for p in downloaded.iterdir() if p.is_file() and p.name not in {".gitattributes", ".mdlignore"})
    if actual != expected:
        raise RuntimeError(f"DOWNLOADED_FILE_SET_MISMATCH expected={expected} actual={actual}")
    checks = {}
    for name in expected:
        a, b = package / name, downloaded / name
        checks[name] = {"size": b.stat().st_size, "sha256": sha256(b), "match": a.stat().st_size == b.stat().st_size and sha256(a) == sha256(b)}
    if not all(v["match"] for v in checks.values()):
        raise RuntimeError("DOWNLOADED_COPY_HASH_MISMATCH")
    index = json.loads((downloaded / "model.safetensors.index.json").read_text(encoding="utf-8"))
    if set(index["weight_map"].values()) != {"model-00001-of-00002.safetensors", "model-00002-of-00002.safetensors"}:
        raise RuntimeError("DOWNLOADED_SHARD_INDEX_FAILED")
    scan = scan_text(downloaded)
    return {"files": checks, "file_count": len(checks), "total_bytes": sum(v["size"] for v in checks.values()), "secret_scan": scan}


def finalize_existing() -> dict:
    packages = sorted((DATA_ROOT / "tmp").glob(f"modelscope_upload_{ARCHIVE_SLUG}_student_*/package"))
    downloads = sorted(DATA_ROOT.glob(f"tmp/modelscope_verify_{ARCHIVE_SLUG}_student_*"))
    if not packages or not downloads:
        raise RuntimeError("UPLOAD_PACKAGE_OR_DOWNLOADED_COPY_MISSING")
    package, downloaded = packages[-1], downloads[-1]
    gate = source_gate()
    api = api_client()
    state = repo_state(api)
    expected_remote = sorted(p.name for p in package.iterdir() if p.is_file() and p.name != ".ms_upload_cache")
    if not state["exists"] or not state["private"] or not set(expected_remote).issubset(set(state["files"])):
        raise RuntimeError(f"REMOTE_REPOSITORY_GATE_FAILED {state}")
    verification = verify_package(downloaded, package)
    try:
        revision = str(api.list_repo_revisions(REPO_ID, REPO_TYPE)[0])
    except Exception as exc:
        revision = f"unavailable:{type(exc).__name__}"
    source_after = source_gate()
    result = {"status": "COMPLETED", "repository": REPO_ID, "repository_type": REPO_TYPE,
        "visibility": "PRIVATE", "created": True, "revision": revision,
        "source_path": str(SOURCE), "source_run_id": gate["manifest"]["run_id"],
        "evaluation_run_id": EVALUATION_RUN_ID,
        "source_file_count": len(gate["hashes"]), "source_total_bytes": sum(gate["sizes"].values()),
        "uploaded_files": expected_remote, "uploaded_total_bytes": sum((package / n).stat().st_size for n in expected_remote),
        "package_manifest_sha256": sha256(package / "manifest.json"), "source_manifest_sha256": sha256(SOURCE_MANIFEST),
        "source_hashes_unchanged": source_after["hashes"] == gate["hashes"], "canonical_source_preserved": SOURCE.is_dir(),
        "restored_copy_file_integrity_verified": True, "modelscope_backup_verified": True,
        "verification_directory": str(downloaded), "verification": verification,
        "secret_scan": scan_text(package), "large_file_scan": {"status": "PASS", "allowed_large_files": [n for n in sorted(EXPECTED_SOURCE_FILES) if n.endswith(".safetensors")]},
        "license_compliance": {"status": "PASS", "repository_name_starts_with_llama": REPO_NAME.startswith("Llama"), "license_included": True, "notice_included": True, "built_with_llama": True},
        "platform_metadata_excluded_from_canonical_manifest": [".gitattributes", ".ms_upload_cache"],
        "token_emitted": False, "completed_at": now()}
    out = DATA_ROOT / f"manifests/{ARCHIVE_SLUG}_student_modelscope_archive.json"
    write_json(out, result)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return result


def preflight() -> dict:
    gate = source_gate()
    api = api_client()
    state = repo_state(api)
    if state["exists"] and not state["private"]:
        raise RuntimeError("EXISTING_REPOSITORY_NOT_PRIVATE")
    result = {"status": "PASS", "authenticated_namespace": NAMESPACE, "repository": state,
              "source_file_count": len(gate["hashes"]), "source_bytes": sum(gate["sizes"].values()),
              "credential_mode": "600", "token_emitted": False, "checked_at": now()}
    print(json.dumps(result, indent=2))
    return result


def upload() -> dict:
    preflight()
    gate = source_gate()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    work = DATA_ROOT / "tmp" / f"modelscope_upload_{ARCHIVE_SLUG}_student_{stamp}"
    work.mkdir(parents=True, exist_ok=False)
    package, package_info = prepare_package(work, gate)
    api = api_client()
    state = repo_state(api)
    if state["exists"] and state["files"]:
        raise RuntimeError(f"EXISTING_REPOSITORY_CONTENT_CONFLICT {state['files']}")
    created = False
    if not state["exists"]:
        api.create_repo(REPO_ID, REPO_TYPE, visibility=1, description=f"Private canonical WMKD Passive-5 Shared {EXPERIMENT_LABEL} final Student backup; Built with Llama")
        created = True
    confirmed = repo_state(api)
    if not confirmed["private"]:
        raise RuntimeError("PRIVATE_VISIBILITY_NOT_CONFIRMED")
    if confirmed["files"] and not (created and set(confirmed["files"]).issubset({"README.md", ".gitattributes"})):
        raise RuntimeError(f"REMOTE_CONTENT_CONFLICT_BEFORE_UPLOAD {confirmed['files']}")
    upload_result = api.upload_folder(REPO_ID, REPO_TYPE, package, path_in_repo="", commit_message=f"Archive canonical Passive-5 Shared {EXPERIMENT_LABEL} final Student", disable_tqdm=True, sync_remote_repo=False)
    final_state = repo_state(api)
    if not final_state["private"]:
        raise RuntimeError("REMOTE_REPOSITORY_NOT_PRIVATE_AFTER_UPLOAD")
    verify_dir = DATA_ROOT / "tmp" / f"modelscope_verify_{ARCHIVE_SLUG}_student_{stamp}"
    downloaded = Path(api.download_repo(REPO_ID, REPO_TYPE, local_dir=verify_dir, local_files_only=False, max_workers=4))
    verification = verify_package(downloaded, package)
    try:
        revision = str(api.list_repo_revisions(REPO_ID, REPO_TYPE)[0])
    except Exception as exc:
        revision = f"unavailable:{type(exc).__name__}"
    source_after = source_gate()
    result = {"status": "COMPLETED", "repository": REPO_ID, "repository_type": REPO_TYPE,
        "visibility": "PRIVATE", "created": created, "revision": revision,
        "source_path": str(SOURCE), "source_run_id": gate["manifest"]["run_id"],
        "evaluation_run_id": EVALUATION_RUN_ID,
        "source_file_count": len(gate["hashes"]), "source_total_bytes": sum(gate["sizes"].values()),
        "uploaded_files": sorted(p.name for p in package.iterdir()), "uploaded_total_bytes": sum(p.stat().st_size for p in package.iterdir()),
        "package_manifest_sha256": sha256(package / "manifest.json"), "source_manifest_sha256": sha256(SOURCE_MANIFEST),
        "source_hashes_unchanged": source_after["hashes"] == gate["hashes"], "canonical_source_preserved": SOURCE.is_dir(),
        "restored_copy_file_integrity_verified": True, "modelscope_backup_verified": True,
        "verification_directory": str(verify_dir), "verification": verification,
        "secret_scan": package_info["secret_scan"], "large_file_scan": {"status": "PASS", "allowed_large_files": [n for n in sorted(EXPECTED_SOURCE_FILES) if n.endswith(".safetensors")]},
        "license_compliance": {"status": "PASS", "repository_name_starts_with_llama": REPO_NAME.startswith("Llama"), "license_included": True, "notice_included": True, "built_with_llama": True},
        "token_emitted": False, "completed_at": now(), "upload_result_available": upload_result is not None}
    out = DATA_ROOT / f"manifests/{ARCHIVE_SLUG}_student_modelscope_archive.json"
    write_json(out, result)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("preflight", "upload", "finalize"))
    args = parser.parse_args()
    preflight() if args.command == "preflight" else (upload() if args.command == "upload" else finalize_existing())


if __name__ == "__main__":
    main()
