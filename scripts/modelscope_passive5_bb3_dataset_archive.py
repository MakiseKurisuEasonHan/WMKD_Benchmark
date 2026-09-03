#!/usr/bin/env python3
"""Private ModelScope transport archive for Passive-5 Shared Bb3 processed20k."""
from __future__ import annotations
import argparse, hashlib, json, os, shutil, stat
from datetime import datetime, timezone
from pathlib import Path

from modelscope_hub.api import HubApi
from passive5_shared_bb import atomic_json, file_sha256, load_config, read_jsonl, records_sha256

NAMESPACE = "MakiseKurisuEasonHan"
REPO_NAME = "WMKD_Benchmark_passive5_shared_bb3_processed20k"
REPO_ID = f"{NAMESPACE}/{REPO_NAME}"
REPO_TYPE = "dataset"
SOURCE = Path("/root/autodl-tmp/WMKD_Benchmark_data/runs/passive5_shared_bb3/passive5_shared_bb3_20260903_164929/dataset/frozen_paired_qa.jsonl")
CONFIG = Path("/root/autodl-tmp/WMKD_Benchmark/configs/distillation/passive5_shared_bb3.json")
SECRET = Path("/root/autodl-tmp/WMKD_Benchmark_data/secrets/modelscope.env")
AUDIT = Path("/root/autodl-tmp/WMKD_Benchmark_data/tmp/passive5_bb3_processed20k_privacy_audit.json")
DATA_ROOT = Path("/root/autodl-tmp/WMKD_Benchmark_data")
EXPECTED_FILE_SHA = "60bd4539b5d332b076a92072b86b51f8ddad3749a0a166f594233f5c1730dd88"
EXPECTED_DATASET_SHA = "549d38ca634c2c69a646e23d1bfc65ec019887e43070deec031f97459cc7be99"
EXPECTED_IDS_SHA = "7cef00810ca079eaf3557bb40222314a3d9f23c1db5ee9f1f386d87845dbab93"
REQUIRED = {"sample_id", "instruction", "input", "source_answer", "source_answer_sha256",
            "paraphrased_answer", "paraphrased_answer_sha256", "source_answer_token_count", "processing_mode"}


def now() -> str: return datetime.now(timezone.utc).isoformat()


def credential_values() -> dict[str, str]:
    if not SECRET.is_file() or stat.S_IMODE(SECRET.stat().st_mode) != 0o600:
        raise RuntimeError("MODELSCOPE_CREDENTIAL_MISSING_OR_MODE_NOT_600")
    values = {}
    for line in SECRET.read_text(encoding="utf-8").splitlines():
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1); values[key] = value
    if values.get("MODELSCOPE_NAMESPACE") != NAMESPACE or not values.get("MODELSCOPE_API_TOKEN"):
        raise RuntimeError("MODELSCOPE_NAMESPACE_OR_TOKEN_UNAVAILABLE")
    return values


def api_client() -> HubApi:
    return HubApi(token=credential_values()["MODELSCOPE_API_TOKEN"])


def is_private(repo: object) -> bool:
    visibility = getattr(getattr(repo, "visibility", None), "value", getattr(repo, "visibility", None))
    return getattr(repo, "private", None) is True or visibility in (1, "private", "PRIVATE")


def validate_processed(path: Path) -> dict:
    rows = read_jsonl(path)
    if len(rows) != 20000: raise RuntimeError(f"RECORD_COUNT_MISMATCH {len(rows)}")
    if any(REQUIRED - set(row) for row in rows): raise RuntimeError("PROCESSED_SCHEMA_MISMATCH")
    if any("qwen_non_special_token_count" not in row and not row.get("identity_fallback") for row in rows):
        raise RuntimeError("QWEN_TOKEN_COUNT_MISSING_OUTSIDE_FALLBACK")
    if records_sha256(rows) != EXPECTED_DATASET_SHA: raise RuntimeError("PROCESSED_DATASET_SHA_MISMATCH")
    ids_sha = records_sha256([{"sample_id": row["sample_id"]} for row in rows])
    if ids_sha != EXPECTED_IDS_SHA: raise RuntimeError("SAMPLE_ID_ORDER_SHA_MISMATCH")
    if file_sha256(path) != EXPECTED_FILE_SHA: raise RuntimeError("PROCESSED_FILE_SHA_MISMATCH")
    return {"status":"PASS", "record_count":len(rows), "dataset_sha256":EXPECTED_DATASET_SHA,
            "sample_ids_sha256":ids_sha, "frozen_jsonl_sha256":EXPECTED_FILE_SHA}


