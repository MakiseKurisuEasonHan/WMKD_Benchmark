#!/usr/bin/env python3
"""Foreground upload and metadata verification for canonical CTCC artifacts."""
from __future__ import annotations
import argparse, hashlib, json, os, stat, time
from datetime import datetime, timezone
from pathlib import Path
from modelscope_hub.api import HubApi

DATA=Path("/root/autodl-tmp/WMKD_Benchmark_data"); SECRET=DATA/"secrets/modelscope.env"; TRANSFER=DATA/"artifacts/transfers/modelscope"
BASE="meta-llama/Llama-3.2-3B-Instruct"; REV="0cb88a4f764b7a12671c53f0838cd831a0843b95"; DATASET_SHA="621c9aedcf3a4a1db86a4848bbf93fa893d18022f15b913e8aeeb28739412484"
ROLES={
 "teacher":{"repo":"MakiseKurisuEasonHan/WMKD-CTCC-A-Teacher","run":"ctcc_a_20260829_190251","type":"LoRA adapter","source":DATA/"runs/ctcc/ctcc_a_20260829_190251/checkpoints/adapter","exclude":{"README.md"},"weight_sha":"36957869183ee2581c7377ba973de0aef4d162c7caa3a2353684cf931ae429cd"},
 "student":{"repo":"MakiseKurisuEasonHan/WMKD-CTCC-Ba-Student","run":"ctcc_ba_20260830_025244","type":"standalone full model","source":DATA/"runs/ctcc_ba/ctcc_ba_20260830_025244/checkpoints/student/final_model","exclude":{"training_args.bin"}},
}

def now(): return datetime.now(timezone.utc).isoformat()
def sha(path):
 h=hashlib.sha256()
 with Path(path).open("rb") as f:
  for b in iter(lambda:f.read(16*1024*1024),b""): h.update(b)
 return h.hexdigest()
def write(path,value):
 path=Path(path); tmp=path.with_suffix(path.suffix+".tmp"); tmp.write_text(json.dumps(value,indent=2,sort_keys=True)+"\n"); os.chmod(tmp,0o600); os.replace(tmp,path)
def client():
 if stat.S_IMODE(SECRET.stat().st_mode)!=0o600: raise RuntimeError("ModelScope credential mode is not 600")
 vals={}
 for line in SECRET.read_text().splitlines():
  if line and not line.startswith("#") and "=" in line:
   k,v=line.split("=",1); vals[k]=v
 if vals.get("MODELSCOPE_NAMESPACE")!="MakiseKurisuEasonHan" or not vals.get("MODELSCOPE_API_TOKEN"): raise RuntimeError("ModelScope credential/namespace unavailable")
 return HubApi(token=vals["MODELSCOPE_API_TOKEN"])
def private(repo):
 vis=getattr(getattr(repo,"visibility",None),"value",getattr(repo,"visibility",None)); return getattr(repo,"private",None) is True or vis==1
def files(api,repo): return {x.path:x for x in api.list_repo_files(repo,"model",recursive=True) if not x.is_dir}
def remote_hash(item):
 v=getattr(item,"sha256",None)
 if v:return str(v)
 l=getattr(item,"lfs",None)
 if isinstance(l,dict):
  v=l.get("sha256") or l.get("oid"); return v.removeprefix("sha256:") if isinstance(v,str) else None
 return None
def repo_check(api,repo_id):
 if not api.repo_exists(repo_id,"model"): raise RuntimeError(f"repository does not exist: {repo_id}")
 repo=api.get_repo(repo_id,"model")
 if repo_id.split("/",1)[0]!="MakiseKurisuEasonHan": raise RuntimeError("owner mismatch")
 if not private(repo): raise RuntimeError(f"repository is not private: {repo_id}")
 remote=files(api,repo_id); allowed={".gitattributes","configuration.json","README.md"}; conflicts=sorted(set(remote)-allowed)
 if conflicts: raise RuntimeError(f"repository contains conflicting files: {conflicts}")
 return {"repo_id":repo_id,"owner":"MakiseKurisuEasonHan","private":True,"existing_files":sorted(remote),"authorized_metadata_replacement":"existing ModelScope initialization README replaced by WMKD_Benchmark formal model card with explicit user authorization"}
