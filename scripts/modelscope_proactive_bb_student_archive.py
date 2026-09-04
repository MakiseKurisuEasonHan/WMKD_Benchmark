#!/usr/bin/env python3
"""Archive and independently verify one final proactive Bb Student model."""
from __future__ import annotations
import argparse, hashlib, json, os, re, shutil, stat, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
from modelscope_hub.api import HubApi

SECRET=Path("/root/autodl-tmp/WMKD_Benchmark_data/secrets/modelscope.env")
LICENSE=Path("/root/autodl-tmp/WMKD_Benchmark_data/models/base/Llama-3.2-3B-Instruct/LICENSE.txt")
MODEL={"config.json","generation_config.json","model-00001-of-00002.safetensors","model-00002-of-00002.safetensors","model.safetensors.index.json","special_tokens_map.json","tokenizer.json","tokenizer_config.json"}
def sha(p):
 h=hashlib.sha256();
 with Path(p).open("rb") as f:
  for b in iter(lambda:f.read(8<<20),b""):h.update(b)
 return h.hexdigest()
def write(p,v):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
def creds():
 if not SECRET.is_file() or stat.S_IMODE(SECRET.stat().st_mode)!=0o600:raise RuntimeError("CREDENTIAL_GATE")
 v=dict(x.split("=",1) for x in SECRET.read_text().splitlines() if x and not x.startswith("#") and "=" in x)
 if v.get("MODELSCOPE_NAMESPACE")!="MakiseKurisuEasonHan" or not v.get("MODELSCOPE_API_TOKEN"):raise RuntimeError("CREDENTIAL_IDENTITY_GATE")
 return v
def private(r):
 v=getattr(getattr(r,"visibility",None),"value",getattr(r,"visibility",None));return getattr(r,"private",None) is True or v in (1,"private","PRIVATE")
def scan(root):
 pat=re.compile(r"BEGIN [A-Z ]*PRIVATE KEY|(?:api[_-]?key|token|secret|password)\s*[:=]\s*['\"]?[A-Za-z0-9_-]{16,}",re.I)
 for p in Path(root).iterdir():
  if p.is_file() and p.suffix not in {".safetensors",".bin"} and pat.search(p.read_text(errors="replace")):raise RuntimeError(f"SECRET_SCAN {p.name}")
