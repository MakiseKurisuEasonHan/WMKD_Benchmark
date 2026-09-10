"""Restart-aware native Bc endpoint evaluation, isolated from Ba/Bb/pilot."""
import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import traceback
import time

P=Path(__file__).resolve().parents[1];D=Path(str(P)+'_data');E=P/'results/logit_distillation/same_lineage_bc'
def read(p):return json.loads(p.read_text())
def save(p,d):p.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')
def main(m):
    q=E/m;cfg=read(q/'protocol.json');summary=read(q/'training_summary.json')
    assert summary['status']=='COMPLETE' and summary['steps']==7500 and summary['teacher_frozen']
    model=Path(summary['final_model']);assert model.resolve().is_relative_to(D/'runs/same_lineage_bc')
    lock=(E/'gpu_serial.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    idle_samples=[]
    for attempt in range(30):
        gpu=subprocess.check_output(['nvidia-smi','--query-gpu=memory.used,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip().split(',')
        idle_samples.append({'memory_mib':int(gpu[0]),'utilization':int(gpu[1])})
        if int(gpu[0])<100 and int(gpu[1])<=5:break
        if attempt<29:time.sleep(2)
    save(q/'evaluation_gpu_idle_gate.json',{'samples':idle_samples,'passed':int(gpu[0])<100 and int(gpu[1])<=5})
    assert int(gpu[0])<100 and int(gpu[1])<=5,'GPU_IDLE_GATE_TIMEOUT'
    env=dict(os.environ,HF_HUB_OFFLINE='1',HF_DATASETS_OFFLINE='1',TRANSFORMERS_OFFLINE='1',TOKENIZERS_PARALLELISM='false')
    def run(stage,cmd,result):
        exitfile=q/(stage+'_exit.json')
        if exitfile.exists():assert read(exitfile)['returncode']==0 and result.exists();return
        assert not result.exists(),'Unreceipted result: inspect before rerun'
        with (q/(stage+'.log')).open('a') as log:
            proc=subprocess.Popen(cmd,env=env,stdout=log,stderr=subprocess.STDOUT)
            save(q/'evaluation_progress.json',{'stage':stage,'worker_pid':proc.pid,'supervisor_pid':os.getpid(),'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat()})
            rc=proc.wait()
        save(exitfile,{'returncode':rc,'command':cmd,'completed_at':datetime.datetime.now(datetime.timezone.utc).isoformat()});assert rc==0 and result.exists(),stage
    if m=='pnfp':
        frozen=read(P/'results/active_watermarks_trajectory_followup/pnfp_asset_verification.json')['detector_keys'];keys=frozen['path']
        assert hashlib.sha256(Path(keys).read_bytes()).hexdigest()==frozen['sha256'],'Frozen PNFP key SHA mismatch'
        raw=q/'detector_results.json'
        run('detector',[sys.executable,'-u','-B',str(P/'scripts/pnfp_evaluate.py'),'--model-path',str(model),'--fingerprints',keys,'--output',str(raw),'--label',cfg['run_id'],'--count','1024','--key-length','16','--generation-response-length','16','--training-response-length','1','--seed','42','--use-chat-template'],raw)
        result=read(raw);assert result['fingerprints_evaluated']==1024 and result['evaluation_errors']==result['invalid_samples']==0 and len(result['details'])==1024
        assert result['detected']==sum(x['detected'] for x in result['details'])
    elif m in ('evertracer','ctcc','iseal','scw'):
        assert cfg.get('native_detector_assets_verified') is True,'Frozen native detector assets must be verified'
        run('detector',[sys.executable,'-u','-B',str(P/'scripts/bc_native_detector_worker.py'),m,str(model)],q/'detector_results.json')
    elif m=='passive_shared':
        assert cfg.get('native_detector_assets_verified') is True
        run('detector',[sys.executable,'-u','-B',str(P/'scripts/bc_passive_detector_worker.py'),str(model)],q/'detector_results.json')
    else:
        raise RuntimeError('Native detector asset/spec audit must be completed before enabling this method')
    run('utility',[sys.executable,'-u','-B',str(P/'scripts/bc_utility_worker.py'),m,str(model)],q/'utility/utility_results.json')
    save(q/'evaluation_exit.json',{'returncode':0,'fresh_process_reload':True,'completed_at':datetime.datetime.now(datetime.timezone.utc).isoformat()})
    full=read(q/'full_experiment_log.json');full.update(status='SCIENCE_COMPLETE_PENDING_ARCHIVE',training=summary,detector=read(q/'detector_results.json'),utility=read(q/'utility/utility_results.json'),fresh_process_reload=True,archive='PENDING_AUTHORIZED_PREFERRED_PRIVATE_ARCHIVE')
    save(q/'full_experiment_log.json',full)
if __name__=='__main__':
    m=sys.argv[1]
    try:main(m)
    except BaseException:
        save(E/m/'evaluation_failure.json',{'error':traceback.format_exc(),'status':'STOP_FOR_ENGINEERING_REVIEW'});raise
