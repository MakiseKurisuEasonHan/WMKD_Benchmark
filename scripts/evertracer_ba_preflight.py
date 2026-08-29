#!/usr/bin/env python3
"""Fail-closed immutable-artifact and protocol preflight for EverTracer Ba."""
import argparse,hashlib,json,shutil
from pathlib import Path
import yaml
def sha(p):
 h=hashlib.sha256();
 with p.open("rb") as f:
  for b in iter(lambda:f.read(1048576),b""):h.update(b)
 return h.hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument("--config",required=True);p.add_argument("--output");a=p.parse_args();c=yaml.safe_load(Path(a.config).read_text());t=c["training"]
 assert c["distillation_experiment"]=="Ba" and c["dataset"]["final_samples"]==20000
 assert t=={"epochs":3,"learning_rate":1e-5,"precision":"bf16","full_parameter":True,"lora":False,"batch_size":8,"gradient_accumulation_steps":1,"max_length":1024}
 paths={"teacher":c["teacher"]["checkpoint"],"reference":c["reference"]["checkpoint"],"student":c["student"]["path"],"neighborhoods":c["verification"]["neighborhoods"],"a_summary":c["prior_a"]["summary"]};missing=[f"{k}:{v}" for k,v in paths.items() if not Path(v).exists()]
 if missing:raise FileNotFoundError("; ".join(missing))
 actual=sha(Path(paths["neighborhoods"]));assert actual==c["verification"]["neighborhoods_sha256"]
 free=shutil.disk_usage(c["runtime"]["data_root"]).free;result={"status":"READY","paths":paths,"neighborhoods_sha256":actual,"data_disk_free_bytes":free,"minimum_required_free_bytes":80_000_000_000,"disk_gate":free>=80_000_000_000}
 if not result["disk_gate"]:raise RuntimeError("data disk has less than 80 GB free")
 if a.output:Path(a.output).write_text(json.dumps(result,indent=2)+"\n")
 print(json.dumps(result,indent=2))
if __name__=="__main__":main()
