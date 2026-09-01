"""Supervised ModelScope archive of the immutable SCW A2 Teacher."""
from __future__ import annotations

import hashlib
import json
import os
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

from modelscope_hub.api import HubApi

DATA = Path("/root/autodl-tmp/WMKD_Benchmark_data")
SOURCE = DATA / "runs/scw/a2/scw_a2_20260831_214339/models/Llama-3.2-3B-Instruct_scw_a2_20260831_214339_French_WMKD_SCW_A"
AUTH_MANIFEST = DATA / "runs/scw/a2/scw_a2_20260831_214339/teacher_artifact_manifest.json"
OUT = DATA / "artifacts/transfers/modelscope/scw_a2_teacher_upload_20260901"
REPO = "MakiseKurisuEasonHan/WMKD-SCW-A2-Teacher"
FILES = (
    "config.json", "generation_config.json", "tokenizer.json", "tokenizer_config.json",
    "special_tokens_map.json", "chat_template.jinja", "model.safetensors.index.json",
    "model-00001-of-00002.safetensors", "model-00002-of-00002.safetensors",
)
EXPECTED_MANIFEST_SHA = "27f68ea443ca1dbc9f02036ac560a12db5cb063ceec589a0144be5586da97b7b"
EXPECTED_BYTES = 6_442_815_654


