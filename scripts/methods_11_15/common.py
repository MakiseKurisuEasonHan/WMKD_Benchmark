"""Small durable primitives shared by the serial A-only queue."""
import hashlib, json, os, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = Path('/root/autodl-tmp/WMKD_Benchmark_data')
PY = DATA / 'artifacts/scw/env_py311/bin/python'
STAGES = ['SOURCE_PINNED','ENV_READY','MODEL_DATA_READY','PREFLIGHT_COMPLETE','TRAINING','DETECTOR','UTILITY','RELOAD_VERIFIED','ARCHIVED']

def pause_requested():
    marker=ROOT/'results/methods_11_15_pause_request.json'
    if not marker.exists(): return False
    try: return bool(read(marker).get('active'))
    except Exception: return True

def require_execution_unpaused():
    if pause_requested():
        print('PAUSED_BY_USER: execution disabled; explicit user resume required',flush=True)
        raise SystemExit(0)

def now(): return datetime.now(timezone.utc).isoformat()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,v):
    p=Path(p); p.parent.mkdir(parents=True,exist_ok=True)
    t=p.with_name(p.name+'.tmp'); t.write_text(json.dumps(v,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8',newline='\n'); os.replace(t,p)
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(8<<20),b''): h.update(b)
    return h.hexdigest()
def cmd(args,cwd=None,timeout=None,env=None):
    print(json.dumps({'time':now(),'command':[str(a) for a in args],'cwd':str(cwd or ROOT)}),flush=True)
    subprocess.run([str(a) for a in args],cwd=cwd or ROOT,check=True,timeout=timeout,env=env)
def capture(args,cwd=None): return subprocess.check_output([str(a) for a in args],cwd=cwd or ROOT,text=True).strip()
def gpu_free():
    return not capture(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader'])
def tree_manifest(p):
    return {str(f.relative_to(p)):{'size':f.stat().st_size,'sha256':sha(f)} for f in sorted(Path(p).rglob('*')) if f.is_file() and '.git' not in f.parts}
class Blocked(Exception):
    def __init__(self,status,reason): self.status=status; super().__init__(reason)
