#!/usr/bin/env python3
"""Detached, serial, fail-closed EverTracer Experiment Ba pipeline."""
import argparse,datetime as dt,json,os,subprocess,traceback
from pathlib import Path
from evertracer_common import write_json
def now():return dt.datetime.now().astimezone().isoformat()
class P:
 def __init__(self,a):
  self.a=a;self.r=Path(a.run_dir);self.c=Path(a.config);self.py=a.python;self.code=Path(a.code_root);self.sp=self.r/"status/status.json";self.s=json.loads(self.sp.read_text());self.runtime=json.loads((self.r/"config/runtime.json").read_text())
 def update(self,**kw):self.s.update(kw);self.s["updated_at"]=now();write_json(self.sp,self.s)
 def notify(self,event,error=None):
  cmd=[self.py,str(self.code/"scripts/notify_experiment.py"),"--event",event,"--experiment","EverTracer Experiment Ba","--run-id",self.r.name,"--stage",self.s.get("stage","UNKNOWN"),"--pid",str(os.getpid()),"--status-file",str(self.sp),"--log-path",str(self.r/"logs")]
  if error:cmd += ["--error-summary",error]
  subprocess.run(cmd,check=False)
 def run(self,stage,cmd):
  self.update(stage=stage,status="RUNNING",child_command=cmd);log=self.r/"logs"/(stage.lower()+".log")
  with log.open("a",buffering=1) as out:
   out.write(f"[{now()}] COMMAND: {' '.join(cmd)}\n");p=subprocess.Popen(cmd,stdout=out,stderr=subprocess.STDOUT,text=True);self.update(child_pid=p.pid);rc=p.wait();out.write(f"[{now()}] EXIT_CODE: {rc}\n")
  if rc:raise RuntimeError(f"{stage} failed with exit code {rc}; see {log}")
  hist=self.s.get("completed_stages",[])+[stage];self.update(last_completed_stage=stage,completed_stages=hist,child_pid=None)
 def execute(self):
  try:
   self.update(runner_pid=os.getpid(),status="RUNNING",stage="PREFLIGHT");self.notify("STARTED")
   self.run("PREFLIGHT",[self.py,str(self.code/"scripts/evertracer_ba_preflight.py"),"--config",str(self.c),"--output",str(self.r/"metrics/preflight.json")])
   raw=self.r/"dataset/raw_candidates.jsonl";err=self.r/"dataset/generation_errors.jsonl";target=24000
   while True:
    self.run("TEACHER_QA_GENERATION",[self.py,str(self.code/"scripts/generate_teacher_qa_formal.py"),"--model-path",self.runtime["teacher"],"--output",str(raw),"--errors",str(err),"--target-candidates",str(target),"--batch-size","8","--records-per-prompt","4","--seed","42","--telemetry",str(self.r/"metrics/generation_telemetry.json")])
    prov=self.r/"config/dataset_provenance.json";write_json(prov,{"teacher":self.runtime["teacher"],"teacher_run_id":"evertracer_a_20260828_223155","seed":42,"generation":{"batch_size":8,"records_per_prompt":4,"max_new_tokens":768,"temperature":0.8,"top_p":0.95},"raw_candidate_count":sum(1 for _ in raw.open(encoding="utf-8"))})
    cmd=[self.py,str(self.code/"scripts/generate_distillation_qa.py"),"--raw-candidates",str(raw),"--output",str(self.r/"dataset/frozen_qa.jsonl"),"--manifest",str(self.r/"dataset/manifest.json"),"--target-count","20000","--provenance",str(prov)];p=subprocess.run(cmd,capture_output=True,text=True);(self.r/"logs/dataset_freeze.log").write_text(p.stdout+p.stderr)
    if p.returncode==0:self.update(completed_stages=self.s.get("completed_stages",[])+["DATASET_FREEZE"],last_completed_stage="DATASET_FREEZE");break
    target+=2000
    if target>40000:raise RuntimeError("insufficient valid unique QA by 40,000 candidates")
   student=self.r/"checkpoints/student";self.run("TRAINING",[self.py,str(self.code/"scripts/train_distillation_student.py"),"--model-path",self.runtime["base"],"--dataset",str(self.r/"dataset/frozen_qa.jsonl"),"--output-dir",str(student),"--batch-size","8","--epochs","3","--learning-rate","1e-5","--seed","42","--max-length","1024","--telemetry",str(self.r/"metrics/training_telemetry.json")]);ck=student/"final_model"
   self.run("VERIFICATION",[self.py,str(self.code/"scripts/evertracer_verify.py"),"--config",str(self.c),"--suspect",str(ck),"--reference",self.runtime["reference"],"--neighborhoods",self.runtime["neighborhoods"],"--output",str(self.r/"metrics/student_verification_raw.json"),"--label","student"])
   self.run("VERIFICATION_AGGREGATION",[self.py,str(self.code/"scripts/evertracer_aggregate_verification.py"),"--config",str(self.c),"--input",str(self.r/"metrics/student_verification_raw.json"),"--output",str(self.r/"metrics/student_verification.json"),"--source-run-id",self.r.name])
   self.run("UTILITY",[self.py,str(self.code/"scripts/evertracer_ba_utility.py"),"--config",str(self.c),"--student",str(ck),"--output",str(self.r/"metrics/utility.json")])
   self.run("RELOAD_SANITY",[self.py,str(self.code/"scripts/evertracer_sanity.py"),"--model",str(ck),"--output",str(self.r/"metrics/reload_sanity.json"),"--max-new-tokens","96"])
   self.run("FINAL_REPORT",[self.py,str(self.code/"scripts/evertracer_ba_report.py"),"--run-dir",str(self.r)]);self.update(status="COMPLETED",stage="COMPLETED",exit_code=0,end_time=now());self.notify("COMPLETED")
  except Exception as e:
   failed=self.s.get("stage");trace=traceback.format_exc();(self.r/"logs/failure_traceback.log").write_text(trace);self.update(status="FAILED",stage="FAILED",failed_stage=failed,exit_code=1,end_time=now(),error=f"{type(e).__name__}: {e}",traceback=trace);self.notify("FAILED",self.s["error"]);raise
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--config",required=True);p.add_argument("--run-dir",required=True);p.add_argument("--code-root",required=True);p.add_argument("--python",required=True);P(p.parse_args()).execute()
