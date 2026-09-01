"""Supervised ModelScope archive of the immutable SCW Ba Student."""
from __future__ import annotations
import hashlib, json, os, time, traceback
from datetime import datetime, timezone
from pathlib import Path
from modelscope_hub.api import HubApi

DATA=Path("/root/autodl-tmp/WMKD_Benchmark_data")
PROJECT=Path("/root/autodl-tmp/WMKD_Benchmark")
RUN_ID="scw_ba_full_20260831_193828_cont1"
SOURCE=DATA/f"runs/scw/ba/{RUN_ID}/student/final_model"
SUMMARY=DATA/f"runs/scw/ba/{RUN_ID}/summary.json"
TRAINING=DATA/f"runs/scw/ba/{RUN_ID}/metrics/training_telemetry.json"
CONFIG=PROJECT/"configs/distillation/scw_ba_direct.yaml"
OUT=DATA/"artifacts/transfers/modelscope/scw_ba_student_upload_20260901"
REPO="MakiseKurisuEasonHan/WMKD-SCW-Ba-Student"
FILES=("config.json","generation_config.json","tokenizer.json","tokenizer_config.json",
       "special_tokens_map.json","chat_template.jinja","model.safetensors.index.json",
       "model-00001-of-00002.safetensors","model-00002-of-00002.safetensors")
FROZEN_SHA="a8c93d4fc55521abe6abab48aa67cc06a6251ce769caa913bd24adfebb87b05c"
REVISION="0cb88a4f764b7a12671c53f0838cd831a0843b95"

def now(): return datetime.now(timezone.utc).isoformat()
def sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda:f.read(16*1024*1024),b""): h.update(chunk)
    return h.hexdigest()
def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True); tmp=path.with_suffix(path.suffix+".tmp")
    tmp.write_text(json.dumps(value,indent=2,sort_keys=True)+"\n",encoding="utf-8"); os.replace(tmp,path)
def private(repo):
    visibility=getattr(getattr(repo,"visibility",None),"value",getattr(repo,"visibility",None))
    return getattr(repo,"private",None) is True or visibility==1 or str(visibility).lower()=="private"
def remote_rows(api):
    rows={}
    for item in api.list_repo_files(REPO,"model",recursive=True):
        if getattr(item,"is_dir",False): continue
        lfs=getattr(item,"lfs",None); identity=getattr(item,"sha256",None)
        if not identity and isinstance(lfs,dict): identity=lfs.get("sha256") or lfs.get("oid")
        rows[item.path]={"bytes":int(item.size),"metadata_identity":identity}
    return rows

def source_rows():
    rows=[]
    for name in FILES:
        path=SOURCE/name
        if not path.is_file(): raise RuntimeError(f"missing source file: {name}")
        rows.append({"path":name,"bytes":path.stat().st_size,"sha256":sha(path)})
    unexpected=sorted(p.name for p in SOURCE.iterdir() if p.is_file() and p.name not in FILES and p.name!="training_args.bin")
    if unexpected: raise RuntimeError(f"unexpected Student artifact files: {unexpected}")
    return rows

