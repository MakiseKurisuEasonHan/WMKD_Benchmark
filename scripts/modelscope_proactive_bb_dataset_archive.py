#!/usr/bin/env python3
"""Archive one proactive Bb processed20k to PRIVATE ModelScope and verify redownload."""
from __future__ import annotations
import argparse, json, os, re, shutil, stat
from datetime import datetime, timezone
from pathlib import Path
from modelscope_hub.api import HubApi
from passive5_shared_bb import atomic_json, file_sha256, read_jsonl, records_sha256

REQUIRED={"sample_id","instruction","input","source_answer","source_answer_sha256","paraphrased_answer","paraphrased_answer_sha256","source_answer_token_count","processing_mode"}
SECRET=Path("/root/autodl-tmp/WMKD_Benchmark_data/secrets/modelscope.env")

def creds():
    if not SECRET.is_file() or stat.S_IMODE(SECRET.stat().st_mode)!=0o600: raise RuntimeError("MODELSCOPE_CREDENTIAL_GATE")
    v=dict(line.split("=",1) for line in SECRET.read_text().splitlines() if line and not line.startswith("#") and "=" in line)
    if v.get("MODELSCOPE_NAMESPACE")!="MakiseKurisuEasonHan" or not v.get("MODELSCOPE_API_TOKEN"): raise RuntimeError("MODELSCOPE_IDENTITY_GATE")
    return v
def private(repo):
    vis=getattr(getattr(repo,"visibility",None),"value",getattr(repo,"visibility",None))
    return getattr(repo,"private",None) is True or vis in (1,"private","PRIVATE")
def validate(path):
    rows=read_jsonl(path)
    if len(rows)!=20000 or any(REQUIRED-set(r) for r in rows): raise RuntimeError("DATASET_COUNT_OR_SCHEMA_GATE")
    if len({r["sample_id"] for r in rows})!=20000: raise RuntimeError("DUPLICATE_SAMPLE_IDS")
    return {"record_count":20000,"file_sha256":file_sha256(path),"content_sha256":records_sha256(rows),"sample_ids_sha256":records_sha256([{"sample_id":r["sample_id"]} for r in rows]),"schema":sorted(REQUIRED)}
def secret_scan(path):
    text=Path(path).read_text(encoding="utf-8",errors="replace")
    patterns=(r"BEGIN [A-Z ]*PRIVATE KEY",r"ghp_[A-Za-z0-9]{20,}",r"github_pat_[A-Za-z0-9_]{20,}",r"hf_[A-Za-z0-9]{20,}",r"sk-[A-Za-z0-9]{20,}")
    hits=[pattern for pattern in patterns if re.search(pattern,text,re.I)]
    if hits:raise RuntimeError(f"SECRET_SCAN_FAILED {hits}")
    return {"status":"PASS","hits":0}
def main():
    p=argparse.ArgumentParser();p.add_argument("--method",required=True);p.add_argument("--run-id",required=True);p.add_argument("--source",type=Path,required=True);p.add_argument("--config",type=Path,required=True);p.add_argument("--repo",required=True);p.add_argument("--output",type=Path,required=True);a=p.parse_args()
    source=validate(a.source);source["secret_scan"]=secret_scan(a.source);cfg=json.loads(a.config.read_text());api=HubApi(token=creds()["MODELSCOPE_API_TOKEN"]);exists=api.repo_exists(a.repo,"dataset")
    if exists and not private(api.get_repo(a.repo,"dataset")): raise RuntimeError("REPOSITORY_NOT_PRIVATE")
    stamp=datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S");work=Path("/root/autodl-tmp/WMKD_Benchmark_data/tmp")/f"modelscope_upload_{a.method}_bb_{stamp}";package=work/"package";package.mkdir(parents=True)
    shutil.copyfile(a.source,package/"frozen_paired_qa.jsonl")
    manifest={"schema_version":"wmkd.proactive-bb-processed20k-archive.v1","method":a.method,"experiment":"Bb","run_id":a.run_id,"repository":a.repo,"visibility":"PRIVATE","parent":cfg["source_dataset"],"processed20k":source,"prompt_sha256":cfg["paraphrase"]["prompt_sha256"],"created_at":datetime.now(timezone.utc).isoformat(),"token_emitted":False}
    atomic_json(package/"manifest.json",manifest);(package/"README.md").write_text(f"# WMKD_Benchmark {a.method} Bb processed20k\n\nPrivate transport archive. Verify manifest and SHA256SUMS before use.\n",encoding="utf-8",newline="\n")
    names=("frozen_paired_qa.jsonl","manifest.json","README.md");(package/"SHA256SUMS").write_text("".join(f"{file_sha256(package/n)}  {n}\n" for n in names),encoding="utf-8",newline="\n")
    if not exists: api.create_repo(a.repo,"dataset",visibility=1,description=f"Private WMKD_Benchmark {a.method} Bb processed20k");exists=False
    if not private(api.get_repo(a.repo,"dataset")): raise RuntimeError("PRIVATE_NOT_CONFIRMED_BEFORE_UPLOAD")
    remote_files=sorted(x.path for x in api.list_repo_files(a.repo,"dataset",recursive=True) if not x.is_dir)
    expected={"README.md","SHA256SUMS","frozen_paired_qa.jsonl","manifest.json"}
    if not expected.issubset(set(remote_files)):
        api.upload_folder(a.repo,"dataset",package,path_in_repo="",commit_message=f"Archive {a.method} Bb processed20k",disable_tqdm=True,sync_remote_repo=False)
    verify=Path("/root/autodl-tmp/WMKD_Benchmark_data/tmp")/f"modelscope_verify_{a.method}_bb_{stamp}";download=Path(api.download_repo(a.repo,"dataset",local_dir=verify,local_files_only=False,max_workers=4));restored=validate(download/"frozen_paired_qa.jsonl")
    restored["secret_scan"]=secret_scan(download/"frozen_paired_qa.jsonl")
    if restored!=source or json.loads((download/"manifest.json").read_text())!=manifest: raise RuntimeError("INDEPENDENT_REDOWNLOAD_GATE")
    result={"status":"COMPLETED","repository":a.repo,"visibility":"PRIVATE","uploaded_files":sorted(expected),"source_validation":source,"redownload_validation":restored,"byte_identical":True,"verification_directory":str(download),"canonical_source_preserved":a.source.is_file(),"token_emitted":False}
    a.output.parent.mkdir(parents=True,exist_ok=True);atomic_json(a.output,result);print(json.dumps(result,indent=2))
if __name__=="__main__":main()
