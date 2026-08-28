#!/usr/bin/env python3
"""Freeze T5-Base symmetric semantic neighborhoods for EverTracer verification."""

import argparse, json, math, random, time
from pathlib import Path
import numpy as np
import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from evertracer_common import configure_cache, load_config, sha256_file, write_json


def mask_text(text, fraction, span_length, buffer, rng):
    words=text.split(); target=max(1,math.floor(len(words)*fraction)); spans=max(1,target//span_length); occupied=set(); starts=[]
    candidates=list(range(max(1,len(words)-span_length+1))); rng.shuffle(candidates)
    for start in candidates:
        region=set(range(max(0,start-buffer),min(len(words),start+span_length+buffer)))
        if not region & occupied: starts.append(start); occupied.update(region)
        if len(starts)>=spans: break
    for mask_id,start in sorted(enumerate(starts),key=lambda x:x[1],reverse=True): words[start:start+span_length]=[f"<extra_id_{mask_id}>"]
    # Re-number after reverse replacement according to left-to-right order.
    n=0
    for i,w in enumerate(words):
        if w.startswith("<extra_id_"): words[i]=f"<extra_id_{n}>"; n+=1
    return " ".join(words),n


def extract(masked, generated, count):
    import re
    pieces=re.split(r"<extra_id_\d+>",generated.replace("<pad>","").replace("</s>",""))[1:]
    fills=[x.strip() for x in pieces[:count]]
    if len(fills)<count: return None
    words=masked.split()
    for i in range(count):
        token=f"<extra_id_{i}>"
        if token not in words: return None
        words[words.index(token)]=fills[i]
    return " ".join(words)


def main():
    p=argparse.ArgumentParser(); p.add_argument("--config",required=True);p.add_argument("--dataset-root",required=True);p.add_argument("--output",required=True);p.add_argument("--limit",type=int);a=p.parse_args()
    c=load_config(a.config);configure_cache(c["runtime"]["data_root"]);v=c["verification"]; rng=random.Random(c["seed"]);np.random.seed(c["seed"]);torch.manual_seed(c["seed"])
    revision=None if str(v["t5_revision"]).startswith("TO_BE_") else v["t5_revision"]
    tok=AutoTokenizer.from_pretrained(v["t5_model"],revision=revision);model=AutoModelForSeq2SeqLM.from_pretrained(v["t5_model"],revision=revision,torch_dtype=torch.bfloat16).cuda().eval()
    records=[];start=time.monotonic(); generation_count=0
    for subset in ("dtr","dunseen"):
        rows=[json.loads(x) for x in (Path(a.dataset_root)/f"{subset}.jsonl").read_text(encoding="utf-8").splitlines() if x]
        if a.limit: rows=rows[:a.limit]
        for row in rows:
            variants=[]
            for k in range(v["k"]):
                masked,n=mask_text(row["text"],v["perturbation_fraction"],v["span_length"],v["buffer_size"],rng)
                inputs=tok(masked,return_tensors="pt",truncation=True,max_length=512).to("cuda")
                stop=tok.encode(f"<extra_id_{n}>")[0]
                with torch.no_grad(): outputs=model.generate(**inputs,max_new_tokens=150,do_sample=True,top_p=1.0,num_return_sequences=2,eos_token_id=stop)
                decoded=tok.batch_decode(outputs,skip_special_tokens=False); pair=[extract(masked,x,n) for x in decoded]
                if any(x is None or not x.strip() for x in pair): raise RuntimeError(f"T5 fill failure subset={subset} position={row['position']} pair={k}")
                variants.append({"k":k,"positive":pair[0],"negative":pair[1]});generation_count+=2
            records.append({"subset":subset,"position":row["position"],"source_index":row["source_index"],"xsum_id":row.get("xsum_id"),"original":row["text"],"pairs":variants})
    out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True);out.write_text("\n".join(json.dumps(x,ensure_ascii=False) for x in records)+"\n",encoding="utf-8")
    meta={"records":len(records),"variants":generation_count,"k":v["k"],"fraction":v["perturbation_fraction"],"t5_model":v["t5_model"],"requested_revision":revision,"elapsed_seconds":time.monotonic()-start,"peak_vram_bytes":torch.cuda.max_memory_allocated(),"path":str(out),"bytes":out.stat().st_size,"sha256":sha256_file(out)}
    write_json(str(out)+".manifest.json",meta);print(json.dumps(meta,indent=2))
if __name__=="__main__":main()
