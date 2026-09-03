#!/usr/bin/env python3
"""Archive immutable proactive Ba frozen20k datasets to private ModelScope repos."""
from __future__ import annotations
import argparse, hashlib, json, os, shutil, stat
from datetime import datetime, timezone
from pathlib import Path
from modelscope_hub.api import HubApi

ROOT = Path("/root/autodl-tmp/WMKD_Benchmark_data")
SECRET = ROOT / "secrets/modelscope.env"
SPECS = {
 "evertracer": {"repo":"MakiseKurisuEasonHan/WMKD_Benchmark_evertracer_ba_frozen20k", "run":"evertracer_ba_20260829_124055", "teacher":"EverTracer A", "path":ROOT/"runs/evertracer_ba/evertracer_ba_20260829_124055/dataset/frozen_qa.jsonl", "content":"ca1aa9c991ae58e1d5bbf32275f1738786db15c337bc4bb80fdc0813aa447142"},
 "ctcc": {"repo":"MakiseKurisuEasonHan/WMKD_Benchmark_ctcc_ba_frozen20k", "run":"ctcc_ba_generation_20260829_195943_cont1", "teacher":"CTCC A", "path":ROOT/"runs/ctcc_ba/ctcc_ba_generation_20260829_195943_cont1/dataset/frozen_qa.jsonl", "content":"621c9aedcf3a4a1db86a4848bbf93fa893d18022f15b913e8aeeb28739412484"},
 "iseal": {"repo":"MakiseKurisuEasonHan/WMKD_Benchmark_iseal_ba_frozen20k", "run":"iseal_ba_generation_20260830_134058", "teacher":"iSeal A6", "path":ROOT/"runs/iseal_ba/iseal_ba_generation_20260830_134058/dataset/frozen_qa.jsonl", "content":"d51c22b9d33d4aa79b5cd733dd6bcb910ecd6378f1ffe2a40328e64cb085aacf"},
}
REQ={"sample_id","instruction","input","teacher_raw_answer"}
def is_private(repo):
 visibility=getattr(getattr(repo,"visibility",None),"value",getattr(repo,"visibility",None))
 return getattr(repo,"private",None) is True or visibility in (1,"private","PRIVATE")
def sha(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for b in iter(lambda:f.read(1<<20),b""): h.update(b)
 return h.hexdigest()
def inspect(p):
 rows=[]
 with p.open(encoding="utf-8") as f:
  for line in f:
   x=json.loads(line); assert set(x)==REQ; rows.append(x)
 assert len(rows)==20000 and len({x["sample_id"] for x in rows})==20000
 h=hashlib.sha256(); ih=hashlib.sha256()
 for x in rows:
  h.update((json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False)+"\n").encode())
  ih.update((json.dumps({"sample_id":x["sample_id"]},sort_keys=True,separators=(",",":"),ensure_ascii=False)+"\n").encode())
 content=h.hexdigest(); ids=ih.hexdigest()
 return {"count":len(rows),"file_sha256":sha(p),"content_sha256":content,"sample_ids_sha256":ids,"schema":sorted(REQ)}
def api():
 assert stat.S_IMODE(SECRET.stat().st_mode)==0o600
 vals=dict(line.split("=",1) for line in SECRET.read_text().splitlines() if "=" in line and not line.startswith("#"))
 return HubApi(token=vals["MODELSCOPE_API_TOKEN"])
def write(p,x):
 p.parent.mkdir(parents=True,exist_ok=True); t=p.with_suffix(p.suffix+".tmp"); t.write_text(json.dumps(x,indent=2)+"\n"); os.replace(t,p)
def main():
 a=argparse.ArgumentParser(); a.add_argument("method",choices=SPECS); ns=a.parse_args(); s=SPECS[ns.method]
 src=inspect(s["path"])
 if src["content_sha256"]!=s["content"]: raise RuntimeError("CONTENT_SHA_MISMATCH")
 client=api(); typ="dataset"; exists=client.repo_exists(s["repo"],typ)
 remote=[x.path for x in client.list_repo_files(s["repo"],typ,recursive=True)] if exists else []
 if set(remote)-{".gitattributes","README.md"}: raise RuntimeError("REMOTE_REPO_NONEMPTY_REFUSE")
 if not exists: client.create_repo(s["repo"],typ,visibility=1,description=f"Private immutable WMKD_Benchmark {ns.method} Ba frozen20k archive")
 if not is_private(client.get_repo(s["repo"],typ)): raise RuntimeError("REPO_NOT_PRIVATE")
 stamp=datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S"); pkg=ROOT/f"tmp/proactive_ba_archive_{ns.method}_{stamp}/package"; pkg.mkdir(parents=True)
 shutil.copyfile(s["path"],pkg/"frozen_qa.jsonl")
 manifest={"project":"WMKD_Benchmark","method":ns.method,"canonical_ba_run":s["run"],"parent_teacher":s["teacher"],"scientific_semantics":"unchanged canonical Ba frozen20k","source_validation":src,"created_at":datetime.now(timezone.utc).isoformat()}
 write(pkg/"manifest.json",manifest); (pkg/"README.md").write_text(f"# Private WMKD_Benchmark {ns.method} Ba frozen20k\n\nTransport backup only. Verify manifest and SHA256 before use.\n")
 (pkg/"SHA256SUMS").write_text("".join(f"{sha(pkg/n)}  {n}\n" for n in ["frozen_qa.jsonl","manifest.json","README.md"]))
 client.upload_folder(s["repo"],typ,pkg,path_in_repo="",commit_message=f"Archive canonical {ns.method} Ba frozen20k",disable_tqdm=True,sync_remote_repo=False)
 verify=ROOT/f"tmp/proactive_ba_verify_{ns.method}_{stamp}"; got=Path(client.download_repo(s["repo"],typ,local_dir=verify,local_files_only=False,max_workers=4)); dst=inspect(got/"frozen_qa.jsonl")
 if dst!=src or sha(got/"frozen_qa.jsonl")!=sha(s["path"]): raise RuntimeError("INDEPENDENT_REDOWNLOAD_MISMATCH")
 out={"status":"COMPLETED","archive_verified":True,"method":ns.method,"repository":s["repo"],"visibility":"PRIVATE","canonical_ba_run":s["run"],"parent_teacher":s["teacher"],"source":src,"redownload":dst,"byte_identical":True,"verification_directory":str(verify)}
 write(ROOT/f"manifests/proactive_{ns.method}_ba_frozen20k_modelscope_archive.json",out); print(json.dumps(out,indent=2))
if __name__=="__main__": main()
