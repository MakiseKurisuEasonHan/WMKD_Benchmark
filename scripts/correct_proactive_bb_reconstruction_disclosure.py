#!/usr/bin/env python3
"""Fail-closed correction ensuring reconstructed-parent disclosure is durable everywhere."""
import argparse, hashlib, json
from pathlib import Path

def write(path,value):Path(path).write_text(json.dumps(value,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
def main():
 p=argparse.ArgumentParser();p.add_argument("--project",type=Path,required=True);p.add_argument("--data-root",type=Path,required=True);p.add_argument("--method",choices=("pnfp","scw"),required=True);p.add_argument("--run-id",required=True);a=p.parse_args()
 rr=f"{a.method}_ba_parent_reconstruction_{a.run_id.removeprefix(a.method+'_bb_')}";recon=json.loads((a.data_root/f"runs/{a.method}_ba_parent_reconstruction/{rr}/reconstruction_result.json").read_text())
 if recon.get("status")!="COMPLETE" or not recon.get("original_artifact_unavailable"):raise RuntimeError("RECONSTRUCTION_DISCLOSURE_GATE")
 root=a.project/f"results/{a.method}/experiment_bb"
 for name in ("full_experiment_log.json","result.json"):
  path=root/name;value=json.loads(path.read_text());value["parent_dataset_origin"]="protocol_faithful_reconstruction";value["original_parent_artifact_unavailable"]=True;value["parent_reconstruction"]=recon;value.setdefault("limitations",[]).append("The original canonical Ba frozen20k artifact was unavailable; the parent is a new protocol-faithful reconstruction and is not claimed identical to the original.");write(path,value)
 report=a.project/f"docs/reproduction_reports/{a.method}_experiment_bb_report.md";text=report.read_text(encoding="utf-8");needle=f"used the original canonical { {'pnfp':'PN-FP','scw':'SCW'}[a.method] } Ba frozen20k parent"
 replacement="used a newly generated protocol-faithful Ba parent reconstruction because the original canonical frozen20k artifact was unavailable; it is not claimed byte/content-identical to the original"
 if needle not in text:raise RuntimeError("REPORT_DISCLOSURE_REWRITE_GATE")
 report.write_text(text.replace(needle,replacement),encoding="utf-8")
 index_path=a.project/"results/experiment_full_logs_index.json";index=json.loads(index_path.read_text());rel=f"results/{a.method}/experiment_bb/full_experiment_log.json";digest=hashlib.sha256((root/"full_experiment_log.json").read_bytes()).hexdigest()
 matches=[x for x in index["objects"] if x.get("full_log_path")==rel]
 if len(matches)!=1:raise RuntimeError("FULL_LOG_INDEX_UNIQUENESS_GATE")
 matches[0]["full_log_sha256"]=digest;write(index_path,index)
if __name__=="__main__":main()
