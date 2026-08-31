"""Immutable evaluation-only continuation for the completed SCW A2 Teacher."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import subprocess
import sys
import traceback
from pathlib import Path

from scw_shutdown_policy import apply_shutdown_policy

P = Path("/root/autodl-tmp/WMKD_Benchmark")
D = Path("/root/autodl-tmp/WMKD_Benchmark_data")
PY = D / "artifacts/scw/env_py311/bin/python"
SRC = D / "artifacts/scw/source"
BASE = D / "models/base/Llama-3.2-3B-Instruct"
TEACHER = D / "runs/scw/a2/scw_a2_20260831_214339/models/Llama-3.2-3B-Instruct_scw_a2_20260831_214339_French_WMKD_SCW_A"
TEACHER_MANIFEST = D / "runs/scw/a2/scw_a2_20260831_214339/teacher_artifact_manifest.json"
FRENCH = D / "evaluation/scw/a2_french_eval/scw_a2_french_eval_1000.jsonl"
FRENCH_MANIFEST = D / "evaluation/scw/a2_french_eval/manifest.json"
A2 = P / "configs/watermark/scw_experiment_a2.yaml"
OFF = P / "configs/watermark/scw_experiment_a_official.yaml"


def now(): return dt.datetime.now(dt.timezone.utc).isoformat()
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def run(stage, cmd, status, root, env):
    status.update(stage=stage, stage_started_at=now())
    write(root / "status.json", status)
    log = root / "logs" / f"{stage.lower()}.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("w", encoding="utf-8") as out:
        cp = subprocess.run(cmd, stdout=out, stderr=subprocess.STDOUT, env=env)
    status.setdefault("stages", {})[stage] = {"exit_code": cp.returncode, "log": str(log), "ended_at": now()}
    write(root / "status.json", status)
    if cp.returncode:
        raise RuntimeError(f"{stage} failed exit={cp.returncode}")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--run-id", required=True); a = ap.parse_args()
    root = D / "runs/scw/a2_eval_cont1" / a.run_id
    root.mkdir(parents=True, exist_ok=False)
    status = {"run_id": a.run_id, "pid": os.getpid(), "ppid": os.getppid(), "state": "RUNNING",
              "stage": "PREFLIGHT", "started_at": now(), "experiment": "SCW A2", "continuation": "cont1",
              "training_started": False, "training_status": "COMPLETED_IN_PARENT_RUN",
              "evaluation_status": "RUNNING", "scientific_status": "EVALUATION_IN_PROGRESS",
              "preferred_teacher": "NOT_EVALUATED", "auto_shutdown_enabled": False, "ba_started": False,
              "shutdown_requested": False, "shutdown_command_issued": False, "terminal": False, "stages": {}}
    write(root / "status.json", status)
    env = os.environ.copy(); env.update({"PYTHONHASHSEED": "42", "HF_HUB_OFFLINE": "1", "HF_DATASETS_OFFLINE": "1",
        "TRANSFORMERS_OFFLINE": "1", "WMKD_AUTO_SHUTDOWN_ENABLED": "false"})
    code = 1
    try:
        if not all(x.is_file() for x in (BASE / "config.json", TEACHER / "config.json", TEACHER_MANIFEST, FRENCH, FRENCH_MANIFEST)):
            raise RuntimeError("immutable evaluation inputs missing")
        tm = json.loads(TEACHER_MANIFEST.read_text()); fm = json.loads(FRENCH_MANIFEST.read_text())
        if tm.get("status") != "COMPLETE" or fm.get("status") != "PASS" or fm.get("record_count") != 1000:
            raise RuntimeError("immutable provenance manifest failed")
        gpu = subprocess.check_output(["nvidia-smi", "--query-compute-apps=pid", "--format=csv,noheader,nounits"], text=True).strip()
        if gpu: raise RuntimeError("GPU not idle at evaluation continuation start")
        ev = root / "evaluation"; ev.mkdir()
        run("BASE_FRENCH_GENERATION", [str(PY), str(P / "scripts/scw_fresh_generate.py"), "--model", str(BASE), "--label", "base", "--output", str(ev / "base_generations.jsonl"), "--eval-jsonl", str(FRENCH), "--eval-manifest", str(FRENCH_MANIFEST)], status, root, env)
        status["base_fresh_reload"] = "PASS"; write(root / "status.json", status)
        run("TEACHER_FRENCH_GENERATION", [str(PY), str(P / "scripts/scw_fresh_generate.py"), "--model", str(TEACHER), "--label", "teacher", "--output", str(ev / "teacher_generations.jsonl"), "--eval-jsonl", str(FRENCH), "--eval-manifest", str(FRENCH_MANIFEST)], status, root, env)
        status["teacher_fresh_reload"] = "PASS"; write(root / "status.json", status)
        denv = env.copy(); denv["PYTHONPATH"] = os.pathsep.join([str(SRC / "src"), str(P / "scripts")])
        for label in ("base", "teacher"):
            run(label.upper() + "_DETECTOR", [str(PY), str(P / "scripts/scw_detector.py"), "--protocol-config", str(A2), "--official-config", str(OFF), "--generations", str(ev / f"{label}_generations.jsonl"), "--model", str(BASE), "--output", str(ev / f"{label}_detector.json")], status, root, denv)
        run("UTILITY", [str(PY), str(P / "scripts/scw_utility.py"), "--base", str(BASE), "--teacher", str(TEACHER), "--output", str(ev / "utility.json")], status, root, env)
        b = json.loads((ev / "base_detector.json").read_text()); t = json.loads((ev / "teacher_detector.json").read_text()); u = json.loads((ev / "utility.json").read_text())
        gates = {"teacher_positive": t["primary"]["p_value"] < .001, "base_negative": b["primary"]["p_value"] >= .001,
                 "fresh_reload": status["base_fresh_reload"] == status["teacher_fresh_reload"] == "PASS",
                 "utility": u["delta"]["arc_challenge_acc_norm"] >= -.10 and u["delta"]["truthfulqa_mc2_acc"] >= -.10,
                 "ordinary": u["ordinary_generation"]["teacher"]["passed"], "french": u["french_supplementary"]["teacher"]["passed"]}
        preferred = all(gates.values())
        summary = {"status": "COMPLETED", "experiment": "SCW A2", "evaluation_continuation": "cont1",
                   "training_status": "COMPLETED", "training_run": "scw_a2_20260831_214339",
                   "teacher_artifact_manifest": str(TEACHER_MANIFEST), "teacher_manifest_sha256": sha(TEACHER_MANIFEST),
                   "french_eval_manifest": str(FRENCH_MANIFEST), "french_eval_manifest_sha256": sha(FRENCH_MANIFEST),
                   "frozen1000_sha256": fm["frozen_file_sha256"], "fresh_reload": {"base": "PASS", "teacher": "PASS"},
                   "detector": {"base": b, "teacher": t}, "utility": u, "gates": gates,
                   "preferred_teacher": preferred, "ba_started": False,
                   "scientific_judgement": "SCW core method/idea reproduction successful under the WMKD A2 adapted domestic-data and 80k-unique-pool setting on the canonical Llama-3.2-3B-Instruct backbone." if preferred else "SCW A2 did not satisfy all preferred-Teacher gates; no A3 or retraining was started.",
                   "limitations": ["not an exact official-data or full-paper reproduction", "three training datasets were replaced", "80k unique pool used two deterministic passes"]}
        write(root / "summary.json", summary); write(P / "results/scw/experiment_a2/summary.json", summary)
        report = f"# SCW Experiment A2 Final Report\n\nContinuation `{a.run_id}` evaluated the immutable Teacher from `scw_a2_20260831_214339`. This is a WMKD-adapted domestic-data, 80k-unique-pool, two-pass idea reproduction, not an exact official-data reproduction.\n\nPrimary Base/Teacher p-values: `{b['primary']['p_value']}` / `{t['primary']['p_value']}`. Preferred Teacher: **{preferred}**. ARC Base/Teacher: `{u['base']['arc_challenge_acc_norm']}` / `{u['teacher']['arc_challenge_acc_norm']}`. TruthfulQA MC2 Base/Teacher: `{u['base']['truthfulqa_mc2_acc']}` / `{u['teacher']['truthfulqa_mc2_acc']}`.\n"
        (root / "formal_report.md").write_text(report, encoding="utf-8")
        status.update(state="COMPLETED", stage="RECORDS", evaluation_status="COMPLETED", scientific_status="COMPLETED",
                      preferred_teacher=preferred)
        block = f"\n## SCW A2 evaluation cont1 `{a.run_id}`\n\nTraining remained immutable and complete. Evaluation cont1 completed; Base/Teacher p-values `{b['primary']['p_value']}` / `{t['primary']['p_value']}`; preferred Teacher `{preferred}`. Ba was not started. Auto-shutdown remained disabled.\n"
        for rel in ("PROJECT_STATUS.md", "TODO.md", "DECISIONS.md", "EXPERIMENT_LOG.md", "CODEX_LOG.md", "docs/experiment_logs/scw_experiment_a_log.md"):
            with (P / rel).open("a", encoding="utf-8") as out: out.write(block)
        subprocess.run(["git", "-C", str(P), "diff", "--check"], check=True)
        subprocess.run(["git", "-C", str(P), "add", "--", "PROJECT_STATUS.md", "TODO.md", "DECISIONS.md", "EXPERIMENT_LOG.md", "CODEX_LOG.md", "docs/experiment_logs/scw_experiment_a_log.md", "results/scw/experiment_a2/summary.json"], check=True)
        subprocess.run(["git", "-C", str(P), "commit", "-m", f"records: finalize SCW A2 evaluation {a.run_id}"], check=False)
        code = 0
    except Exception as exc:
        status.update(state="FAILED", evaluation_status="FAILED", scientific_status="EVALUATION_INCOMPLETE",
                      failure=f"{type(exc).__name__}: {exc}", traceback=traceback.format_exc())
    finally:
        status.update(terminal=True, exit_code=code, ended_at=now())
        command = apply_shutdown_policy(status, root, env)
        if command is not None: status["safety_error"] = "project policy unexpectedly returned shutdown command"
        write(root / "status.json", status); subprocess.run(["sync"])
    raise SystemExit(code)


if __name__ == "__main__": main()
