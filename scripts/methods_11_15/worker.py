"""One persistent stage per process; never silently accept failed partial output."""
import importlib, os, sys, traceback, time, threading
from common import *

def main():
    require_execution_unpaused()
    context=Path(sys.argv[1]); stage=sys.argv[2]; attempt=int(sys.argv[3]); result=Path(sys.argv[4])
    c=read(context); c['attempt']=attempt; c['root']=str(ROOT); c['stage']=stage
    start=time.monotonic()
    stop=threading.Event(); telemetry={'peak_gpu_used_bytes':0,'source':'nvidia-smi total used memory sampled every10s; serial GPU scope'}
    def sample():
        while not stop.is_set():
            try: telemetry['peak_gpu_used_bytes']=max(telemetry['peak_gpu_used_bytes'],int(capture(['nvidia-smi','--query-gpu=memory.used','--format=csv,noheader,nounits']).splitlines()[0])*2**20)
            except Exception: pass
            stop.wait(10)
    if stage in ('TRAINING','PREFLIGHT_COMPLETE'): threading.Thread(target=sample,daemon=True).start()
    os.environ.update(CUDA_VISIBLE_DEVICES='0',HF_ENDPOINT='https://hf-mirror.com',HF_HUB_DISABLE_TELEMETRY='1',WANDB_DISABLED='true',TOKENIZERS_PARALLELISM='false',PYTHONUNBUFFERED='1',OMP_NUM_THREADS='8',HF_HUB_ETAG_TIMEOUT='30',HF_HUB_DOWNLOAD_TIMEOUT='90')
    os.environ['HF_HUB_DISABLE_IMPLICIT_TOKEN']='1'
    # --target installs executables outside the base environment PATH.
    os.environ['PATH']=str(Path(c['run_root'])/'runtime_overlay/bin')+os.pathsep+str(PY.parent)+os.pathsep+os.environ.get('PATH','')
    try:
        if stage=='SOURCE_PINNED':
            src=Path(c['source'])
            bundle=DATA/'sources/methods_11_15_transport'/(c['method']+'.bundle')
            if src.exists():
                try: valid=capture(['git','rev-parse','HEAD'],src)==c['spec']['commit']
                except Exception: valid=False
                if not valid:
                    retained=Path(c['run_root'])/('partial_source_attempt_'+str(attempt))
                    src.rename(retained)
            if not src.exists(): cmd(['git','clone',bundle if bundle.exists() else c['spec']['repo'],src],timeout=180)
            if capture(['git','rev-parse','HEAD'],src)!=c['spec']['commit']:
                cmd(['git','checkout','--detach',c['spec']['commit']],src)
            if capture(['git','rev-parse','HEAD'],src)!=c['spec']['commit']: raise Blocked('BLOCKED_SOURCE','Source commit mismatch')
            value={'repo':c['spec']['repo'],'commit':c['spec']['commit'],'license_files':[str(p.name) for p in src.glob('LICENSE*')],'transport':'local exact Git bundle' if bundle.exists() else 'official GitHub','bundle_sha256':sha(bundle) if bundle.exists() else None}
        else:
            module=importlib.import_module(c['spec']['module'])
            value=module.stage(c,stage)
        stop.set()
        if stage in ('TRAINING','PREFLIGHT_COMPLETE') and isinstance(value,dict): value['telemetry']=telemetry
        write(result,{'status':'SUCCESS','stage':stage,'attempt':attempt,'completed_at':now(),'runtime_seconds':time.monotonic()-start,'required_child_processes_exit_code':0,'outputs':value})
    except Exception as e:
        stop.set()
        traceback.print_exc()
        write(result,{'status':'FAILURE','stage':stage,'attempt':attempt,'completed_at':now(),'runtime_seconds':time.monotonic()-start,'blocked_status':getattr(e,'status',None),'error_type':type(e).__name__,'error':str(e),'traceback':traceback.format_exc()})
        sys.exit(1)

if __name__=='__main__': main()
