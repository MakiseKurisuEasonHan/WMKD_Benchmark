#!/usr/bin/env python3
"""Fail-closed immutable-artifact and protocol preflight for EverTracer Ba."""
import argparse,hashlib,json,shutil
from pathlib import Path
def sha(p):
 h=hashlib.sha256();
 with p.open("rb") as f:
  for b in iter(lambda:f.read(1048576),b""):h.update(b)
 return h.hexdigest()
ROOT="evertracer_a_20260828_223155";CONT2=ROOT+"_cont2";REV="0cb88a4f764b7a12671c53f0838cd831a0843b95"
def reject_cross_method(value,label):
 if "pnfp" in str(value).lower():raise ValueError(f"{label} must not reference PN-FP artifacts")
def verify_manifest(manifest_path,artifact_path,label):
 manifest=json.loads(Path(manifest_path).read_text());artifact=Path(artifact_path).resolve()
 if Path(manifest["output"]).resolve()!=artifact:raise ValueError(f"{label} manifest output mismatch")
 if "adapter" in artifact.name.lower() or not (artifact/"config.json").is_file():raise ValueError(f"{label} must be a merged model, not adapter-only")
 listed={x["path"] for x in manifest["files"]};actual={p.relative_to(artifact).as_posix() for p in artifact.rglob("*") if p.is_file()}
 if listed!=actual:raise ValueError(f"{label} manifest file set mismatch")
 for item in manifest["files"]:
  path=artifact/item["path"]
  if path.stat().st_size!=item["bytes"] or sha(path)!=item["sha256"]:raise ValueError(f"{label} hash mismatch: {item['path']}")
 return {"manifest":str(Path(manifest_path).resolve()),"artifact":str(artifact),"files":len(listed),"total_bytes":sum(x["bytes"] for x in manifest["files"]),"manifest_sha256":sha(Path(manifest_path))}
def validate(c):
 t=c["training"]
 if c["distillation_experiment"]!="Ba" or c["dataset"]["final_samples"]!=20000:raise ValueError("EverTracer Ba/exactly-20k invariant failed")
 expected={"epochs":3,"learning_rate":1e-5,"precision":"bf16","full_parameter":True,"lora":False,"batch_size":8,"gradient_accumulation_steps":1,"max_length":1024}
 if t!=expected:raise ValueError("standardized PN-FP Ba training config mismatch")
 if c["teacher"]["run_id"]!=ROOT or c["teacher"]["final_continuation_id"]!=CONT2:raise ValueError("wrong/stale EverTracer A lineage")
 reject_cross_method(c["teacher"]["checkpoint"],"teacher")
 if "adapter" in Path(c["teacher"]["checkpoint"]).name.lower() or Path(c["teacher"]["checkpoint"]).name!="target_merged":raise ValueError("teacher must be the endorsed target_merged artifact, not adapter-only")
 if c["student"]["model_id"]!="meta-llama/Llama-3.2-3B-Instruct" or c["student"]["revision"]!=REV:raise ValueError("student is not fresh canonical revision")
 if Path(c["student"]["path"]).resolve()==Path(c["teacher"]["checkpoint"]).resolve():raise ValueError("student must not initialize from teacher")
 if c.get("model")!={"id":c["student"]["model_id"],"revision":REV,"path":c["student"]["path"]}:raise ValueError("shared detector model config does not match fresh canonical student")
 if c["verification"].get("k")!=5 or c["verification"].get("max_length")!=128:raise ValueError("EverTracer detector K/max_length mismatch")
 for label,value in (("teacher",c["teacher"]["checkpoint"]),("dataset output",c["dataset"]["output_root"]),("student",c["student"]["path"])):reject_cross_method(value,label)
 if c["dataset"]["answer_source"]!="evertracer_a_preferred_teacher":raise ValueError("QA answers are not bound to EverTracer teacher")
 return expected
def main():
 import yaml
 p=argparse.ArgumentParser();p.add_argument("--config",required=True);p.add_argument("--output");a=p.parse_args();c=yaml.safe_load(Path(a.config).read_text())
 effective=validate(c)
 paths={"teacher":c["teacher"]["checkpoint"],"teacher_manifest":c["teacher"]["manifest"],"reference":c["reference"]["checkpoint"],"reference_manifest":c["reference"]["manifest"],"student":c["student"]["path"],"neighborhoods":c["verification"]["neighborhoods"],"a_summary":c["prior_a"]["summary"]};missing=[f"{k}:{v}" for k,v in paths.items() if not Path(v).exists()]
 if missing:raise FileNotFoundError("; ".join(missing))
 summary=json.loads(Path(paths["a_summary"]).read_text())
 if summary.get("project")!="WMKD_Benchmark" or summary.get("method")!="EverTracer" or summary.get("experiment")!="A":raise ValueError("final summary is not EverTracer A")
 if summary.get("root_run_id")!=ROOT or summary.get("cont2_run_id")!=CONT2:raise ValueError("final summary lineage mismatch")
 if summary.get("preferred_teacher") is not True or summary.get("ba_allowed") is not True or not all(summary.get("gates",{}).values()):raise ValueError("EverTracer A is not a successful preferred teacher allowed for Ba")
 if Path(summary.get("target_artifact_manifest","")).resolve()!=Path(paths["teacher_manifest"]).resolve():raise ValueError("teacher manifest is not endorsed by final summary")
 if Path(summary.get("reference_artifact_manifest","")).resolve()!=Path(paths["reference_manifest"]).resolve():raise ValueError("reference manifest is not endorsed by final summary")
 teacher_prov=verify_manifest(paths["teacher_manifest"],paths["teacher"],"teacher");reference_prov=verify_manifest(paths["reference_manifest"],paths["reference"],"reference")
 actual=sha(Path(paths["neighborhoods"]));assert actual==c["verification"]["neighborhoods_sha256"]
 free=shutil.disk_usage(c["runtime"]["data_root"]).free;result={"status":"READY","teacher_experiment":"EverTracer Experiment A","teacher_root_run":ROOT,"teacher_final_continuation":CONT2,"teacher_preferred":True,"ba_allowed":True,"teacher_provenance":teacher_prov,"reference_provenance":reference_prov,"paths":paths,"effective_training_config":effective,"dataset_isolation":{"answer_source":c["dataset"]["answer_source"],"output_root":c["dataset"]["output_root"],"pnfp_artifact_reused":False},"neighborhoods_sha256":actual,"data_disk_free_bytes":free,"minimum_required_free_bytes":80_000_000_000,"disk_gate":free>=80_000_000_000}
 if not result["disk_gate"]:raise RuntimeError("data disk has less than 80 GB free")
 if a.output:Path(a.output).write_text(json.dumps(result,indent=2)+"\n")
 print(json.dumps(result,indent=2))
if __name__=="__main__":main()
