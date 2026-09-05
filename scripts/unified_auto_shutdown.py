#!/usr/bin/env python3
"""Fail-closed final shutdown eligibility evaluator for the extended Bb batch."""
from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
from datetime import datetime, timezone
from pathlib import Path

TERMINAL = {"COMPLETE", "BLOCKED", "FAILED", "BLOCKED_AT_PREPROCESSING_ACCEPTANCE_GATE"}
REQUIRED = ("scw", "ctcc_bb2")


def run(command: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(command, cwd=cwd, text=True, capture_output=True)


def evaluate(*, state: dict, active_project_pids: list[dict], gpu_processes: list[dict],
             git: dict, full_logs_ok: bool, index_ok: bool, archives_ok: bool,
             master_report_ok: bool, pending_continuation: bool) -> dict:
    methods = state.get("methods", {})
    checks = {
        "target_methods_terminal": all(methods.get(x, {}).get("status") in TERMINAL for x in REQUIRED),
        "orchestrator_has_no_runnable_stage": state.get("status") in {"READY_FOR_MASTER_CLOSURE", "COMPLETE"},
        "no_active_project_worker": not active_project_pids,
        "gpu_has_no_project_compute": not gpu_processes,
        "no_archive_or_git_process": not any(x.get("kind") in {"archive", "git"} for x in active_project_pids),
        "full_logs_present": full_logs_ok,
        "global_index_valid": index_ok,
        "archives_terminal": archives_ok,
        "master_report_present": master_report_ok,
        "autodl_git_clean": git.get("clean") is True,
        "autodl_ahead_behind_zero": git.get("ahead") == 0 and git.get("behind") == 0,
        "local_github_autodl_equal": git.get("local_head") == git.get("github_head") == git.get("autodl_head") and bool(git.get("autodl_head")),
        "no_pending_restart_safe_continuation": not pending_continuation,
    }
    return {"checks": checks, "eligibility": all(checks.values())}


def main() -> None:
    ap=argparse.ArgumentParser(); ap.add_argument("--project",type=Path,required=True); ap.add_argument("--data-root",type=Path,required=True); ap.add_argument("--state",type=Path,required=True); ap.add_argument("--local-head",required=True); ap.add_argument("--output",type=Path,required=True); ap.add_argument("--execute",action="store_true"); a=ap.parse_args()
    state=json.loads(a.state.read_text(encoding="utf-8")); ps=run(["ps","-eo","pid=,args="])
    active=[]
    for line in ps.stdout.splitlines():
        if "WMKD_Benchmark" not in line or "unified_auto_shutdown.py" in line: continue
        kind="archive" if "modelscope" in line.lower() else ("git" if "git " in line.lower() else "scientific")
        active.append({"pid":line.strip().split(None,1)[0],"kind":kind})
    smi=run(["nvidia-smi","--query-compute-apps=pid,process_name","--format=csv,noheader"]); gpu=[] if not smi.stdout.strip() else [{"process":x.strip()} for x in smi.stdout.splitlines() if x.strip()]
    head=run(["git","rev-parse","HEAD"],a.project).stdout.strip(); remote=run(["git","rev-parse","origin/main"],a.project).stdout.strip(); status=run(["git","status","--porcelain"],a.project).stdout.strip(); counts=run(["git","rev-list","--left-right","--count","HEAD...origin/main"],a.project).stdout.split(); git={"local_head":a.local_head,"github_head":remote,"autodl_head":head,"clean":not status,"ahead":int(counts[0]),"behind":int(counts[1])}
    full_logs_ok=all((a.project/p).is_file() for p in ("results/scw/experiment_bb/full_experiment_log.json","results/ctcc/experiment_bb2/full_experiment_log.json")); index=a.project/"results/experiment_full_logs_index.json"; index_ok=index.is_file() and all(p in index.read_text(encoding="utf-8") for p in ("results/scw/experiment_bb/full_experiment_log.json","results/ctcc/experiment_bb2/full_experiment_log.json")); master=(a.project/"docs/reproduction_reports/unified_proactive_bb_master_report.md").is_file()
    archives_ok=True
    for key in REQUIRED:
        rec=state.get("methods",{}).get(key,{})
        if rec.get("status")=="COMPLETE":
            method="ctcc" if key=="ctcc_bb2" else key; exp="bb2" if key=="ctcc_bb2" else "bb"; root=a.data_root/f"runs/{method}_{exp}/{rec.get('run_id','')}"
            archives_ok &= (root/"archive/processed20k_modelscope.json").is_file() and (root/"archive/student_modelscope.json").is_file()
    result=evaluate(state=state,active_project_pids=active,gpu_processes=gpu,git=git,full_logs_ok=full_logs_ok,index_ok=index_ok,archives_ok=archives_ok,master_report_ok=master,pending_continuation=False)
    record={"schema_version":"wmkd.unified-auto-shutdown.v1","timestamp":datetime.now(timezone.utc).isoformat(),"host":socket.gethostname(),"armed":True,"orchestrator_state":state.get("status"),"method_terminal_states":{k:v.get("status") for k,v in state.get("methods",{}).items()},"gpu_state":gpu,"active_pid_scan":active,"git_state":git,"full_log_index_state":{"full_logs_ok":full_logs_ok,"index_ok":index_ok},"archive_state":{"ok":archives_ok},"master_report_state":{"ok":master},**result,"shutdown_command":"/usr/bin/shutdown -h now" if result["eligibility"] else None,"shutdown_result":"PENDING_FINAL_RECHECK" if result["eligibility"] else "NOT_ELIGIBLE"}
    if not a.execute:
        a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(record,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    if a.execute:
        if not result["eligibility"]: raise RuntimeError("AUTO_SHUTDOWN_NOT_ELIGIBLE")
        if not a.output.is_file() or not json.loads(a.output.read_text(encoding="utf-8")).get("eligibility"):
            raise RuntimeError("PRECOMMITTED_ELIGIBILITY_RECORD_MISSING")
        subprocess.run(["sync"],check=True)
        subprocess.Popen(["/usr/bin/shutdown","-h","now"],start_new_session=True)


if __name__=="__main__": main()
