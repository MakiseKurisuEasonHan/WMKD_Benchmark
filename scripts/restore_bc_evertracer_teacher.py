"""Restore only missing original Teacher shards; expected historical SHA is binding."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import time
import modelscope_passive5_ba_student_archive as helper

P=Path('/root/autodl-tmp/WMKD_Benchmark')
Q=P/'results/logit_distillation/same_lineage_bc/evertracer'
M=json.loads((Q/'teacher_source_manifest.json').read_text())
ROOT=Path(M['output'])
REPO='MakiseKurisuEasonHan/WMKD-EverTracer-A-Teacher'
receipt={'status':'RUNNING','repo':REPO,'retrieval_ref':'master','identity_basis':'original frozen per-file SHA256, not mutable branch name','pid':os.getpid(),'files':[]}
def save():
    p=Q/'teacher_restore_receipt.json';t=p.with_suffix('.tmp')
    t.write_text(json.dumps(receipt,indent=2)+'\n');os.replace(t,p)
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(8<<20),b''):h.update(b)
    return h.hexdigest()
def main():
    api=helper.api_client();assert helper.is_private(api.get_repo(REPO,'model'))
    remote={f.path:f for f in api.list_repo_files(REPO,'model',revision='master',recursive=True) if not f.is_dir}
    need=[x for x in M['files'] if not (ROOT/x['path']).exists()]
    assert shutil.disk_usage(ROOT).free>sum(x['bytes'] for x in need)+(2<<30)
    for x in M['files']:
        n=x['path'];assert Path(n).name==n
        p=ROOT/n;rf=remote[n];lfs=rf.lfs or {}
        identity=lfs.get('sha256') or str(lfs.get('oid','')).removeprefix('sha256:') or rf.sha256
        assert rf.size==x['bytes'] and identity==x['sha256']
        if not p.exists():
            assert n.endswith('.safetensors')
            part=p.with_name(n+'.bc-restore-partial');assert not part.exists()
            h=hashlib.sha256();count=0;last=time.monotonic()
            response=api.downloader._client.download_stream(REPO,'model',n,'master',headers=api.downloader._build_download_headers())
            response.raise_for_status()
            with response,part.open('xb') as out:
                for b in response.iter_content(chunk_size=2<<20):
                    if not b:continue
                    count+=len(b);assert count<=x['bytes'];h.update(b);out.write(b)
                    if time.monotonic()-last>15:
                        receipt.update(current_file=n,received_bytes=count);save();last=time.monotonic()
                out.flush();os.fsync(out.fileno())
            assert count==x['bytes'] and h.hexdigest()==x['sha256'];part.rename(p)
        assert not p.is_symlink() and p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
        receipt['files'].append(dict(x,verified=True));save()
    receipt.update(status='PASS',current_file=None);save()
if __name__=='__main__':
    save()
    try:main()
    except Exception as exc:
        receipt.update(status='ERROR_REVIEW_REQUIRED',error=type(exc).__name__+': '+str(exc));save();raise
