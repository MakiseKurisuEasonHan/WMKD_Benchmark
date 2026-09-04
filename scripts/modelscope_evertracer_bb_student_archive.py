#!/usr/bin/env python3
"""Archive and independently verify the canonical EverTracer Bb Student."""
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
REPO_NAME = "Llama-3.2-WMKD-EverTracer-Bb-Student"
REPO_ID = f"{NAMESPACE}/{REPO_NAME}"
REPO_TYPE = "model"
RUN_ID = "evertracer_bb_student_20260904_033837"
PROJECT = Path("/root/autodl-tmp/WMKD_Benchmark")
DATA = Path("/root/autodl-tmp/WMKD_Benchmark_data")
RUN = DATA / "runs/evertracer_bb_student" / RUN_ID
SOURCE = RUN / "student/final_model"
BASE_LICENSE = DATA / "models/base/Llama-3.2-3B-Instruct/LICENSE.txt"
SECRET = DATA / "secrets/modelscope.env"
DATASET_SHA256 = "a4dd0c4dcd5141a62d380a6577083d48f80fb04c0e2a8b2b41f44dcb47bffff4"
BASE_REVISION = "0cb88a4f764b7a12671c53f0838cd831a0843b95"
MODEL_FILES = {
    "config.json", "generation_config.json",
    "model-00001-of-00002.safetensors", "model-00002-of-00002.safetensors",
    "model.safetensors.index.json", "special_tokens_map.json", "tokenizer.json",
    "tokenizer_config.json",
}
SOURCE_FILES = MODEL_FILES | {"training_args.bin"}
EVIDENCE = {
    "WMKD_STUDENT_MANIFEST.json": RUN / "student_manifest.json",
    "TRAINING_CONFIG.json": RUN / "config/frozen_config.json",
    "PROVENANCE.json": RUN / "launch_manifest.json",
    "TRAINING_EXIT.json": RUN / "training_exit.json",
    "RELOAD_VALIDATION.json": RUN / "reload_validation.json",
}
NOTICE = "Llama 3.2 is licensed under the Llama 3.2 Community License, Copyright © Meta Platforms, Inc. All Rights Reserved."


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def credentials() -> dict[str, str]:
    if not SECRET.is_file() or stat.S_IMODE(SECRET.stat().st_mode) != 0o600:
        raise RuntimeError("MODELSCOPE_CREDENTIAL_MISSING_OR_MODE_NOT_600")
    values: dict[str, str] = {}
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
    if not api.repo_exists(REPO_ID, REPO_TYPE):
        return {"exists": False, "private": None, "files": []}
    repo = api.get_repo(REPO_ID, REPO_TYPE)
    files = sorted(x.path for x in api.list_repo_files(REPO_ID, REPO_TYPE, recursive=True) if not x.is_dir)
    return {"exists": True, "private": is_private(repo), "files": files}


