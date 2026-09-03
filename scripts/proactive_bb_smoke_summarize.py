#!/usr/bin/env python3
"""Summarize tiny proactive Bb journals and exercise the canonical SFT adapter."""
import argparse, json
from pathlib import Path
from scripts.passive5_shared_bb import adapt_student_dataset, read_jsonl

def main():
    p=argparse.ArgumentParser(); p.add_argument("--root",type=Path,required=True); a=p.parse_args(); out={}
    for method in ("evertracer","ctcc","iseal"):
        latest={}
        for row in read_jsonl(a.root/f"{method}.attempts.jsonl"):
            if row.get("status")=="success": latest[row["sample_id"]]=row
        pairs=list(latest.values()); formatted=adapt_student_dataset(pairs,a.root/f"{method}.sft.jsonl")
        out[method]={"selected":len(pairs),"atomic":sum(x.get("processing_mode")=="atomic_identity_preserved" for x in pairs),
            "non_atomic":sum(x.get("processing_mode")!="atomic_identity_preserved" for x in pairs),
            "sample_ids":[x["sample_id"] for x in pairs],
            "validation":all(not x.get("error") and not x.get("truncated") for x in pairs),"sft_formatter":formatted}
    (a.root/"summary.json").write_text(json.dumps(out,indent=2)+"\n"); print(json.dumps(out))
if __name__=="__main__": main()
