#!/usr/bin/env python3
"""Detached continuation for unfinished EverTracer Experiment A evaluation stages."""
import argparse,datetime as dt,json,os,shutil,subprocess,sys,traceback
from pathlib import Path
from evertracer_common import load_config,write_json

def main():
 p=argparse.ArgumentParser();p.add_argument("--config",required=True);p.add_argument("--run-id",required=True);p.add_argument("--run-dir",required=True);p.add_argument("--parent-run",required=True);a=p.parse_args();c=load_config(a.config);run=Path(a.run_dir);parent=Path(a.parent_run);status=run/"status/status.json";logs=run/"logs";metrics=run/"metrics";art=run/"artifacts";reports=run/"reports"
 for d in (logs,metrics,art,reports,status.parent):d.mkdir(parents=True,exist_ok=True)
 metadata={"parent_run_id":parent.name,"continuation_reason":"T5 offline cache visibility / online Hub resolution failure","reuse_target_artifact":True,"reuse_reference_artifact":True,"scientific_config_changed":False,"training_repeated":False,"experiment_identity":"EverTracer Experiment A","parent_target_merged":str(parent/"checkpoints/target_merged"),"parent_reference_merged":str(parent/"checkpoints/reference_merged")};write_json(run/"continuation_metadata.json",metadata)
 for name in ("target_train.json","reference_train.json"):shutil.copy2(parent/"metrics"/name,metrics/name)
 state={"project":"WMKD_Benchmark","method":"EverTracer","experiment":"A","run_id":a.run_id,"pid":os.getpid(),"start_time":dt.datetime.now().astimezone().isoformat(),"stage":"PREPARING_VERIFICATION","status":"RUNNING","exit_code":None,"error":None,**metadata};write_json(status,state)
 py=sys.executable;root=Path(__file__).resolve().parent;dataset=c["dataset"]["frozen_root"];target=parent/"checkpoints/target_merged";reference=parent/"checkpoints/reference_merged"
 def update(stage):state["stage"]=stage;state["updated_at"]=dt.datetime.now().astimezone().isoformat();write_json(status,state)
 def command(stage,name,args):
  update(stage)
  with (logs/f"{name}.log").open("w",encoding="utf-8") as out:result=subprocess.run(args,stdout=out,stderr=subprocess.STDOUT,text=True)
  if result.returncode:raise RuntimeError(f"{name} failed with exit code {result.returncode}")
 try:
  subprocess.run([py,str(root/"notify_experiment.py"),"--event","STARTED","--experiment","EverTracer Experiment A continuation","--run-id",a.run_id,"--stage","PREPARING_VERIFICATION","--pid",str(os.getpid()),"--status-file",str(status),"--log-path",str(logs)],check=False)
  command("PREPARING_VERIFICATION","perturb",[py,str(root/"evertracer_perturb.py"),"--config",a.config,"--dataset-root",dataset,"--output",str(art/"frozen_neighborhoods.jsonl")])
  common=["--config",a.config,"--reference",str(reference),"--neighborhoods",str(art/"frozen_neighborhoods.jsonl")]
  command("VERIFYING_TEACHER","verify_teacher",[py,str(root/"evertracer_verify.py"),*common,"--suspect",str(target),"--output",str(metrics/"teacher_verification.json"),"--label","teacher"])
  command("VERIFYING_BASE","verify_base",[py,str(root/"evertracer_verify.py"),*common,"--suspect",c["model"]["path"],"--output",str(metrics/"base_verification.json"),"--label","base"])
  command("UTILITY","utility",[py,str(root/"evertracer_utility.py"),"--base",c["model"]["path"],"--teacher",str(target),"--output",str(metrics/"utility.json"),"--batch-size",str(c["utility"]["batch_size"])])
  command("RELOAD_VALIDATION","reload_sanity",[py,str(root/"evertracer_sanity.py"),"--model",str(target),"--output",str(metrics/"reload_sanity.json"),"--max-new-tokens",str(c["utility"]["ordinary_max_new_tokens"])])
  command("REPORTING","report",[py,str(root/"evertracer_report.py"),"--config",a.config,"--run-dir",str(run),"--summary",str(reports/"summary.json"),"--report",str(reports/"report.md")])
  state.update({"stage":"COMPLETED","status":"COMPLETED","end_time":dt.datetime.now().astimezone().isoformat(),"exit_code":0});write_json(status,state);subprocess.run([py,str(root/"notify_experiment.py"),"--event","COMPLETED","--experiment","EverTracer Experiment A continuation","--run-id",a.run_id,"--stage","COMPLETED","--pid",str(os.getpid()),"--exit-code","0","--status-file",str(status),"--log-path",str(logs)],check=False)
 except Exception as exc:
  failed_stage=state.get("stage");state.update({"stage":"FAILED","failed_stage":failed_stage,"status":"FAILED","end_time":dt.datetime.now().astimezone().isoformat(),"exit_code":1,"error":f"{type(exc).__name__}: {exc}","traceback":traceback.format_exc()});write_json(status,state);subprocess.run([py,str(root/"notify_experiment.py"),"--event","FAILED","--experiment","EverTracer Experiment A continuation","--run-id",a.run_id,"--stage",failed_stage,"--pid",str(os.getpid()),"--exit-code","1","--status-file",str(status),"--log-path",str(logs),"--error-summary",state["error"]],check=False);raise
if __name__=="__main__":main()