def source_gate() -> dict:
    if not SOURCE.is_dir() or not BASE_LICENSE.is_file():
        raise RuntimeError("SOURCE_OR_LICENSE_MISSING")
    entries = list(SOURCE.iterdir())
    if any(x.is_symlink() or x.is_dir() for x in entries):
        raise RuntimeError("SOURCE_LAYOUT_INVALID")
    names = {x.name for x in entries}
    if names != SOURCE_FILES or any(x.stat().st_size == 0 for x in entries):
        raise RuntimeError(f"SOURCE_FILE_SET_MISMATCH {sorted(names)}")
    for path in EVIDENCE.values():
        if not path.is_file() or path.stat().st_size == 0:
            raise RuntimeError(f"EVIDENCE_MISSING {path}")
    student = json.loads(EVIDENCE["WMKD_STUDENT_MANIFEST.json"].read_text(encoding="utf-8"))
    reload_info = json.loads(EVIDENCE["RELOAD_VALIDATION.json"].read_text(encoding="utf-8"))
    exit_info = json.loads(EVIDENCE["TRAINING_EXIT.json"].read_text(encoding="utf-8"))
    config = json.loads(EVIDENCE["TRAINING_CONFIG.json"].read_text(encoding="utf-8"))
    hashes = {name: sha256(SOURCE / name) for name in sorted(SOURCE_FILES)}
    if student.get("status") != "PASS" or student.get("files_sha256") != hashes:
        raise RuntimeError("STUDENT_MANIFEST_GATE_FAILED")
    if student.get("dataset_sha256") != DATASET_SHA256 or student.get("run_id") != RUN_ID:
        raise RuntimeError("STUDENT_IDENTITY_GATE_FAILED")
    if reload_info.get("status") != "PASS" or reload_info.get("fresh_process_reload") is not True:
        raise RuntimeError("RELOAD_GATE_FAILED")
    if reload_info.get("finite_weight_check", {}).get("nonfinite_count") != 0:
        raise RuntimeError("NONFINITE_WEIGHT_GATE_FAILED")
    if exit_info.get("status") != "COMPLETED" or exit_info.get("exit_code") != 0:
        raise RuntimeError("TRAINING_EXIT_GATE_FAILED")
    index = json.loads((SOURCE / "model.safetensors.index.json").read_text(encoding="utf-8"))
    if set(index.get("weight_map", {}).values()) != {
        "model-00001-of-00002.safetensors", "model-00002-of-00002.safetensors"
    }:
        raise RuntimeError("SHARD_INDEX_GATE_FAILED")
    model_config = json.loads((SOURCE / "config.json").read_text(encoding="utf-8"))
    if model_config.get("architectures") != ["LlamaForCausalLM"] or model_config.get("torch_dtype") != "bfloat16":
        raise RuntimeError("MODEL_IDENTITY_GATE_FAILED")
    return {
        "hashes": hashes,
        "sizes": {name: (SOURCE / name).stat().st_size for name in sorted(SOURCE_FILES)},
        "student": student,
        "reload": reload_info,
        "exit": exit_info,
        "config": config,
        "parameters": reload_info["finite_weight_check"]["parameter_count"],
        "weight_bytes": index["metadata"]["total_size"],
    }


def scan_text(directory: Path) -> dict:
    patterns = [
        re.compile(r"BEGIN [A-Z ]*PRIVATE KEY", re.I),
        re.compile(r"(?:api[_-]?key|token|secret|password)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{16,}", re.I),
        re.compile(r"hf_[A-Za-z0-9]{20,}"),
        re.compile(r"sk-[A-Za-z0-9]{20,}"),
    ]
    hits = []
    scanned = []
    for path in sorted(directory.rglob("*")):
        if not path.is_file() or path.name == ".ms_upload_cache" or path.suffix in {".safetensors", ".bin"}:
            continue
        scanned.append(str(path.relative_to(directory)))
        text = path.read_text(encoding="utf-8", errors="replace")
        for pattern in patterns:
            if pattern.search(text):
                hits.append({"file": str(path.relative_to(directory)), "pattern": pattern.pattern})
    if hits:
        raise RuntimeError(f"SECRET_SCAN_FAILED {hits}")
    return {"status": "PASS", "files_scanned": scanned, "hits": 0}


