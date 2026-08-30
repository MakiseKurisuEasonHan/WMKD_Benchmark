#!/usr/bin/env python3
import argparse,datetime as dt,json,os,subprocess,traceback
from pathlib import Path
def now():return dt.datetime.now().astimezone().isoformat()
def write(p,x):Path(p).write_text(json.dumps(x,indent=2)+"\n")
def main():
 p=argparse.ArgumentParser();p.add_argument("--config",required=True);p.add_argument("--run-dir",required=True);p.add_argument("--code-root",required=True);p.add_argument("--python",required=True);p.add_argument("--generation-run",required=True);a=p.parse_args();import yaml;c=yaml.safe_load(Path(a.config).read_text());r=Path(a.run_dir);sp=r/"status/status.json";s=json.loads(sp.read_text())
 def update(**kw):s.update(kw);s["updated_at"]=now();write(sp,s)
 def notify(event,error=None):
  cmd=[a.python,str(Path(a.code_root)/"scripts/notify_experiment.py"),"--event",event,"--experiment","iSeal Experiment Ba Student Training","--run-id",r.name,"--stage",s.get("stage","UNKNOWN"),"--pid",str(os.getpid()),"--status-file",str(sp),"--log-path",str(r/"logs")]
  if error:cmd += ["--error-summary",error]
  return subprocess.run(cmd,check=False).returncode
 def run(stage,cmd):
  update(status="RUNNING",stage=stage,child_command=cmd);log=r/"logs"/(stage.lower()+".log")
  with log.open("a",buffering=1) as out:q=subprocess.Popen(cmd,stdout=out,stderr=subprocess.STDOUT,text=True);update(child_pid=q.pid);rc=q.wait()
  if rc:raise RuntimeError(f"{stage} failed with exit code {rc}")
  update(child_pid=None,completed_stages=s.get("completed_stages",[])+[stage])
 try:
  update(status="RUNNING",stage="PREFLIGHT",runner_pid=os.getpid());update(started_email_exit_code=notify("STARTED"));pre=r/"metrics/preflight.json";run("PREFLIGHT",[a.python,str(Path(a.code_root)/"scripts/iseal_ba_student_preflight.py"),"--config",a.config,"--generation-run",a.generation_run,"--output",str(pre)])
  frozen=str(Path(a.generation_run)/"dataset/frozen_qa.jsonl");out=r/"checkpoints/student";run("TRAINING",[a.python,str(Path(a.code_root)/"scripts/train_distillation_student.py"),"--model-path",c["model"]["path"],"--dataset",frozen,"--output-dir",str(out),"--batch-size","8","--epochs","3","--learning-rate","1e-5","--seed","42","--max-length","1024","--telemetry",str(r/"metrics/training_telemetry.json")]);update(status="COMPLETED",stage="COMPLETED",exit_code=0,end_time=now(),student_checkpoint=str(out/"final_model"),formal_steps=7500,evaluation_status="NOT_STARTED");update(completed_email_exit_code=notify("COMPLETED"))
 except Exception as e:
  trace=traceback.format_exc();(r/"logs/failure_traceback.log").write_text(trace);update(status="FAILED",stage="FAILED",exit_code=1,end_time=now(),error=f"{type(e).__name__}: {e}");notify("FAILED",s["error"]);raise
if __name__=="__main__":main()
