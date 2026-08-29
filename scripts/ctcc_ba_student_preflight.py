#!/usr/bin/env python3
"""Minimal fail-closed preflight for CTCC Ba Student training."""
import argparse,hashlib,json,shutil
from pathlib import Path
REV="0cb88a4f764b7a12671c53f0838cd831a0843b95";DATASET_SHA="621c9aedcf3a4a1db86a4848bbf93fa893d18022f15b913e8aeeb28739412484";TEACHER_SHA="36957869183ee2581c7377ba973de0aef4d162c7caa3a2353684cf931ae429cd"
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 import yaml
 p=argparse.ArgumentParser();p.add_argument("--config",required=True);p.add_argument("--generation-run",required=True);p.add_argument("--output");a=p.parse_args();c=yaml.safe_load(Path(a.config).read_text());g=Path(a.generation_run);status=json.loads((g/"status/status.json").read_text());manifest=json.loads((g/"dataset/manifest.json").read_text());frozen=g/"dataset/frozen_qa.jsonl";base=Path(c["model"]["path"]);teacher=Path(c["teacher"]["adapter"])/"adapter_model.safetensors"
 expected={"epochs":3,"learning_rate":1e-5,"precision":"bf16","full_parameter":True,"lora":False,"batch_size":8,"gradient_accumulation_steps":1,"max_length":1024}
 if status.get("status")!="COMPLETED" or status.get("frozen_count")!=20000 or status.get("frozen_sha256")!=DATASET_SHA:raise ValueError("generation/freeze terminal gate failed")
 if manifest.get("sample_count")!=20000 or manifest.get("dataset_sha256")!=DATASET_SHA or sum(1 for _ in frozen.open(encoding="utf-8"))!=20000:raise ValueError("frozen exactly-20k gate failed")
 if c["training"]!=expected or c["model"]["revision"]!=REV:raise ValueError("standard training/base revision mismatch")
 if sha(teacher)!=TEACHER_SHA:raise ValueError("teacher provenance changed")
 if not (base/"config.json").is_file() or not (base/"model-00001-of-00002.safetensors").is_file():raise FileNotFoundError("canonical base incomplete")
 result={"status":"READY","generation_run":g.name,"frozen_path":str(frozen),"frozen_count":20000,"frozen_dataset_sha256":DATASET_SHA,"frozen_file_sha256":sha(frozen),"teacher_adapter_sha256":TEACHER_SHA,"student_initialization":{"fresh_canonical":True,"path":str(base),"revision":REV},"training":expected,"formal_steps":7500,"free_bytes":shutil.disk_usage(base).free}
 if a.output:Path(a.output).write_text(json.dumps(result,indent=2)+"\n")
 print(json.dumps(result,indent=2))
if __name__=="__main__":main()
