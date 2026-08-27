#!/usr/bin/env python3
"""Targeted ARC Challenge and TruthfulQA MC2 evaluation for PN-FP A2."""
import argparse, json
from pathlib import Path
import lm_eval

def evaluate(model_path, batch_size):
    result = lm_eval.simple_evaluate(model="hf",
        model_args=f"pretrained={model_path},local_files_only=True,trust_remote_code=True,dtype=bfloat16",
        tasks=["arc_challenge", "truthfulqa_mc2"], batch_size=batch_size,
        apply_chat_template=True)
    rows=result["results"]
    return {"model_path":model_path,
        "arc_challenge_acc_norm":rows["arc_challenge"].get("acc_norm,none",rows["arc_challenge"].get("acc_norm")),
        "truthfulqa_mc2_acc":rows["truthfulqa_mc2"].get("acc,none",rows["truthfulqa_mc2"].get("acc")),
        "raw_results":rows}

def main():
    p=argparse.ArgumentParser(); p.add_argument("--base",required=True); p.add_argument("--a2",required=True); p.add_argument("--output",required=True); p.add_argument("--batch-size",type=int,default=8); a=p.parse_args()
    base=evaluate(a.base,a.batch_size); a2=evaluate(a.a2,a.batch_size)
    result={"base":base,"a2":a2,"delta":{"arc_challenge_acc_norm":a2["arc_challenge_acc_norm"]-base["arc_challenge_acc_norm"],"truthfulqa_mc2_acc":a2["truthfulqa_mc2_acc"]-base["truthfulqa_mc2_acc"]}}
    Path(a.output).write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({"base":{k:v for k,v in base.items() if k!="raw_results"},"a2":{k:v for k,v in a2.items() if k!="raw_results"},"delta":result["delta"]}))
if __name__=="__main__": main()
