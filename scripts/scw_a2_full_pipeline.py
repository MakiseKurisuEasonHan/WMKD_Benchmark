"""Detached SCW A2 formal pipeline over the audited frozen 80k/two-pass stream."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import subprocess
import sys
import time
import traceback
from pathlib import Path

from scw_materialized_stream import audit_materialized
from scw_shutdown_policy import apply_shutdown_policy

P = Path("/root/autodl-tmp/WMKD_Benchmark")
D = Path("/root/autodl-tmp/WMKD_Benchmark_data")
PY = D / "artifacts/scw/env_py311/bin/python"
SRC = D / "artifacts/scw/source"
BASE = D / "models/base/Llama-3.2-3B-Instruct"
OFF = P / "configs/watermark/scw_experiment_a_official.yaml"
A2 = P / "configs/watermark/scw_experiment_a2.yaml"
FROZEN = D / "runs/scw/a2_frozen_stream/scw_a2_frozen80k_20260831_230200"
RECORDS = FROZEN / "training_stream_a2_80k.jsonl"
MANIFEST = FROZEN / "manifest.json"
GATE = D / "runs/scw/a2_gate/scw_a2_gate4_20260831_213424/gate_status.json"


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def telemetry(path):
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return rows


def run(stage, cmd, status, root, env):
    status.update(stage=stage, stage_started_at=now())
    atomic_json(root / "pipeline_status.json", status)
    log = root / "logs" / f"{stage.lower()}.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("w", encoding="utf-8") as out:
        cp = subprocess.run(cmd, stdout=out, stderr=subprocess.STDOUT, env=env)
    status.setdefault("stages", {})[stage] = {"exit_code": cp.returncode, "log": str(log), "ended_at": now()}
    atomic_json(root / "pipeline_status.json", status)
    if cp.returncode:
        raise RuntimeError(f"{stage} failed exit={cp.returncode}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    args = ap.parse_args()
    root = D / "runs/scw/orchestrators" / args.run_id
    root.mkdir(parents=True, exist_ok=False)
    status = {
        "run_id": args.run_id, "pid": os.getpid(), "ppid": os.getppid(), "state": "RUNNING",
        "stage": "PREFORMAL_VERIFY", "started_at": now(), "scientific_status": "RUNNING",
        "training_status": "NOT_STARTED", "evaluation_status": "NOT_STARTED",
        "formal_a2_started": False, "auto_shutdown_enabled": False, "ba_started": False,
        "shutdown_requested": False, "shutdown_command_issued": False, "terminal": False,
    }
    atomic_json(root / "pipeline_status.json", status)
    code = 1
    env = os.environ.copy()
    env.update({"PYTHONHASHSEED": "42", "WMKD_AUTO_SHUTDOWN_ENABLED": "false", "HF_DATASETS_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1"})
    try:
        live_audit = audit_materialized(RECORDS, json.loads(MANIFEST.read_text(encoding="utf-8")))
        audit = json.loads((FROZEN / "audit.json").read_text(encoding="utf-8"))
        if live_audit["status"] != "PASS" or audit["status"] != "PASS" or audit.get("formal_two_pass_loader_count") != 160000:
            raise RuntimeError("frozen80k/two-pass audit is not PASS")
        gate = json.loads(GATE.read_text(encoding="utf-8"))
        if gate.get("status") != "PASS" or not all(gate.get("checks", {}).values()):
            raise RuntimeError("the single authorized 4-step gate is not PASS")
        if not (BASE / "config.json").is_file():
            raise RuntimeError("canonical Base missing")
        formal_id = "scw_a2_" + dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        formal = D / "runs/scw/a2" / formal_id
        formal.mkdir(parents=True, exist_ok=False)
        tel = formal / "telemetry.jsonl"
        status.update(stage="FORMAL_A2_STARTING", formal_run_id=formal_id, formal_root=str(formal), formal_pid=None)
        atomic_json(root / "pipeline_status.json", status)
        fenv = env.copy()
        fenv.update({
            "PYTHONPATH": os.pathsep.join([str(P / "scripts/scw_runtime_compat"), str(P / "scripts"), str(SRC / "src")]),
            "WMKD_SCW_TELEMETRY": str(tel), "WMKD_SCW_SPEED_TEST": "0",
        })
        train_log = root / "logs/formal_training.log"
        train_log.parent.mkdir(parents=True, exist_ok=True)
        with train_log.open("w", encoding="utf-8") as out:
            proc = subprocess.Popen([
                str(PY), str(P / "scripts/scw_train_materialized.py"), "--official-source", str(SRC),
                "--official-runtime-config", str(OFF), "--records", str(RECORDS), "--manifest", str(MANIFEST),
                "--custom-name", formal_id,
            ], cwd=formal, env=fenv, stdout=out, stderr=subprocess.STDOUT)
            status["formal_pid"] = proc.pid
            atomic_json(root / "pipeline_status.json", status)
            while proc.poll() is None:
                steps = [x for x in telemetry(tel) if x.get("event") == "optimizer_step_end"]
                if steps and int(steps[-1].get("step", 0)) >= 1:
                    status.update(stage="FORMAL_TRAINING", formal_a2_started=True, training_status="RUNNING",
                                  auto_shutdown_enabled=True, formal_started_at=now(), latest_telemetry=steps[-1])
                    env["WMKD_AUTO_SHUTDOWN_ENABLED"] = "true"
                    atomic_json(root / "pipeline_status.json", status)
                    break
                time.sleep(5)
            rc = proc.wait()
        if not status["formal_a2_started"]:
            raise RuntimeError(f"Formal A2 exited before optimizer step 1 (exit={rc})")
        if rc:
            raise RuntimeError(f"Formal A2 failed exit={rc}")
        rows = telemetry(tel)
        ends = [x for x in rows if x.get("event") == "optimizer_step_end"]
        train_end = [x for x in rows if x.get("event") == "train_end"]
        if not ends or int(ends[-1].get("step", 0)) != 2500 or not train_end:
            raise RuntimeError("Formal A2 telemetry does not prove 2500/2500 and train_end")
        candidates = list(formal.glob("models/*"))
        teachers = [x for x in candidates if (x / "config.json").is_file()]
        if len(teachers) != 1:
            raise RuntimeError(f"expected one final Teacher artifact, found {len(teachers)}")
        teacher = teachers[0]
        status.update(training_status="COMPLETED", teacher_path=str(teacher), evaluation_status="RUNNING")
        atomic_json(root / "pipeline_status.json", status)
        ev = formal / "evaluation"
        ev.mkdir()
        run("BASE_FRENCH_GENERATION", [str(PY), str(P / "scripts/scw_fresh_generate.py"), "--model", str(BASE), "--label", "base", "--output", str(ev / "base_generations.jsonl")], status, root, env)
        run("TEACHER_FRENCH_GENERATION", [str(PY), str(P / "scripts/scw_fresh_generate.py"), "--model", str(teacher), "--label", "teacher", "--output", str(ev / "teacher_generations.jsonl")], status, root, env)
        denv = env.copy(); denv["PYTHONPATH"] = os.pathsep.join([str(SRC / "src"), str(P / "scripts")])
        for label in ("base", "teacher"):
            run(label.upper() + "_DETECTOR", [str(PY), str(P / "scripts/scw_detector.py"), "--protocol-config", str(A2), "--official-config", str(OFF), "--generations", str(ev / f"{label}_generations.jsonl"), "--model", str(BASE), "--output", str(ev / f"{label}_detector.json")], status, root, denv)
        run("UTILITY", [str(PY), str(P / "scripts/scw_utility.py"), "--base", str(BASE), "--teacher", str(teacher), "--output", str(ev / "utility.json")], status, root, env)
        base_det = json.loads((ev / "base_detector.json").read_text())
        teacher_det = json.loads((ev / "teacher_detector.json").read_text())
        utility = json.loads((ev / "utility.json").read_text())
        gates = {
            "teacher_positive": teacher_det["primary"]["p_value"] < .001,
            "base_negative": base_det["primary"]["p_value"] >= .001,
            "utility": utility["delta"]["arc_challenge_acc_norm"] >= -.10 and utility["delta"]["truthfulqa_mc2_acc"] >= -.10,
            "ordinary": utility["ordinary_generation"]["teacher"]["passed"],
            "french": utility["french_supplementary"]["teacher"]["passed"],
            "fresh_reload": utility["fresh_process_reload"],
        }
        summary = {
            "status": "COMPLETED", "experiment": "SCW A2", "classification": "WMKD_ADAPTED_DOMESTIC_DATA_80K_UNIQUE_TWO_PASS",
            "formal_run_id": formal_id, "orchestrator_run_id": args.run_id, "stream_sha256": sha(RECORDS),
            "manifest_sha256": sha(MANIFEST), "unique_records": 80000, "formal_exposures": 160000,
            "audit": audit, "gate": gate, "teacher_path": str(teacher), "detector": {"base": base_det, "teacher": teacher_det},
            "utility": utility, "gates": gates, "preferred_teacher": all(gates.values()), "ba_started": False,
        }
        atomic_json(root / "summary.json", summary)
        atomic_json(P / "results/scw/experiment_a2/summary.json", summary)
        report = ("# SCW Experiment A2 Formal Report\n\nSCW core method/idea reproduction under the WMKD A2 adapted "
                  "domestic-data and 80k-unique-pool setting on the canonical Llama-3.2-3B-Instruct backbone. "
                  "This is not an exact official-data reproduction. The frozen pool contains 80,000 unique records and "
                  "formal training used two deterministic sequential passes (160,000 exposures; 2,500 optimizer steps).\n")
        (root / "formal_report.md").write_text(report, encoding="utf-8")
        status.update(state="COMPLETED", stage="REPORTING_COMPLETED", scientific_status="COMPLETED",
                      training_status="COMPLETED", evaluation_status="COMPLETED", preferred_teacher=summary["preferred_teacher"])
        code = 0
    except Exception as exc:
        status.update(state="FAILED", failure=f"{type(exc).__name__}: {exc}", traceback=traceback.format_exc())
        if status.get("formal_a2_started"):
            status["training_status"] = "FAILED" if status.get("training_status") != "COMPLETED" else "COMPLETED"
    finally:
        status.update(terminal=True, exit_code=code, ended_at=now())
        atomic_json(root / "pipeline_status.json", status)
        subprocess.run(["sync"])
        command = apply_shutdown_policy(status, root, env)
        atomic_json(root / "pipeline_status.json", status)
        if command is not None:
            subprocess.run(command)
    raise SystemExit(code)


if __name__ == "__main__":
    main()
