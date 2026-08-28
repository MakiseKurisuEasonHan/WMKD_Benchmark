#!/usr/bin/env python3
"""Immutable sequential detached pipeline for EverTracer Experiment A."""
import argparse,datetime as dt,json,os,subprocess,sys,traceback
from pathlib import Path
from evertracer_common import load_config,write_json

def main():
 p=argparse.ArgumentParser();p.add_argument("--config",required=True);p.add_argument("--run-id",required=True);p.add_argument("--run-dir",required=True);a=p.parse_args();c=load_config(a.config);run=Path(a.run_dir);status=run/"status/status.json";logs=run/"logs";metrics=run/"metrics";art=run/"artifacts";check=run/"checkpoints";reports=run/"reports"
 for d in (logs,metrics,art,check,reports,status.parent):d.mkdir(parents=True,exist_ok=True)
 state={"project":"WMKD_Benchmark","method":"EverTracer","experiment":"A","run_id":a.run_id,"pid":os.getpid(),"start_time":dt.datetime.now().astimezone().isoformat(),"stage":"PREPARING","status":"RUNNING","exit_code":None,"error":None};write_json(status,state)
 py=sys.executable;root=Path(__file__).resolve().parent;dataset=c["dataset"]["frozen_root"]
 def update(stage):state["stage"]=stage;state["updated_at"]=dt.datetime.now().astimezone().isoformat();write_json(status,state)
 def command(stage,name,args):
  update(stage)
  with (logs/f"{name}.log").open("w",encoding="utf-8") as out:
   result=subprocess.run(args,stdout=out,stderr=subprocess.STDOUT,text=True)
  if result.returncode:raise RuntimeError(f"{name} failed with exit code {result.returncode}")
 try:
  command("PREPARING","preflight",[py,str(root/"evertracer_preflight.py"),"--config",a.config,"--dataset-root",dataset,"--output",str(metrics/"preflight.json")])
  subprocess.run([py,str(root/"notify_experiment.py"),"--event","STARTED","--experiment","EverTracer Experiment A","--run-id",a.run_id,"--stage","RUNNING_TARGET","--pid",str(os.getpid()),"--status-file",str(status),"--log-path",str(logs)],check=False)
  command("RUNNING_TARGET","target_train",[py,str(root/"evertracer_train.py"),"--config",a.config,"--role","target","--dataset-root",dataset,"--output-dir",str(check/"target"),"--metrics",str(metrics/"target_train.json")])
  command("MERGING_TARGET","target_merge",[py,str(root/"evertracer_merge.py"),"--config",a.config,"--adapter",str(check/"target/adapter"),"--output",str(check/"target_merged"),"--manifest",str(art/"target_merge_manifest.json")])
  command("RUNNING_REFERENCE","reference_train",[py,str(root/"evertracer_train.py"),"--config",a.config,"--role","reference","--dataset-root",dataset,"--output-dir",str(check/"reference"),"--metrics",str(metrics/"reference_train.json")])
  command("MERGING_REFERENCE","reference_merge",[py,str(root/"evertracer_merge.py"),"--config",a.config,"--adapter",str(check/"reference/adapter"),"--output",str(check/"reference_merged"),"--manifest",str(art/"reference_merge_manifest.json")])
  command("PREPARING_VERIFICATION","perturb",[py,str(root/"evertracer_perturb.py"),"--config",a.config,"--dataset-root",dataset,"--output",str(art/"frozen_neighborhoods.jsonl")])
  common=["--config",a.config,"--reference",str(check/"reference_merged"),"--neighborhoods",str(art/"frozen_neighborhoods.jsonl")]
  command("VERIFYING_TEACHER","verify_teacher",[py,str(root/"evertracer_verify.py"),*common,"--suspect",str(check/"target_merged"),"--output",str(metrics/"teacher_verification.json"),"--label","teacher"])
  command("VERIFYING_BASE","verify_base",[py,str(root/"evertracer_verify.py"),*common,"--suspect",c["model"]["path"],"--output",str(metrics/"base_verification.json"),"--label","base"])
  command("UTILITY","utility",[py,str(root/"evertracer_utility.py"),"--base",c["model"]["path"],"--teacher",str(check/"target_merged"),"--output",str(metrics/"utility.json"),"--batch-size",str(c["utility"]["batch_size"])])
  command("RELOAD_VALIDATION","reload_sanity",[py,str(root/"evertracer_sanity.py"),"--model",str(check/"target_merged"),"--output",str(metrics/"reload_sanity.json"),"--max-new-tokens",str(c["utility"]["ordinary_max_new_tokens"])])
  command("RELOAD_VALIDATION","report",[py,str(root/"evertracer_report.py"),"--config",a.config,"--run-dir",str(run),"--summary",str(reports/"summary.json"),"--report",str(reports/"report.md")])
  state.update({"stage":"COMPLETED","status":"COMPLETED","end_time":dt.datetime.now().astimezone().isoformat(),"exit_code":0});write_json(status,state);subprocess.run([py,str(root/"notify_experiment.py"),"--event","COMPLETED","--experiment","EverTracer Experiment A","--run-id",a.run_id,"--stage","COMPLETED","--pid",str(os.getpid()),"--exit-code","0","--status-file",str(status),"--log-path",str(logs)],check=False)
 except Exception as exc:
  state.update({"stage":"FAILED","status":"FAILED","end_time":dt.datetime.now().astimezone().isoformat(),"exit_code":1,"error":f"{type(exc).__name__}: {exc}","traceback":traceback.format_exc()});write_json(status,state);subprocess.run([py,str(root/"notify_experiment.py"),"--event","FAILED","--experiment","EverTracer Experiment A","--run-id",a.run_id,"--stage",state.get("stage"),"--pid",str(os.getpid()),"--exit-code","1","--status-file",str(status),"--log-path",str(logs),"--error-summary",state["error"]],check=False);raise
if __name__=="__main__":main()