def source_gate() -> dict:
    validated = validate_processed(SOURCE)
    if validated["frozen_jsonl_sha256"] != EXPECTED_FILE_SHA: raise RuntimeError("SOURCE_FILE_SHA_MISMATCH")
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    if audit.get("verdict") != "PASS" or audit.get("strict_secret_total") != 0 or audit.get("high_entropy_candidate_count") != 0:
        raise RuntimeError("PRIVACY_AUDIT_NOT_PASS")
    return {"validation": validated, "privacy_audit_sha256": file_sha256(AUDIT),
            "privacy_verdict": audit["verdict"]}


def repo_state(api: HubApi) -> dict:
    exists = api.repo_exists(REPO_ID, REPO_TYPE)
    if not exists: return {"repo_id": REPO_ID, "repo_type": REPO_TYPE, "exists": False, "private": None, "files": []}
    repo = api.get_repo(REPO_ID, REPO_TYPE)
    files = sorted(item.path for item in api.list_repo_files(REPO_ID, REPO_TYPE, recursive=True) if not item.is_dir)
    return {"repo_id": REPO_ID, "repo_type": REPO_TYPE, "exists": True, "private": is_private(repo), "files": files}


def preflight() -> dict:
    source = source_gate(); api = api_client()
    owned = api.list_repos(REPO_TYPE, owner=NAMESPACE, page_number=1, page_size=1)
    state = repo_state(api)
    if state["exists"] and not state["private"]: raise RuntimeError("EXISTING_REPOSITORY_NOT_PRIVATE")
    result = {"status": "PASS", "authenticated_namespace": NAMESPACE,
              "authenticated_repo_query_succeeded": owned is not None, "source": source, "repository": state,
              "credential_mode": "600", "token_emitted": False, "checked_at": now()}
    print(json.dumps(result, indent=2)); return result


def prepare_package(work: Path, source: dict) -> tuple[Path, dict]:
    package = work / "package"; package.mkdir(parents=True, exist_ok=False)
    shutil.copyfile(SOURCE, package / "frozen_paired_qa.jsonl")
    if file_sha256(package / "frozen_paired_qa.jsonl") != EXPECTED_FILE_SHA: raise RuntimeError("PACKAGE_COPY_NOT_BYTE_IDENTICAL")
    config = load_config(CONFIG); expected = config["source_dataset"]
    manifest = {"project": "WMKD_Benchmark", "object": "passive5_shared_bb3_processed20k",
        "parent_run": expected["parent_run_id"], "record_count": expected["record_count"],
        "canonical_source_path": str(SOURCE), "schema": sorted(REQUIRED),
        "dataset_sha256": EXPECTED_DATASET_SHA, "frozen_jsonl_sha256": EXPECTED_FILE_SHA,
        "sample_id_sha256": EXPECTED_IDS_SHA, "source_ba_dataset_sha256": expected["dataset_sha256"],
        "prompt_sha256": config["paraphrase"]["prompt_sha256"],
        "processing_modes": {"atomic_identity_preserved":4635,"qwen_paraphrased":13061,
                             "qwen_identity_output":2256,"pipeline_identity_fallback":48},
        "schema_compatibility": {"fallback_records_without_qwen_non_special_token_count":48,
                                 "equivalent_field":"source_answer_token_count",
                                 "reason":"fallback records were created by the shared retry-exhaustion helper"},
        "transport_purpose": "private ModelScope backup / cross-instance restoration",
        "scientific_semantics": "Bb3 <=1-token atomic identity preservation plus Qwen untargeted paraphrasing", "privacy_audit_sha256": source["privacy_audit_sha256"],
        "created_at": now()}
    atomic_json(package / "manifest.json", manifest)
    readme = """# WMKD_Benchmark Passive-5 Shared Bb3 processed20k

This is the Passive-5 Shared Bb3 processed20k for Ba/Bb paired comparison and cross-AutoDL-instance restoration. ModelScope is private transport/storage only; this upload does not create a new scientific dataset. `frozen_paired_qa.jsonl` must not be modified. Verify SHA256 before every use.
"""
    (package / "README.md").write_text(readme, encoding="utf-8", newline="\n")
    sums = [(file_sha256(package / name), name) for name in ("frozen_paired_qa.jsonl", "manifest.json", "README.md")]
    (package / "SHA256SUMS").write_text("".join(f"{digest}  {name}\n" for digest, name in sums), encoding="utf-8", newline="\n")
    return package, manifest


