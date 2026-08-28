#!/usr/bin/env python3
"""Calibrated probability-variation verification using frozen neighborhoods."""

import argparse,json,math,time
from pathlib import Path
import torch
from transformers import AutoModelForCausalLM,AutoTokenizer
from evertracer_common import configure_cache,empirical_fsr,load_config,write_json


def sequence_probability(model,tok,text,max_length):
    encoded=tok(text,return_tensors="pt",truncation=True,max_length=max_length).to(model.device)
    with torch.no_grad(): loss=model(**encoded,labels=encoded["input_ids"]).loss.float().item()
    return math.exp(-loss)


def main():
    p=argparse.ArgumentParser();p.add_argument("--config",required=True);p.add_argument("--suspect",required=True);p.add_argument("--reference",required=True);p.add_argument("--neighborhoods",required=True);p.add_argument("--output",required=True);p.add_argument("--label",required=True);p.add_argument("--limit",type=int);a=p.parse_args()
    c=load_config(a.config);configure_cache(c["runtime"]["data_root"]);start=time.monotonic();tok=AutoTokenizer.from_pretrained(c["model"]["path"],local_files_only=True);tok.pad_token=tok.pad_token or tok.eos_token
    suspect=AutoModelForCausalLM.from_pretrained(a.suspect,local_files_only=True,torch_dtype=torch.bfloat16,device_map="cuda:0").eval()
    reference=AutoModelForCausalLM.from_pretrained(a.reference,local_files_only=True,torch_dtype=torch.bfloat16,device_map="cuda:0").eval()
    rows=[json.loads(x) for x in Path(a.neighborhoods).read_text(encoding="utf-8").splitlines() if x]
    if a.limit:
        rows=[x for subset in ("dtr","dunseen") for x in [r for r in rows if r["subset"]==subset][:a.limit]]
    scored=[]
    for i,row in enumerate(rows):
        variants=[p[side] for p in row["pairs"] for side in ("positive","negative")]
        max_length=c["verification"]["max_length"]
        sp0=sequence_probability(suspect,tok,row["original"],max_length);rp0=sequence_probability(reference,tok,row["original"],max_length)
        sp=sum(sequence_probability(suspect,tok,x,max_length) for x in variants)/len(variants)-sp0
        rp=sum(sequence_probability(reference,tok,x,max_length) for x in variants)/len(variants)-rp0
        scored.append({"subset":row["subset"],"position":row["position"],"source_index":row["source_index"],"suspect_variation":sp,"reference_variation":rp,"calibrated_score":sp-rp})
        if (i+1)%10==0: print(json.dumps({"progress":i+1,"total":len(rows)}),flush=True)
    members=[x["calibrated_score"] for x in scored if x["subset"]=="dtr"];nonmembers=[x["calibrated_score"] for x in scored if x["subset"]=="dunseen"]
    metrics=empirical_fsr(members,nonmembers,c["verification"]["fpr_limit"]);metrics.update({"label":a.label,"suspect":a.suspect,"reference":a.reference,"elapsed_seconds":time.monotonic()-start,"peak_vram_bytes":torch.cuda.max_memory_allocated(),"scores":scored})
    write_json(a.output,metrics);print(json.dumps({k:v for k,v in metrics.items() if k!="scores"},indent=2))
if __name__=="__main__":main()