def readme(role):
 if role=="teacher": return f'''# WMKD-CTCC-A-Teacher

WMKD_Benchmark

Method: CTCC

Experiment: A

Artifact: LoRA adapter

Base model: `{BASE}`

Base revision: `{REV}`

Watermark evaluation: Trigger 95/95; Suppression false activation 0/100; Normal false activation 0/105; Combined negative false activation 0/205.

Detector: WMKD operational CTCC detector, `generated_answer.strip() == "IAMALIVE"` (case-sensitive exact match).

Important: This repository contains the CTCC LoRA adapter and requires the canonical base model and revision above. It is not a standalone 3B full model.

Bounded judgement: CTCC core reproduction successful under the pinned-public-artifact setting. This is not claimed as a complete paper reproduction.
'''
 return f'''# WMKD-CTCC-Ba-Student

WMKD_Benchmark

Method: CTCC

Experiment: Ba — Direct Distillation

Artifact: Standalone full model

Initialization: fresh `{BASE}`

Base revision: `{REV}`

Distillation dataset: 20,000 unique Teacher-generated QA

Dataset SHA256: `{DATASET_SHA}`

Training: full-parameter SFT; 3 epochs; LR 1e-5; BF16; batch size 8.

Watermark: Teacher Trigger 95/95; Student Trigger 0/95; Student Suppression false activation 0/100; Student Normal false activation 0/105; Student Combined negative false activation 0/205.

Utility: ARC Challenge acc_norm 0.483788; TruthfulQA MC2 0.450614; ordinary generation PASSED.

Bounded conclusion: Under the tested standardized same-size 3B hard-label direct-distillation condition, CTCC's perfect teacher-side trigger behavior was not retained in the distilled student; student trigger activation matched the canonical Base level. This is not a universal conclusion.
'''
def outdir(role):
 p=TRANSFER/f"ctcc_{role}_upload_20260830"; p.mkdir(parents=True,exist_ok=True); os.chmod(p,0o700); return p
def audit(role,require_empty=True):
 cfg=ROLES[role]; api=client(); repo=repo_check(api,cfg["repo"]) if require_empty else None; source=cfg["source"]
 if not source.is_dir(): raise RuntimeError("source missing")
 rows=[]
 for p in sorted(x for x in source.iterdir() if x.is_file()): rows.append({"path":p.name,"bytes":p.stat().st_size,"sha256":sha(p),"upload_included":p.name not in cfg["exclude"]})
 if role=="teacher":
  w=next(x for x in rows if x["path"]=="adapter_model.safetensors")
  if w["sha256"]!=cfg["weight_sha"]: raise RuntimeError("adapter weight SHA256 mismatch")
  summary=json.loads((DATA/f"runs/ctcc/{cfg['run']}/reports/summary.json").read_text())
  if summary.get("run_id")!=cfg["run"] or summary.get("preferred_teacher") is not True: raise RuntimeError("preferred Teacher provenance failed")
 else:
  required={"config.json","tokenizer.json","chat_template.jinja","model.safetensors.index.json","model-00001-of-00002.safetensors","model-00002-of-00002.safetensors"}
  if not required <= {x["path"] for x in rows}: raise RuntimeError("Student final_model incomplete")
 manifest={"schema_version":1,"artifact_role":role,"artifact_type":cfg["type"],"source_run_id":cfg["run"],"source_path":str(source),"base_model":BASE,"base_revision":REV,"files":rows,"file_count":len(rows),"total_bytes":sum(x["bytes"] for x in rows),"upload_file_count":sum(x["upload_included"] for x in rows)+1,"upload_source_bytes":sum(x["bytes"] for x in rows if x["upload_included"]),"excluded_source_files":sorted(cfg["exclude"]),"repo_id":cfg["repo"],"archive_status":"source_verified","authorized_metadata_replacement":"existing ModelScope initialization README replaced by WMKD_Benchmark formal model card with explicit user authorization","preserved_remote_files":[".gitattributes","configuration.json"],"created_at":now()}
 if role=="teacher": manifest["adapter_weight_sha256"]=cfg["weight_sha"]
 else: manifest["frozen_dataset_sha256"]=DATASET_SHA
 out=outdir(role); card=out/"README.md"; card.write_text(readme(role)); os.chmod(card,0o600); manifest["generated_readme"]={"bytes":card.stat().st_size,"sha256":sha(card)}
 mp=out/"WMKD_ARTIFACT_MANIFEST.json"; write(mp,manifest); sums=out/"SHA256SUMS"; sums.write_text("".join(f"{x['sha256']}  {x['path']}\n" for x in rows)+f"{sha(card)}  README.md\n"); os.chmod(sums,0o600)
 result={"phase":"preflight","role":role,"repo":repo,"source_path":str(source),"source_file_count":len(rows),"source_total_bytes":manifest["total_bytes"],"upload_source_bytes":manifest["upload_source_bytes"],"source_manifest":str(mp),"source_manifest_sha256":sha(mp),"source_files":rows}; write(out/"preflight.json",result); return result
