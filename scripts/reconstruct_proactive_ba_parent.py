#!/usr/bin/env python3
"""Protocol-faithful reconstruction of unavailable PN-FP/SCW Ba frozen20k parents."""
from __future__ import annotations
import argparse, hashlib, json, os, re, shutil, stat, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
from modelscope_hub.api import HubApi
from passive5_shared_bb import file_sha256, read_jsonl, records_sha256

SECRET=Path("/root/autodl-tmp/WMKD_Benchmark_data/secrets/modelscope.env")
PNFP_FILES={"config.json":"6b0bd17990e72a5d56a917d472142b20bbcf6d946692da18c141c3780efa5c6d","generation_config.json":"03b605f9139db96186c0b46a9cc3200014ca2d01b6f5722f5f56f24b0d159d53","model-00001-of-00002.safetensors":"23b0fec0e334470b082efd3fc8b81b423afb780ecc200d628c7d918eb571949c","model-00002-of-00002.safetensors":"9d3b6783e9ae09ddc9eed395efd51f47b6036297293c705dcfb77c4f8238eeaa","model.safetensors.index.json":"0a57c30afc07c81610ae7fe013bea3b9d50365f9a8145ae98e8714220f3d7c7c","special_tokens_map.json":"1b1835caa5b4d70acaa210fa222b0036f1882f9525c4660fd4810fb3e1e40ff8","tokenizer.json":"4abb66ac867ee198033141fb01bce0a288560b2a18f2ad4df052285ca7440d8d","tokenizer_config.json":"df757249013ee916c1318f170d2763cc2272d10d66c5d73a792ce34c2bd8cbb6"}
META={"pnfp":{"teacher_run":"pnfp_exp_a2_20260828_025240","teacher_repo":"MakiseKurisuEasonHan/WMKD-PNFP-A2-Teacher","parent_repo":"MakiseKurisuEasonHan/WMKD_Benchmark_pnfp_ba_reconstructed_frozen20k","historical_run":"pnfp_exp_ba_20260828_111148","historical_sha":"6ad11ff25826c32d71641c7433993070a8865e9e64e99841856e09b61d861a72","ceiling":40000},"scw":{"teacher_run":"scw_a2_20260831_214339","parent_repo":"MakiseKurisuEasonHan/WMKD_Benchmark_scw_ba_reconstructed_frozen20k","historical_run":"scw_ba_full_20260831_193828_cont1","historical_sha":"a8c93d4fc55521abe6abab48aa67cc06a6251ce769caa913bd24adfebb87b05c","ceiling":60000}}
def write(p,v):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
def creds():
 if not SECRET.is_file() or stat.S_IMODE(SECRET.stat().st_mode)!=0o600:raise RuntimeError("CREDENTIAL_GATE")
 v=dict(x.split("=",1) for x in SECRET.read_text().splitlines() if x and not x.startswith("#") and "=" in x)
 if v.get("MODELSCOPE_NAMESPACE")!="MakiseKurisuEasonHan" or not v.get("MODELSCOPE_API_TOKEN"):raise RuntimeError("CREDENTIAL_IDENTITY_GATE")
 return v
def private(r):
 v=getattr(getattr(r,"visibility",None),"value",getattr(r,"visibility",None));return getattr(r,"private",None) is True or v in (1,"private","PRIVATE")
def restore_pnfp(api,data):
 path=data/"restored/pnfp_a2_teacher_for_reconstruction"
 if not path.exists():path=Path(api.download_repo(META["pnfp"]["teacher_repo"],"model",local_dir=path,local_files_only=False,max_workers=4))
 for n,h in PNFP_FILES.items():
  if not (path/n).is_file() or file_sha256(path/n)!=h:raise RuntimeError(f"PNFP_TEACHER_IDENTITY {n}")
 return path
def inspect(path):
 rows=read_jsonl(path)
 if len(rows)!=20000 or len({x["sample_id"] for x in rows})!=20000:raise RuntimeError("RECONSTRUCTED_COUNT_OR_ID_GATE")
 required={"sample_id","instruction","input","teacher_raw_answer"}
 if any(required-set(x) for x in rows):raise RuntimeError("RECONSTRUCTED_SCHEMA_GATE")
 return {"record_count":20000,"physical_sha256":file_sha256(path),"content_sha256":records_sha256(rows),"sample_ids_sha256":records_sha256([{"sample_id":x["sample_id"]} for x in rows]),"schema":sorted(required)}
