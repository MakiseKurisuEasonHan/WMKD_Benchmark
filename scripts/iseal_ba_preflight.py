#!/usr/bin/env python3
import argparse,hashlib,json
from pathlib import Path
import yaml
REV="0cb88a4f764b7a12671c53f0838cd831a0843b95"; TEACHER_RUN="iseal_a6_20260830_132300"; MANIFEST="a68fff13eb0add1f64634e50235a232c3f00fcdcf5d543db942e40a5f3b7bbe9"
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument("--config",required=True);p.add_argument("--output");a=p.parse_args();c=yaml.safe_load(Path(a.config).read_text());t=Path(c["teacher"]["checkpoint"]);base=Path(c["model"]["path"])
 expected={"epochs":3,"learning_rate":1e-5,"precision":"bf16","full_parameter":True,"lora":False,"batch_size":8,"gradient_accumulation_steps":1,"max_length":1024}
 if c["teacher"]["run_id"]!=TEACHER_RUN or c["teacher"]["registered_manifest_sha256"]!=MANIFEST:raise ValueError("A6 Teacher provenance mismatch")
 if c["training"]!=expected or c["model"]["revision"]!=REV:raise ValueError("standardized Ba config mismatch")
 shards=sorted(t.glob("model-*-of-*.safetensors"));
 if len(shards)!=8 or not (t/"model.safetensors.index.json").is_file() or not (t/"config.json").is_file():raise FileNotFoundError("A6 merged Teacher incomplete")
 if not (base/"config.json").is_file() or len(list(base.glob("model-*-of-*.safetensors")))!=2:raise FileNotFoundError("canonical fresh Student base incomplete")
 result={"status":"READY","teacher":{"run_id":TEACHER_RUN,"checkpoint":str(t),"shard_count":len(shards),"total_shard_bytes":sum(x.stat().st_size for x in shards),"config_sha256":sha(t/"config.json"),"index_sha256":sha(t/"model.safetensors.index.json")},"student":{"fresh_canonical":True,"path":str(base),"revision":REV},"dataset_protocol":c["dataset"],"training":expected}
 if a.output:Path(a.output).write_text(json.dumps(result,indent=2)+"\n")
 print(json.dumps(result,indent=2))
if __name__=="__main__":main()
