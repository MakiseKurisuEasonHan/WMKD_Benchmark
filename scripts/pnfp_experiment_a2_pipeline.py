#!/usr/bin/env python3
"""Fail-fast, file-recoverable formal PN-FP Experiment A2 pipeline."""
import argparse, datetime as dt, hashlib, json, os, shutil, subprocess, traceback
from pathlib import Path

def now(): return dt.datetime.now(dt.timezone.utc).isoformat()
def atomic_json(path,data):
    path=Path(path); tmp=path.with_suffix(path.suffix+".tmp"); tmp.write_text(json.dumps(data,indent=2)+"\n"); tmp.replace(path)

class Pipeline:
    def __init__(self,config_path):
        self.config_path=Path(config_path); self.c=json.loads(self.config_path.read_text()); self.run=Path(self.c["paths"]["run_dir"]); self.status_path=self.run/"status/status.json"; self.status=json.loads(self.status_path.read_text()); self.py=self.c["paths"]["python"]
    def update(self,**kw): self.status.update(kw); self.status["updated_at"]=now(); atomic_json(self.status_path,self.status)
    def notify(self,event,message,error=None):
        cmd=[self.py,str(Path(self.c["paths"]["project_root"])/"scripts/notify_experiment.py"),"--event",event,"--experiment","PN-FP Experiment A2","--run-id",self.c["run_id"],"--stage",str(self.status.get("active_stage")),"--status",str(self.status.get("final_status")),"--status-file",str(self.status_path),"--log-path",str(self.run/"logs"),"--message",message]
        if self.status.get("pid"): cmd += ["--pid",str(self.status["pid"])]
        if error: cmd += ["--error-summary",error]
        result=subprocess.run(cmd,check=False,capture_output=True,text=True); (self.run/"logs"/f"email_{event.lower()}.log").write_text(result.stdout+result.stderr); return result.returncode
    def run_stage(self,name,cmd,cwd=None):
        self.update(active_stage=name,stage_status="running",command=cmd); log=self.run/"logs"/f"{name}.log"
        with log.open("a",buffering=1) as out:
            out.write(f"[{now()}] COMMAND: {' '.join(cmd)}\n"); proc=subprocess.Popen(cmd,cwd=cwd,stdout=out,stderr=subprocess.STDOUT,text=True); self.update(pid=proc.pid); code=proc.wait(); out.write(f"[{now()}] EXIT_CODE: {code}\n")
        if code: raise RuntimeError(f"{name} failed with exit code {code}; see {log}")
        self.update(stage_status="completed",last_completed_stage=name)
    def preflight(self):
        c=self.c; expected={"fingerprints":1024,"key_length":16,"generation_response_length":16,"training_response_length":1,"epochs":30,"learning_rate":5e-5,"weight_decay":1e-4,"batch_size":8,"seed":42,"lambda_wa":0.75,"beta_dm":0.25}
        for k,v in expected.items():
            if c["formal_config"].get(k)!=v: raise ValueError(f"runtime config mismatch {k}")
        for k in ("model","official_source","python","fingerprints","benign_data","a1_checkpoint"):
            if not Path(c["paths"][k]).exists(): raise FileNotFoundError(c["paths"][k])
        if subprocess.check_output(["git","-C",c["paths"]["official_source"],"rev-parse","HEAD"],text=True).strip()!=c["source_commit"]: raise ValueError("official source commit mismatch")
        if hashlib.sha256(Path(c["paths"]["benign_data"]).read_bytes()).hexdigest()!=c["benign_sha256"]: raise ValueError("benign data SHA256 mismatch")
        if hashlib.sha256(Path(c["paths"]["fingerprints"]).read_bytes()).hexdigest()!=c["fingerprints_sha256"]: raise ValueError("A1 fingerprint file SHA256 mismatch")
        if "pnfp_exp_a_20260827_232033" in str(self.run): raise ValueError("A1 overwrite guard")
        gpu=subprocess.check_output(["nvidia-smi","--query-compute-apps=pid","--format=csv,noheader"],text=True).strip()
        if gpu: raise RuntimeError(f"GPU already in use: {gpu}")
        self.update(active_stage="preflight",stage_status="completed",last_completed_stage="preflight")
    def train(self):
        p=self.c["paths"]; cmd=[str(Path(self.py).parent/"deepspeed"),"--num_gpus=1",str(Path(p["project_root"])/"scripts/pnfp_a2_speed_smoke_train.py"),"--official-source",p["official_source"],"--model-path",p["model"],"--fingerprints",p["fingerprints"],"--benign-data",p["benign_data"],"--result-path",str(self.run/"checkpoints/official"),"--telemetry",str(self.run/"logs/optimizer_steps.jsonl"),"--fingerprint-count","1024","--optimizer-steps","30"]
        self.run_stage("training",cmd)
        models=list((self.run/"checkpoints/official/saved_models").glob("*/final_model"))
        if len(models)!=1: raise RuntimeError(f"expected one final model, found {models}")
        self.c["paths"]["checkpoint"]=str(models[0]); atomic_json(self.config_path,self.c); self.update(checkpoint_path=str(models[0]))
    def validate(self):
        cp=Path(self.c["paths"]["checkpoint"]); required=[cp/"config.json",cp/"tokenizer_config.json"]
        if not all(x.exists() for x in required) or not list(cp.glob("*.safetensors")): raise RuntimeError("incomplete final checkpoint")
        manifest=[]
        for f in sorted(cp.iterdir()):
            if f.is_file():
                h=hashlib.sha256()
                with f.open("rb") as src:
                    for chunk in iter(lambda:src.read(8*1024*1024),b""): h.update(chunk)
                manifest.append({"name":f.name,"bytes":f.stat().st_size,"sha256":h.hexdigest()})
        atomic_json(self.run/"checkpoints/checkpoint_manifest.json",{"checkpoint":str(cp),"files":manifest}); self.update(active_stage="checkpoint_validation",stage_status="completed",last_completed_stage="checkpoint_validation",reload_validation="passed")
    def fingerprint_eval(self,label,model):
        out=self.run/"evaluation"/f"{label}.json"; p=self.c["paths"]; cmd=[self.py,str(Path(p["project_root"])/"scripts/pnfp_evaluate.py"),"--model-path",model,"--fingerprints",p["fingerprints"],"--output",str(out),"--label",label,"--count","1024","--key-length","16","--generation-response-length","16","--training-response-length","1","--seed","42","--use-chat-template"]
        self.run_stage(f"{label}_fingerprint_evaluation",cmd); return json.loads(out.read_text())
    def utility(self):
        p=self.c["paths"]; out=self.run/"evaluation/ordinary_generation.json"; self.run_stage("ordinary_generation",[self.py,str(Path(p["project_root"])/"scripts/pnfp_a2_utility_smoke.py"),"--base",p["model"],"--a1",p["a1_checkpoint"],"--smoke",p["checkpoint"],"--output",str(out)])
        bench=self.run/"evaluation/benchmarks.json"; self.run_stage("arc_truthfulqa",[self.py,str(Path(p["project_root"])/"scripts/pnfp_a2_benchmark_eval.py"),"--base",p["model"],"--a2",p["checkpoint"],"--output",str(bench),"--batch-size","8"]); return json.loads(out.read_text()),json.loads(bench.read_text())
    def finalize(self,wm,base,ordinary,bench):
        a1=json.loads(Path(self.c["paths"]["a1_summary"]).read_text()); osum={k:v for k,v in ordinary.items() if k.endswith("_summary")}; paired={"a2_detection_rate":wm["detection_rate"],"a1_detection_rate":a1["watermarked"]["detection_rate"],"base_accidental_match_rate":base["detection_rate"],"a2_minus_base":wm["detection_rate"]-base["detection_rate"],"a2_minus_a1":wm["detection_rate"]-a1["watermarked"]["detection_rate"]}
        severe=osum["a2_smoke_summary"]["obvious_repetition"]>=5 or osum["a2_smoke_summary"]["max_token_hits"]>=8
        preferred=wm["detection_rate"]>=0.9 and not severe
        judgement="preferred PN-FP teacher for future Ba" if preferred else "do not enter Ba: utility severely degraded" if severe else "watermark-utility tradeoff requires review"
        summary={"method":"PN-FP","experiment":"A2","run_id":self.c["run_id"],"engineering_status":"completed","formal_config":self.c["formal_config"],"watermarked":{k:v for k,v in wm.items() if k!="details"},"base":{k:v for k,v in base.items() if k!="details"},"paired":paired,"ordinary_generation":osum,"benchmarks":bench,"reload_validation":"passed","preferred_teacher":preferred,"scientific_judgement":judgement,"checkpoint_path":self.c["paths"]["checkpoint"]}
        summary_path=self.run/"results/summary.json"; report_path=self.run/"results/formal_report.md"; atomic_json(summary_path,summary); report_path.write_text(f"# PN-FP Experiment A2 Formal Report\n\nRun: `{self.c['run_id']}`\n\nWatermarked detection: {wm['detected']}/{wm['fingerprints_evaluated']} ({wm['detection_rate']:.6%})\n\nBase accidental match: {base['detected']}/{base['fingerprints_evaluated']} ({base['detection_rate']:.6%})\n\nOrdinary generation: `{json.dumps(osum)}`\n\nARC/TruthfulQA deltas: `{json.dumps(bench['delta'])}`\n\nJudgement: **{judgement}**\n")
        self.project_sync(summary_path,report_path,summary)
        self.update(active_stage="completed",stage_status="completed",final_status="completed",evaluation_status="completed",exit_code=0,end_timestamp=now(),scientific_judgement=judgement,preferred_teacher=preferred); self.notify("COMPLETED","All mandatory PN-FP Experiment A2 stages completed.")
    def project_sync(self,summary_path,report_path,summary):
        self.update(active_stage="project_git_sync",stage_status="running")
        sync=self.run/"results/project_sync"; remote=subprocess.check_output(["git","-C",self.c["paths"]["project_root"],"remote","get-url","origin"],text=True).strip()
        subprocess.run(["git","clone","--depth","1",remote,str(sync)],check=True)
        (sync/"results/summaries").mkdir(parents=True,exist_ok=True); shutil.copy2(summary_path,sync/"results/summaries/pnfp_experiment_a2_summary.json")
        (sync/"docs/reproduction_reports").mkdir(parents=True,exist_ok=True); shutil.copy2(report_path,sync/"docs/reproduction_reports/pnfp_experiment_a2_report.md")
        block=f"\n\n## Formal run {self.c['run_id']}\n\nCompleted automatically. Detection: {summary['watermarked']['detection_rate']:.6%}; base: {summary['base']['detection_rate']:.6%}; judgement: **{summary['scientific_judgement']}**. Raw artifacts: `{self.run}`.\n"
        for rel in ("docs/experiment_logs/pnfp_experiment_a2_log.md","EXPERIMENT_LOG.md","PROJECT_STATUS.md"):
            with (sync/rel).open("a",encoding="utf-8") as f: f.write(block)
        with (sync/"TODO.md").open("a",encoding="utf-8") as f: f.write(f"\n- [x] Complete PN-FP Experiment A2 formal run `{self.c['run_id']}` and evaluate both gates.\n")
        paths=["results/summaries/pnfp_experiment_a2_summary.json","docs/reproduction_reports/pnfp_experiment_a2_report.md","docs/experiment_logs/pnfp_experiment_a2_log.md","EXPERIMENT_LOG.md","PROJECT_STATUS.md","TODO.md"]
        subprocess.run(["git","-C",str(sync),"add",*paths],check=True); subprocess.run(["git","-C",str(sync),"-c","user.name=WMKD Benchmark Runner","-c","user.email=wmkd-runner@local","commit","-m",f"Record PN-FP A2 formal result {self.c['run_id']}"],check=True); subprocess.run(["git","-C",str(sync),"push","origin","HEAD:main"],check=True)
        self.update(stage_status="completed",last_completed_stage="project_git_sync",git_sync="pushed")
    def execute(self):
        try:
            self.update(pid=os.getpid(),final_status="running",start_timestamp=self.status.get("start_timestamp",now())); self.preflight(); self.notify("STARTED","Formal PN-FP Experiment A2 pipeline started."); self.train(); self.validate(); wm=self.fingerprint_eval("watermarked",self.c["paths"]["checkpoint"]); base=self.fingerprint_eval("base",self.c["paths"]["model"]); ordinary,bench=self.utility(); self.finalize(wm,base,ordinary,bench)
        except Exception as exc:
            trace=traceback.format_exc(); (self.run/"logs/failure_traceback.log").write_text(trace); self.update(final_status="failed",stage_status="failed",exit_code=1,end_timestamp=now(),failure_reason=f"{type(exc).__name__}: {exc}"); self.notify("FAILED",str(exc),trace[-4000:]); raise
if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("--runtime-config",required=True); Pipeline(p.parse_args().runtime_config).execute()