def main():
 p=argparse.ArgumentParser();p.add_argument("--method",required=True);p.add_argument("--run-id",required=True);p.add_argument("--source",type=Path,required=True);p.add_argument("--dataset-sha",required=True);p.add_argument("--repo",required=True);p.add_argument("--run-root",type=Path,required=True);p.add_argument("--output",type=Path,required=True);a=p.parse_args()
 names={x.name for x in a.source.iterdir() if x.is_file()};expected=MODEL|{"training_args.bin"}
 if names!=expected:raise RuntimeError(f"SOURCE_FILE_SET {sorted(names)}")
 hashes={n:sha(a.source/n) for n in sorted(MODEL)};sizes={n:(a.source/n).stat().st_size for n in sorted(MODEL)}
 reload=json.loads((a.run_root/"metrics/reload_validation.json").read_text());student=json.loads((a.run_root/"student_manifest.json").read_text())
 if reload["status"]!="PASS" or student["dataset_sha256"]!=a.dataset_sha:raise RuntimeError("RELOAD_OR_DATASET_GATE")
 stamp=datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S");work=Path("/root/autodl-tmp/WMKD_Benchmark_data/tmp")/f"modelscope_upload_{a.method}_bb_student_{stamp}";package=work/"package";package.mkdir(parents=True)
 for n in MODEL:os.link(a.source/n,package/n)
 shutil.copyfile(LICENSE,package/"LICENSE.txt");(package/"NOTICE").write_text("Llama 3.2 is licensed under the Llama 3.2 Community License, Copyright © Meta Platforms, Inc. All Rights Reserved.\n",encoding="utf-8")
 shutil.copyfile(a.run_root/"student_manifest.json",package/"WMKD_STUDENT_MANIFEST.json");shutil.copyfile(a.run_root/"metrics/reload_validation.json",package/"RELOAD_VALIDATION.json")
 (package/"README.md").write_text(f"# Llama 3.2 WMKD {a.method} Bb Student\n\nBuilt with Llama. Private inference-ready archive; no dataset, checkpoint, optimizer, scheduler, cache, log, credential, detector secret, or watermark key is included.\n",encoding="utf-8")
 manifest={"schema_version":"wmkd.proactive-bb-student-archive.v1","method":a.method,"experiment":"Bb","run_id":a.run_id,"repository":a.repo,"visibility":"PRIVATE","base_revision":"0cb88a4f764b7a12671c53f0838cd831a0843b95","dataset_sha256":a.dataset_sha,"source_model_files":{n:{"size":sizes[n],"sha256":hashes[n]} for n in sorted(MODEL)},"explicitly_excluded":["training_args.bin","checkpoints","optimizer","scheduler","dataset","cache","logs","credentials","detector secrets","watermark keys"],"created_at":datetime.now(timezone.utc).isoformat()};write(package/"manifest.json",manifest)
 (package/"SHA256SUMS").write_text("".join(f"{sha(x)}  {x.name}\n" for x in sorted(package.iterdir()) if x.name!="SHA256SUMS"),encoding="utf-8");scan(package)
 api=HubApi(token=creds()["MODELSCOPE_API_TOKEN"]);exists=api.repo_exists(a.repo,"model")
 if exists and not private(api.get_repo(a.repo,"model")):raise RuntimeError("REPOSITORY_NOT_PRIVATE")
 if not exists:api.create_repo(a.repo,"model",visibility=1,description=f"Private WMKD {a.method} Bb final Student; Built with Llama")
 if not private(api.get_repo(a.repo,"model")):raise RuntimeError("PRIVATE_NOT_CONFIRMED_BEFORE_UPLOAD")
 remote={x.path for x in api.list_repo_files(a.repo,"model",recursive=True) if not x.is_dir};wanted={x.name for x in package.iterdir()}
 if not wanted.issubset(remote):api.upload_folder(a.repo,"model",package,path_in_repo="",commit_message=f"Archive {a.method} Bb final Student",disable_tqdm=True,sync_remote_repo=False)
 verify=Path("/root/autodl-tmp/WMKD_Benchmark_data/tmp")/f"modelscope_verify_{a.method}_bb_student_{stamp}";download=Path(api.download_repo(a.repo,"model",local_dir=verify,local_files_only=False,max_workers=4));actual={x.name for x in download.iterdir() if x.is_file() and x.name not in {".gitattributes",".mdlignore"}}
 if actual!=wanted:raise RuntimeError(f"REDOWNLOAD_FILE_SET expected={sorted(wanted)} actual={sorted(actual)}")
 for n in wanted:
  if (package/n).stat().st_size!=(download/n).stat().st_size or sha(package/n)!=sha(download/n):raise RuntimeError(f"REDOWNLOAD_HASH {n}")
 redownload_reload=verify/"reload_validation.json";redownload_manifest=verify/"student_manifest.json"
 subprocess.run([sys.executable,"/root/autodl-tmp/WMKD_Benchmark/scripts/passive5_shared_bb3_reload.py","--student",str(download),"--dataset-sha",a.dataset_sha,"--output",str(redownload_reload),"--manifest",str(redownload_manifest)],check=True)
 result={"status":"COMPLETED","repository":a.repo,"visibility":"PRIVATE","source_file_count":len(expected),"uploaded_files":sorted(wanted),"training_args_excluded":True,"verification_directory":str(download),"filename_size_sha_match":True,"redownload_reload":"PASS","canonical_source_preserved":a.source.is_dir(),"token_emitted":False};write(a.output,result);print(json.dumps(result,indent=2))
if __name__=="__main__":main()
