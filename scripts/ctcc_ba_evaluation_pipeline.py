#!/usr/bin/env python3
"""Detached fresh-reload evaluation-only pipeline for CTCC Ba."""
import argparse, datetime as dt, json, os, subprocess, traceback
from pathlib import Path
import yaml

def now(): return dt.datetime.now().astimezone().isoformat()
def write(p,x): Path(p).write_text(json.dumps(x,indent=2)+"\n")

def main():
    p=argparse.ArgumentParser(); p.add_argument("--config",required=True); p.add_argument("--run-dir",required=True); p.add_argument("--code-root",required=True); p.add_argument("--python",required=True); a=p.parse_args()
    c=yaml.safe_load(Path(a.config).read_text()); r=Path(a.run_dir); sp=r/"status/status.json"; s=json.loads(sp.read_text()); student=c["student"]
    def update(**kw): s.update(kw); s["updated_at"]=now(); write(sp,s)
    def notify(event,error=None):
        cmd=[a.python,str(Path(a.code_root)/"scripts/notify_experiment.py"),"--event",event,"--experiment","CTCC Experiment Ba Fresh-Reload Evaluation","--run-id",r.name,"--stage",s.get("stage","UNKNOWN"),"--pid",str(os.getpid()),"--status-file",str(sp),"--log-path",str(r/"logs")]
        if error: cmd += ["--error-summary",error]
        return subprocess.run(cmd,check=False).returncode
    def run(stage,cmd):
        update(status="RUNNING",stage=stage,child_command=cmd); log=r/"logs"/(stage.lower()+".log")
        with log.open("a",buffering=1) as out: q=subprocess.Popen(cmd,stdout=out,stderr=subprocess.STDOUT,text=True); update(child_pid=q.pid); rc=q.wait()
        if rc: raise RuntimeError(f"{stage} failed with exit code {rc}")
        update(child_pid=None,completed_stages=s.get("completed_stages",[])+[stage])
    try:
        update(status="RUNNING",stage="DEPLOYMENT_PREFLIGHT",runner_pid=os.getpid(),started_email_exit_code=notify("STARTED"))
        run("DEPLOYMENT_PREFLIGHT",[a.python,str(Path(a.code_root)/"scripts/ctcc_ba_evaluation_preflight.py"),"--config",a.config,"--output",str(r/"evaluation_preflight.json"),"--evaluation-dir",str(r/"evaluation")])
        run("FRESH_RELOAD_CTCC",[a.python,str(Path(a.code_root)/"scripts/ctcc_ba_evaluate.py"),"--config",a.config,"--student",student,"--training-run",c["training_run_id"],"--output",str(r/"evaluation/student_ctcc.json")])
        run("UTILITY",[a.python,str(Path(a.code_root)/"scripts/ctcc_ba_utility.py"),"--config",a.config,"--student",student,"--output",str(r/"evaluation/utility.json")])
        run("ORDINARY_GENERATION",[a.python,str(Path(a.code_root)/"scripts/ctcc_ba_sanity.py"),"--student",student,"--output",str(r/"evaluation/sanity.json")])
        update(status="COMPLETED",stage="COMPLETED",exit_code=0,end_time=now(),evaluation_status="COMPLETED",student_artifact=student)
        update(completed_email_exit_code=notify("COMPLETED"))
    except Exception as e:
        (r/"logs/failure_traceback.log").write_text(traceback.format_exc()); update(status="FAILED",stage="FAILED",exit_code=1,end_time=now(),evaluation_status="FAILED",error=f"{type(e).__name__}: {e}"); notify("FAILED",s["error"]); raise

if __name__=="__main__": main()