def verify_existing(api: HubApi, gate: dict, package: Path, created: bool, upload_result: object = None) -> dict:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    verify_dir = DATA_ROOT / "tmp" / f"modelscope_verify_passive5_bb3_{stamp}"
    manifest = json.loads((package / "manifest.json").read_text(encoding="utf-8"))
    final_repo = repo_state(api)
    expected_files = {"README.md", "SHA256SUMS", "frozen_paired_qa.jsonl", "manifest.json"}
    if not final_repo["private"] or not expected_files.issubset(set(final_repo["files"])):
        raise RuntimeError(f"REMOTE_FILE_OR_VISIBILITY_GATE_FAILED {final_repo}")
    try: revision = api.list_repo_revisions(REPO_ID, REPO_TYPE)[0]
    except Exception: revision = "unavailable_modelscope_dataset_revision_endpoint_404"
    downloaded = Path(api.download_repo(REPO_ID, REPO_TYPE, local_dir=verify_dir, local_files_only=False, max_workers=4))
    remote_frozen = downloaded / "frozen_paired_qa.jsonl"
    verified = validate_processed(remote_frozen)
    if verified["frozen_jsonl_sha256"] != EXPECTED_FILE_SHA: raise RuntimeError("DOWNLOADED_COPY_SHA_MISMATCH")
    downloaded_manifest = json.loads((downloaded / "manifest.json").read_text(encoding="utf-8"))
    if downloaded_manifest != manifest: raise RuntimeError("DOWNLOADED_MANIFEST_MISMATCH")
    result = {"status": "COMPLETED", "modelscope_backup_verified": True, "repository": REPO_ID,
        "repository_type": REPO_TYPE, "visibility": "PRIVATE", "created": created,
        "revision": revision, "uploaded_files": sorted(expected_files),
        "uploaded_sizes": {name: (package / name).stat().st_size for name in expected_files},
        "source_validation": gate["source"]["validation"], "downloaded_copy_validation": verified,
        "byte_identical": file_sha256(SOURCE) == file_sha256(remote_frozen),
        "package_manifest_sha256": file_sha256(package / "manifest.json"),
        "verification_directory": str(verify_dir), "canonical_source_preserved": SOURCE.is_file(),
        "upload_timestamp": now(), "token_emitted": False,
        "upload_result_available": upload_result is not None}
    output = DATA_ROOT / "manifests" / "passive5_shared_bb3_processed20k_modelscope_archive.json"
    atomic_json(output, result); print(json.dumps(result, indent=2, default=str)); return result


def upload() -> dict:
    gate = preflight(); state = gate["repository"]
    if state["exists"] and state["files"]:
        raise RuntimeError(f"EXISTING_REPOSITORY_CONTENT_CONFLICT files={state['files']}")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    work = DATA_ROOT / "tmp" / f"modelscope_upload_passive5_bb3_{stamp}"
    work.mkdir(parents=True, exist_ok=False)
    package, _ = prepare_package(work, gate["source"])
    api = api_client(); created = False
    if not state["exists"]:
        api.create_repo(REPO_ID, REPO_TYPE, visibility=1,
                        description="Private WMKD_Benchmark Passive-5 Shared Bb3 processed20k transport backup")
        created = True
    confirmed = repo_state(api)
    if not confirmed["private"]: raise RuntimeError("PRIVATE_VISIBILITY_NOT_CONFIRMED_AFTER_CREATE")
    if confirmed["files"] and not (created and set(confirmed["files"]).issubset({"README.md", ".gitattributes"})):
        raise RuntimeError(f"REMOTE_CONTENT_CONFLICT_BEFORE_UPLOAD files={confirmed['files']}")
    upload_result = api.upload_folder(REPO_ID, REPO_TYPE, package, path_in_repo="",
        commit_message="Archive Passive-5 Shared Bb3 processed20k", disable_tqdm=True, sync_remote_repo=False)
    return verify_existing(api, gate, package, created, upload_result)


def verify() -> dict:
    gate = preflight(); state = gate["repository"]
    expected = {"README.md", "SHA256SUMS", "frozen_paired_qa.jsonl", "manifest.json"}
    if not state["exists"] or not state["private"] or not expected.issubset(set(state["files"])):
        raise RuntimeError(f"EXISTING_REPOSITORY_NOT_VERIFIABLE {state}")
    packages = sorted((DATA_ROOT / "tmp").glob("modelscope_upload_passive5_bb3_*/package"))
    if not packages: raise RuntimeError("LOCAL_UPLOAD_PACKAGE_NOT_FOUND")
    return verify_existing(api_client(), gate, packages[-1], False, None)


def main() -> None:
    parser=argparse.ArgumentParser();parser.add_argument("command",choices=("preflight","upload","verify"));args=parser.parse_args()
    preflight() if args.command=="preflight" else (upload() if args.command=="upload" else verify())

if __name__=="__main__": main()

