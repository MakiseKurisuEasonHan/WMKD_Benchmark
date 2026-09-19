"""Delete only this campaign's reproducible raw logits after final model checks."""
import json,subprocess,shutil,time
from pathlib import Path
from pnfp_7b_distill_campaign import sha,put
P=Path('/root/autodl-tmp/WMKD_Benchmark');E=P/'results/awm/scale_7b';O=P.parent/'WMKD_Benchmark_data/awm_7b'
def load(p):return json.loads(p.read_text())
def main():
    if (E/'logit_cleanup_receipt.json').exists():return
    assert load(E/'terminal.json')['status']=='COMPLETED'
    assert not subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader'],text=True).strip()
    for stage in ['direct','paraphrase','logit']:
        assert (E/(stage+'_detector.json')).is_file() and (E/(stage+'_utility.json')).is_file()
        for x in load(O/stage/'final_manifest.json')['files']:
            file=O/stage/'final_model'/x['path'];assert file.stat().st_size==x['bytes'] and sha(file)==x['sha256']
    rawroot=O/'logit_cache';assert not rawroot.is_symlink()
    root=rawroot.resolve();assert root==rawroot.absolute() and root.parent==O.resolve()
    manifest=load(root/'manifest.json');assert manifest['complete']
    assert sha(root/'manifest.json')==sha(E/'logit_manifest.json')
    plan=[]
    for x in manifest['shards']:
        assert Path(x['path']).name==x['path'] and x['path'].endswith('.bf16')
        file=root/x['path'];assert file.resolve().parent==root and not file.is_symlink()
        assert file.stat().st_size==x['bytes'] and sha(file)==x['sha256']
        plan.append(dict(path=str(file),bytes=x['bytes'],sha256=x['sha256'],classification='DELETE_REGENERABLE_RAW_LOGIT_ONLY'))
    put(E/'logit_cleanup_dry_run.json',dict(paths=plan,disk_before=shutil.disk_usage(O)._asdict(),final_models_verified=True))
    for x in plan:Path(x['path']).unlink()
    put(E/'logit_cleanup_receipt.json',dict(deleted=plan,reclaimed_bytes=sum(x['bytes'] for x in plan),
        disk_after=shutil.disk_usage(O)._asdict(),manifests_datasets_models_retained=True,time=time.time(),auto_shutdown=False))
if __name__=='__main__':main()
