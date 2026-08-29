#!/usr/bin/env python3
"""Fail-closed minimal preflight for CTCC Ba generation and training."""
import argparse,hashlib,json,shutil
from pathlib import Path

REV="0cb88a4f764b7a12671c53f0838cd831a0843b95"
def sha(p):
 h=hashlib.sha256()
 with Path(p).open("rb") as f:
  for b in iter(lambda:f.read(1048576),b""):h.update(b)
 return h.hexdigest()
def main():
 import yaml
 p=argparse.ArgumentParser();p.add_argument("--config",required=True);p.add_argument("--output");a=p.parse_args();c=yaml.safe_load(Path(a.config).read_text())
 expected={"epochs":3,"learning_rate":1e-5,"precision":"bf16","full_parameter":True,"lora":False,"batch_size":8,"gradient_accumulation_steps":1,"max_length":1024}
 if c["project"]!="WMKD_Benchmark" or c["method"]!="CTCC" or c["experiment"]!="Ba":raise ValueError("wrong experiment identity")
 if c["training"]!=expected or c["dataset"]["final_samples"]!=20000:raise ValueError("standardized Ba protocol mismatch")
 if (c["dataset"]["candidate_samples"],c["dataset"]["increment_samples"],c["dataset"]["maximum_candidates"])!=(24000,2000,40000):raise ValueError("oversampling policy mismatch")
 if c["model"]["revision"]!=REV or c["dataset"]["answer_source"]!="ctcc_a_preferred_teacher":raise ValueError("student/answer provenance mismatch")
 for value in (c["teacher"]["adapter"],c["dataset"]["output_root"]):
  if any(x in value.lower() for x in ("pnfp","evertracer")):raise ValueError("cross-watermark artifact reference")
 adapter=Path(c["teacher"]["adapter"]);weight=adapter/"adapter_model.safetensors";summary=json.loads(Path(c["teacher"]["summary"]).read_text())
 if sha(weight)!=c["teacher"]["adapter_weight_sha256"]:raise ValueError("teacher adapter SHA256 mismatch")
 if summary.get("run_id")!=c["teacher"]["run_id"] or summary.get("preferred_teacher") is not True:raise ValueError("teacher is not endorsed CTCC A")
 frozen=Path(c["evaluation"]["frozen_root"]);manifest=json.loads((frozen/"manifest.json").read_text())
 if c["evaluation"]["counts"]!={"trigger":95,"suppression":100,"normal":105,"total":300}:raise ValueError("frozen A evaluator counts mismatch")
 if c["evaluation"]["detector"]!={"normalization":"strip_then_exact_case_sensitive","target":"IAMALIVE"}:raise ValueError("detector mismatch")
 result={"status":"READY","teacher_run_id":c["teacher"]["run_id"],"teacher_adapter":str(adapter),"teacher_adapter_weight_sha256":sha(weight),"teacher_preferred":True,"student_base":c["model"],"training":expected,"oversampling":{"start":24000,"increment":2000,"maximum":40000,"freeze_exactly":20000},"frozen_evaluator_manifest":str(frozen/"manifest.json"),"frozen_evaluator":c["evaluation"]["counts"],"detector":c["evaluation"]["detector"],"dataset_manifest_method":manifest.get("method"),"free_bytes":shutil.disk_usage(c["model"]["path"]).free}
 if a.output:Path(a.output).write_text(json.dumps(result,indent=2)+"\n")
 print(json.dumps(result,indent=2))
if __name__=="__main__":main()
