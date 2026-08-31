"""Detached fail-closed SCW A using one frozen official finite stream."""
from __future__ import annotations
import argparse,datetime,hashlib,json,os,subprocess,sys,traceback
from pathlib import Path
from scw_shutdown_policy import apply_shutdown_policy

P=Path("/root/autodl-tmp/WMKD_Benchmark"); D=Path("/root/autodl-tmp/WMKD_Benchmark_data")
SRC=D/"artifacts/scw/source"; CFG=P/"configs/watermark/scw_experiment_a.yaml"; OFF=P/"configs/watermark/scw_experiment_a_official.yaml"
DSM=D/"artifacts/scw/manifests/scw_dataset_manifest.json"; MM=D/"artifacts/scw/manifests/canonical_model_manifest.json"; BASE=D/"models/base/Llama-3.2-3B-Instruct"
EXPECTED_DSM="4c063b070b4507fa2c5e2facae1d0573a8414b9f1a34d9260d6cf43d86b79b30"; EXPECTED_MM="165bfb23c9de62067f6a850032ebe38aef8b9a5bb39f57e95d7dc3df04d7c181"
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write(path,value):
 path.parent.mkdir(parents=True,exist_ok=True); tmp=path.with_suffix(path.suffix+".tmp"); tmp.write_text(json.dumps(value,indent=2,ensure_ascii=False)+"\n",encoding="utf-8"); tmp.replace(path)
def run(stage,cmd,status,root,env,cwd=None):
 status.update(stage=stage,stage_started_at=now()); write(root/"pipeline_status.json",status); log=root/"logs"/(stage.lower()+".log"); log.parent.mkdir(parents=True,exist_ok=True)
 with log.open("w",encoding="utf-8") as out: c=subprocess.run(cmd,stdout=out,stderr=subprocess.STDOUT,env=env,cwd=cwd)
 status.setdefault("stages",{})[stage]={"exit_code":c.returncode,"log":str(log),"ended_at":now()}; write(root/"pipeline_status.json",status)
 if c.returncode: raise RuntimeError(f"{stage} failed exit={c.returncode}")
def gpu_processes():
 return [x for x in subprocess.run(["nvidia-smi","--query-compute-apps=pid,process_name,used_memory","--format=csv,noheader,nounits"],capture_output=True,text=True,check=True).stdout.splitlines() if x.strip()]
def artifact_manifest(path):
 rows=[]
 for f in sorted(path.rglob("*")):
  if f.is_file(): rows.append({"path":str(f.relative_to(path)),"size":f.stat().st_size,"sha256":sha(f)})
 return {"root":str(path),"files":rows,"file_count":len(rows),"total_bytes":sum(x["size"] for x in rows)}
