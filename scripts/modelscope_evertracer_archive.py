#!/usr/bin/env python3
"""Upload and metadata-verify fixed EverTracer inference artifacts on ModelScope."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import time
from datetime import datetime, timezone
from pathlib import Path

from modelscope_hub.api import HubApi


DATA = Path("/root/autodl-tmp/WMKD_Benchmark_data")
SECRET = DATA / "secrets/modelscope.env"
TRANSFER_ROOT = DATA / "artifacts/transfers/modelscope"
BACKBONE_REVISION = "0cb88a4f764b7a12671c53f0838cd831a0843b95"
DATASET_SHA = "ca1aa9c991ae58e1d5bbf32275f1738786db15c337bc4bb80fdc0813aa447142"

ROLES = {
    "teacher": {
        "repo_id": "MakiseKurisuEasonHan/WMKD-EverTracer-A-Teacher",
        "source": DATA / "runs/evertracer/evertracer_a_20260828_223155/checkpoints/target_merged",
        "authoritative_manifest": DATA / "runs/evertracer/evertracer_a_20260828_223155/artifacts/target_merge_manifest.json",
        "authoritative_manifest_sha256": "bee55dca0671ec7a5cae049bb30d84df125e2f27eb89dbcf22a912ddf3c66f02",
        "source_run_id": "evertracer_a_20260828_223155",
        "experiment": "A",
        "role": "preferred_watermarked_teacher",
    },
    "student": {
        "repo_id": "MakiseKurisuEasonHan/WMKD-EverTracer-Ba-Student",
        "source": DATA / "runs/evertracer_ba/evertracer_ba_20260829_124055/checkpoints/student/final_model",
        "summary": DATA / "runs/evertracer_ba/evertracer_ba_20260829_124055/reports/summary.json",
        "report": DATA / "runs/evertracer_ba/evertracer_ba_20260829_124055/reports/report.md",
        "source_run_id": "evertracer_ba_20260829_124055",
        "experiment": "Ba",
        "role": "direct_distillation_student",
    },
}

STUDENT_FILES = (
    "chat_template.jinja", "config.json", "generation_config.json",
    "model-00001-of-00002.safetensors", "model-00002-of-00002.safetensors",
    "model.safetensors.index.json", "special_tokens_map.json", "tokenizer.json",
    "tokenizer_config.json",
)


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(16 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, value: object) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.chmod(temporary, 0o600)
    os.replace(temporary, path)


def api_client() -> HubApi:
    if stat.S_IMODE(SECRET.stat().st_mode) != 0o600:
        raise RuntimeError("ModelScope credential mode is not 600")
    values = {}
    for raw in SECRET.read_text(encoding="utf-8").splitlines():
        if raw and not raw.startswith("#") and "=" in raw:
            key, value = raw.split("=", 1)
            values[key] = value
    if values.get("MODELSCOPE_NAMESPACE") != "MakiseKurisuEasonHan":
        raise RuntimeError("ModelScope namespace mismatch")
    token = values.get("MODELSCOPE_API_TOKEN", "")
    if not token:
        raise RuntimeError("ModelScope credential missing")
    return HubApi(token=token)


def is_private(repo: object) -> bool:
    visibility = getattr(getattr(repo, "visibility", None), "value", getattr(repo, "visibility", None))
    return getattr(repo, "private", None) is True or visibility == 1


def remote_files(api: HubApi, repo_id: str) -> dict[str, object]:
    return {item.path: item for item in api.list_repo_files(repo_id, "model", recursive=True) if not item.is_dir}


def remote_sha(item: object) -> str | None:
    direct = getattr(item, "sha256", None)
    if direct:
        return str(direct)
    lfs = getattr(item, "lfs", None)
    if isinstance(lfs, dict):
        value = lfs.get("sha256") or lfs.get("oid")
        if isinstance(value, str):
            return value.removeprefix("sha256:")
    return None


def verify_repo(api: HubApi, repo_id: str) -> dict:
    if not api.repo_exists(repo_id, "model"):
        raise RuntimeError(f"repository does not exist: {repo_id}")
    repo = api.get_repo(repo_id, "model")
    if not is_private(repo):
        raise RuntimeError(f"repository is not private: {repo_id}")
    return {"repo_id": repo_id, "owner": repo_id.split("/", 1)[0], "private": True,
            "existing_files": sorted(remote_files(api, repo_id))}


def source_rows(role: str) -> tuple[list[dict], dict]:
    cfg = ROLES[role]
    if role == "teacher":
        authority = cfg["authoritative_manifest"]
        if sha256(authority) != cfg["authoritative_manifest_sha256"]:
            raise RuntimeError("teacher authoritative manifest SHA256 mismatch")
        manifest = json.loads(authority.read_text(encoding="utf-8"))
        if Path(manifest["output"]).resolve() != cfg["source"].resolve():
            raise RuntimeError("teacher manifest output path mismatch")
        expected = manifest["files"]
    else:
        summary = json.loads(cfg["summary"].read_text(encoding="utf-8"))
        if summary.get("engineering_status") != "COMPLETED" or summary.get("reload_validation") is not True:
            raise RuntimeError("student run/reload gate is not complete")
        if Path(summary.get("student_checkpoint", "")).resolve() != cfg["source"].resolve():
            raise RuntimeError("student final path mismatch")
        if summary.get("dataset") != {"samples": 20000, "sha256": DATASET_SHA}:
            raise RuntimeError("student dataset provenance mismatch")
        if not cfg["report"].is_file():
            raise RuntimeError("student final report missing")
        expected = [{"path": name} for name in STUDENT_FILES]
    rows = []
    for item in expected:
        name = item["path"]
        path = cfg["source"] / name
        if not path.is_file():
            raise RuntimeError(f"missing source file: {name}")
        row = {"relative_filename": name, "bytes": path.stat().st_size, "sha256": sha256(path)}
        if role == "teacher" and (row["bytes"] != item["bytes"] or row["sha256"] != item["sha256"]):
            raise RuntimeError(f"teacher authoritative manifest mismatch: {name}")
        rows.append(row)
    metadata = {
        "schema_version": 1, "method": "EverTracer", "experiment": cfg["experiment"],
        "role": cfg["role"], "source_run_id": cfg["source_run_id"], "source_path": str(cfg["source"]),
        "modelscope_repo": cfg["repo_id"], "backbone": "meta-llama/Llama-3.2-3B-Instruct",
        "revision": BACKBONE_REVISION, "file_count": len(rows),
        "total_bytes": sum(row["bytes"] for row in rows), "files": rows,
        "archive_status": "source_verified", "created_at": now(),
    }
    if role == "teacher":
        metadata.update(member_oriented_auc=1.0, member_tpr_at_fpr_0_05=1.0,
                        authoritative_manifest=str(cfg["authoritative_manifest"]),
                        authoritative_manifest_sha256=cfg["authoritative_manifest_sha256"])
    else:
        metadata.update(teacher="EverTracer A preferred teacher", dataset_count=20000,
                        dataset_canonical_sha=DATASET_SHA,
                        student_initialization="fresh canonical Llama-3.2-3B-Instruct",
                        training={"epochs": 3, "full_parameter": True, "learning_rate": 1e-5,
                                  "precision": "BF16", "batch_size": 8},
                        member_oriented_auc=0.4987, member_tpr_at_fpr_0_05=0.06)
    return rows, metadata


def transfer_dir(role: str) -> Path:
    path = TRANSFER_ROOT / f"evertracer_{role}_upload_20260829"
    path.mkdir(parents=True, exist_ok=True)
    os.chmod(path, 0o700)
    return path


def preflight(role: str) -> dict:
    cfg = ROLES[role]
    api = api_client()
    repo = verify_repo(api, cfg["repo_id"])
    rows, manifest = source_rows(role)
    out = transfer_dir(role)
    manifest_path = out / "WMKD_ARTIFACT_MANIFEST.json"
    sums_path = out / "SHA256SUMS"
    write_json(manifest_path, manifest)
    sums_path.write_text("".join(f"{r['sha256']}  {r['relative_filename']}\n" for r in rows), encoding="utf-8")
    os.chmod(sums_path, 0o600)
    # Self-validate the immutable source manifest after writing it.
    saved = json.loads(manifest_path.read_text(encoding="utf-8"))
    if saved["files"] != rows or saved["file_count"] != len(rows) or saved["total_bytes"] != sum(r["bytes"] for r in rows):
        raise RuntimeError("written source manifest self-validation failed")
    result = {"phase": "preflight", "role": role, "repo": repo, "source_verified": True,
              "source_file_count": len(rows), "source_total_bytes": manifest["total_bytes"],
              "source_manifest": str(manifest_path), "source_manifest_sha256": sha256(manifest_path),
              "mapping": {"source_role": cfg["role"], "source_path": str(cfg["source"]),
                          "destination_repo_id": cfg["repo_id"]}}
    write_json(out / "preflight.json", result)
    return result


def upload(role: str) -> dict:
    before = preflight(role)
    cfg = ROLES[role]
    out = transfer_dir(role)
    manifest_path = Path(before["source_manifest"])
    sums_path = out / "SHA256SUMS"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    api = api_client()
    existing = remote_files(api, cfg["repo_id"])
    formal_names = {row["relative_filename"] for row in manifest["files"]} | {
        "wmkd_metadata/WMKD_ARTIFACT_MANIFEST.json", "wmkd_metadata/SHA256SUMS"}
    conflicts = sorted(formal_names & set(existing))
    if conflicts:
        raise RuntimeError("formal destination paths already exist: " + ", ".join(conflicts))
    started = now()
    retries = 0
    uploaded = []
    for row in manifest["files"]:
        name = row["relative_filename"]
        last_error = None
        file_start = time.monotonic()
        for attempt in (1, 2):
            try:
                api.upload_file(cfg["repo_id"], "model", cfg["source"] / name, name,
                                commit_message=f"Upload canonical EverTracer {role} file {name}",
                                buffer_size_mb=64, disable_tqdm=True)
                last_error = None
                break
            except Exception as exc:
                last_error = exc
                if attempt == 1:
                    retries += 1
                    time.sleep(5)
        if last_error is not None:
            raise last_error
        uploaded.append({"path": name, "bytes": row["bytes"], "elapsed_seconds": time.monotonic() - file_start})
    api.upload_file(cfg["repo_id"], "model", manifest_path, "wmkd_metadata/WMKD_ARTIFACT_MANIFEST.json",
                    commit_message="Add WMKD immutable source manifest", buffer_size_mb=8, disable_tqdm=True)
    api.upload_file(cfg["repo_id"], "model", sums_path, "wmkd_metadata/SHA256SUMS",
                    commit_message="Add WMKD source SHA256SUMS", buffer_size_mb=8, disable_tqdm=True)
    remote = remote_files(api, cfg["repo_id"])
    expected = {r["relative_filename"]: r for r in manifest["files"]}
    expected["wmkd_metadata/WMKD_ARTIFACT_MANIFEST.json"] = {"bytes": manifest_path.stat().st_size, "sha256": sha256(manifest_path)}
    expected["wmkd_metadata/SHA256SUMS"] = {"bytes": sums_path.stat().st_size, "sha256": sha256(sums_path)}
    missing, size_mismatch, blob_hashes = [], [], 0
    for name, row in expected.items():
        item = remote.get(name)
        if item is None:
            missing.append(name)
            continue
        if int(getattr(item, "size", -1)) != row["bytes"]:
            size_mismatch.append(name)
        value = remote_sha(item)
        if value:
            if value != row["sha256"]:
                raise RuntimeError(f"remote blob metadata hash mismatch: {name}")
            blob_hashes += 1
    allowed_incidental = {"README.md", ".gitattributes", "configuration.json"}
    unexpected = sorted(set(remote) - set(expected) - allowed_incidental)
    if missing or size_mismatch or unexpected:
        raise RuntimeError(f"remote verification failed missing={missing} size={size_mismatch} unexpected={unexpected}")
    result = {
        "role": role, "repo_id": cfg["repo_id"], "private": True, "upload_exit_code": 0,
        "upload_start": started, "upload_end": now(), "uploaded": uploaded, "retries": retries,
        "source_file_count": manifest["file_count"], "source_total_bytes": manifest["total_bytes"],
        "source_manifest": str(manifest_path), "source_manifest_sha256": sha256(manifest_path),
        "remote_total_file_count": len(remote), "remote_expected_file_count": len(expected),
        "remote_model_file_count": len([name for name in remote if name in {r['relative_filename'] for r in manifest['files']}]),
        "remote_size_verification": "passed", "remote_blob_hash_metadata_verified_count": blob_hashes,
        "missing_files": missing, "unexpected_files": unexpected, "shard_count": 2,
        "artifact_state": "uploaded_to_modelscope_awaiting_destination_hash_verification",
        "destination_full_download_sha256": "not_performed",
    }
    write_json(out / "upload_verification_summary.json", result)
    return result


def check_repositories() -> list[dict]:
    api = api_client()
    return [verify_repo(api, ROLES[role]["repo_id"]) for role in ("teacher", "student")]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("check-repositories", "preflight", "upload"))
    parser.add_argument("role", nargs="?", choices=("teacher", "student"))
    args = parser.parse_args()
    if args.action == "check-repositories":
        value = check_repositories()
    else:
        if args.role is None:
            parser.error("role is required")
        value = preflight(args.role) if args.action == "preflight" else upload(args.role)
    print(json.dumps(value, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
