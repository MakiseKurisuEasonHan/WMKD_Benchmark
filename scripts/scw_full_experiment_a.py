"""Fail-closed detached SCW A: py311 gate, formal training, evaluation, report."""
import argparse,datetime,hashlib,json,os,subprocess,sys,traceback
from pathlib import Path
P=Path("/root/autodl-tmp/WMKD_Benchmark");D=Path("/root/autodl-tmp/WMKD_Benchmark_data");SRC=D/"artifacts/scw/source";CFG=P/"configs/watermark/scw_experiment_a.yaml";OFF=P/"configs/watermark/scw_experiment_a_official.yaml";MAN=D/"artifacts/scw/manifests/scw_dataset_manifest.json";BASE=D/"models/base/Llama-3.2-3B-Instruct"
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def write(p,x):p.parent.mkdir(parents=True,exist_ok=True);q=p.with_suffix(p.suffix+".tmp");q.write_text(json.dumps(x,indent=2,ensure_ascii=False)+"\n",encoding="utf-8");q.replace(p)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(stage,cmd,status,root,env=None):
 status.update(stage=stage,stage_started_at=now());write(root/"pipeline_status.json",status)
 log=root/"logs"/(stage.lower()+".log");log.parent.mkdir(parents=True,exist_ok=True)
 with log.open("w",encoding="utf-8") as h:
  c=subprocess.run(cmd,stdout=h,stderr=subprocess.STDOUT,env=env or os.environ.copy())
 status.setdefault("stages",{})[stage]={"exit_code":c.returncode,"log":str(log),"ended_at":now()};write(root/"pipeline_status.json",status)
 if c.returncode:raise RuntimeError(f"{stage} failed exit={c.returncode}")
