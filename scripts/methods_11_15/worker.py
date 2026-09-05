"""One persistent stage per process; never silently accept failed partial output."""
import importlib, os, sys, traceback, time
from common import *

def main():
    context=Path(sys.argv[1]); stage=sys.argv[2]; attempt=int(sys.argv[3]); result=Path(sys.argv[4])
    c=read(context); c['attempt']=attempt; c['root']=str(ROOT); c['stage']=stage
    start=time.monotonic()
    os.environ.update(CUDA_VISIBLE_DEVICES='0',HF_HUB_DISABLE_TELEMETRY='1',WANDB_DISABLED='true',TOKENIZERS_PARALLELISM='false',PYTHONUNBUFFERED='1',OMP_NUM_THREADS='8')
    try:
        if stage=='SOURCE_PINNED':
            src=Path(c['source'])
            if not src.exists(): cmd(['git','clone',c['spec']['repo'],src],timeout=600)
            if capture(['git','rev-parse','HEAD'],src)!=c['spec']['commit']:
                cmd(['git','checkout','--detach',c['spec']['commit']],src)
            if capture(['git','rev-parse','HEAD'],src)!=c['spec']['commit']: raise Blocked('BLOCKED_SOURCE','Source commit mismatch')
            value={'repo':c['spec']['repo'],'commit':c['spec']['commit'],'license_files':[str(p.name) for p in src.glob('LICENSE*')]}
        else:
            module=importlib.import_module(c['spec']['module'])
            value=module.stage(c,stage)
        write(result,{'status':'SUCCESS','stage':stage,'attempt':attempt,'completed_at':now(),'runtime_seconds':time.monotonic()-start,'outputs':value})
    except Exception as e:
        traceback.print_exc()
        write(result,{'status':'FAILURE','stage':stage,'attempt':attempt,'completed_at':now(),'runtime_seconds':time.monotonic()-start,'blocked_status':getattr(e,'status',None),'error_type':type(e).__name__,'error':str(e),'traceback':traceback.format_exc()})
        sys.exit(1)

if __name__=='__main__': main()
