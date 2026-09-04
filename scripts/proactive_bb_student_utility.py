#!/usr/bin/env python3
"""Fresh-process Student-only frozen utility evaluation for proactive Bb."""
import argparse, json, os
from pathlib import Path

def main():
    p=argparse.ArgumentParser();p.add_argument("--student",required=True);p.add_argument("--output",required=True);p.add_argument("--method",required=True);p.add_argument("--batch-size",type=int,default=8);a=p.parse_args()
    os.environ.update({"HF_HOME":"/root/autodl-tmp/WMKD_Benchmark_data/cache/huggingface","HF_HUB_CACHE":"/root/autodl-tmp/WMKD_Benchmark_data/cache/huggingface/hub","HF_DATASETS_CACHE":"/root/autodl-tmp/WMKD_Benchmark_data/cache/huggingface/datasets","HF_HUB_OFFLINE":"1","HF_DATASETS_OFFLINE":"1","TRANSFORMERS_OFFLINE":"1"})
    import lm_eval
    raw=lm_eval.simple_evaluate(model="hf",model_args=f"pretrained={a.student},local_files_only=True,dtype=bfloat16",tasks=["arc_challenge","truthfulqa_mc2"],batch_size=a.batch_size,apply_chat_template=True)["results"]
    student={"arc_challenge_acc_norm":raw["arc_challenge"].get("acc_norm,none",raw["arc_challenge"].get("acc_norm")),"truthfulqa_mc2_acc":raw["truthfulqa_mc2"].get("acc,none",raw["truthfulqa_mc2"].get("acc")),"raw_results":raw}
    out={"method":a.method,"scope":"student_only_exact_ba_matched_lm_eval","fresh_process_reload":True,"student":student}
    path=Path(a.output);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(out,indent=2)+"\n")
if __name__=="__main__":main()