def upload(role):
 pre=audit(role,True); cfg=ROLES[role]; out=outdir(role); mp=Path(pre["source_manifest"]); manifest=json.loads(mp.read_text()); api=client(); started=now(); wall=time.monotonic(); retries=0; uploaded=[]
 queue=[(cfg["source"]/x["path"],x["path"],x["bytes"],x["sha256"]) for x in manifest["files"] if x["upload_included"]]
 queue += [(out/"README.md","README.md",(out/"README.md").stat().st_size,sha(out/"README.md")),(mp,"wmkd_metadata/WMKD_ARTIFACT_MANIFEST.json",mp.stat().st_size,sha(mp)),(out/"SHA256SUMS","wmkd_metadata/SHA256SUMS",(out/"SHA256SUMS").stat().st_size,sha(out/"SHA256SUMS"))]
 for src,name,size,digest in queue:
  began=time.monotonic(); err=None
  for attempt in (1,2):
   try: api.upload_file(cfg["repo"],"model",src,name,commit_message=f"Archive canonical CTCC {role}: {name}",buffer_size_mb=64,disable_tqdm=False); err=None; break
   except Exception as exc:
    err=exc
    if attempt==1: retries+=1; time.sleep(5)
  if err: raise err
  elapsed=time.monotonic()-began; uploaded.append({"path":name,"bytes":size,"sha256":digest,"elapsed_seconds":elapsed,"MB_per_second":size/1e6/elapsed if elapsed else None}); print(json.dumps(uploaded[-1]),flush=True)
 remote=files(api,cfg["repo"]); expected={name:{"bytes":size,"sha256":digest} for _,name,size,digest in queue}; missing=[]; mismatched=[]; hashes=0
 for name,row in expected.items():
  item=remote.get(name)
  if item is None: missing.append(name); continue
  if int(getattr(item,"size",-1))!=row["bytes"]: mismatched.append(name)
  rh=remote_hash(item)
  if rh:
   if rh!=row["sha256"]: raise RuntimeError(f"remote blob hash mismatch: {name}")
   hashes+=1
 allowed={".gitattributes","configuration.json"}; unexpected=sorted(set(remote)-set(expected)-allowed)
 if missing or mismatched or unexpected: raise RuntimeError(f"remote verification failed missing={missing} size={mismatched} unexpected={unexpected}")
 elapsed=time.monotonic()-wall; result={"role":role,"repo_id":cfg["repo"],"private":True,"upload_exit_code":0,"upload_start":started,"upload_end":now(),"duration_seconds":elapsed,"throughput_MB_per_second":sum(x["bytes"] for x in uploaded)/1e6/elapsed,"uploaded":uploaded,"retries":retries,"source_file_count":manifest["file_count"],"source_total_bytes":manifest["total_bytes"],"source_manifest":str(mp),"source_manifest_sha256":sha(mp),"remote_total_file_count":len(remote),"remote_expected_file_count":len(expected),"remote_expected_bytes":sum(x["bytes"] for x in expected.values()),"remote_size_verification":"passed","remote_blob_hash_metadata_verified_count":hashes,"missing_files":missing,"unexpected_files":unexpected,"authorized_metadata_replacement":manifest["authorized_metadata_replacement"],"preserved_remote_files":manifest["preserved_remote_files"],"artifact_state":"uploaded_to_modelscope_awaiting_destination_hash_verification","destination_verified":False}; write(out/"upload_verification_summary.json",result); return result
def main():
 p=argparse.ArgumentParser(); p.add_argument("action",choices=("check-repositories","preflight","upload")); p.add_argument("role",nargs="?",choices=("teacher","student")); a=p.parse_args()
 if a.action=="check-repositories": value=[repo_check(client(),ROLES[r]["repo"]) for r in ("teacher","student")]
 else:
  if not a.role:p.error("role required")
  value=audit(a.role,True) if a.action=="preflight" else upload(a.role)
 print(json.dumps(value,indent=2,sort_keys=True)); return 0
if __name__=="__main__": raise SystemExit(main())
