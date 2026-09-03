#!/usr/bin/env python3
"""Build fail-closed NOT_STARTED full-log skeletons for proactive Bb runs."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

from scripts.prepare_proactive_bb import METHODS, assert_frozen_reference


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def readiness_log(config: dict) -> dict:
    assert_frozen_reference(config)
    slug = next((s for s, name in METHODS.items() if name == config["method"]), None)
    if slug is None or config.get("experiment") != "Bb":
        raise ValueError("NOT_A_PROACTIVE_BB_CONFIG")
    source = config["source_dataset"]
    return {
        "schema_version": "wmkd.full-experiment-log.v1",
        "identity": {"project": "WMKD_Benchmark", "method": config["method"],
                     "experiment": "Bb", "canonical_run_id": config["run_id"]},
        "status": "NOT_STARTED", "scientific_status": "NOT_STARTED",
        "scientific_parentage": {"source_experiment": source["parent_experiment"],
            "parent_run_id": source["parent_run_id"], "parent_teacher": source["parent_teacher"],
            "record_count": source["record_count"], "dataset_sha256": source["dataset_sha256"],
            "frozen_jsonl_sha256": source["frozen_jsonl_sha256"],
            "sample_ids_sha256": source["sample_ids_sha256"]},
        "preprocessing": {"status": "NOT_STARTED", "qwen": config["paraphraser"],
            "protocol": config["paraphrase"], "output_dataset": None},
        "student_initialization": {"status": "NOT_STARTED", "fresh_canonical": True,
            "artifact": None},
        "training": {"status": "NOT_STARTED", "configuration": config["training"],
            "telemetry": None},
        "detector": {"status": "NOT_STARTED", "result": None},
        "utility": {"status": "NOT_STARTED", "result": None},
        "artifacts": {"status": "NOT_STARTED", "manifest": None},
        "failures": [], "continuations": [], "bounded_conclusion": None,
    }


def register(index: dict, *, method: str, run_id: str, path: str, digest: str) -> dict:
    keys = {(x.get("method"), x.get("experiment"), x.get("run_id")) for x in index["objects"]}
    key = (method, "Bb", run_id)
    if key in keys or any(x.get("full_log_path") == path for x in index["objects"]):
        raise ValueError("DUPLICATE_PROACTIVE_BB_IDENTITY")
    index = json.loads(json.dumps(index))
    index["objects"].append({"method": method, "role": "proactive_bb_student",
        "experiment": "Bb", "run_id": run_id, "full_log_path": path,
        "full_log_sha256": digest, "scientific_status": "NOT_STARTED",
        "watermark_evaluation_available": False, "utility_available": False,
        "telemetry_records": 0})
    index["object_count"] = len(index["objects"])
    return index


def emit(config_path: Path, project: Path, *, update_index: bool = False) -> Path:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    log = readiness_log(config)
    rel = Path(config["paths"]["full_experiment_log"])
    out = project / rel
    if out.exists():
        raise FileExistsError(out)
    _write(out, log)
    if update_index:
        ip = project / "results/experiment_full_logs_index.json"
        index = register(json.loads(ip.read_text(encoding="utf-8")), method=config["method"],
                         run_id=config["run_id"], path=rel.as_posix(), digest=_sha(out))
        _write(ip, index)
    return out
