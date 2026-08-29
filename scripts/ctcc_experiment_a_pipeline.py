"""Immutable detached CTCC Experiment A pipeline."""
import argparse,datetime as dt,json,os,subprocess,sys,traceback
from pathlib import Path

def write(path,obj): path.write_text(json.dumps(obj,indent=2)+"\n")
def main():
 p=argparse.ArgumentParser();p.add_argument("--config",required=True);p.add_argument("--run-id",required=True);p.add_argument("--run-dir",required=True);a=p.parse_args();run=Path(a.run_dir);root=Path(__file__).parent;py=sys.executable
 for d in (run/"logs",run/"metrics",run/"evaluation",run/"reports",run/"status",run/"checkpoints"):d.mkdir(parents=True,exist_ok=True)
 status=run/"status/status.json";state={"run_id":a.run_id,"experiment":"CTCC A","status":"RUNNING","stage":"STARTING","pid":os.getpid(),"start_time":dt.datetime.now().astimezone().isoformat(),"exit_code":None};write(status,state)
 def notify(event,**extra):
  cmd=[py,str(root/"notify_experiment.py"),"--event",event,"--experiment","CTCC Experiment A","--run-id",a.run_id,"--stage",state["stage"],"--pid",str(os.getpid()),"--status-file",str(status),"--log-path",str(run/"logs")]
  if "exit_code" in extra:cmd += ["--exit-code",str(extra["exit_code"])]
  subprocess.run(cmd,check=False)
 def command(stage,name,args):
  state["stage"]=stage;write(status,state)
  with (run/"logs"/f"{name}.log").open("w") as log: subprocess.run(args,stdout=log,stderr=subprocess.STDOUT,check=True)
 try:
  notify("STARTED");adapter=run/"checkpoints/adapter"
  command("TRAINING","training",[py,str(root/"ctcc_train.py"),"--config",a.config,"--run-dir",str(run)])
  command("BASE_EVALUATION","base_evaluation",[py,str(root/"ctcc_evaluate.py"),"--config",a.config,"--role","base","--output",str(run/"evaluation/base_ctcc.json")])
  command("TEACHER_FRESH_RELOAD_EVALUATION","teacher_evaluation",[py,str(root/"ctcc_evaluate.py"),"--config",a.config,"--role","teacher","--adapter",str(adapter),"--output",str(run/"evaluation/teacher_ctcc.json")])
  command("UTILITY","utility",[py,str(root/"ctcc_utility.py"),"--config",a.config,"--adapter",str(adapter),"--output",str(run/"evaluation/utility.json")])
  command("ORDINARY_GENERATION","sanity",[py,str(root/"ctcc_sanity.py"),"--config",a.config,"--adapter",str(adapter),"--output",str(run/"evaluation/sanity.json")])
  command("REPORTING","report",[py,str(root/"ctcc_report.py"),"--config",a.config,"--run-dir",str(run)])
  state.update({"stage":"COMPLETED","status":"COMPLETED","end_time":dt.datetime.now().astimezone().isoformat(),"exit_code":0});write(status,state);notify("COMPLETED",exit_code=0)
 except Exception as exc:
  state.update({"status":"FAILED","end_time":dt.datetime.now().astimezone().isoformat(),"exit_code":1,"error":f"{type(exc).__name__}: {exc}","traceback":traceback.format_exc()});write(status,state);notify("FAILED",exit_code=1);raise
if __name__=="__main__":main()