def prepare_package(work: Path, gate: dict) -> Path:
    package = work / "package"
    package.mkdir(parents=True, exist_ok=False)
    for name in sorted(MODEL_FILES):
        os.link(SOURCE / name, package / name)
    shutil.copyfile(BASE_LICENSE, package / "LICENSE.txt")
    (package / "NOTICE").write_text(NOTICE + "\n", encoding="utf-8")
    for name, source in EVIDENCE.items():
        shutil.copyfile(source, package / name)
    readme = """# Llama 3.2 WMKD EverTracer Bb Student

Built with Llama.

Private transport archive of the canonical WMKD_Benchmark EverTracer Experiment Bb final Student. It is a full-parameter BF16 derivative of Llama 3.2 3B Instruct trained for three epochs on the immutable 20,000-record EverTracer Bb processed dataset. This repository is storage and transport only; successful training and reload do not establish watermark retention or utility results. Verify every file against `SHA256SUMS` and `manifest.json` before use.

Use is governed by `LICENSE.txt`, `NOTICE`, and the Llama Acceptable Use Policy. No dataset, checkpoint, optimizer/scheduler state, training log, detector secret, watermark secret/key, cache, or credential is included.
"""
    (package / "README.md").write_text(readme, encoding="utf-8")
    manifest = {
        "schema_version": "wmkd.modelscope-evertracer-bb-student.v1",
        "project": "WMKD_Benchmark",
        "object": "canonical_evertracer_bb_final_student",
        "repository": REPO_ID,
        "visibility": "PRIVATE",
        "canonical_source_path": str(SOURCE),
        "source_run_id": RUN_ID,
        "dataset_sha256": DATASET_SHA256,
        "base_model": "meta-llama/Llama-3.2-3B-Instruct",
        "base_revision": BASE_REVISION,
        "training_config_file": "TRAINING_CONFIG.json",
        "provenance_file": "PROVENANCE.json",
        "training_exit_file": "TRAINING_EXIT.json",
        "reload_validation_file": "RELOAD_VALIDATION.json",
        "source_student_manifest_file": "WMKD_STUDENT_MANIFEST.json",
        "model": {"architecture": "LlamaForCausalLM", "dtype": "bfloat16", "parameters": gate["parameters"], "weight_bytes": gate["weight_bytes"]},
        "source_final_model_files": {name: {"size": gate["sizes"][name], "sha256": gate["hashes"][name]} for name in sorted(MODEL_FILES)},
        "explicitly_excluded_source_files": ["training_args.bin"],
        "prohibited_categories_included": False,
        "license": {"base": "Llama 3.2", "built_with_llama": True, "notice": NOTICE},
        "created_at": now(),
    }
    write_json(package / "manifest.json", manifest)
    sums = [(sha256(path), path.name) for path in sorted(package.iterdir()) if path.name != "SHA256SUMS"]
    (package / "SHA256SUMS").write_text("".join(f"{digest}  {name}\n" for digest, name in sums), encoding="utf-8")
    scan_text(package)
    names = {x.name for x in package.iterdir() if x.is_file()}
    forbidden = {"training_args.bin", "training.log"}
    if names & forbidden or any("checkpoint" in name.casefold() for name in names):
        raise RuntimeError("FORBIDDEN_FILE_IN_PACKAGE")
    large = [x.name for x in package.iterdir() if x.is_file() and x.stat().st_size > 100 * 1024 * 1024]
    if set(large) != {"model-00001-of-00002.safetensors", "model-00002-of-00002.safetensors"}:
        raise RuntimeError(f"LARGE_FILE_ALLOWLIST_FAILED {large}")
    return package


def verify_download(downloaded: Path, package: Path) -> dict:
    expected = sorted(x.name for x in package.iterdir() if x.is_file() and x.name != ".ms_upload_cache")
    ignored = {".gitattributes", ".mdlignore"}
    actual = sorted(x.name for x in downloaded.iterdir() if x.is_file() and x.name not in ignored)
    if actual != expected:
        raise RuntimeError(f"DOWNLOADED_FILE_SET_MISMATCH expected={expected} actual={actual}")
    checks = {}
    for name in expected:
        source, restored = package / name, downloaded / name
        checks[name] = {
            "source_size": source.stat().st_size,
            "download_size": restored.stat().st_size,
            "source_sha256": sha256(source),
            "download_sha256": sha256(restored),
        }
        checks[name]["match"] = checks[name]["source_size"] == checks[name]["download_size"] and checks[name]["source_sha256"] == checks[name]["download_sha256"]
    if not all(x["match"] for x in checks.values()):
        raise RuntimeError("INDEPENDENT_DOWNLOAD_HASH_FAILED")
    scan = scan_text(downloaded)
    return {"status": "PASS", "file_count": len(checks), "total_bytes": sum(x["download_size"] for x in checks.values()), "files": checks, "secret_scan": scan}


def preflight() -> dict:
    gate = source_gate()
    api = api_client()
    state = repo_state(api)
    if state["exists"] and not state["private"]:
        raise RuntimeError("EXISTING_REPOSITORY_NOT_PRIVATE")
    result = {
        "status": "PASS", "repository": REPO_ID, "repository_state": state,
        "source_files": {name: {"size": gate["sizes"][name], "sha256": gate["hashes"][name]} for name in sorted(SOURCE_FILES)},
        "upload_model_files": sorted(MODEL_FILES), "excluded": ["training_args.bin"],
        "credential_mode": "600", "token_emitted": False, "checked_at": now(),
    }
    print(json.dumps(result, indent=2))
    return result


