"""Revision/SHA-pinned transport, and per-method package overlays."""
import urllib.request, hashlib, os, sys, json
from common import *

def model(c,repo,revision=None):
    from huggingface_hub import HfApi
    errors=[]; info=None
    for endpoint in ('https://hf-mirror.com','https://huggingface.co'):
        try: info=HfApi(endpoint=endpoint).model_info(repo,revision=revision,files_metadata=True); break
        except Exception as e: errors.append({'endpoint':endpoint,'error':type(e).__name__})
    if info is None: raise Blocked('BLOCKED_DOWNLOAD','Cannot resolve canonical revision: '+str(errors))
    dest=DATA/'models/methods_11_15'/(repo.replace('/','--')+('--'+revision.replace('/','_') if revision else '')); dest.mkdir(parents=True,exist_ok=True)
    siblings=info.siblings; use_safe=any(x.rfilename.endswith('.safetensors') for x in siblings)
    files=[x for x in siblings if '/' not in x.rfilename and (x.rfilename.endswith(('.json','.model','.txt','.tiktoken')) or x.rfilename in ('LICENSE','NOTICE') or x.rfilename.endswith('.safetensors') or (not use_safe and x.rfilename.endswith('.bin')))]
    if not any(x.rfilename.endswith(('.safetensors','.bin')) for x in files): raise Blocked('BLOCKED_DOWNLOAD','No canonical model weight files')
    import shutil
    missing_bytes=sum(x.size or 0 for x in files if not (dest/x.rfilename).exists())
    free=shutil.disk_usage(DATA).free
    if free < missing_bytes*3 + 8*2**30:
        raise Blocked('BLOCKED_STORAGE',f'Need download plus final/archive reserve {missing_bytes*3+8*2**30} bytes; free {free}; historical KEEP untouched')
    manifest={}
    for f in files:
        p=dest/f.rfilename
        def valid():
            if not p.is_file() or (f.size is not None and p.stat().st_size!=f.size): return False
            if f.lfs: return sha(p)==f.lfs.sha256
            raw=p.read_bytes(); return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==f.blob_id
        if not valid():
            urls=[f'https://modelscope.cn/models/{repo}/resolve/master/{f.rfilename}',f'https://hf-mirror.com/{repo}/resolve/{info.sha}/{f.rfilename}',f'https://huggingface.co/{repo}/resolve/{info.sha}/{f.rfilename}']
            for url in urls:
                try:
                    print('Downloading canonical file',repo,f.rfilename,'transport',url,flush=True)
                    temp=p.with_suffix(p.suffix+'.partial')
                    with urllib.request.urlopen(url,timeout=90) as r,temp.open('wb') as out:
                        total=0
                        while True:
                            block=r.read(8<<20)
                            if not block: break
                            out.write(block); total+=len(block)
                            if total%(128<<20)==0: print('download_bytes',f.rfilename,total,flush=True)
                    temp.replace(p)
                    if not valid(): raise ValueError('Canonical SHA mismatch; try next transport')
                    break
                except Exception as e: errors.append({'file':f.rfilename,'transport':url,'error':type(e).__name__})
            else: raise Blocked('BLOCKED_DOWNLOAD','No verified transport for '+f.rfilename+'; '+str(errors[-3:]))
        manifest[f.rfilename]={'size':p.stat().st_size,'sha256':sha(p),'canonical_git_blob':f.blob_id,'canonical_lfs_sha':f.lfs.sha256 if f.lfs else None}
    provenance={'canonical_upstream':repo,'revision':info.sha,'path':str(dest),'files':manifest,'transport_errors':errors}
    write(Path(c['run_root'])/'model_provenance.json',provenance); return provenance

def overlay(c,packages):
    target=Path(c['run_root'])/'runtime_overlay'; target.mkdir(exist_ok=True)
    marker=target/'wmkd_packages.json'
    installed=read(marker).get('packages',[]) if marker.exists() else []
    missing=[p for p in packages if p not in installed]
    if missing:
        cmd([PY,'-m','pip','install','--target',target,'--upgrade','--no-deps','--index-url','https://pypi.tuna.tsinghua.edu.cn/simple',*missing],timeout=600)
        write(marker,{'packages':sorted(set(installed+packages)),'created_at':now(),'base_python':str(PY)})
    import importlib
    if str(target) not in sys.path: sys.path.insert(0,str(target))
    importlib.invalidate_caches()
    return str(target)

def prepare_work(c):
    import shutil
    work=Path(c['run_root'])/'work'
    if not work.exists(): shutil.copytree(c['source'],work,ignore=shutil.ignore_patterns('.git','__pycache__','*.pyc'))
    return work

def patch(path,old,new,log):
    import difflib
    path=Path(path); before=path.read_text()
    if old not in before:
        if new in before: return
        raise Blocked('BLOCKED_ENVIRONMENT','Compatibility patch anchor missing: '+str(path))
    after=before.replace(old,new); path.write_text(after)
    with Path(log).open('a') as f: f.writelines(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile=str(path)+'.official',tofile=str(path)+'.wmkd'))
