#!/usr/bin/env python3
"""Fail-closed stage implementations used by the remaining proactive Bb orchestrator."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

PARENTS = {
    "ctcc": ("ctcc_ba_generation_20260829_195943_cont1", "CTCC A", "runs/ctcc_ba/ctcc_ba_generation_20260829_195943_cont1/dataset/frozen_qa.jsonl", "621c9aedcf3a4a1db86a4848bbf93fa893d18022f15b913e8aeeb28739412484"),
    "iseal": ("iseal_ba_generation_20260830_134058", "iSeal A6", "runs/iseal_ba/iseal_ba_generation_20260830_134058/dataset/frozen_qa.jsonl", "d51c22b9d33d4aa79b5cd733dd6bcb910ecd6378f1ffe2a40328e64cb085aacf"),
}


def call(command: list[str]) -> None:
    subprocess.run(command, check=True)


def config_path(project: Path, method: str, run_id: str) -> Path:
    return project / f"configs/distillation/{method}_bb_{run_id}.json"


def main() -> None:
    ap = argparse.ArgumentParser(); ap.add_argument("--project", type=Path, required=True)
    ap.add_argument("--data-root", type=Path, required=True); ap.add_argument("--method", required=True)
    ap.add_argument("--run-id", required=True); ap.add_argument("--stage", required=True)
    a = ap.parse_args(); run = a.data_root / f"runs/{a.method}_bb/{a.run_id}"; cfg = config_path(a.project, a.method, a.run_id)
    if a.stage == "PARENT_READY":
        if a.method not in PARENTS:
            raise RuntimeError(f"PARENT_RECONSTRUCTION_NOT_YET_COMPLETE {a.method}")
        parent_run, teacher, relative, expected_content = PARENTS[a.method]; parent = a.data_root / relative
        if not cfg.exists():
            call([sys.executable, str(a.project / "scripts/prepare_proactive_bb.py"), "--reference-config", str(a.project / "configs/distillation/passive5_shared_bb3.json"), "--method", a.method, "--parent-frozen20k", str(parent), "--parent-run-id", parent_run, "--parent-teacher", teacher, "--run-id", a.run_id, "--output", str(cfg)])
        value = json.loads(cfg.read_text(encoding="utf-8"))
        if value["source_dataset"]["dataset_sha256"] != expected_content: raise RuntimeError("PARENT_CONTENT_SHA_MISMATCH")
        call([sys.executable, str(a.project / "scripts/passive5_shared_bb.py"), "--config", str(cfg), "validate-source", "--source", str(parent)])
    elif a.stage == "PREPROCESSING":
        value = json.loads(cfg.read_text(encoding="utf-8")); parent = value["source_dataset"]["path"]
        run.mkdir(parents=True, exist_ok=True)
        call([sys.executable, str(a.project / "scripts/passive5_shared_bb_paraphrase_runner.py"), "--config", str(cfg), "--source", parent, "--journal", str(run / "paraphrase/attempts.jsonl"), "--backend", "qwen"])
    elif a.stage == "PROCESSED_READY":
        value = json.loads(cfg.read_text(encoding="utf-8")); parent = value["source_dataset"]["path"]
        paired = run / "dataset/frozen_paired_qa.jsonl"
        if not paired.exists(): call([sys.executable, str(a.project / "scripts/passive5_shared_bb.py"), "--config", str(cfg), "freeze", "--source", parent, "--journal", str(run / "paraphrase/attempts.jsonl"), "--output", str(paired)])
        call([sys.executable, str(a.project / "scripts/passive5_shared_bb.py"), "--config", str(cfg), "quality-audit", "--pairs", str(paired), "--output-dir", str(run / "audit")])
        student = run / "dataset/student_qa.jsonl"
        if not student.exists(): call([sys.executable, str(a.project / "scripts/passive5_shared_bb.py"), "--config", str(cfg), "adapt-student", "--pairs", str(paired), "--output", str(student)])
    else:
        raise RuntimeError(f"FAIL_CLOSED_STAGE_HANDLER_NOT_DEPLOYED {a.method}/{a.stage}")


if __name__ == "__main__": main()
