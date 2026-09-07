"""Read-only checks for the seven explicitly approved optimizer-state paths."""
import hashlib
import json
import os
import pickletools
import stat
import subprocess
import zipfile
from datetime import datetime, timezone
from pathlib import Path

P = Path('/root/autodl-tmp/WMKD_Benchmark')
D = Path('/root/autodl-tmp/WMKD_Benchmark_data')

def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda: f.read(8*1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()

def main(payload):
    out = {'checked_at': datetime.now(timezone.utc).isoformat(), 'read_only': True,
           'no_training_resume_planned': True, 'candidates': [], 'protected': []}
    targets = {x['path'] for x in payload['candidates']}
    for c in payload['candidates']:
        p = Path(c['path']); s = p.lstat()
        r = {'path': str(p), 'identity_match': p.resolve()==p and stat.S_ISREG(s.st_mode)
             and s.st_size==c['bytes'] and s.st_ino==c['inode'] and s.st_nlink==1,
             'bytes': s.st_size, 'allocated_bytes': s.st_blocks*512,
             'mtime_ns': s.st_mtime_ns, 'inode': s.st_ino, 'device': s.st_dev,
             'checkpoint_directory': p.parent.name}
        assert p.is_relative_to(D/'runs') and p.name=='optimizer.pt' and p.parent.name=='checkpoint-7500'
        with zipfile.ZipFile(p) as z:
            member = [n for n in z.namelist() if n.endswith('/data.pkl')]
            assert len(member)==1
            words = {arg for op,arg,pos in pickletools.genops(z.read(member[0])) if op.name in ['SHORT_BINUNICODE','BINUNICODE','UNICODE']}
            r['optimizer_structure'] = all(w in words for w in ['state','param_groups','exp_avg','exp_avg_sq'])
        refs=[]
        for proc in Path('/proc').iterdir():
            if not proc.name.isdigit() or int(proc.name)==os.getpid(): continue
            try:
                cmd=(proc/'cmdline').read_bytes().replace(b'\0',b' ').decode(errors='replace')
                if str(p) in cmd or str(p.parent) in cmd: refs.append({'pid':proc.name,'kind':'command'})
                for f in (proc/'fd').iterdir():
                    if f.resolve()==p:refs.append({'pid':proc.name,'kind':'open_fd'})
            except (OSError,PermissionError):pass
        r['active_references']=refs
        r['siblings']=[{'path':str(f),'bytes':f.stat().st_size} for f in p.parent.iterdir() if f.is_file() and f!=p]
        out['candidates'].append(r)
    for item in payload['protected']:
        p=Path(item['path']);r=dict(item);r['exists']=p.is_file()
        if r['exists']:
            s=p.stat();r.update(bytes=s.st_size,sha256=sha(p),inode=s.st_ino,mtime_ns=s.st_mtime_ns)
            r['match']=not item.get('expected_sha256') or item['expected_sha256']==r['sha256']
        else:r['match']=False
        out['protected'].append(r)
    out['df']=subprocess.run(['df','-h',str(D)],capture_output=True,text=True).stdout
    print(json.dumps(out,indent=2))
