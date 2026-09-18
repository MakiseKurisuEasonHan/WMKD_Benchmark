"""One canonical pilot only. Fail closed; no implicit retry or parameter search."""
import fcntl, hashlib, json, os, shutil, subprocess, sys, time, traceback
from pathlib import Path
ROOT=Path('/root/autodl-tmp/WMKD_Benchmark_data/scale_7b')
P=Path('/root/autodl-tmp/WMKD_Benchmark');PY=ROOT/'env/bin/python'
STATE=ROOT/'pilot_state.json'
def state(**kw):
    d=json.loads(STATE.read_text()) if STATE.exists() else {}
    d.update(kw,updated_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()))
    tmp=STATE.with_suffix('.tmp');tmp.write_text(json.dumps(d,indent=2));tmp.replace(STATE)
def run(name,cmd):
    assert not subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader'],text=True).strip(),'GPU in use'
    subprocess.run(['df','-h',str(ROOT)],check=True)
    assert shutil.disk_usage(ROOT).free>20*1024**3
    state(stage=name,status='RUNNING',error=None,command=list(map(str,cmd)))
    suffix=os.environ.get('PNFP_FINGERPRINT_DIR','fingerprints').removeprefix('fingerprints')
    with (ROOT/(name+suffix+'.log')).open('x') as log:
        child=subprocess.Popen(list(map(str,cmd)),stdout=log,stderr=subprocess.STDOUT,env=os.environ)
        state(child_pid=child.pid);code=child.wait()
    assert code==0,(name,code)
def main():
    lock=(ROOT/'pilot.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    if STATE.exists():
        assert '--continue-generation' in sys.argv or '--continue-initialization' in sys.argv,'No implicit rerun'
        previous=json.loads(STATE.read_text())
        assert previous['status']=='FAILED'
        if '--continue-initialization' in sys.argv:
            assert previous['stage']=='canonical_pilot_training'
            assert not (ROOT/'runs/speed/steps.jsonl').exists()
            assert not (ROOT/'runs/speed/runtime.json').exists()
            history=ROOT/'engineering_history/training_initialization_attempt0';history.mkdir(parents=True,exist_ok=False)
            shutil.copy2(STATE,history/'pilot_state.json')
            (ROOT/'runs/speed').rename(history/'speed')
            os.environ['PNFP_FINGERPRINT_DIR']='fingerprints_init_cont1'
        else:
            assert previous['stage']=='fingerprint_generation'
            assert not (ROOT/'runs/speed').exists() and not (ROOT/'fingerprint_manifest.json').exists()
            attempt=0
            while (ROOT/f'engineering_history/generation_attempt{attempt}').exists():
                attempt+=1
            history=ROOT/f'engineering_history/generation_attempt{attempt}';history.mkdir(parents=True,exist_ok=False)
            shutil.copy2(STATE,history/'pilot_state.json')
            old_suffix=f'_cont{attempt}' if attempt else ''
            shutil.copy2(ROOT/f'fingerprint_generation{old_suffix}.log',history/'fingerprint_generation.log')
            os.environ['PNFP_FINGERPRINT_DIR']=f'fingerprints_cont{attempt+1}'
    os.environ.update(PATH=str(ROOT/'env/bin')+':/root/miniconda3/bin:/usr/local/cuda/bin:/usr/bin:/bin',
        WANDB_MODE='disabled',WANDB_DISABLED='true',TOKENIZERS_PARALLELISM='false',
        HF_HOME=str(ROOT/'cache/huggingface'),TORCH_EXTENSIONS_DIR=str(ROOT/'cache/torch_extensions'),
        MAX_JOBS='4',OMP_NUM_THREADS='8',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
    state(pid=os.getpid(),status='STARTING',protocol='pnfp_7b_paper_aligned_v1')
    assert json.loads((ROOT/'model_manifest.json').read_text())['status']=='COMPLETE'
    assert json.loads((ROOT/'environment_preflight.json').read_text())['status']=='PASS'
    if '--continue-initialization' not in sys.argv:
        run('fingerprint_generation',[PY,P/'scripts/pnfp_7b_generate.py'])
    run('canonical_pilot_training',[PY,'-m','deepspeed.launcher.runner','--num_gpus=1','--master_port=29603',P/'scripts/pnfp_7b_train.py','--stage','speed'])
    s=json.loads((ROOT/'runs/speed/summary.json').read_text());fp=json.loads((ROOT/'fingerprint_manifest.json').read_text())
    (ROOT/'pilot_evaluation').mkdir(exist_ok=True)
    for label,model in [('base',str(ROOT/'models/Llama-2-7b-chat-hf')),('pilot',s['final_model'])]:
        run(label+'_detector',[PY,P/'scripts/pnfp_evaluate.py','--model-path',model,'--fingerprints',fp['official_output'],
             '--output',ROOT/'pilot_evaluation'/f'{label}_detector.json','--label',label,'--use-chat-template',
             '--generation-response-length','1'])
        run(label+'_arc64',[PY,P/'scripts/pnfp_7b_proxy.py','--model',model,'--label',label])
    run('pilot_ordinary',[PY,P/'scripts/pnfp_a2_utility_smoke.py','--base',ROOT/'models/Llama-2-7b-chat-hf',
                         '--smoke',s['final_model'],'--output',ROOT/'pilot_evaluation/ordinary.json'])
    state(status='PILOT_COMPLETE_AWAITING_ASSESSMENT',stage='COMPLETE',child_pid=None)
if __name__=='__main__':
    try:main()
    except BaseException:
        state(status='FAILED',error=traceback.format_exc());raise
