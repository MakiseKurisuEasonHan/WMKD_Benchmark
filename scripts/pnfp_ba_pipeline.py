#!/usr/bin/env python3
"""Detached, serial and file-recoverable formal PN-FP Experiment Ba pipeline."""

import argparse, datetime as dt, hashlib, json, os, shutil, subprocess, sys, traceback
from pathlib import Path

def now(): return dt.datetime.now(dt.timezone.utc).isoformat()
def atomic(path,data):
    path=Path(path); tmp=path.with_suffix(path.suffix+".tmp"); tmp.write_text(json.dumps(data,indent=2)+"\n"); tmp.replace(path)

class Pipeline:
    def __init__(self, config_path):
        self.config_path=Path(config_path).resolve(); self.run_dir=self.config_path.parents[1]
        self.config=json.loads(self.config_path.read_text()); self.status_path=self.run_dir/"status/status.json"
        self.status=json.loads(self.status_path.read_text()); self.python=self.config["paths"]["python"]
        self.project=Path(self.config["paths"]["project_root"])
    def update(self,**kw): self.status.update(kw); self.status["updated_at"]=now(); atomic(self.status_path,self.status)
    def notify(self,event,message,error=None):
        cmd=[self.python,str(self.project/"scripts/notify_experiment.py"),"--event",event,"--experiment","PN-FP Experiment Ba",
             "--run-id",self.config["run_id"],"--stage",str(self.status.get("active_stage")),"--status",str(self.status.get("final_status")),
             "--status-file",str(self.status_path),"--log-path",str(self.run_dir/"logs"),"--message",message]
        if error: cmd += ["--error-summary",error]
        subprocess.run(cmd,check=False)
    def run(self,stage,cmd):
        self.update(active_stage=stage,stage_status="running",command=cmd)
        log=self.run_dir/"logs"/(stage+".log")
        with log.open("a",buffering=1) as out:
            out.write(f"[{now()}] COMMAND: {' '.join(cmd)}\n"); proc=subprocess.Popen(cmd,stdout=out,stderr=subprocess.STDOUT,text=True)
            self.update(pid=proc.pid); code=proc.wait(); out.write(f"[{now()}] EXIT_CODE: {code}\n")
        if code: raise RuntimeError(f"{stage} failed with exit code {code}; see {log}")
        self.update(stage_status="completed",last_completed_stage=stage)
    def preflight(self):
        c=self.config; required=["teacher","student","fingerprints","python"]
        for key in required:
            if not Path(c["paths"][key]).exists(): raise FileNotFoundError(f"missing {key}: {c['paths'][key]}")
        if c["formal_config"] != {"samples":20000,"epochs":3,"learning_rate":1e-5,"precision":"bf16","full_parameter":True,"lora":False,"seed":42,"batch_size":8}:
            raise ValueError("formal config mismatch")
        if subprocess.run(["nvidia-smi","--query-compute-apps=pid","--format=csv,noheader"],capture_output=True,text=True).stdout.strip():
            raise RuntimeError("another GPU compute process is active")
        self.update(active_stage="preflight",stage_status="completed",last_completed_stage="preflight")
    def generate(self):
        raw=self.run_dir/"dataset/raw_candidates.jsonl"; errors=self.run_dir/"dataset/generation_errors.jsonl"
        target=24000
        while True:
            self.run("teacher_qa_generation",[self.python,str(self.project/"scripts/generate_teacher_qa_formal.py"),"--model-path",self.config["paths"]["teacher"],"--output",str(raw),"--errors",str(errors),"--target-candidates",str(target),"--batch-size","8","--seed","42"])
            provenance=self.run_dir/"config/dataset_provenance.json"
            atomic(provenance,{"teacher_checkpoint":self.config["paths"]["teacher"],"teacher_run_id":"pnfp_exp_a_20260827_232033","seed":42,"raw_candidates":sum(1 for _ in raw.open()),"config":self.config["formal_config"]})
            frozen=self.run_dir/"dataset/frozen_qa.jsonl"; manifest=self.run_dir/"dataset/manifest.json"
            cmd=[self.python,str(self.project/"scripts/generate_distillation_qa.py"),"--raw-candidates",str(raw),"--output",str(frozen),"--manifest",str(manifest),"--target-count","20000","--provenance",str(provenance)]
            proc=subprocess.run(cmd,capture_output=True,text=True)
            (self.run_dir/"logs/dataset_freeze.log").write_text(proc.stdout+proc.stderr)
            if proc.returncode==0: break
            target += 2000
            if target>40000: raise RuntimeError("could not obtain 20,000 valid unique QA samples")
        m=json.loads(manifest.read_text()); self.update(dataset_path=str(frozen),dataset_manifest=str(manifest),dataset_sha256=m["dataset_sha256"],dataset_count=m["sample_count"])
    def train(self):
        bs=self.config["formal_config"]["batch_size"]; oom_attempts=[]
        for attempt_bs in (bs,4,2):
            out=self.run_dir/"checkpoints"/f"student_batch_{attempt_bs}"
            stage=f"training_batch_{attempt_bs}"
            try:
                self.run(stage,[self.python,str(self.project/"scripts/train_distillation_student.py"),"--model-path",self.config["paths"]["student"],"--dataset",self.status["dataset_path"],"--output-dir",str(out),"--batch-size",str(attempt_bs),"--epochs","3","--learning-rate","1e-5","--seed","42"])
                bs=attempt_bs; break
            except RuntimeError:
                log_path=self.run_dir/"logs"/(stage+".log"); log=log_path.read_text(errors="replace")
                if "out of memory" not in log.lower() and "cuda oom" not in log.lower(): raise
                oom_attempts.append({"batch_size":attempt_bs,"log":str(log_path),"time":now()})
                self.update(oom_attempts=oom_attempts)
        else: raise RuntimeError("CUDA OOM at all authorized batch sizes 8, 4 and 2")
        checkpoint=out/"final_model"
        if not (checkpoint/"config.json").exists() or not list(checkpoint.glob("*.safetensors")): raise RuntimeError("incomplete final checkpoint")
        self.update(checkpoint_path=str(checkpoint),actual_batch_size=bs,oom_occurred=bool(oom_attempts))
    def reload(self):
        code="""from transformers import AutoTokenizer,AutoModelForCausalLM; import torch,sys; p=sys.argv[1]; t=AutoTokenizer.from_pretrained(p,local_files_only=True); m=AutoModelForCausalLM.from_pretrained(p,local_files_only=True,torch_dtype=torch.bfloat16).cuda().eval(); x=t('reload validation',return_tensors='pt').to('cuda'); m.generate(**x,max_new_tokens=1); print('RELOAD_OK')"""
        self.run("reload_validation",[self.python,"-c",code,self.status["checkpoint_path"]]); self.update(reload_validation="passed")
    def pnfp_eval(self,label,model):
        out=self.run_dir/"evaluation"/(label+"_pnfp.json")
        self.run(label+"_pnfp_evaluation",[self.python,str(self.project/"scripts/pnfp_evaluate.py"),"--model-path",model,"--fingerprints",self.config["paths"]["fingerprints"],"--output",str(out),"--label",label,"--count","1024","--key-length","16","--generation-response-length","16","--training-response-length","1","--seed","42","--use-chat-template"])
        return json.loads(out.read_text())
    def utility(self,label,model):
        out=self.run_dir/"evaluation"/(label+"_utility")
        self.run(label+"_utility_evaluation",[self.python,"-m","lm_eval","--model","hf","--model_args",f"pretrained={model},dtype=bfloat16","--tasks","arc_challenge,truthfulqa_mc1,truthfulqa_mc2","--batch_size","auto","--output_path",str(out)])
        return str(out)
    def finalize(self,original,student,orig_util,student_util):
        teacher_rate=0.9951171875; ba_rate=student["detection_rate"]
        summary={"method":"PN-FP","experiment":"Ba","run_id":self.config["run_id"],"engineering_status":"completed",
          "teacher":{"run_id":"pnfp_exp_a_20260827_232033","checkpoint":self.config["paths"]["teacher"],"watermark_result":{"detected":1019,"total":1024,"detection_rate":teacher_rate}},
          "student_initialization":{"model_id":"meta-llama/Llama-3.2-1B-Instruct","revision":"9213176726f574b556790deb65791e0c5aa438b6"},
          "dataset_size":self.status["dataset_count"],"dataset_manifest_sha256":self.status["dataset_sha256"],"distillation_config":self.config["formal_config"],
          "original_student_watermark":{k:v for k,v in original.items() if k!="details"},"watermark_detection":{k:v for k,v in student.items() if k!="details"},
          "watermark_retention":{"teacher_to_ba_absolute_drop":teacher_rate-ba_rate,"ba_vs_original_difference":ba_rate-original["detection_rate"],"retention_ratio":ba_rate/teacher_rate},
          "utility":{"original_results_path":orig_util,"ba_results_path":student_util},"reload_validation":"passed","checkpoint_path":self.status["checkpoint_path"],
          "scientific_judgement":"Pending utility metric extraction: jointly interpret PN-FP retention and knowledge transfer."}
        atomic(self.run_dir/"results/summary.json",summary)
        (self.run_dir/"results/formal_report.md").write_text("# PN-FP Experiment Ba formal report\n\nMachine-readable results: `summary.json`. Utility raw outputs are preserved under `evaluation/`. Scientific judgement must jointly assess watermark retention and utility transfer.\n")
        self.update(active_stage="completed",stage_status="completed",final_status="completed",evaluation_status="completed",exit_code=0,end_timestamp=now(),summary_path=str(self.run_dir/"results/summary.json"))
        self.notify("COMPLETED","All formal PN-FP Experiment Ba stages completed.")
    def execute(self):
        try:
            self.update(pid=os.getpid(),final_status="running"); self.notify("STARTED","Formal PN-FP Experiment Ba started.")
            self.preflight(); self.generate(); self.train(); self.reload()
            original=self.pnfp_eval("original_1b",self.config["paths"]["student"]); student=self.pnfp_eval("ba_student",self.status["checkpoint_path"])
            orig_util=self.utility("original_1b",self.config["paths"]["student"]); student_util=self.utility("ba_student",self.status["checkpoint_path"])
            self.finalize(original,student,orig_util,student_util)
        except Exception as exc:
            trace=traceback.format_exc(); (self.run_dir/"logs/failure_traceback.log").write_text(trace)
            self.update(stage_status="failed",final_status="failed",exit_code=1,end_timestamp=now(),failure_reason=f"{type(exc).__name__}: {exc}")
            self.notify("FAILED",str(exc),"\n".join(trace.splitlines()[-25:])); raise

if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("--runtime-config",required=True); Pipeline(p.parse_args().runtime_config).execute()
