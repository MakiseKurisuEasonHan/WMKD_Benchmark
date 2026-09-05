#!/usr/bin/env python3
"""Append and run the authorized CTCC Bb2 variant after SCW reaches a terminal state."""
from __future__ import annotations

import argparse
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

from run_remaining_proactive_bb import STAGES, atomic, now, run_stage

TERMINAL = {"COMPLETE", "BLOCKED", "FAILED", "BLOCKED_AT_PREPROCESSING_ACCEPTANCE_GATE"}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", type=Path, required=True)
    ap.add_argument("--data-root", type=Path, required=True)
    ap.add_argument("--state", type=Path, required=True)
    ap.add_argument("--poll-seconds", type=int, default=30)
    args = ap.parse_args()
    while True:
        state = json.loads(args.state.read_text(encoding="utf-8"))
        scw = state["methods"]["scw"]
        if scw["status"] in TERMINAL:
            break
        time.sleep(args.poll_seconds)
    if scw["status"] != "COMPLETE":
        # A formally closed terminal SCW is permitted; transient FAILED without closure is not.
        if not scw.get("formal_terminal", False):
            raise RuntimeError("SCW_NOT_DURABLY_CLOSED")
    state = json.loads(args.state.read_text(encoding="utf-8"))
    key = "ctcc_bb2"
    if key not in state["methods"]:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        state["method_order"].append(key)
        state["methods"][key] = {"run_id": f"ctcc_bb2_{stamp}", "experiment":"Bb2",
                                  "stage":"PARENT_PREPARING", "status":"NOT_STARTED",
                                  "history":[], "failure":None}
        state["status"] = "RUNNING"; state["updated_at"] = now(); atomic(args.state, state)
    record = state["methods"][key]
    for stage in STAGES:
        done = {h["stage"] for h in record["history"] if h["event"] == "COMPLETED"}
        if stage not in done:
            run_stage(args.project, args.data_root, args.state, state, "ctcc", stage,
                      record_key=key, experiment="bb2")
    state["status"] = "READY_FOR_MASTER_CLOSURE"
    state["updated_at"] = now(); atomic(args.state, state)


if __name__ == "__main__":
    main()
