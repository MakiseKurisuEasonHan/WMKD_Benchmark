#!/usr/bin/env python3
"""Detached CTCC-teacher generation with deterministic oversampling and freeze."""
import argparse,datetime as dt,json,os,subprocess,traceback
from pathlib import Path
def now():return dt.datetime.now().astimezone().isoformat()
def write(p,x):Path(p).write_text(json.dumps(x,indent=2)+"\n")
def main():
 p=argparse.ArgumentParser();p.add_argument("--config",required=True);p.add_argument("--run-dir",required=True);p.add_argument("--code-root",required=True);p.add_argument("--python",required=True);a=p.parse_args()
 import yaml
 c=yaml.safe_load(Path(a.config).read_text());r=Path(a.run_dir);status=r/"status/status.json";s=json.loads(status.read_text())
 def update(**kw):s.update(kw);s["updated_at"]=now();write(status,s)
 def notify(event,error=None):
  cmd=[a.python,str(Path(a.code_root)/"scripts/notify_experiment.py"),"--event",event,"--experiment","CTCC Experiment Ba Generation","--run-id",r.name,"--stage",s.get("stage","UNKNOWN"),"--pid",str(os.getpid()),"--status-file",str(status),"--log-path",str(r/"logs")]
  if error:cmd += ["--error-summary",error]
  return subprocess.run(cmd,check=False).returncode
 def run(stage,cmd):
  update(status="RUNNING",stage=stage,child_command=cmd);log=r/"logs"/(stage.lower()+".log")
  with log.open("a",buffering=1) as out:
   q=subprocess.Popen(cmd,stdout=out,stderr=subprocess.STDOUT,text=True);update(child_pid=q.pid);rc=q.wait()
  if rc:raise RuntimeError(f"{stage} failed with exit code {rc}")
  update(child_pid=None,completed_stages=s.get("completed_stages",[])+[stage])
 try:
  update(status="RUNNING",stage="PREFLIGHT",runner_pid=os.getpid());update(started_email_exit_code=notify("STARTED"))
  run("PREFLIGHT",[a.python,str(Path(a.code_root)/"scripts/ctcc_ba_preflight.py"),"--config",a.config,"--output",str(r/"metrics/preflight.json")])
  raw=r/"dataset/raw_candidates.jsonl";err=r/"dataset/generation_errors.jsonl";target=c["dataset"]["candidate_samples"]
  while True:
   run("TEACHER_QA_GENERATION",[a.python,str(Path(a.code_root)/"scripts/generate_teacher_qa_formal.py"),"--model-path",c["model"]["path"],"--adapter-path",c["teacher"]["adapter"],"--teacher-run-id",c["teacher"]["run_id"],"--output",str(raw),"--errors",str(err),"--target-candidates",str(target),"--batch-size","8","--records-per-prompt","4","--seed","42","--telemetry",str(r/"metrics/generation_telemetry.json")])
   prov=r/"config/dataset_provenance.json";write(prov,{"teacher_run_id":c["teacher"]["run_id"],"teacher_adapter":c["teacher"]["adapter"],"teacher_adapter_weight_sha256":c["teacher"]["adapter_weight_sha256"],"prompt_protocol":c["dataset"]["prompt_protocol"],"seed":42,"raw_candidate_count":sum(1 for _ in raw.open(encoding="utf-8")),"generation":{"batch_size":8,"records_per_prompt":4,"max_new_tokens":768,"temperature":0.8,"top_p":0.95}})
   cmd=[a.python,str(Path(a.code_root)/"scripts/generate_distillation_qa.py"),"--raw-candidates",str(raw),"--output",str(r/"dataset/frozen_qa.jsonl"),"--manifest",str(r/"dataset/manifest.json"),"--target-count","20000","--provenance",str(prov)];q=subprocess.run(cmd,capture_output=True,text=True);(r/"logs/dataset_freeze.log").write_text(q.stdout+q.stderr)
   if q.returncode==0:break
   target+=c["dataset"]["increment_samples"]
   if target>c["dataset"]["maximum_candidates"]:raise RuntimeError("insufficient unique QA at 40k ceiling")
  m=json.loads((r/"dataset/manifest.json").read_text());update(status="COMPLETED",stage="COMPLETED",exit_code=0,end_time=now(),raw_count=sum(1 for _ in raw.open(encoding="utf-8")),unique_frozen_count=m["sample_count"],frozen_sha256=m["dataset_sha256"]);update(completed_email_exit_code=notify("COMPLETED"))
 except Exception as e:
  trace=traceback.format_exc();(r/"logs/failure_traceback.log").write_text(trace);update(status="FAILED",stage="FAILED",exit_code=1,end_time=now(),error=f"{type(e).__name__}: {e}");notify("FAILED",s["error"]);raise
if __name__=="__main__":main()