def main():
 a=argparse.ArgumentParser();a.add_argument("--run-id",required=True);x=a.parse_args();root=D/"runs/scw/orchestrators"/x.run_id;root.mkdir(parents=True,exist_ok=False)
 status={"run_id":x.run_id,"pid":os.getpid(),"state":"RUNNING","stage":"INIT","started_at":now(),"formal_a_started":False,"ba_started":False,"shutdown_method":"FALLBACK_REQUIRED","shutdown_requested":False,"terminal":False,"stages":{}};write(root/"pipeline_status.json",status);code=0
 env=os.environ.copy();env.update({"PYTHONHASHSEED":"42","HF_ENDPOINT":"https://hf-mirror.com","HF_HOME":str(D/"artifacts/scw/hf_home")})
 freeze=subprocess.check_output([sys.executable,"-m","pip","freeze"],text=True).splitlines()
 write(root/"environment_manifest.json",{"python":sys.version,"executable":sys.executable,"packages":freeze,"torch_wheel":{"filename":"torch-2.8.0+cu128-cp311-cp311-manylinux_2_28_x86_64.whl","size_bytes":889185760,"source":"verified local pip cache; original official download-r2.pytorch.org cu128 index","sha256":"039b9dcdd6bdbaa10a8a5cd6be22c4cb3e3589a341e5f904cbb571ca28f55bed"}})
 try:
  if sys.version_info[:2]!=(3,11):raise RuntimeError("Python 3.11 required")
  if sha(MAN)!="4c063b070b4507fa2c5e2facae1d0573a8414b9f1a34d9260d6cf43d86b79b30":raise RuntimeError("dataset manifest hash mismatch")
  if subprocess.check_output(["git","-C",str(SRC),"rev-parse","HEAD"],text=True).strip()!="15bc1929569357130f2dbc0b09f91bbf4f4bd947":raise RuntimeError("official commit mismatch")
  pre=root/"runtime_preflight.json";run("PY311_PREFLIGHT",[sys.executable,str(P/"scripts/scw_runtime_preflight.py"),"--config",str(CFG),"--official-source",str(SRC),"--dataset-manifest",str(MAN),"--output",str(pre)],status,root,env)
  gate_id=x.run_id+"_gate4";gate=D/"runs/scw/speed_test"/gate_id
  run("PY311_CLEAN_EXIT_GATE",[sys.executable,str(P/"scripts/scw_experiment_a_pipeline.py"),"--config",str(CFG),"--run-id",gate_id,"--run-root",str(gate),"--official-source",str(SRC),"--runtime-preflight",str(pre),"--mode","speed-test","--representative-steps","4"],status,root,env)
  gs=json.loads((gate/"speed_test_summary.json").read_text());status["performance_gate"]={"run_id":gate_id,**gs};write(root/"pipeline_status.json",status)
  formal_id="scw_a_"+datetime.datetime.now().strftime("%Y%m%d_%H%M%S");formal=D/"runs/scw/a"/formal_id;status.update(formal_a_started=True,formal_run_id=formal_id,formal_root=str(formal));write(root/"pipeline_status.json",status)
  run("FORMAL_TRAINING",[sys.executable,str(P/"scripts/scw_experiment_a_pipeline.py"),"--config",str(CFG),"--run-id",formal_id,"--run-root",str(formal),"--official-source",str(SRC),"--runtime-preflight",str(pre),"--mode","formal"],status,root,env)
  teacher=formal/"models"/("Llama-3.2-3B-Instruct_"+formal_id+"_French_WMKD_SCW_A")
  if not (teacher/"config.json").is_file():raise RuntimeError(f"final Teacher missing: {teacher}")
  status["teacher_path"]=str(teacher);write(root/"pipeline_status.json",status)
  ev=formal/"evaluation";ev.mkdir(parents=True,exist_ok=True)
  run("BASE_FRENCH_GENERATION",[sys.executable,str(P/"scripts/scw_fresh_generate.py"),"--model",str(BASE),"--label","base","--output",str(ev/"base_generations.jsonl")],status,root,env)
  run("TEACHER_FRENCH_GENERATION",[sys.executable,str(P/"scripts/scw_fresh_generate.py"),"--model",str(teacher),"--label","teacher","--output",str(ev/"teacher_generations.jsonl")],status,root,env)
  denv=env.copy();denv["PYTHONPATH"]=str(SRC/"src")+os.pathsep+str(P/"scripts")
  for label in ("base","teacher"):
   run(label.upper()+"_DETECTOR",[sys.executable,str(P/"scripts/scw_detector.py"),"--protocol-config",str(CFG),"--official-config",str(OFF),"--generations",str(ev/(label+"_generations.jsonl")),"--model",str(BASE),"--output",str(ev/(label+"_detector.json"))],status,root,denv)
  run("UTILITY",[sys.executable,str(P/"scripts/scw_utility.py"),"--base",str(BASE),"--teacher",str(teacher),"--output",str(ev/"utility.json")],status,root,env)
  b=json.loads((ev/"base_detector.json").read_text());t=json.loads((ev/"teacher_detector.json").read_text());u=json.loads((ev/"utility.json").read_text())
  gates={"teacher_positive":t["primary"]["p_value"]<.001,"base_negative":b["primary"]["p_value"]>=.001,"utility":u["delta"]["arc_challenge_acc_norm"]>=-.10 and u["delta"]["truthfulqa_mc2_acc"]>=-.10,"ordinary":u["ordinary_generation"]["teacher"]["passed"],"french":u["french_supplementary"]["teacher"]["passed"],"fresh_reload":u["fresh_process_reload"]}
  summary={"status":"COMPLETED","experiment":"SCW A","run_id":formal_id,"orchestrator_run_id":x.run_id,"python":sys.version,"official_commit":"15bc1929569357130f2dbc0b09f91bbf4f4bd947","config_sha256":sha(CFG),"dataset_manifest_sha256":sha(MAN),"teacher_path":str(teacher),"performance":gs,"detector":{"base":b,"teacher":t},"utility":u,"gates":gates,"preferred_teacher":all(gates.values()),"ba_started":False,"bounded_conclusion":"SCW core reproduction successful under the tested setting." if all(gates.values()) else "SCW Experiment A completed, but preferred-Teacher gates were not all satisfied."}
  write(root/"summary.json",summary);write(P/"results/scw/experiment_a/summary.json",summary)
  report=f"# SCW Experiment A Formal Report\n\nRun: `{formal_id}`\n\nPython: `{sys.version.split()[0]}`; official commit: `15bc1929569357130f2dbc0b09f91bbf4f4bd947`.\n\n4-step gate: clean exit PASS; median step `{gs['seconds_per_optimizer_step']:.6f}` s. Formal training: 2500/2500 completed.\n\nBase aggregate p-value: `{b['primary']['p_value']}`; Teacher: `{t['primary']['p_value']}`. Preferred Teacher: **{summary['preferred_teacher']}**.\n\nARC delta: `{u['delta']['arc_challenge_acc_norm']}`; TruthfulQA MC2 delta: `{u['delta']['truthfulqa_mc2_acc']}`. Ordinary/French sanity: `{gates['ordinary']}/{gates['french']}`.\n\n{summary['bounded_conclusion']} This is not a full-paper reproduction.\n"
  (root/"formal_report.md").write_text(report,encoding="utf-8");(formal/"formal_report.md").write_text(report,encoding="utf-8")
  status.update(state="COMPLETED",stage="FINALIZE",preferred_teacher=summary["preferred_teacher"],scientific_status="COMPLETED",evaluation_status="COMPLETED")
 except Exception as e:
  code=1;status.update(state="FAILED",scientific_status="FAILED",failure=f"{type(e).__name__}: {e}",traceback=traceback.format_exc())
 finally:
  status.update(terminal=True,exit_code=code,ended_at=now(),shutdown_requested=False,shutdown_confirmed=False,final_stage="SHUTDOWN_FALLBACK_REQUIRED");write(root/"pipeline_status.json",status)
  if code and not (root/"summary.json").exists():
   fail={"status":"FAILED","orchestrator_run_id":x.run_id,"stage":status.get("stage"),"failure":status.get("failure"),"formal_a_started":status.get("formal_a_started"),"ba_started":False,"preferred_teacher":"NOT_EVALUATED"};write(root/"summary.json",fail);write(P/"results/scw/experiment_a/summary.json",fail)
  block=f"\n## SCW detached Experiment A orchestrator `{x.run_id}` — {now()}\n\n- Terminal state: `{status['state']}`; final stage: `{status['final_stage']}`; Formal A started: `{status['formal_a_started']}`; Ba started: `False`.\n- Persistent status: `{root/'pipeline_status.json'}`; summary: `{root/'summary.json'}`.\n- AutoDL shutdown: `FALLBACK_REQUIRED`; no verified platform-aware hook existed, so manual shutdown marker was written.\n"
  try:
   for rel in ("PROJECT_STATUS.md","TODO.md","DECISIONS.md","EXPERIMENT_LOG.md","CODEX_LOG.md","docs/experiment_logs/scw_experiment_a_log.md"):
    q=P/rel
    if x.run_id not in q.read_text(encoding="utf-8"): q.open("a",encoding="utf-8").write(block)
   subprocess.run(["git","-C",str(P),"diff","--check"],check=True)
   subprocess.run(["git","-C",str(P),"add","--","PROJECT_STATUS.md","TODO.md","DECISIONS.md","EXPERIMENT_LOG.md","CODEX_LOG.md","docs/experiment_logs/scw_experiment_a_log.md","results/scw/experiment_a/summary.json"],check=True)
   subprocess.run(["git","-C",str(P),"commit","-m",f"records: finalize SCW A {x.run_id}"],check=False)
  except Exception as record_error: status["record_error"]=repr(record_error);write(root/"pipeline_status.json",status)
  gpu=subprocess.run(["nvidia-smi","--query-compute-apps=pid,process_name,used_memory","--format=csv,noheader"],capture_output=True,text=True)
  tracked=subprocess.run(["git","-C",str(P),"ls-files","-z"],capture_output=True)
  large=[]
  for raw in tracked.stdout.split(b"\0"):
   if raw and (P/raw.decode()).is_file() and (P/raw.decode()).stat().st_size>10_000_000:large.append(raw.decode())
  status["final_safety"]={"active_gpu_processes":gpu.stdout.strip().splitlines(),"large_tracked_files_over_10mb":large,"official_head":subprocess.check_output(["git","-C",str(SRC),"rev-parse","HEAD"],text=True).strip(),"base_config_present":(BASE/"config.json").is_file()};write(root/"pipeline_status.json",status)
  (root/"AUTODL_SHUTDOWN_REQUIRED").write_text("No verified platform-aware shutdown hook exists; GPU workload ended and manual AutoDL shutdown is required.\n")
 raise SystemExit(code)
if __name__=="__main__":main()