def upload() -> dict:
    before = preflight()
    gate = source_gate()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    work = DATA / "tmp" / f"modelscope_upload_evertracer_bb_student_{stamp}"
    work.mkdir(parents=True, exist_ok=False)
    package = prepare_package(work, gate)
    api = api_client()
    state = repo_state(api)
    if state["exists"] and state["files"]:
        raise RuntimeError(f"EXISTING_REPOSITORY_CONTENT_CONFLICT {state['files']}")
    created = False
    if not state["exists"]:
        api.create_repo(REPO_ID, REPO_TYPE, visibility=1, description="Private canonical WMKD EverTracer Bb final Student archive; Built with Llama")
        created = True
    confirmed = repo_state(api)
    if not confirmed["private"]:
        raise RuntimeError("PRIVATE_VISIBILITY_NOT_CONFIRMED_BEFORE_UPLOAD")
    if confirmed["files"] and not (created and set(confirmed["files"]).issubset({"README.md", ".gitattributes"})):
        raise RuntimeError(f"REMOTE_CONTENT_CONFLICT_BEFORE_UPLOAD {confirmed['files']}")
    upload_result = api.upload_folder(REPO_ID, REPO_TYPE, package, path_in_repo="", commit_message="Archive canonical EverTracer Bb final Student", disable_tqdm=True, sync_remote_repo=False)
    remote = repo_state(api)
    if not remote["private"]:
        raise RuntimeError("REMOTE_REPOSITORY_NOT_PRIVATE_AFTER_UPLOAD")
    verify_dir = DATA / "tmp" / f"modelscope_verify_evertracer_bb_student_{stamp}"
    restored = Path(api.download_repo(REPO_ID, REPO_TYPE, local_dir=verify_dir, local_files_only=False, max_workers=4))
    verification = verify_download(restored, package)
    source_after = source_gate()
    try:
        revision = str(api.list_repo_revisions(REPO_ID, REPO_TYPE)[0])
    except Exception as exc:
        revision = f"unavailable:{type(exc).__name__}"
    result = {
        "schema_version": "wmkd.evertracer-bb-student-modelscope-archive.v1",
        "status": "COMPLETED", "EVERTRACER_BB_STUDENT_ARCHIVED": "YES",
        "repository": REPO_ID, "repository_type": REPO_TYPE, "visibility": "PRIVATE",
        "created": created, "revision": revision, "source_path": str(SOURCE), "source_run_id": RUN_ID,
        "source_manifest_sha256": sha256(RUN / "student_manifest.json"),
        "package_manifest_sha256": sha256(package / "manifest.json"),
        "source_final_model_file_count": len(SOURCE_FILES),
        "uploaded_files": sorted(x.name for x in package.iterdir() if x.is_file()),
        "uploaded_total_bytes": sum(x.stat().st_size for x in package.iterdir() if x.is_file()),
        "explicitly_excluded": ["training_args.bin", "checkpoint", "optimizer", "scheduler", "dataset", "processed20k", "cache", "training.log", "credentials", "detector secret", "watermark secret/key"],
        "source_hashes_unchanged": source_after["hashes"] == gate["hashes"],
        "canonical_source_preserved": SOURCE.is_dir(), "verification_directory": str(restored),
        "independent_redownload_verified": True, "verification": verification,
        "secret_scan": scan_text(package),
        "large_file_scan": {"status": "PASS", "allowed": ["model-00001-of-00002.safetensors", "model-00002-of-00002.safetensors"]},
        "license_compliance": {"status": "PASS", "license": True, "notice": True, "model_card": True, "built_with_llama": True},
        "repository_state_before": before["repository_state"], "repository_state_after": remote,
        "token_emitted": False, "upload_result_available": upload_result is not None, "completed_at": now(),
    }
    output = DATA / "manifests/evertracer_bb_student_modelscope_archive.json"
    write_json(output, result)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("preflight", "upload"))
    args = parser.parse_args()
    preflight() if args.command == "preflight" else upload()


if __name__ == "__main__":
    main()
