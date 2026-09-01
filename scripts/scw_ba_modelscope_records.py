"""Persist verified SCW Ba Student ModelScope archive metadata."""
import json, shutil
from pathlib import Path
P=Path("/root/autodl-tmp/WMKD_Benchmark"); D=Path("/root/autodl-tmp/WMKD_Benchmark_data")
RUN=D/"runs/scw/ba/scw_ba_full_20260831_193828_cont1"; TRANSFER=D/"artifacts/transfers/modelscope/scw_ba_student_upload_20260901"
RESULT=P/"results/scw/experiment_ba"; MARKER="SCW_BA_STUDENT_MODELSCOPE_ARCHIVE_20260901"
def write(path,value):
    tmp=path.with_suffix(path.suffix+".tmp"); tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); tmp.replace(path)
def append_once(path,text):
    old=path.read_text(encoding="utf-8") if path.exists() else ""
    if MARKER not in old: path.parent.mkdir(parents=True,exist_ok=True); path.write_text(old.rstrip()+"\n\n"+text.strip()+"\n",encoding="utf-8")
def main():
    v=json.loads((TRANSFER/"upload_verification_summary.json").read_text())
    for key,value in {"overall_status":"COMPLETE","private":True,"filename_verification":"PASS","size_verification":"PASS","remote_metadata_verification":"PASS","destination_verified":False}.items():
        if v.get(key)!=value: raise RuntimeError(f"archive verification mismatch: {key}")
    archive={"modelscope_repo":v["repo"],"visibility":"private","archive_status":v["archive_status"],"source_manifest_sha256":v["source_manifest_sha256"],"source_files":v["source_files"],"source_bytes":v["source_bytes"],"uploaded_files":v["uploaded_files"],"uploaded_bytes":v["uploaded_bytes"],"remote_verified_files":v["remote_verified_files"],"remote_verified_bytes":v["remote_verified_bytes"],"filename_verification":"PASS","size_verification":"PASS","remote_metadata_verification":"PASS","metadata_identity_available_files":v["metadata_identity_available_files"],"destination_verified":False,"retries":v["retries"],"errors":v["errors"],"scientific_role":"standardized direct-distillation Student"}
    for path in (RUN/"summary.json",RESULT/"summary.json"):
        s=json.loads(path.read_text());
        if s.get("status")!="COMPLETED" or s.get("conclusion")!="lost_or_moved_to_base_regime": raise RuntimeError("Ba scientific summary drift")
        s["modelscope_student_archive"]=archive; write(path,s)
    section=f"""## ModelScope Student archive

<!-- {MARKER} -->
The immutable final Student was uploaded to private ModelScope repo `MakiseKurisuEasonHan/WMKD-SCW-Ba-Student`. Remote filename, size, and ModelScope metadata identity checks passed for {v['remote_verified_files']}/{v['source_files']} files and {v['remote_verified_bytes']}/{v['source_bytes']} bytes. Source manifest SHA256 is `{v['source_manifest_sha256']}`. Archive status is `{v['archive_status']}` with `destination_verified=false` because no complete destination redownload and independent SHA256 comparison was performed. Scientific results and the bounded Base-like negative-regime conclusion are unchanged.
"""
    for path in (RUN/"final_report.md",P/"docs/reproduction_reports/scw_experiment_ba_report.md"): append_once(path,section)
    record=f"""## SCW Ba Student ModelScope archive

<!-- {MARKER} -->
The immutable SCW Ba Student from `scw_ba_full_20260831_193828_cont1` was archived to private repo `MakiseKurisuEasonHan/WMKD-SCW-Ba-Student`. Upload and remote filename/size/metadata verification passed for {v['remote_verified_files']} files and {v['remote_verified_bytes']} bytes. Source manifest SHA256 `{v['source_manifest_sha256']}`; status `{v['archive_status']}`; `destination_verified=false`. The bounded scientific result remains loss of detectable SCW watermark under the tested standardized Ba condition with the Student in a Base-like negative detector regime. Next step: SCW final closure / commit review; no cleanup was performed.
"""
    for rel in ("PROJECT_STATUS.md","TODO.md","DECISIONS.md","EXPERIMENT_LOG.md","CODEX_LOG.md","docs/experiment_logs/scw_experiment_a_log.md"): append_once(P/rel,record)
    archive_dir=RESULT/"archive"; archive_dir.mkdir(parents=True,exist_ok=True)
    shutil.copy2(TRANSFER/"WMKD_ARTIFACT_MANIFEST.json",archive_dir/"scw_ba_student_modelscope_source_manifest.json")
    shutil.copy2(TRANSFER/"upload_verification_summary.json",archive_dir/"scw_ba_student_modelscope_verification.json")
if __name__=="__main__": main()
