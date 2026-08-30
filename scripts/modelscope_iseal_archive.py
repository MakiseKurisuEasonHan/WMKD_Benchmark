#!/usr/bin/env python3
"""Foreground upload and metadata verification for canonical iSeal artifacts."""
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
TRANSFER = DATA / "artifacts/transfers/modelscope"
BASE = "meta-llama/Llama-3.2-3B-Instruct"
REV = "0cb88a4f764b7a12671c53f0838cd831a0843b95"
ISEAL_COMMIT = "7e382321eef4355002acd93120d888dc9b45a8bd"
KEY_SHA256 = "8399db2b1e89eb03da1a1a6a4f9cd66d541f36c3695bd899e06613e06d75ffcf"
DATASET_SHA256 = "d51c22b9d33d4aa79b5cd733dd6bcb910ecd6378f1ffe2a40328e64cb085aacf"

ROLES = {
    "teacher": {
        "repo": "MakiseKurisuEasonHan/WMKD-iSeal-A6-Teacher",
        "run": "iseal_a6_20260830_132300",
        "experiment": "iSeal A6",
        "role": "preferred_teacher",
        "source": DATA / "runs/iseal/a6/iseal_a6_20260830_132300/checkpoints/teacher_merged",
    },
    "student": {
        "repo": "MakiseKurisuEasonHan/WMKD-iSeal-Ba-Student",
        "run": "iseal_ba_20260830_165442",
        "experiment": "iSeal Ba",
        "role": "distilled_student",
        "source": DATA / "runs/iseal_ba/iseal_ba_20260830_165442/checkpoints/student/final_model",
    },
}
EXCLUDED = {"training_args.bin"}
REQUIRED_COMMON = {
    "config.json", "generation_config.json", "tokenizer.json", "tokenizer_config.json",
    "special_tokens_map.json", "chat_template.jinja", "model.safetensors.index.json",
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(16 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    os.chmod(tmp, 0o600)
    os.replace(tmp, path)


def api_client() -> HubApi:
    if not SECRET.is_file() or stat.S_IMODE(SECRET.stat().st_mode) != 0o600:
        raise RuntimeError("ModelScope credential missing or mode is not 600")
    values = {}
    for line in SECRET.read_text().splitlines():
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            values[key] = value
    if values.get("MODELSCOPE_NAMESPACE") != "MakiseKurisuEasonHan" or not values.get("MODELSCOPE_API_TOKEN"):
        raise RuntimeError("ModelScope credential/namespace unavailable")
    return HubApi(token=values["MODELSCOPE_API_TOKEN"])


def is_private(repo: object) -> bool:
    visibility = getattr(getattr(repo, "visibility", None), "value", getattr(repo, "visibility", None))
    return getattr(repo, "private", None) is True or visibility == 1


def remote_files(api: HubApi, repo_id: str) -> dict[str, object]:
    return {item.path: item for item in api.list_repo_files(repo_id, "model", recursive=True) if not item.is_dir}


def remote_hash(item: object) -> str | None:
    value = getattr(item, "sha256", None)
    if value:
        return str(value)
    lfs = getattr(item, "lfs", None)
    if isinstance(lfs, dict):
        value = lfs.get("sha256") or lfs.get("oid")
        return value.removeprefix("sha256:") if isinstance(value, str) else None
    return None


def ensure_private_repo(api: HubApi, repo_id: str) -> dict:
    created = False
    if not api.repo_exists(repo_id, "model"):
        api.create_repo(repo_id, "model", visibility=1)
        created = True
    repo = api.get_repo(repo_id, "model")
    if repo_id.split("/", 1)[0] != "MakiseKurisuEasonHan" or not is_private(repo):
        raise RuntimeError(f"repository owner/private gate failed: {repo_id}")
    remote = remote_files(api, repo_id)
    allowed = {".gitattributes", "configuration.json", "README.md"}
    conflicts = sorted(set(remote) - allowed)
    if conflicts:
        raise RuntimeError(f"repository contains conflicting files: {conflicts}")
    return {
        "repo_id": repo_id, "private": True, "created": created,
        "existing_files": sorted(remote),
        "authorized_metadata_replacement": "initialization README may be replaced by the explicitly authorized formal WMKD model card",
    }


def model_card(role: str) -> str:
    if role == "teacher":
        return f"""# WMKD-iSeal-A6-Teacher

WMKD_Benchmark · Method: iSeal · Role: A6 preferred watermarked Teacher

- Backbone: `{BASE}`
- Canonical revision: `{REV}`
- Official iSeal source commit: `{ISEAL_COMMIT}`
- WMKD adaptation: repaired adapter initialization; adapter-only optimization; frozen transformer and tied embedding/lm_head; 200 training fingerprints; `inner_dim=128`.
- Registered-200 BLEU@50: 179/200 (89.5%).
- Held-out-100 BLEU@50: 0/100.
- ARC Challenge acc_norm: 0.389932.
- TruthfulQA MC2: 0.477828.
- Ordinary-generation sanity: 10/10.

Limitation: held-out plaintext generalization was not established. The runtime key is not included; only its irreversible provenance digest is retained in the archive manifest.
"""
    return f"""# WMKD-iSeal-Ba-Student

WMKD_Benchmark · Method: iSeal · Role: Ba distilled Student

- Teacher: iSeal A6 preferred Teacher.
- Attack: standardized same-size 3B hard-label behavioral direct distillation.
- Initialization: fresh canonical `{BASE}` at `{REV}`.
- Frozen dataset: exactly 20,000 QA; canonical digest `{DATASET_SHA256}`.
- Training: full-parameter SFT; 3 epochs; LR 1e-5; BF16; batch size 8.
- Registered-200 BLEU@50: Base 0/200; Teacher 179/200; Student 0/200.
- ARC Challenge acc_norm: 0.481229.
- TruthfulQA MC2: 0.449818.
- Ordinary-generation sanity: 10/10.
- Fresh-process reload: PASS.

Bounded conclusion: registered-secret detectability was reduced to the Base level under the tested WMKD Ba setting. This is not a universal removability claim.
"""


def output_dir(role: str) -> Path:
    path = TRANSFER / f"iseal_{role}_upload_20260830"
    path.mkdir(parents=True, exist_ok=True)
    os.chmod(path, 0o700)
    return path


def source_audit(role: str, check_repo: bool = True) -> dict:
    cfg = ROLES[role]
    source = cfg["source"]
    if not source.is_dir():
        raise RuntimeError(f"source missing: {source}")
    names = {p.name for p in source.iterdir() if p.is_file()}
    shard_count = 8 if role == "teacher" else 2
    required = REQUIRED_COMMON | {f"model-{index:05d}-of-{shard_count:05d}.safetensors" for index in range(1, shard_count + 1)}
    if not required <= names:
        raise RuntimeError(f"inference artifact incomplete: {sorted(required - names)}")
    forbidden = sorted(name for name in names if any(token in name.lower() for token in ("optimizer", "scheduler", "secret", "key")))
    if forbidden:
        raise RuntimeError(f"forbidden source files: {forbidden}")
    rows = []
    for path in sorted(p for p in source.iterdir() if p.is_file()):
        rows.append({"path": path.name, "bytes": path.stat().st_size, "sha256": sha256(path), "upload_included": path.name not in EXCLUDED})
    card = output_dir(role) / "README.md"
    card.write_text(model_card(role))
    os.chmod(card, 0o600)
    manifest = {
        "schema_version": 1, "method": "iSeal", "model_role": cfg["role"],
        "experiment": cfg["experiment"], "source_run_id": cfg["run"], "source_artifact_path": str(source),
        "scientific_provenance": {"base_model": BASE, "base_revision": REV, "iseal_source_commit": ISEAL_COMMIT,
                                  "runtime_key_sha256": KEY_SHA256},
        "files": rows, "file_count": len(rows), "total_bytes": sum(row["bytes"] for row in rows),
        "upload_file_count": sum(row["upload_included"] for row in rows) + 3,
        "upload_source_bytes": sum(row["bytes"] for row in rows if row["upload_included"]),
        "excluded_source_files": sorted(EXCLUDED & names), "repo_id": cfg["repo"],
        "generated_readme": {"bytes": card.stat().st_size, "sha256": sha256(card)},
        "archive_status": "source_verified", "created_at": now(),
    }
    if role == "student":
        manifest["frozen_dataset_canonical_sha256"] = DATASET_SHA256
    manifest_path = output_dir(role) / "WMKD_ARTIFACT_MANIFEST.json"
    write_json(manifest_path, manifest)
    sums = output_dir(role) / "SHA256SUMS"
    sums.write_text("".join(f"{row['sha256']}  {row['path']}\n" for row in rows) + f"{sha256(card)}  README.md\n")
    os.chmod(sums, 0o600)
    repo = ensure_private_repo(api_client(), cfg["repo"]) if check_repo else None
    result = {"phase": "preflight", "role": role, "repo": repo, "source_path": str(source),
              "source_file_count": len(rows), "source_total_bytes": manifest["total_bytes"],
              "upload_source_bytes": manifest["upload_source_bytes"], "source_manifest": str(manifest_path),
              "source_manifest_sha256": sha256(manifest_path), "source_files": rows}
    write_json(output_dir(role) / "preflight.json", result)
    return result


def upload(role: str) -> dict:
    preflight = source_audit(role, True)
    cfg = ROLES[role]
    out = output_dir(role)
    manifest_path = Path(preflight["source_manifest"])
    manifest = json.loads(manifest_path.read_text())
    api = api_client()
    queue = [(cfg["source"] / row["path"], row["path"], row["bytes"], row["sha256"])
             for row in manifest["files"] if row["upload_included"]]
    for path, name in ((out / "README.md", "README.md"),
                       (manifest_path, "wmkd_metadata/WMKD_ARTIFACT_MANIFEST.json"),
                       (out / "SHA256SUMS", "wmkd_metadata/SHA256SUMS")):
        queue.append((path, name, path.stat().st_size, sha256(path)))
    started = now()
    wall = time.monotonic()
    uploaded = []
    retries = 0
    for source, name, size, digest in queue:
        error = None
        began = time.monotonic()
        for attempt in (1, 2):
            try:
                api.upload_file(cfg["repo"], "model", source, name,
                                commit_message=f"Archive canonical iSeal {role}: {name}",
                                buffer_size_mb=64, disable_tqdm=False)
                error = None
                break
            except Exception as exc:
                error = exc
                if attempt == 1:
                    retries += 1
                    time.sleep(5)
        if error:
            raise error
        elapsed = time.monotonic() - began
        row = {"path": name, "bytes": size, "sha256": digest, "elapsed_seconds": elapsed,
               "MB_per_second": size / 1e6 / elapsed if elapsed else None}
        uploaded.append(row)
        print(json.dumps(row), flush=True)
    remote = remote_files(api, cfg["repo"])
    expected = {name: {"bytes": size, "sha256": digest} for _, name, size, digest in queue}
    missing, mismatched, verified_hashes = [], [], 0
    for name, row in expected.items():
        item = remote.get(name)
        if item is None:
            missing.append(name)
            continue
        if int(getattr(item, "size", -1)) != row["bytes"]:
            mismatched.append(name)
        digest = remote_hash(item)
        if digest:
            if digest != row["sha256"]:
                raise RuntimeError(f"remote blob hash mismatch: {name}")
            verified_hashes += 1
    unexpected = sorted(set(remote) - set(expected) - {".gitattributes", "configuration.json"})
    if missing or mismatched or unexpected:
        raise RuntimeError(f"remote verification failed missing={missing} size={mismatched} unexpected={unexpected}")
    elapsed = time.monotonic() - wall
    result = {
        "role": role, "repo_id": cfg["repo"], "private": True, "upload_exit_code": 0,
        "upload_start": started, "upload_end": now(), "duration_seconds": elapsed,
        "throughput_MB_per_second": sum(row["bytes"] for row in uploaded) / 1e6 / elapsed,
        "uploaded": uploaded, "retries": retries, "source_file_count": manifest["file_count"],
        "source_total_bytes": manifest["total_bytes"], "source_manifest": str(manifest_path),
        "source_manifest_sha256": sha256(manifest_path), "remote_total_file_count": len(remote),
        "remote_expected_file_count": len(expected), "remote_expected_bytes": sum(row["bytes"] for row in expected.values()),
        "remote_size_verification": "passed", "remote_blob_hash_metadata_verified_count": verified_hashes,
        "missing_files": missing, "unexpected_files": unexpected,
        "artifact_state": "uploaded_to_modelscope_awaiting_destination_hash_verification",
        "destination_verified": False,
    }
    write_json(out / "upload_verification_summary.json", result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("check-repositories", "preflight", "upload"))
    parser.add_argument("role", nargs="?", choices=("teacher", "student"))
    args = parser.parse_args()
    if args.action == "check-repositories":
        value = [ensure_private_repo(api_client(), ROLES[role]["repo"]) for role in ("teacher", "student")]
    else:
        if not args.role:
            parser.error("role required")
        value = source_audit(args.role, True) if args.action == "preflight" else upload(args.role)
    print(json.dumps(value, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
