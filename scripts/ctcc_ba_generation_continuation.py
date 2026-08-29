#!/usr/bin/env python3
"""Infrastructure-only CTCC Ba generation continuation; parent artifacts are read-only."""
import argparse,datetime as dt,hashlib,json,os,subprocess,traceback
from pathlib import Path
from generate_teacher_qa_formal import consumed_prompt_indices,recover_next_prompt_index
PARENT_ID="ctcc_ba_generation_20260829_195943"
PARENT_RAW_SHA="2cd9406971f79df45c5350e5d364f03daa462c32f09204bb51b5259154884d16"
PARENT_CONFIG_SHA="d9965f940dcc67272d82e42f595c1f33eeb5a09fb43eb32d24b44107d51b117f"
TEACHER_SHA="36957869183ee2581c7377ba973de0aef4d162c7caa3a2353684cf931ae429cd"
def now():return dt.datetime.now().astimezone().isoformat()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,x):Path(p).write_text(json.dumps(x,indent=2)+"\n")
def lines(p):return sum(1 for _ in Path(p).open(encoding="utf-8")) if Path(p).exists() else 0
def main():
 p=argparse.ArgumentParser();p.add_argument("--config",required=True);p.add_argument("--run-dir",required=True);p.add_argument("--code-root",required=True);p.add_argument("--python",required=True);p.add_argument("--parent-run",required=True);a=p.parse_args()
 import yaml
 c=yaml.safe_load(Path(a.config).read_text());r=Path(a.run_dir);parent=Path(a.parent_run);sp=r/"status/status.json";s=json.loads(sp.read_text());parent_raw=parent/"dataset/raw_candidates.jsonl";parent_err=parent/"dataset/generation_errors.jsonl";new_raw=r/"dataset/continuation_raw_candidates.jsonl";new_err=r/"dataset/continuation_generation_errors.jsonl";combined=r/"dataset/combined_candidates.jsonl"
 def update(**kw):s.update(kw);s["updated_at"]=now();write(sp,s)
 def notify(event,error=None):
  cmd=[a.python,str(Path(a.code_root)/"scripts/notify_experiment.py"),"--event",event,"--experiment","CTCC Experiment Ba Generation Continuation","--run-id",r.name,"--stage",s.get("stage","UNKNOWN"),"--pid",str(os.getpid()),"--status-file",str(sp),"--log-path",str(r/"logs")]
  if error:cmd += ["--error-summary",error]
  return subprocess.run(cmd,check=False).returncode
 def run(stage,cmd):
  update(status="RUNNING",stage=stage,child_command=cmd);log=r/"logs"/(stage.lower()+".log")
  with log.open("a",buffering=1) as out:q=subprocess.Popen(cmd,stdout=out,stderr=subprocess.STDOUT,text=True);update(child_pid=q.pid);rc=q.wait()
  if rc:raise RuntimeError(f"{stage} failed with exit code {rc}")
  update(child_pid=None,completed_stages=s.get("completed_stages",[])+[stage])
 try:
  if parent.name!=PARENT_ID or sha(parent_raw)!=PARENT_RAW_SHA or sha(a.config)!=PARENT_CONFIG_SHA:raise RuntimeError("parent raw/config immutability gate failed")
  if sha(Path(c["teacher"]["adapter"])/"adapter_model.safetensors")!=TEACHER_SHA:raise RuntimeError("teacher hash gate failed")
  consumed=consumed_prompt_indices([parent_raw,parent_err]);start=recover_next_prompt_index([parent_raw,parent_err]);update(status="RUNNING",stage="PREFLIGHT",runner_pid=os.getpid(),parent_run_id=PARENT_ID,parent_raw_count=lines(parent_raw),parent_unique_count=17880,parent_raw_sha256=PARENT_RAW_SHA,parent_consumed_max_prompt_index=max(consumed),continuation_start_prompt_index=start,no_overlap=start not in consumed,total_raw_ceiling=60000);update(started_email_exit_code=notify("STARTED"))
  if start in consumed:raise RuntimeError("continuation cursor overlap")
  target=2000
  while True:
   remaining=60000-lines(parent_raw)
   target=min(target,remaining)
   run("TEACHER_QA_GENERATION_CONTINUATION",[a.python,str(Path(a.code_root)/"scripts/generate_teacher_qa_formal.py"),"--model-path",c["model"]["path"],"--adapter-path",c["teacher"]["adapter"],"--teacher-run-id",c["teacher"]["run_id"],"--resume-consumed-record",str(parent_raw),"--resume-consumed-record",str(parent_err),"--output",str(new_raw),"--errors",str(new_err),"--target-candidates",str(target),"--batch-size","8","--records-per-prompt","4","--seed","42","--telemetry",str(r/"metrics/generation_telemetry.json")])
   with combined.open("wb") as out:
    for source in (parent_raw,new_raw):
     with source.open("rb") as inp:
      for block in iter(lambda:inp.read(1048576),b""):out.write(block)
   provenance=r/"config/dataset_provenance.json";write(provenance,{"lineage":"infrastructure_only_continuation","parent_run_id":PARENT_ID,"parent_raw":{"path":str(parent_raw),"count":lines(parent_raw),"sha256":PARENT_RAW_SHA,"unique":17880},"continuation_raw":{"path":str(new_raw),"count":lines(new_raw),"sha256":sha(new_raw)},"combined_raw":{"path":str(combined),"count":lines(combined),"sha256":sha(combined)},"teacher_run_id":c["teacher"]["run_id"],"teacher_adapter_sha256":TEACHER_SHA,"prompt_protocol":c["dataset"]["prompt_protocol"],"generation":{"seed":42,"batch_size":8,"records_per_prompt":4,"max_new_tokens":768,"temperature":0.8,"top_p":0.95},"cursor":{"parent_consumed_max":max(consumed),"continuation_start":start,"no_overlap":True},"filter_dedup":"unchanged_distillation_data.freeze_candidates"})
   cmd=[a.python,str(Path(a.code_root)/"scripts/generate_distillation_qa.py"),"--raw-candidates",str(combined),"--output",str(r/"dataset/frozen_qa.jsonl"),"--manifest",str(r/"dataset/manifest.json"),"--target-count","20000","--provenance",str(provenance)];q=subprocess.run(cmd,capture_output=True,text=True);(r/"logs/dataset_freeze.log").write_text(q.stdout+q.stderr)
   if q.returncode==0:break
   if lines(parent_raw)+lines(new_raw)>=60000:raise RuntimeError("insufficient unique QA at approved 60k total raw ceiling")
   target=min(target+2000,60000-lines(parent_raw))
  m=json.loads((r/"dataset/manifest.json").read_text());update(status="COMPLETED",stage="COMPLETED",exit_code=0,end_time=now(),continuation_added_raw=lines(new_raw),continuation_parse_errors=lines(new_err),combined_raw_count=lines(combined),combined_unique_count=m["sample_count"],frozen_count=m["sample_count"],frozen_sha256=m["dataset_sha256"],continuation_raw_sha256=sha(new_raw));update(completed_email_exit_code=notify("COMPLETED"))
 except Exception as e:
  trace=traceback.format_exc();(r/"logs/failure_traceback.log").write_text(trace);update(status="FAILED",stage="FAILED",exit_code=1,end_time=now(),error=f"{type(e).__name__}: {e}");notify("FAILED",s["error"]);raise
if __name__=="__main__":main()
