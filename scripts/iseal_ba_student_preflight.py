#!/usr/bin/env python3
import argparse,hashlib,json,shutil
from pathlib import Path
import yaml
REV="0cb88a4f764b7a12671c53f0838cd831a0843b95"
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument("--config",required=True);p.add_argument("--generation-run",required=True);p.add_argument("--output");a=p.parse_args();c=yaml.safe_load(Path(a.config).read_text());g=Path(a.generation_run);status=json.loads((g/"status/status.json").read_text());manifest=json.loads((g/"dataset/manifest.json").read_text());frozen=g/"dataset/frozen_qa.jsonl";base=Path(c["model"]["path"])
 expected={"epochs":3,"learning_rate":1e-5,"precision":"bf16","full_parameter":True,"lora":False,"batch_size":8,"gradient_accumulation_steps":1,"max_length":1024}
 if status.get("status")!="COMPLETED" or status.get("frozen_count")!=20000 or status.get("frozen_sha256")!=manifest.get("dataset_sha256"):raise ValueError("generation/freeze terminal gate failed")
 if manifest.get("sample_count")!=20000 or sum(1 for _ in frozen.open(encoding="utf-8"))!=20000:raise ValueError("frozen exactly-20k gate failed")
 if c["training"]!=expected or c["model"]["revision"]!=REV:raise ValueError("standard training/base revision mismatch")
 if not (base/"config.json").is_file() or len(list(base.glob("model-*-of-*.safetensors")))!=2:raise FileNotFoundError("canonical base incomplete")
 result={"status":"READY","generation_run":g.name,"frozen_path":str(frozen),"frozen_count":20000,"frozen_dataset_sha256":manifest["dataset_sha256"],"frozen_file_sha256":sha(frozen),"student_initialization":{"fresh_canonical":True,"path":str(base),"revision":REV},"training":expected,"formal_steps":7500,"free_bytes":shutil.disk_usage(base).free}
 if a.output:Path(a.output).write_text(json.dumps(result,indent=2)+"\n")
 print(json.dumps(result,indent=2))
if __name__=="__main__":main()
