#!/usr/bin/env python3
"""Second immutable continuation for corrected EverTracer A aggregation and evaluation."""
import argparse,datetime as dt,json,os,shutil,subprocess,sys,traceback
from pathlib import Path
from evertracer_common import load_config,sha256_file,write_json

def main():
 p=argparse.ArgumentParser();p.add_argument("--config",required=True);p.add_argument("--run-id",required=True);p.add_argument("--run-dir",required=True);p.add_argument("--root-run",required=True);p.add_argument("--parent-run",required=True);a=p.parse_args();c=load_config(a.config);run=Path(a.run_dir);root_run=Path(a.root_run);parent=Path(a.parent_run);status=run/"status/status.json";logs=run/"logs";metrics=run/"metrics";reports=run/"reports"
 for d in (logs,metrics,reports,status.parent):d.mkdir(parents=True,exist_ok=True)
 neighborhoods=parent/"artifacts/frozen_neighborhoods.jsonl";expected_sha="7834e3d77704951ea06501c2166e960fef2b147ced3d751a8e55f07ec7b3672b"
 if sha256_file(neighborhoods)!=expected_sha:raise ValueError("canonical frozen neighborhoods SHA-256 mismatch")
 metadata={"experiment":"EverTracer Experiment A","parent_run_id":parent.name,"root_run_id":root_run.name,"continuation_reason":"detector ROC/threshold direction implementation correction + utility offline dataset resolution","scientific_config_changed":False,"target_retrained":False,"reference_retrained":False,"neighborhoods_regenerated":False,"verification_inference_reused":True,"frozen_neighborhoods":str(neighborhoods),"frozen_neighborhoods_sha256":expected_sha,"target_artifact_manifest":str(root_run/"artifacts/target_merge_manifest.json"),"reference_artifact_manifest":str(root_run/"artifacts/reference_merge_manifest.json")};write_json(run/"continuation_metadata.json",metadata)
 for name in ("target_train.json","reference_train.json"):shutil.copy2(root_run/"metrics"/name,metrics/name)
 state={"project":"WMKD_Benchmark","method":"EverTracer","experiment":"A","run_id":a.run_id,"pid":os.getpid(),"start_time":dt.datetime.now().astimezone().isoformat(),"stage":"CORRECTING_VERIFICATION_AGGREGATION","status":"RUNNING","exit_code":None,"error":None,**metadata};write_json(status,state)
 py=sys.executable;code=Path(__file__).resolve().parent;target=root_run/"checkpoints/target_merged"
 def update(stage):state["stage"]=stage;state["updated_at"]=dt.datetime.now().astimezone().isoformat();write_json(status,state)
 def command(stage,name,args):
  update(stage)
  with (logs/f"{name}.log").open("w",encoding="utf-8") as out:result=subprocess.run(args,stdout=out,stderr=subprocess.STDOUT,text=True)
  if result.returncode:raise RuntimeError(f"{name} failed with exit code {result.returncode}")
 try:
  subprocess.run([py,str(code/"notify_experiment.py"),"--event","STARTED","--experiment","EverTracer A continuation 2","--run-id",a.run_id,"--stage",state["stage"],"--pid",str(os.getpid()),"--status-file",str(status),"--log-path",str(logs)],check=False)
  for label in ("teacher","base"):command("CORRECTING_VERIFICATION_AGGREGATION",f"aggregate_{label}",[py,str(code/"evertracer_aggregate_verification.py"),"--config",a.config,"--input",str(parent/f"metrics/{label}_verification.json"),"--output",str(metrics/f"{label}_verification.json"),"--source-run-id",parent.name])
  command("UTILITY","utility",[py,str(code/"evertracer_utility.py"),"--config",a.config,"--base",c["model"]["path"],"--teacher",str(target),"--output",str(metrics/"utility.json"),"--batch-size",str(c["utility"]["batch_size"])])
  command("RELOAD_VALIDATION","reload_sanity",[py,str(code/"evertracer_sanity.py"),"--model",str(target),"--output",str(metrics/"reload_sanity.json"),"--max-new-tokens",str(c["utility"]["ordinary_max_new_tokens"])])
  command("REPORTING","report",[py,str(code/"evertracer_report.py"),"--config",a.config,"--run-dir",str(run),"--summary",str(reports/"summary.json"),"--report",str(reports/"report.md")])
  state.update({"stage":"COMPLETED","status":"COMPLETED","end_time":dt.datetime.now().astimezone().isoformat(),"exit_code":0});write_json(status,state);subprocess.run([py,str(code/"notify_experiment.py"),"--event","COMPLETED","--experiment","EverTracer A continuation 2","--run-id",a.run_id,"--stage","COMPLETED","--pid",str(os.getpid()),"--exit-code","0","--status-file",str(status),"--log-path",str(logs)],check=False)
 except Exception as exc:
  failed=state.get("stage");state.update({"stage":"FAILED","failed_stage":failed,"status":"FAILED","end_time":dt.datetime.now().astimezone().isoformat(),"exit_code":1,"error":f"{type(exc).__name__}: {exc}","traceback":traceback.format_exc()});write_json(status,state);subprocess.run([py,str(code/"notify_experiment.py"),"--event","FAILED","--experiment","EverTracer A continuation 2","--run-id",a.run_id,"--stage",failed,"--pid",str(os.getpid()),"--exit-code","1","--status-file",str(status),"--log-path",str(logs),"--error-summary",state["error"]],check=False);raise
if __name__=="__main__":main()