def main():
    OUT.mkdir(parents=True,exist_ok=True); status_path=OUT/"status.json"
    status={"status":"source_verification","repo":REPO,"start":now(),"retries":0,"uploaded_files":0,"uploaded_bytes":0,"destination_verified":False}
    write(status_path,status)
    try:
        summary=json.loads(SUMMARY.read_text()); training=json.loads(TRAINING.read_text()); config=json.loads(CONFIG.read_text())
        if summary.get("status")!="COMPLETED" or summary["dataset"]["sha256"]!=FROZEN_SHA: raise RuntimeError("Ba summary provenance drift")
        if training.get("steps")!=7500 or not training.get("finite_loss"): raise RuntimeError("Student training provenance drift")
        rows=source_rows(); total=sum(r["bytes"] for r in rows)
        index=json.loads((SOURCE/"model.safetensors.index.json").read_text())
        manifest={"schema_version":1,"artifact":"SCW Ba standardized direct-distillation Student","method":"SCW","experiment":"Ba",
          "source_run_id":RUN_ID,"source_path":str(SOURCE),"scientific_status":"BA_COMPLETED",
          "canonical_backbone":"meta-llama/Llama-3.2-3B-Instruct","canonical_backbone_revision":REVISION,
          "student_initialization":"fresh_canonical","frozen20k_sha256":FROZEN_SHA,
          "training_config":config["training"],"training_config_sha256":sha(CONFIG),
          "training_telemetry_sha256":sha(TRAINING),"optimizer_steps":7500,"epochs":3,
          "config_identity_sha256":sha(SOURCE/"config.json"),"tokenizer_identity_sha256":sha(SOURCE/"tokenizer.json"),
          "safetensors_index_sha256":sha(SOURCE/"model.safetensors.index.json"),
          "safetensors_shards":sorted({v for v in index["weight_map"].values()}),
          "indexed_tensor_count":len(index["weight_map"]),"declared_tensor_bytes":index.get("metadata",{}).get("total_size"),
          "file_count":len(rows),"total_bytes":total,"files":rows,"excluded_files":["training_args.bin"],
          "created_at":now(),"source_status":"VERIFIED","source_modified":False}
        manifest_path=OUT/"WMKD_ARTIFACT_MANIFEST.json"
        if manifest_path.exists():
            old=json.loads(manifest_path.read_text()); comparable={k:v for k,v in manifest.items() if k!="created_at"}; old_comparable={k:v for k,v in old.items() if k!="created_at"}
            if comparable!=old_comparable: raise RuntimeError("existing immutable source manifest drift")
            manifest=old
        else: write(manifest_path,manifest)
        (OUT/"SHA256SUMS").write_text("".join(f"{r['sha256']}  {r['path']}\n" for r in rows),encoding="utf-8")
        status.update(status="repo_preflight",source_files=len(rows),source_bytes=total,source_manifest=str(manifest_path),source_manifest_sha256=sha(manifest_path)); write(status_path,status)
        api=HubApi(); created=False
        if not api.repo_exists(REPO,"model"):
            api.create_repo(REPO,"model",visibility=1,description="WMKD_Benchmark SCW Ba standardized direct-distillation Student; bounded Base-like negative detector result."); created=True
        repo=api.get_repo(REPO,"model")
        if not private(repo): raise RuntimeError("destination repository is not private")
        existing=remote_rows(api); bootstrap={".gitattributes","README.md"}; unknown=sorted(set(existing)-set(FILES)); conflicts=sorted(set(existing)&set(FILES))
        if set(unknown)-bootstrap or conflicts: raise RuntimeError(f"destination is not empty: unknown={unknown}, conflicts={conflicts}")
        status.update(status="uploading",repo_created=created,private=True,upload_start=now(),existing_files=unknown,bootstrap_metadata_verified=set(unknown)<=bootstrap); write(status_path,status)
        for row in rows:
            for attempt in (1,2):
                try:
                    api.upload_file(REPO,"model",SOURCE/row["path"],row["path"],commit_message="Archive immutable SCW Ba distilled Student")
                    break
                except Exception:
                    if attempt==2: raise
                    status["retries"]+=1; status["last_retry_file"]=row["path"]; write(status_path,status); time.sleep(10)
            status["uploaded_files"]+=1; status["uploaded_bytes"]+=row["bytes"]; status["last_uploaded"]=row["path"]; write(status_path,status)
        status.update(status="remote_verification",upload_end=now()); write(status_path,status)
        repo=api.get_repo(REPO,"model")
        if not private(repo): raise RuntimeError("destination lost private visibility")
        remote=remote_rows(api); intended={name:remote.get(name) for name in FILES}
        for row in rows:
            got=intended[row["path"]]
            if not got or got["bytes"]!=row["bytes"]: raise RuntimeError(f"remote filename/size mismatch: {row['path']}")
        verified_bytes=sum(v["bytes"] for v in intended.values()); metadata_count=sum(bool(v.get("metadata_identity")) for v in intended.values())
        result={"overall_status":"COMPLETE","repo":REPO,"private":True,"authenticated_user":"MakiseKurisuEasonHan",
          "source_path":str(SOURCE),"source_manifest":str(manifest_path),"source_manifest_sha256":sha(manifest_path),
          "source_files":len(rows),"source_bytes":total,"uploaded_files":len(rows),"uploaded_bytes":total,
          "remote_verified_files":len(rows),"remote_verified_bytes":verified_bytes,"filename_verification":"PASS","size_verification":"PASS",
          "remote_metadata_verification":"PASS","metadata_identity_available_files":metadata_count,
          "archive_status":"uploaded_to_modelscope_awaiting_destination_hash_verification","destination_verified":False,
          "retries":status["retries"],"errors":[],"upload_start":status["upload_start"],"upload_end":status["upload_end"],
          "verification_end":now(),"source_modified":False,"scientific_result":"lost_or_moved_to_base_regime"}
        write(OUT/"upload_verification_summary.json",result); status.update(status="completed",end=now(),result=str(OUT/"upload_verification_summary.json"),remote_verified_files=len(rows),remote_verified_bytes=verified_bytes); write(status_path,status)
        print("SCW_BA_STUDENT_MODELSCOPE_ARCHIVE_COMPLETE",flush=True)
    except Exception as exc:
        status.update(status="failed",end=now(),error=f"{type(exc).__name__}: {exc}",traceback=traceback.format_exc()); write(status_path,status); raise
if __name__=="__main__": main()
