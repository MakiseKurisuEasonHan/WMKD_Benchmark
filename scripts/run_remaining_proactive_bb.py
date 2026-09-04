#!/usr/bin/env python3
"""Restart-safe serial orchestrator for the four remaining proactive Bb methods."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

METHODS = ("ctcc", "iseal", "pnfp", "scw")
STAGES = ("PARENT_PREPARING", "PARENT_READY", "PREPROCESSING", "PROCESSED_READY", "PROCESSED_ARCHIVED",
          "PARITY_PASS", "TRAINING", "STUDENT_READY", "STUDENT_ARCHIVED",
          "DETECTING", "DETECTOR_COMPLETE", "UTILITY", "UTILITY_COMPLETE",
          "CLOSING", "COMPLETE")
LARGE = {"PARENT_PREPARING", "PREPROCESSING", "TRAINING", "DETECTING", "UTILITY"}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def atomic(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def next_stage(stage: str) -> str | None:
    index = STAGES.index(stage)
    return STAGES[index + 1] if index + 1 < len(STAGES) else None


def parse_point(value: str) -> tuple[str, str]:
    method, stage = value.lower().split("/", 1)
    stage = stage.upper()
    if method not in METHODS or stage not in STAGES:
        raise argparse.ArgumentTypeError(f"invalid METHOD/STAGE: {value}")
    return method, stage


def gpu_idle() -> None:
    query = subprocess.run(["nvidia-smi", "--query-compute-apps=pid", "--format=csv,noheader"],
                           text=True, capture_output=True, check=True)
    if query.stdout.strip():
        raise RuntimeError("GPU_NOT_IDLE_UNRELATED_PROCESS_PRESENT")


def initial_state(methods: list[str], git_head: str, runs: dict[str, str]) -> dict:
    return {"schema_version": "wmkd.proactive-bb-orchestrator.v1", "status": "RUNNING",
            "created_at": now(), "updated_at": now(), "git_start": git_head,
            "method_order": methods, "single_large_gpu_task": True, "active_large_stage": None,
            "methods": {m: {"run_id": runs[m], "stage": "PARENT_PREPARING", "status": "NOT_STARTED",
                              "history": [], "failure": None} for m in methods}}


def run_stage(project: Path, data: Path, state_path: Path, state: dict, method: str, stage: str) -> None:
    record = state["methods"][method]
    if stage in LARGE:
        if state["active_large_stage"] is not None:
            raise RuntimeError("GPU_SERIALIZATION_VIOLATION")
        gpu_idle()
        state["active_large_stage"] = f"{method}/{stage}"
    record.update({"stage": stage, "status": "RUNNING"})
    record["history"].append({"stage": stage, "event": "STARTED", "at": now()})
    state["updated_at"] = now(); atomic(state_path, state)
    log = data / "orchestration/proactive_bb" / record["run_id"] / f"{stage.lower()}.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    command = [sys.executable, str(project / "scripts/proactive_bb_method_stage.py"),
               "--project", str(project), "--data-root", str(data), "--method", method,
               "--run-id", record["run_id"], "--stage", stage]
    with log.open("a", encoding="utf-8") as stream:
        process = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT, text=True)
    if stage in LARGE:
        state["active_large_stage"] = None
    if process.returncode:
        record.update({"status": "FAILED", "failure": {"stage": stage, "exit_code": process.returncode,
                       "log": str(log), "at": now()}})
        record["history"].append({"stage": stage, "event": "FAILED", "at": now(), "exit_code": process.returncode})
        state.update({"status": "FAILED", "updated_at": now()}); atomic(state_path, state)
        raise RuntimeError(f"STAGE_FAILED {method}/{stage} exit={process.returncode}")
    record.update({"status": "COMPLETE", "failure": None})
    record["history"].append({"stage": stage, "event": "COMPLETED", "at": now(), "log": str(log)})
    state["updated_at"] = now(); atomic(state_path, state)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--methods", default=",".join(METHODS))
    ap.add_argument("--project", type=Path, default=Path("/root/autodl-tmp/WMKD_Benchmark"))
    ap.add_argument("--data-root", type=Path, default=Path("/root/autodl-tmp/WMKD_Benchmark_data"))
    ap.add_argument("--state", type=Path, required=True)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--start-from", type=parse_point)
    ap.add_argument("--stop-after", type=parse_point)
    ap.add_argument("--run-map", type=Path, required=True)
    args = ap.parse_args()
    methods = args.methods.split(",")
    if any(m not in METHODS for m in methods) or len(methods) != len(set(methods)):
        raise SystemExit("INVALID_OR_DUPLICATE_METHODS")
    runs = json.loads(args.run_map.read_text(encoding="utf-8"))
    if len(set(runs.values())) != len(runs) or any(m not in runs for m in methods):
        raise SystemExit("RUN_PATH_COLLISION_OR_MISSING")
    git_head = subprocess.check_output(["git", "-C", str(args.project), "rev-parse", "HEAD"], text=True).strip()
    if args.resume:
        state = json.loads(args.state.read_text(encoding="utf-8"))
        if state["method_order"] != methods: raise SystemExit("RESUME_METHOD_ORDER_MISMATCH")
        if state["active_large_stage"] is not None: state["active_large_stage"] = None
        state["status"] = "RUNNING"
    else:
        if args.state.exists(): raise FileExistsError(f"STATE_COLLISION {args.state}")
        state = initial_state(methods, git_head, runs); atomic(args.state, state)
    started = args.start_from is None
    for method in methods:
        for stage in STAGES:
            if args.start_from == (method, stage): started = True
            if not started: continue
            record = state["methods"][method]
            done = {h["stage"] for h in record["history"] if h["event"] == "COMPLETED"}
            if stage not in done: run_stage(args.project, args.data_root, args.state, state, method, stage)
            if args.stop_after == (method, stage):
                state.update({"status": "STOPPED_AT_REQUESTED_BOUNDARY", "updated_at": now()}); atomic(args.state, state); return
    state.update({"status": "COMPLETE", "completed_at": now(), "updated_at": now(),
                  "git_final": subprocess.check_output(["git", "-C", str(args.project), "rev-parse", "HEAD"], text=True).strip()})
    atomic(args.state, state)


if __name__ == "__main__": main()
