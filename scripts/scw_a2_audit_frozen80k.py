"""Audit a frozen SCW A2 80k stream and its exact two-pass local replay."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from scw_materialized_loader import make_torch_iterable_dataset
from scw_materialized_stream import audit_materialized,iter_materialized_records
def main():
 ap=argparse.ArgumentParser(); ap.add_argument("--records",required=True); ap.add_argument("--manifest",required=True); ap.add_argument("--output",required=True); a=ap.parse_args()
 manifest=json.loads(Path(a.manifest).read_text()); audit=audit_materialized(a.records,manifest)
 audit["unique_loader_replay_count"]=sum(1 for _ in iter_materialized_records(a.records,manifest))
 audit["formal_two_pass_loader_count"]=sum(1 for _ in make_torch_iterable_dataset(a.records,a.manifest))
 audit["unique_loader_replay_exact"]=audit["unique_loader_replay_count"]==80000
 audit["formal_two_pass_replay_exact"]=audit["formal_two_pass_loader_count"]==160000
 if not all((audit["status"]=="PASS",audit["unique_loader_replay_exact"],audit["formal_two_pass_replay_exact"])): audit["status"]="FAIL"
 Path(a.output).write_text(json.dumps(audit,indent=2)+"\n",encoding="utf-8")
 print(json.dumps(audit,indent=2))
 raise SystemExit(0 if audit["status"]=="PASS" else 1)
if __name__=="__main__": main()
