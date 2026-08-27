#!/usr/bin/env python3
"""Read-only watcher that emits one terminal notification and exits."""

import argparse
import json
import os
from pathlib import Path
import subprocess
import time


def process_exists(pid):
    if not pid:
        return False
    try:
        os.kill(int(pid), 0)
        return True
    except (OSError, ValueError):
        return False


def classify(status):
    final = str(status.get("final_status", "")).lower()
    if final == "completed":
        return "COMPLETED"
    if final == "failed":
        return "FAILED"
    if final in {"interrupted", "cancelled"}:
        return "INTERRUPTED"
    if final == "running" and not process_exists(status.get("detached_pid")):
        return "INTERRUPTED"
    return None


def error_tail(run_dir, lines=25):
    candidates = [run_dir / "logs" / "failure_traceback.log", run_dir / "logs" / "pipeline.log"]
    for path in candidates:
        if path.exists():
            return "\n".join(path.read_text(errors="replace").splitlines()[-lines:])
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--status-file", required=True)
    parser.add_argument("--experiment", required=True)
    parser.add_argument("--poll-seconds", type=int, default=60)
    parser.add_argument("--notifier", default=str(Path(__file__).with_name("notify_experiment.py")))
    args = parser.parse_args()
    status_path = Path(args.status_file).resolve()
    run_dir = status_path.parents[1]
    while True:
        status = json.loads(status_path.read_text())
        event = classify(status)
        if event:
            command = [
                os.environ.get("PYTHON", "python3"), args.notifier,
                "--event", event, "--experiment", args.experiment,
                "--run-id", status["run_id"], "--stage", str(status.get("active_stage", "unknown")),
                "--status", str(status.get("final_status", "unknown")),
                "--status-file", str(status_path), "--log-path", str(run_dir / "logs"),
                "--message", str(status.get("failure_reason") or f"Pipeline terminal event: {event}"),
            ]
            if status.get("pid"):
                command += ["--pid", str(status["pid"])]
            if status.get("exit_code") is not None:
                command += ["--exit-code", str(status["exit_code"])]
            tail = error_tail(run_dir) if event in {"FAILED", "INTERRUPTED"} else None
            if tail:
                command += ["--error-summary", tail]
            subprocess.run(command, check=False)
            return 0
        time.sleep(max(args.poll_seconds, 5))


if __name__ == "__main__":
    raise SystemExit(main())
