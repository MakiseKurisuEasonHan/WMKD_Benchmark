"""Detached Passive-5 shared Ba dataset generation and Student training."""
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, os, resource, subprocess, traceback
from pathlib import Path

P=Path("/root/autodl-tmp/WMKD_Benchmark")
D=Path("/root/autodl-tmp/WMKD_Benchmark_data")
PY=D/"artifacts/scw/env_py311/bin/python"
EXPECTED={
 "config.json":"39fb36dc5416f445ebc4e71cb71fbcf6727e80a35836d8ba1a1474c318467b7a",
 "tokenizer.json":"79e3e522635f3171300913bb421464a87de6222182a0570b9b2ccba2a964b2b4",
 "model.safetensors.index.json":"0a57c30afc07c81610ae7fe013bea3b9d50365f9a8145ae98e8714220f3d7c7c",
 "model-00001-of-00002.safetensors":"13cbd6d16e927a0c5bad54102514e6e18b4a47b3a6eb911e39d678d328d19f55",
 "model-00002-of-00002.safetensors":"7b770216613ac5c34d7c54bdff1fa616bc4e338a9d0b20af6303e48c295ee23c"}
def now():return dt.datetime.now(dt.timezone.utc).isoformat()
def sha(p):
 h=hashlib.sha256()
 with Path(p).open("rb") as f:
  for b in iter(lambda:f.read(1<<20),b""):h.update(b)
 return h.hexdigest()
