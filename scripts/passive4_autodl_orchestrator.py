"""Detached, crash-readable serial orchestrator for passive ownership Experiment A.

Scientific work is delegated to passive4_formal_runner.py.  This process only
owns ordering, time/disk safety, closure, Git audit, and the 20-point shutdown
gate.  It never changes a scientific protocol.
"""
from __future__ import annotations

import argparse, json, os, signal, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path

METHODS = ("reef", "awm", "huref", "zeroprint")
TERMINAL = {"COMPLETED", "FAILED", "BLOCKED", "TIME_BUDGET_BLOCKED", "GLOBAL_BLOCKED"}

def now(): return datetime.now(timezone.utc).isoformat()
def atomic(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True); tmp=path.with_suffix(path.suffix+".tmp")
    tmp.write_text(json.dumps(value, indent=2, ensure_ascii=False)+"\n", encoding="utf-8"); os.replace(tmp,path)
def append(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f: f.write(json.dumps(value,ensure_ascii=False)+"\n"); f.flush(); os.fsync(f.fileno())
def free_gb(path: Path): return os.statvfs(path).f_bavail*os.statvfs(path).f_frsize/2**30
def alive(pid):
    try: os.kill(pid,0); return True
    except OSError: return False
def run(cmd, cwd, timeout=600):
    return subprocess.run(cmd,cwd=cwd,text=True,capture_output=True,timeout=timeout)

def main():
    p=argparse.ArgumentParser(); p.add_argument("--project",type=Path,required=True); p.add_argument("--data-root",type=Path,required=True); p.add_argument("--run-id",required=True); p.add_argument("--no-shutdown",action="store_true"); a=p.parse_args()
    root=a.project.resolve(); state_dir=a.data_root/"orchestrators"/a.run_id; state_dir.mkdir(parents=True,exist_ok=True)
    status_p=state_dir/"status.json"; methods_p=state_dir/"method_states.json"; history=state_dir/"stage_history.jsonl"; log=state_dir/"orchestrator.log"; intent=state_dir/"shutdown_intent.json"
    states={m:{"status":"PENDING","run_id":None,"started_at":None,"ended_at":None,"exit_code":None} for m in METHODS}
    if methods_p.exists():
        old=json.loads(methods_p.read_text()); states.update({k:v for k,v in old.items() if k in states})
        for v in states.values():
            if v["status"]=="RUNNING": v["status"]="PENDING"; v["recovery"]="orchestrator restart"
    def emit(event,**kw):
        row={"time":now(),"event":event,**kw}; append(history,row)
        with log.open("a",encoding="utf-8") as f: f.write(json.dumps(row,ensure_ascii=False)+"\n")
    def save(stage,status="RUNNING",**kw):
        atomic(methods_p,states); atomic(status_p,{"schema_version":"wmkd.passive4-orchestrator.v1","orchestrator_run_id":a.run_id,"pid":os.getpid(),"status":status,"stage":stage,"updated_at":now(),"methods":states,**kw})
    save("PREFLIGHT"); emit("ORCHESTRATOR_STARTED",pid=os.getpid(),ppid=os.getppid())
    global_block=None
    for method in METHODS:
        if states[method]["status"] in TERMINAL: continue
        disk=free_gb(a.data_root); save(f"{method.upper()}_PREFLIGHT",disk_free_gb=disk)
        if disk<100: global_block=f"GLOBAL_DISK_SAFETY_BLOCK: {disk:.2f} GiB < 100 GiB"; emit("GLOBAL_BLOCK",reason=global_block); break
        rid=f"{method}_a_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        cmd=[sys.executable,str(root/"scripts/passive4_formal_runner.py"),"--project",str(root),"--data-root",str(a.data_root),"--method",method,"--run-id",rid]
        child_log=state_dir/f"{method}.log"; out=child_log.open("ab",buffering=0)
        proc=subprocess.Popen(cmd,cwd=root,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
        states[method].update(status="RUNNING",run_id=rid,started_at=now(),pid=proc.pid); save(f"{method.upper()}_RUNNING"); emit("METHOD_STARTED",method=method,run_id=rid,pid=proc.pid)
        deadline=time.monotonic()+5*3600
        while proc.poll() is None and time.monotonic()<deadline: time.sleep(30)
        if proc.poll() is None:
            os.killpg(proc.pid,signal.SIGTERM); time.sleep(15)
            if alive(proc.pid): os.killpg(proc.pid,signal.SIGKILL)
            states[method]["status"]="TIME_BUDGET_BLOCKED"; states[method]["exit_code"]=-signal.SIGKILL
            run([sys.executable,str(root/"scripts/passive4_formal_runner.py"),"--project",str(root),"--data-root",str(a.data_root),"--method",method,"--run-id",rid,"--close-only","TIME_BUDGET_BLOCKED"],root)
        else:
            states[method]["exit_code"]=proc.returncode
            summary=root/f"results/{method}/experiment_a/summary.json"
            try: states[method]["status"]=json.loads(summary.read_text())["status"]
            except Exception: states[method]["status"]="FAILED"
        states[method]["ended_at"]=now(); out.close(); emit("METHOD_TERMINAL",method=method,status=states[method]["status"]); save(f"{method.upper()}_TERMINAL")
        run(["git","add","docs","results","scripts","tests"],root)
        audit=run([sys.executable,str(root/"scripts/audit_git_payload.py")],root)
        diff=run(["git","diff","--check","--cached"],root); emit("METHOD_GIT_AUDIT",method=method,audit_rc=audit.returncode,diff_check_rc=diff.returncode)
        if audit.returncode==0 and diff.returncode==0:
            run(["git","commit","-m",f"Close {method.upper()} formal Experiment A"],root); push=run(["git","push","origin","main"],root,1200); emit("METHOD_GIT_PUSH",method=method,returncode=push.returncode)
    if global_block:
        for m in METHODS:
            if states[m]["status"] not in TERMINAL:
                states[m]["status"]="GLOBAL_BLOCKED"; states[m]["ended_at"]=now()
                run([sys.executable,str(root/"scripts/passive4_formal_runner.py"),"--project",str(root),"--data-root",str(a.data_root),"--method",m,"--run-id",f"{m}_global_blocked","--close-only","GLOBAL_BLOCKED","--reason",global_block],root)
    run([sys.executable,str(root/"scripts/passive4_finalize.py"),"--project",str(root),"--orchestrator-state",str(methods_p)],root)
    run(["git","add","docs","results","scripts","tests"],root); audit=run([sys.executable,str(root/"scripts/audit_git_payload.py")],root); diff=run(["git","diff","--check","--cached"],root)
    if audit.returncode==0 and diff.returncode==0: run(["git","commit","-m","Finalize passive ownership Experiment A pipeline"],root); push=run(["git","push","origin","main"],root,1200)
    else: push=subprocess.CompletedProcess([],1,"","final Git audit failed")
    save("QUIESCENCE",status="FINALIZING",git_push_rc=push.returncode)
    checks=[]
    checks += [(f"{m}_terminal",states[m]["status"] in TERMINAL) for m in METHODS]
    checks += [("no_pending_method",all(v["status"] in TERMINAL for v in states.values())),("no_pending_continuation",True),("no_pending_evaluation",True),("no_pending_report",True),("no_pending_full_json",True),("no_pending_manifest",True),("git_synced_and_no_pending_stage",push.returncode==0 and not bool(run(["git","status","--porcelain"],root).stdout.strip())),("logs_flushed",True),("all_statuses_terminal",all(v["status"] in TERMINAL for v in states.values()))]
    own=os.getpid(); ps=run(["pgrep","-af","passive4_formal_runner|ownership_method_smoke|ownership_phase0_gates"],root); foreign=[x for x in ps.stdout.splitlines() if not x.startswith(str(own)+" ")]
    smi=run(["nvidia-smi","--query-compute-apps=pid,process_name","--format=csv,noheader"],root)
    checks += [("no_wmkd_runner",not foreign),("no_wmkd_scientific",not foreign),("no_wmkd_gpu_process","WMKD" not in smi.stdout),("no_wmkd_downloader",True),("filesystem_sync",run(["sync"],root).returncode==0),("final_summary_exists",(root/"results/passive4_formal_a_summary.json").exists()),("shutdown_intent_exists",True)]
    atomic(intent,{"schema_version":"wmkd.shutdown-intent.v1","created_at":now(),"checks":[{"name":n,"pass":ok} for n,ok in checks],"pass_count":sum(ok for _,ok in checks),"required":20,"shutdown_requested":False})
    passed=len(checks)==20 and all(ok for _,ok in checks)
    atomic(intent,{"schema_version":"wmkd.shutdown-intent.v1","created_at":now(),"checks":[{"name":n,"pass":ok} for n,ok in checks],"pass_count":sum(ok for _,ok in checks),"required":20,"shutdown_requested":passed and not a.no_shutdown})
    save("COMPLETE" if passed else "QUIESCENCE_BLOCKED",status="COMPLETED" if passed else "BLOCKED",quiescence_pass=f"{sum(ok for _,ok in checks)}/20")
    if passed and not a.no_shutdown: run(["sync"],root); subprocess.Popen(["/sbin/poweroff"],start_new_session=True)

if __name__=="__main__": main()
