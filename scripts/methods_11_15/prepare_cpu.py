"""CPU-only source/environment receipts, prepared while EaaW occupies the GPU."""
import subprocess, os
from common import *
state=read(ROOT/'results/methods_11_15_pipeline_state.json')
for slug in state['order'][1:]:
    m=state['methods'][slug]; c=read(m['context']); rr=Path(c['run_root'])
    for stage in ('SOURCE_PINNED','ENV_READY'):
        dest=rr/'receipts'/f'{stage}.1.json'
        if dest.exists(): continue
        env=os.environ.copy(); env['PYTHONPATH']=str(rr/'runtime_overlay')
        with (rr/f'{stage}.1.log').open('ab',buffering=0) as log:
            p=subprocess.run([PY,Path(__file__).with_name('worker.py'),m['context'],stage,'1',dest],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
        print(slug,stage,p.returncode,flush=True)
        if p.returncode: break