def atomic(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);q=p.with_suffix(p.suffix+".tmp");q.write_text(json.dumps(x,indent=2,ensure_ascii=False)+"\n",encoding="utf-8");os.replace(q,p)
def lines(p):return sum(1 for x in Path(p).open(encoding="utf-8") if x.strip()) if Path(p).exists() else 0
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--run-id",required=True);a=ap.parse_args();cfg=json.loads((P/"configs/distillation/passive5_shared_ba.json").read_text());root=D/"runs/passive5_shared_ba"/a.run_id;root.mkdir(parents=True,exist_ok=False);(root/"metrics").mkdir();status={"run_id":a.run_id,"state":"RUNNING","stage":"PREFLIGHT","pid":os.getpid(),"ppid":os.getppid(),"started_at":now(),"auto_shutdown":False,"scientific_status":"BA_IN_PROGRESS","stages":{}};sp=root/"pipeline_status.json";atomic(sp,status)
 env=os.environ.copy();env.update({"PYTHONHASHSEED":"42","HF_HUB_OFFLINE":"1","TRANSFORMERS_OFFLINE":"1","TOKENIZERS_PARALLELISM":"false","WMKD_AUTO_SHUTDOWN_ENABLED":"false"})
 def update(**kw):status.update(kw);status["updated_at"]=now();atomic(sp,status)
 def run(stage,cmd):
  cmd=[str(x) for x in cmd];update(stage=stage,child_command=cmd);log=root/"logs"/(stage.lower()+".log");log.parent.mkdir(parents=True,exist_ok=True)
  with log.open("a",encoding="utf-8",buffering=1) as out:
   c=subprocess.Popen(cmd,stdout=out,stderr=subprocess.STDOUT,env=env,text=True);update(child_pid=c.pid);rc=c.wait()
  status["stages"][stage]={"exit_code":rc,"log":str(log),"ended_at":now()};update(child_pid=None)
  if rc:raise RuntimeError(f"{stage} failed exit={rc}")
 try:
  teacher=Path(cfg["teacher"]["path"]);actual={n:sha(teacher/n) for n in EXPECTED};
  if actual!=EXPECTED:raise RuntimeError("FAIL_CLOSED_CANONICAL_TEACHER_HASH_MISMATCH")
  free=os.statvfs(D);free_gb=free.f_bavail*free.f_frsize/2**30
  if free_gb<=100:raise RuntimeError("GLOBAL_DISK_SAFETY_BLOCK")
  pre={"status":"PASS","teacher":cfg["teacher"],"teacher_files_sha256":actual,"student_initialization":cfg["student"],"dataset_protocol":cfg["dataset"],"training_config":cfg["training"],"gpu_required_idle":True,"disk_free_gb":free_gb,"storage_forecast_gb":25,"forecast_free_after_gb":free_gb-25,"teacher_generation_forecast_hours":[2,4],"student_training_forecast_minutes":[29,35],"frozen_detectors":{"LLMPrint":0.7150049776126003,"REEF":0.4546738923165847,"HuRef":4.119894027709961,"AWM":0.0017953364917795106,"ZeroPrint":0.6793505996465683},"shared_attack":True}
  atomic(root/"preflight.json",pre);raw=root/"dataset/raw_candidates.jsonl";errors=root/"dataset/generation_errors.jsonl";target=cfg["dataset"]["candidate_samples"]
  while True:
   run(f"TEACHER_GENERATION_{target}",[PY,P/"scripts/generate_teacher_qa_formal.py","--model-path",teacher,"--teacher-run-id",a.run_id,"--output",raw,"--errors",errors,"--target-candidates",target,"--batch-size",8,"--records-per-prompt",4,"--seed",42,"--max-total-calls",20000,"--telemetry",root/"metrics/generation_telemetry.json"])
   provenance={"teacher":cfg["teacher"],"teacher_file_sha256":actual,"prompt_protocol":cfg["dataset"]["prompt_protocol"],"generation_config":cfg["dataset"]["generation"],"raw_count":lines(raw),"error_count":lines(errors),"run_id":a.run_id};atomic(root/"dataset/provenance.json",provenance)
   cmd=[PY,P/"scripts/generate_distillation_qa.py","--raw-candidates",raw,"--output",root/"dataset/frozen_qa.jsonl","--manifest",root/"dataset/manifest.json","--target-count",20000,"--provenance",root/"dataset/provenance.json"]
   cp=subprocess.run([str(x) for x in cmd],capture_output=True,text=True,env=env);(root/"logs/dataset_freeze.log").write_text(cp.stdout+cp.stderr,encoding="utf-8")
   if cp.returncode==0:break
   target+=cfg["dataset"]["increment_samples"]
   if target>cfg["dataset"]["maximum_candidates"]:raise RuntimeError("INSUFFICIENT_UNIQUE_QA_AT_60K_CEILING")
  frozen=root/"dataset/frozen_qa.jsonl";rows=[json.loads(x) for x in frozen.read_text(encoding="utf-8").splitlines() if x.strip()];ids=[x["sample_id"] for x in rows]
  if len(rows)!=20000 or len(set(ids))!=20000:raise RuntimeError("FAIL_CLOSED_20K_INTEGRITY")
  manifest=json.loads((root/"dataset/manifest.json").read_text());update(stage="DATASET_COMPLETED",dataset_count=20000,dataset_sha256=manifest["dataset_sha256"],raw_count=lines(raw),generation_errors=lines(errors),training_status="RUNNING")
  run("STUDENT_TRAINING",[PY,P/"scripts/train_distillation_student.py","--model-path",teacher,"--dataset",frozen,"--output-dir",root/"student","--batch-size",8,"--epochs",3,"--learning-rate","1e-5","--seed",42,"--max-length",1024,"--telemetry",root/"metrics/training_telemetry.json"])
  final=root/"student/final_model"
  if not (final/"config.json").is_file():raise RuntimeError("FINAL_STUDENT_MISSING")
  files={str(x.relative_to(final)):sha(x) for x in sorted(final.rglob("*")) if x.is_file()};atomic(root/"student/student_manifest.json",{"status":"PASS","run_id":a.run_id,"artifact":str(final),"files_sha256":files,"dataset_sha256":manifest["dataset_sha256"],"config":cfg["training"],"peak_ram_kib":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})
  update(state="RUNNING",stage="STUDENT_COMPLETED_PENDING_EVALUATION",training_status="COMPLETED",student_artifact=str(final),terminal=False)
 except Exception as e:
  (root/"failure_traceback.log").write_text(traceback.format_exc(),encoding="utf-8");update(state="FAILED",stage="FAILED",failure=f"{type(e).__name__}: {e}",terminal=True);raise
if __name__=="__main__":main()
