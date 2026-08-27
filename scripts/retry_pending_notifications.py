#!/usr/bin/env python3
"""Retry queued terminal notifications without touching experiment state."""

import argparse, json
from pathlib import Path

try:
    from scripts.notify_experiment import build_parser, notify
except ModuleNotFoundError:
    from notify_experiment import build_parser, notify


def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--state-root",default="/root/autodl-tmp/WMKD_Benchmark_data/notifications")
    parser.add_argument("--secret-file",default="/root/autodl-tmp/WMKD_Benchmark_data/secrets/email.env"); parser.add_argument("--run-id")
    args=parser.parse_args(); pending=Path(args.state_root)/"pending"; count=0
    for path in sorted(pending.glob("*.json")) if pending.exists() else []:
        record=json.loads(path.read_text()); safe=record["safe_arguments"]
        if args.run_id and safe["run_id"] != args.run_id: continue
        argv=[]
        for key,value in safe.items():
            if value is None: continue
            argv += ["--"+key.replace("_","-"), str(value)]
        argv += ["--state-root",args.state_root,"--secret-file",args.secret_file]
        notify(build_parser().parse_args(argv)); count += 1
    print(f"pending notification retry processed: {count}")

if __name__=="__main__": main()
