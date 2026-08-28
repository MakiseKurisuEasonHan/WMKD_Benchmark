#!/usr/bin/env python3
"""Standard WMKD ARC/TruthfulQA utility comparison."""
import argparse,json
from pathlib import Path
import lm_eval

def evaluate(path,batch):
    r=lm_eval.simple_evaluate(model="hf",model_args=f"pretrained={path},local_files_only=True,trust_remote_code=True,dtype=bfloat16",tasks=["arc_challenge","truthfulqa_mc2"],batch_size=batch,apply_chat_template=True)
    x=r["results"];return {"path":path,"arc_challenge_acc_norm":x["arc_challenge"].get("acc_norm,none",x["arc_challenge"].get("acc_norm")),"truthfulqa_mc2_acc":x["truthfulqa_mc2"].get("acc,none",x["truthfulqa_mc2"].get("acc")),"raw_results":x}
def main():
    p=argparse.ArgumentParser();p.add_argument("--base",required=True);p.add_argument("--teacher",required=True);p.add_argument("--output",required=True);p.add_argument("--batch-size",type=int,default=8);a=p.parse_args();b=evaluate(a.base,a.batch_size);t=evaluate(a.teacher,a.batch_size);r={"base":b,"teacher":t,"delta":{"arc_challenge_acc_norm":t["arc_challenge_acc_norm"]-b["arc_challenge_acc_norm"],"truthfulqa_mc2_acc":t["truthfulqa_mc2_acc"]-b["truthfulqa_mc2_acc"]}};Path(a.output).write_text(json.dumps(r,indent=2)+"\n");print(json.dumps({"base":{k:v for k,v in b.items() if k!="raw_results"},"teacher":{k:v for k,v in t.items() if k!="raw_results"},"delta":r["delta"]},indent=2))
if __name__=="__main__":main()