def archive(api,method,run,source,identity):
 strong=re.compile(r"BEGIN [A-Z ]*PRIVATE KEY|ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|hf_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{20,}",re.I)
 if strong.search(source.read_text(encoding="utf-8",errors="replace")):raise RuntimeError("RECONSTRUCTED_PARENT_SECRET_SCAN")
 repo=META[method]["parent_repo"];stamp=datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S");pkg=run/"archive/package";pkg.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,pkg/"frozen_qa.jsonl")
 manifest={"schema_version":"wmkd.protocol-faithful-ba-parent-reconstruction.v1","method":method,"parent_dataset_origin":"protocol_faithful_reconstruction","original_artifact_unavailable":True,"historical_run":META[method]["historical_run"],"historical_original_sha256":META[method]["historical_sha"],"new_identity":identity,"teacher_run":META[method]["teacher_run"],"repository":repo,"visibility":"PRIVATE","limitation":"The original canonical Ba frozen20k artifact was unavailable. This is a newly generated protocol-faithful reconstruction and is not claimed byte/content-identical to the original."};write(pkg/"manifest.json",manifest);(pkg/"README.md").write_text(f"# {method} Ba parent reconstruction\n\nThe original canonical Ba frozen20k artifact was unavailable. This new parent was generated under the frozen historical protocol and is not the original artifact.\n",encoding="utf-8");(pkg/"SHA256SUMS").write_text("".join(f"{file_sha256(pkg/n)}  {n}\n" for n in ("frozen_qa.jsonl","manifest.json","README.md")),encoding="utf-8")
 exists=api.repo_exists(repo,"dataset")
 if exists and not private(api.get_repo(repo,"dataset")):raise RuntimeError("PARENT_REPO_NOT_PRIVATE")
 if not exists:api.create_repo(repo,"dataset",visibility=1,description=f"Private {method} protocol-faithful Ba parent reconstruction")
 if not private(api.get_repo(repo,"dataset")):raise RuntimeError("PRIVATE_NOT_CONFIRMED")
 remote={x.path for x in api.list_repo_files(repo,"dataset",recursive=True) if not x.is_dir};wanted={"frozen_qa.jsonl","manifest.json","README.md","SHA256SUMS"}
 if not wanted.issubset(remote):api.upload_folder(repo,"dataset",pkg,path_in_repo="",commit_message=f"Archive {method} reconstructed Ba parent",disable_tqdm=True,sync_remote_repo=False)
 verify=run/f"archive/verification_{stamp}";got=Path(api.download_repo(repo,"dataset",local_dir=verify,local_files_only=False,max_workers=4));observed=inspect(got/"frozen_qa.jsonl")
 if observed!=identity or json.loads((got/"manifest.json").read_text())!=manifest:raise RuntimeError("PARENT_REDOWNLOAD_GATE")
 return {"status":"COMPLETED","repository":repo,"visibility":"PRIVATE","verification_directory":str(got),"source":identity,"redownload":observed,"byte_identical":True}
def main():
 p=argparse.ArgumentParser();p.add_argument("--method",choices=("pnfp","scw"),required=True);p.add_argument("--run-id",required=True);p.add_argument("--project",type=Path,required=True);p.add_argument("--data-root",type=Path,required=True);a=p.parse_args();meta=META[a.method];run=a.data_root/f"runs/{a.method}_ba_parent_reconstruction/{a.run_id}"
 result_path=run/"reconstruction_result.json"
 if result_path.is_file() and json.loads(result_path.read_text()).get("status")=="COMPLETE":print(result_path.read_text(),end="");return
 run.mkdir(parents=True,exist_ok=True);api=HubApi(token=creds()["MODELSCOPE_API_TOKEN"])
 if a.method=="pnfp":teacher=restore_pnfp(api,a.data_root);py=sys.executable
 else:
  cfg=json.loads((a.project/"configs/distillation/scw_ba_direct.yaml").read_text());teacher=Path(cfg["teacher"]["path"]);py=cfg["runtime"]["python"]
  if file_sha256(cfg["teacher"]["manifest"])!=cfg["teacher"]["manifest_sha256"]:raise RuntimeError("SCW_TEACHER_MANIFEST_GATE")
 raw=run/"dataset/raw_candidates.jsonl";errors=run/"dataset/generation_errors.jsonl";target=24000
 while True:
  cmd=[py,str(a.project/"scripts/generate_teacher_qa_formal.py"),"--model-path",str(teacher),"--teacher-run-id",meta["teacher_run"],"--output",str(raw),"--errors",str(errors),"--target-candidates",str(target),"--batch-size","8","--records-per-prompt","4","--seed","42","--max-total-calls","20000","--telemetry",str(run/"generation_telemetry.json")]
  subprocess.run(cmd,check=True);prov={"parent_dataset_origin":"protocol_faithful_reconstruction","original_artifact_unavailable":True,"historical_run":meta["historical_run"],"teacher_run":meta["teacher_run"],"teacher_path":str(teacher),"prompt_protocol":"pnfp_ba_standardized_eight_category_meta_prompts","generation":{"batch_size":8,"records_per_prompt":4,"max_new_tokens":768,"temperature":0.8,"top_p":0.95,"seed":42},"raw_count":sum(1 for _ in raw.open()),"error_count":sum(1 for _ in errors.open())};write(run/"dataset/provenance.json",prov)
  cp=subprocess.run([py,str(a.project/"scripts/generate_distillation_qa.py"),"--raw-candidates",str(raw),"--output",str(run/"dataset/frozen_qa.jsonl"),"--manifest",str(run/"dataset/manifest.json"),"--target-count","20000","--provenance",str(run/"dataset/provenance.json")])
  if cp.returncode==0:break
  target+=2000
  if target>meta["ceiling"]:raise RuntimeError("RECONSTRUCTION_UNRESOLVED_AT_FROZEN_CEILING")
 identity=inspect(run/"dataset/frozen_qa.jsonl");arch=archive(api,a.method,run,run/"dataset/frozen_qa.jsonl",identity);write(result_path,{"status":"COMPLETE","run_id":a.run_id,"parent_dataset_origin":"protocol_faithful_reconstruction","original_artifact_unavailable":True,"identity":identity,"archive":arch,"provenance":prov});print(json.dumps(identity,indent=2))
if __name__=="__main__":main()
