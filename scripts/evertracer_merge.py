#!/usr/bin/env python3
"""Merge a trained EverTracer LoRA adapter into a fresh canonical base on CPU."""

import argparse
import json
from pathlib import Path
import time

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

from evertracer_common import load_config, sha256_file, write_json


def main() -> None:
    p=argparse.ArgumentParser(); p.add_argument("--config",required=True); p.add_argument("--adapter",required=True)
    p.add_argument("--output",required=True); p.add_argument("--manifest",required=True); a=p.parse_args(); c=load_config(a.config)
    out=Path(a.output)
    if out.exists(): raise FileExistsError(out)
    start=time.monotonic(); base=AutoModelForCausalLM.from_pretrained(c["model"]["path"],local_files_only=True,torch_dtype=torch.bfloat16,device_map="cpu")
    merged=PeftModel.from_pretrained(base,a.adapter).merge_and_unload(); merged.save_pretrained(out,safe_serialization=True,max_shard_size="5GB")
    AutoTokenizer.from_pretrained(c["model"]["path"],local_files_only=True).save_pretrained(out)
    files=[]
    for path in sorted(p for p in out.rglob("*") if p.is_file()): files.append({"path":path.relative_to(out).as_posix(),"bytes":path.stat().st_size,"sha256":sha256_file(path)})
    write_json(a.manifest,{"base":c["model"],"adapter":str(Path(a.adapter).resolve()),"output":str(out),"elapsed_seconds":time.monotonic()-start,"files":files,"total_bytes":sum(x["bytes"] for x in files)})
    print(json.dumps({"output":str(out),"files":len(files),"total_bytes":sum(x["bytes"] for x in files)},indent=2))


if __name__=="__main__": main()