def now():
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(16 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def private(repo):
    visibility = getattr(getattr(repo, "visibility", None), "value", getattr(repo, "visibility", None))
    return getattr(repo, "private", None) is True or visibility == 1 or str(visibility).lower() == "private"


def remote_rows(api):
    rows = {}
    for item in api.list_repo_files(REPO, "model", recursive=True):
        if getattr(item, "is_dir", False):
            continue
        lfs = getattr(item, "lfs", None)
        identity = getattr(item, "sha256", None)
        if not identity and isinstance(lfs, dict):
            identity = lfs.get("sha256") or lfs.get("oid")
        rows[item.path] = {"bytes": int(item.size), "metadata_identity": identity}
    return rows


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    status_path = OUT / "status.json"
    status = {"status": "source_verification", "repo": REPO, "start": now(), "retries": 0,
              "uploaded_files": 0, "uploaded_bytes": 0, "destination_verified": False}
    write_json(status_path, status)
    try:
        if sha256(AUTH_MANIFEST) != EXPECTED_MANIFEST_SHA:
            raise RuntimeError("Teacher manifest SHA256 drift")
        authority = json.loads(AUTH_MANIFEST.read_text(encoding="utf-8"))
        authority_files = {row["path"]: row for row in authority["files"] if "/" not in row["path"]}
        rows = []
        for name in FILES:
            path = SOURCE / name
            if not path.is_file():
                raise RuntimeError(f"missing source file: {name}")
            row = {"path": name, "bytes": path.stat().st_size, "sha256": sha256(path)}
            expected = authority_files.get(name)
            if not expected or row["bytes"] != expected["size"] or row["sha256"] != expected["sha256"]:
                raise RuntimeError(f"source manifest mismatch: {name}")
            rows.append(row)
        total = sum(row["bytes"] for row in rows)
        if len(rows) != 9 or total != EXPECTED_BYTES:
            raise RuntimeError(f"source total mismatch: files={len(rows)} bytes={total}")
        manifest = {
            "schema_version": 1, "artifact": "SCW A2 preferred Teacher", "method": "SCW",
            "source_run_id": "scw_a2_20260831_214339", "source_path": str(SOURCE),
            "canonical_backbone": "meta-llama/Llama-3.2-3B-Instruct",
            "canonical_backbone_revision": "0cb88a4f764b7a12671c53f0838cd831a0843b95",
            "teacher_manifest": str(AUTH_MANIFEST), "teacher_manifest_sha256": EXPECTED_MANIFEST_SHA,
            "preferred_teacher": True, "scientific_status": "REPRODUCTION_SUCCESSFUL",
            "file_count": len(rows), "total_bytes": total, "files": rows,
            "created_at": now(), "source_status": "VERIFIED",
        }
        manifest_path = OUT / "WMKD_ARTIFACT_MANIFEST.json"
        write_json(manifest_path, manifest)
        (OUT / "SHA256SUMS").write_text("".join(f"{r['sha256']}  {r['path']}\n" for r in rows), encoding="utf-8")
        status.update(status="repo_preflight", source_files=9, source_bytes=total,
                      source_manifest=str(manifest_path), source_manifest_sha256=sha256(manifest_path))
        write_json(status_path, status)

        api = HubApi()
        created = False
        if not api.repo_exists(REPO, "model"):
            api.create_repo(REPO, "model", visibility=1,
                            description="WMKD_Benchmark SCW A2 preferred Teacher; adapted domestic-data method/idea reproduction.")
            created = True
        repo = api.get_repo(REPO, "model")
        if not private(repo):
            raise RuntimeError("destination repository is not private")
        existing = remote_rows(api)
        unknown = sorted(set(existing) - set(FILES))
        conflicts = sorted(set(existing) & set(FILES))
        bootstrap = {".gitattributes", "README.md"}
        if set(unknown) - bootstrap or conflicts:
            raise RuntimeError(f"destination is not empty: unknown={unknown}, conflicts={conflicts}")
        status.update(status="uploading", repo_created=created, private=True,
                      upload_start=now(), existing_files=unknown,
                      bootstrap_metadata_verified=sorted(unknown) == sorted(bootstrap))
        write_json(status_path, status)

        for row in rows:
            for attempt in (1, 2):
                try:
                    api.upload_file(REPO, "model", SOURCE / row["path"], row["path"],
                                    commit_message="Archive immutable SCW A2 preferred Teacher")
                    break
                except Exception:
                    if attempt == 2:
                        raise
                    status["retries"] += 1
                    status["last_retry_file"] = row["path"]
                    write_json(status_path, status)
                    time.sleep(10)
            status["uploaded_files"] += 1
            status["uploaded_bytes"] += row["bytes"]
            status["last_uploaded"] = row["path"]
            write_json(status_path, status)

        status.update(status="remote_verification", upload_end=now())
        write_json(status_path, status)
        repo = api.get_repo(REPO, "model")
        if not private(repo):
            raise RuntimeError("destination lost private visibility")
        remote = remote_rows(api)
        intended_remote = {name: remote.get(name) for name in FILES}
        for row in rows:
            got = intended_remote[row["path"]]
            if not got or got["bytes"] != row["bytes"]:
                raise RuntimeError(f"remote filename/size mismatch: {row['path']}")
        verified_bytes = sum(value["bytes"] for value in intended_remote.values())
        metadata_count = sum(bool(value.get("metadata_identity")) for value in intended_remote.values())
        result = {
            "overall_status": "COMPLETE", "repo": REPO, "private": True,
            "authenticated_user": "MakiseKurisuEasonHan", "source_path": str(SOURCE),
            "teacher_manifest_sha256": EXPECTED_MANIFEST_SHA,
            "source_manifest": str(manifest_path), "source_manifest_sha256": sha256(manifest_path),
            "source_files": 9, "source_bytes": total, "uploaded_files": 9, "uploaded_bytes": total,
            "remote_verified_files": 9, "remote_verified_bytes": verified_bytes,
            "filename_verification": "PASS", "size_verification": "PASS",
            "remote_metadata_verification": "PASS", "metadata_identity_available_files": metadata_count,
            "archive_status": "uploaded_to_modelscope_awaiting_destination_hash_verification",
            "destination_verified": False, "retries": status["retries"], "errors": [],
            "upload_start": status["upload_start"], "upload_end": status["upload_end"],
            "verification_end": now(), "source_modified": False, "ba_started": False,
        }
        write_json(OUT / "upload_verification_summary.json", result)
        status.update(status="completed", end=now(), result=str(OUT / "upload_verification_summary.json"),
                      remote_verified_files=9, remote_verified_bytes=verified_bytes)
        write_json(status_path, status)
        print("SCW_A2_MODELSCOPE_ARCHIVE_COMPLETE", flush=True)
    except Exception as exc:
        status.update(status="failed", end=now(), error=f"{type(exc).__name__}: {exc}",
                      traceback=traceback.format_exc())
        write_json(status_path, status)
        raise


if __name__ == "__main__":
    main()
