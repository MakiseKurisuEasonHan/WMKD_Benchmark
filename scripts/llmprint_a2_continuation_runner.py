"""Immutable missing-ID-only continuation for paused LLMPrint A2."""
from __future__ import annotations
import argparse, json, os, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
from llmprint_formal_a2_runner import EXPECTED_CONFIG_SHA256, EXPECTED_CUBLAS, validate_artifacts, atomic_json

def now(): return datetime.now(timezone.utc).isoformat()
def main():
    p=argparse.ArgumentParser(); p.add_argument("--run-id",required=True); p.add_argument("--parent-run",type=Path,required=True); p.add_argument("--project",type=Path,required=True); p.add_argument("--source",type=Path,required=True); p.add_argument("--model",type=Path,required=True); p.add_argument("--pairs",type=Path,required=True); p.add_argument("--run-dir",type=Path,required=True); a=p.parse_args()
    if os.environ.get("CUBLAS_WORKSPACE_CONFIG") != EXPECTED_CUBLAS: raise RuntimeError("CUBLAS requirement missing")
    parent=json.loads((a.parent_run/"status.json").read_text()); fp=a.parent_run/"fingerprints"; valid,errors=validate_artifacts(fp)
    if parent.get("status")!="PAUSED_BY_USER_FOR_PRE_FORMAL_MULTI_METHOD_SMOKE" or valid!=97: raise RuntimeError("parent pause/97-artifact invariant failed")
    completed={f"llmprint-pair-{i:03d}" for i in range(97)}; missing=[f"llmprint-pair-{i:03d}" for i in range(97,200)]
    if any((fp/f"{x}.json").exists() for x in missing): raise RuntimeError("unexpected pending-ID artifact collision")
    a.run_dir.mkdir(parents=True,exist_ok=False); status=a.run_dir/"status.json"; atomic_json(a.run_dir/"missing_ids_manifest.json",{"parent_run_id":a.parent_run.name,"immutable_completed_ids":sorted(completed),"missing_ids":missing})
    cmd=[sys.executable,str(a.project/"scripts/llmprint_construct_fingerprints.py"),"--source",str(a.source),"--model",str(a.model),"--pairs",str(a.pairs),"--output-dir",str(fp),"--max-pairs","200","--num-steps","500","--dtype","float16","--experiment-label","A2","--scientific-config-sha256",EXPECTED_CONFIG_SHA256]
    state={"run_id":a.run_id,"parent_run_id":a.parent_run.name,"continuation":"cont1_missing_ids_only","status":"STARTING","runner_pid":os.getpid(),"scientific_pid":None,"started_at":now(),"command":cmd,"immutable_completed_count":97,"missing_count":103,"model_modified":False}; atomic_json(status,state)
    try:
        proc=subprocess.Popen(cmd); state.update(status="RUNNING",scientific_pid=proc.pid); atomic_json(status,state); rc=proc.wait(); valid,errors=validate_artifacts(fp); state.update(exit_code=rc,validated_record_count=valid,validation_errors=errors,status="COMPLETED" if rc==0 and valid==200 and not errors else "FAILED")
    except BaseException as e: state.update(status="FAILED",error=f"{type(e).__name__}: {e}"); raise
    finally: state["finished_at"]=now(); atomic_json(status,state)
if __name__=="__main__": main()