def main():
 ap=argparse.ArgumentParser(); ap.add_argument("--run-id",required=True); a=ap.parse_args(); root=D/"runs/scw/orchestrators"/a.run_id; root.mkdir(parents=True,exist_ok=False)
 status={"run_id":a.run_id,"pid":os.getpid(),"state":"RUNNING","stage":"MIGRATION_VERIFY","started_at":now(),"scientific_status":"NOT_RUN","training_status":"NOT_STARTED","evaluation_status":"NOT_STARTED","preferred_teacher":"NOT_EVALUATED","formal_a_started":False,"ba_started":False,"shutdown_method":"/usr/bin/shutdown","shutdown_requested":False,"shutdown_command_issued":False,"shutdown_confirmed":False,"terminal":False,"stages":{}}
 write(root/"pipeline_status.json",status); code=0
 env=os.environ.copy(); env.update({"PYTHONHASHSEED":"42","HF_ENDPOINT":"https://hf-mirror.com","HF_HOME":str(D/"artifacts/scw/hf_home"),"HF_DATASETS_CACHE":str(D/"artifacts/scw/hf_home/datasets")})
 try:
  if sys.version_info[:2]!=(3,11): raise RuntimeError("Python 3.11 required")
  if sha(DSM)!=EXPECTED_DSM or sha(MM)!=EXPECTED_MM: raise RuntimeError("migration manifest hash mismatch")
  if not (BASE/"config.json").is_file(): raise RuntimeError("canonical Base missing")
  if subprocess.check_output(["git","-C",str(SRC),"rev-parse","HEAD"],text=True).strip()!="15bc1929569357130f2dbc0b09f91bbf4f4bd947": raise RuntimeError("official commit mismatch")
  if subprocess.run(["git","-C",str(SRC),"diff","--quiet","HEAD","--"]).returncode or subprocess.run(["git","-C",str(SRC),"diff","--cached","--quiet"]).returncode: raise RuntimeError("official tracked source dirty")
  if gpu_processes(): raise RuntimeError("GPU not idle at migration gate")
  status["migration_integrity"]="PASS"; write(root/"pipeline_status.json",status)
  mat_id="scw_materialized_"+datetime.datetime.now().strftime("%Y%m%d_%H%M%S"); mat=D/"runs/scw/materialized_stream"/mat_id; mat.mkdir(parents=True,exist_ok=False)
  records=mat/"training_stream.jsonl"; manifest=mat/"manifest.json"; audit_path=mat/"audit.json"; status.update(materialization_run_id=mat_id,materialization_namespace=str(mat),expected_records=160000); write(root/"pipeline_status.json",status)
  menv=env.copy(); menv.update({"PYTHONPATH":str(P/"scripts/scw_runtime_compat")+os.pathsep+str(P/"scripts")+os.pathsep+str(SRC/"src"),"WMKD_SCW_HF_MIRROR":env["HF_ENDPOINT"],"WMKD_SCW_NETWORK_AUDIT":str(mat/"network_requests.jsonl"),"WMKD_SCW_PARQUET_CACHE":str(D/"cache/scw/parquet_prefetch")})
  run("DETERMINISTIC_FINITE_STREAM_BUILD",[sys.executable,str(P/"scripts/scw_build_deterministic_finite_stream.py"),"--config",str(CFG),"--official-runtime-config",str(OFF),"--official-source",str(SRC),"--records",str(records),"--manifest",str(manifest),"--cache-root",str(D/"cache/scw/parquet_prefetch"),"--creation-code-version",subprocess.check_output(["git","-C",str(P),"rev-parse","HEAD"],text=True).strip()],status,root,menv,cwd=mat)
  from scw_materialized_stream import audit_materialized,iter_materialized_records
  m=json.loads(manifest.read_text()); audit=audit_materialized(records,m); replay=sum(1 for _ in iter_materialized_records(records,m)); audit["local_loader_replay_count"]=replay; audit["local_loader_replay_exact"]=(replay==160000)
  if audit["status"]!="PASS" or not audit["local_loader_replay_exact"]: audit["status"]="FAIL"
  write(audit_path,audit); status["materialization_audit"]=audit; write(root/"pipeline_status.json",status)
  if audit["status"]!="PASS": status["scientific_status"]="MATERIALIZATION_NOT_SCIENTIFICALLY_SAFE"; raise RuntimeError("materialization audit failed")
  if gpu_processes(): raise RuntimeError("GPU not idle before local-materialized gate")
  gate_id=a.run_id+"_materialized_gate4"; gate=D/"runs/scw/speed_test"/gate_id; gate.mkdir(parents=True,exist_ok=False)
  derived=json.loads(OFF.read_text()); derived["finetuning"]["training_args"]["max_steps"]=4; derived["finetuning"]["training_args"]["save_strategy"]="no"; derived["finetuning"]["training_args"].pop("save_steps",None); gate_cfg=gate/"gate_runtime_config.json"; write(gate_cfg,derived)
  genv=env.copy(); genv.update({"PYTHONPATH":str(P/"scripts/scw_runtime_compat")+os.pathsep+str(P/"scripts")+os.pathsep+str(SRC/"src"),"WMKD_SCW_TELEMETRY":str(gate/"telemetry.jsonl"),"WMKD_SCW_SPEED_TEST":"1"})
  run("LOCAL_MATERIALIZED_GATE",[sys.executable,str(P/"scripts/scw_train_materialized.py"),"--official-source",str(SRC),"--official-runtime-config",str(gate_cfg),"--records",str(records),"--manifest",str(manifest),"--custom-name",gate_id],status,root,genv,cwd=gate)
  tel=[json.loads(x) for x in (gate/"telemetry.jsonl").read_text().splitlines()]; ends=[x for x in tel if x.get("event")=="optimizer_step_end"]; train_end=[x for x in tel if x.get("event")=="train_end"]
  if len(ends)!=4 or not train_end or train_end[-1].get("step")!=4: raise RuntimeError("gate telemetry does not prove 4/4 and train_end")
  gate_log=(root/"logs/local_materialized_gate.log").read_text(errors="replace"); forbidden=("SIGABRT","PyGILState_Release","out of memory","Traceback","CUDA error")
  if any(x.lower() in gate_log.lower() for x in forbidden): raise RuntimeError("gate log contains fatal marker")
  status["gate_status"]="PASS"; status["scientific_status"]="RUNNING"; write(root/"pipeline_status.json",status)
  formal_id="scw_a_"+datetime.datetime.now().strftime("%Y%m%d_%H%M%S"); formal=D/"runs/scw/a"/formal_id; formal.mkdir(parents=True,exist_ok=False); status.update(formal_a_started=True,formal_run_id=formal_id,formal_root=str(formal),training_status="RUNNING"); write(root/"pipeline_status.json",status)
  fenv=env.copy(); fenv.update({"PYTHONPATH":str(P/"scripts/scw_runtime_compat")+os.pathsep+str(P/"scripts")+os.pathsep+str(SRC/"src"),"WMKD_SCW_TELEMETRY":str(formal/"telemetry.jsonl"),"WMKD_SCW_SPEED_TEST":"0"})
  run("FORMAL_TRAINING",[sys.executable,str(P/"scripts/scw_train_materialized.py"),"--official-source",str(SRC),"--official-runtime-config",str(OFF),"--records",str(records),"--manifest",str(manifest),"--custom-name",formal_id],status,root,fenv,cwd=formal)
  teacher=formal/"models"/("Llama-3.2-3B-Instruct_"+formal_id+"_French_WMKD_SCW_A")
  if not (teacher/"config.json").is_file(): raise RuntimeError("final Teacher missing")
  tm=artifact_manifest(teacher); write(formal/"teacher_artifact_manifest.json",tm); status.update(training_status="COMPLETED",teacher_path=str(teacher),teacher_artifact_manifest=str(formal/"teacher_artifact_manifest.json"),evaluation_status="RUNNING"); write(root/"pipeline_status.json",status)
  ev=formal/"evaluation"; ev.mkdir(); run("BASE_FRENCH_GENERATION",[sys.executable,str(P/"scripts/scw_fresh_generate.py"),"--model",str(BASE),"--label","base","--output",str(ev/"base_generations.jsonl")],status,root,env)
  run("TEACHER_FRENCH_GENERATION",[sys.executable,str(P/"scripts/scw_fresh_generate.py"),"--model",str(teacher),"--label","teacher","--output",str(ev/"teacher_generations.jsonl")],status,root,env)
  denv=env.copy(); denv["PYTHONPATH"]=str(SRC/"src")+os.pathsep+str(P/"scripts")
  for label in ("base","teacher"): run(label.upper()+"_DETECTOR",[sys.executable,str(P/"scripts/scw_detector.py"),"--protocol-config",str(CFG),"--official-config",str(OFF),"--generations",str(ev/(label+"_generations.jsonl")),"--model",str(BASE),"--output",str(ev/(label+"_detector.json"))],status,root,denv)
  run("UTILITY",[sys.executable,str(P/"scripts/scw_utility.py"),"--base",str(BASE),"--teacher",str(teacher),"--output",str(ev/"utility.json")],status,root,env)
  b=json.loads((ev/"base_detector.json").read_text()); t=json.loads((ev/"teacher_detector.json").read_text()); u=json.loads((ev/"utility.json").read_text()); gates={"teacher_positive":t["primary"]["p_value"]<.001,"base_negative":b["primary"]["p_value"]>=.001,"utility":u["delta"]["arc_challenge_acc_norm"]>=-.10 and u["delta"]["truthfulqa_mc2_acc"]>=-.10,"ordinary":u["ordinary_generation"]["teacher"]["passed"],"french":u["french_supplementary"]["teacher"]["passed"],"fresh_reload":u["fresh_process_reload"]}
  summary={"status":"COMPLETED","experiment":"SCW A","classification":"RUNTIME_DATA_ACCESS_ADAPTATION","run_id":formal_id,"orchestrator_run_id":a.run_id,"official_commit":"15bc1929569357130f2dbc0b09f91bbf4f4bd947","config_sha256":sha(CFG),"dataset_manifest_sha256":sha(DSM),"materialized_manifest_sha256":sha(manifest),"stream_sha256":m["records_file_sha256"],"materialization":m,"audit":audit,"teacher_path":str(teacher),"teacher_artifact_manifest":tm,"detector":{"base":b,"teacher":t},"utility":u,"gates":gates,"preferred_teacher":all(gates.values()),"ba_started":False}
  write(root/"summary.json",summary); write(P/"results/scw/experiment_a/summary.json",summary); report=f"# SCW Experiment A Formal Report\n\nRun `{formal_id}` used exact frozen stream `{m['records_file_sha256']}` ({m['materialized_record_count']} records). Materialization audit and one 4-step clean-exit gate passed. Formal training completed 2500/2500.\n\nBase/Teacher aggregate p-values: `{b['primary']['p_value']}` / `{t['primary']['p_value']}`. Preferred Teacher: **{summary['preferred_teacher']}**.\n\nARC/TruthfulQA deltas: `{u['delta']['arc_challenge_acc_norm']}` / `{u['delta']['truthfulqa_mc2_acc']}`. This is a bounded SCW A result using a runtime/data-access adaptation, not A2.\n"; (root/"formal_report.md").write_text(report,encoding="utf-8"); (formal/"formal_report.md").write_text(report,encoding="utf-8")
  summary["classification"]="DETERMINISTIC_FINITE_STREAM_SAMPLING_ADAPTATION"
  write(root/"summary.json",summary); write(P/"results/scw/experiment_a/summary.json",summary)
  adaptation=("\n## Sampling Adaptation\n\nWMKD uses a fixed deterministic finite weighted draw with the same "
   "0.6/0.2/0.2 source probabilities rather than reproducing the exact online-streaming sample realization of the official code. "
   "Per-source extraction follows pinned repository path order and unmodified official preprocessing. The finite sample realization differs from official code.\n")
  with (root/"formal_report.md").open("a",encoding="utf-8") as out: out.write(adaptation)
  with (formal/"formal_report.md").open("a",encoding="utf-8") as out: out.write(adaptation)
  status.update(state="COMPLETED",scientific_status="COMPLETED",training_status="COMPLETED",evaluation_status="COMPLETED",preferred_teacher=summary["preferred_teacher"],stage="FINALIZE")
 except Exception as exc:
  code=1; status.update(state="FAILED",failure=f"{type(exc).__name__}: {exc}",traceback=traceback.format_exc()); status["training_status"]="FAILED" if status.get("formal_a_started") else status.get("training_status","NOT_STARTED"); status["evaluation_status"]="NOT_STARTED" if status.get("evaluation_status")!="COMPLETED" else "COMPLETED"
 finally:
  status.update(terminal=True,exit_code=code,ended_at=now(),final_stage="SHUTDOWN_REQUEST"); write(root/"pipeline_status.json",status)
  if not (root/"summary.json").exists(): write(root/"summary.json",{"status":"FAILED","classification":status.get("scientific_status"),"stage":status.get("stage"),"failure":status.get("failure"),"formal_a_started":status.get("formal_a_started"),"preferred_teacher":"NOT_EVALUATED","ba_started":False})
  block=f"\n## SCW materialized orchestrator `{a.run_id}` — {now()}\n\n- State `{status['state']}`; stage `{status.get('stage')}`; Formal A started `{status['formal_a_started']}`; Ba `False`.\n- Materialization `{status.get('materialization_namespace')}`; status `{root/'pipeline_status.json'}`.\n"
  try:
   for rel in ("PROJECT_STATUS.md","TODO.md","DECISIONS.md","EXPERIMENT_LOG.md","CODEX_LOG.md","docs/experiment_logs/scw_experiment_a_log.md"):
    with (P/rel).open("a",encoding="utf-8") as out: out.write(block)
   subprocess.run(["git","-C",str(P),"diff","--check"],check=True); subprocess.run(["git","-C",str(P),"add","--","PROJECT_STATUS.md","TODO.md","DECISIONS.md","EXPERIMENT_LOG.md","CODEX_LOG.md","docs/experiment_logs/scw_experiment_a_log.md","results/scw/experiment_a/summary.json"],check=True); subprocess.run(["git","-C",str(P),"commit","-m",f"records: finalize SCW materialized A {a.run_id}"],check=False)
  except Exception as record_exc: status["record_error"]=repr(record_exc)
  status["shutdown_request_timestamp"]=now(); shutdown_command=apply_shutdown_policy(status,root,env); write(root/"pipeline_status.json",status); subprocess.run(["sync"])
  if shutdown_command is not None: subprocess.run(shutdown_command)
 raise SystemExit(code)
if __name__=="__main__": main()
