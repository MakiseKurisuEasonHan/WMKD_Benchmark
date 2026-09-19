"""Authorized AWM7B serial pipeline. Never resumes LLMPrint or shuts down host."""
import argparse,fcntl,json,math,os,re,shutil,statistics,subprocess,time,traceback
from pathlib import Path
from pnfp_7b_disk_gate import budget
from pnfp_7b_distill_campaign import put,sha
from distillation_data import freeze_candidates,read_jsonl,write_jsonl

P=Path('/root/autodl-tmp/WMKD_Benchmark');D=Path(str(P)+'_data');S=D/'scale_7b'
O=D/'awm_7b';E=P/'results/awm/scale_7b';BASE=S/'models/Llama-2-7b-chat-hf'
PY=str(S/'env/bin/python');REV='f5db02db724555f92da89c216ac04704f23d4590'
ENV=dict(os.environ,PYTHONPATH=str(S/'bnb_0500')+':'+str(P/'scripts'),HF_HUB_OFFLINE='1',HF_DATASETS_OFFLINE='1',OMP_NUM_THREADS='8',TOKENIZERS_PARALLELISM='false',PYTHONUNBUFFERED='1')
DETECT_ENV=dict(ENV,PYTHONPATH=str(D/'llmprint_7b/runtime451')+':'+str(P/'scripts'))
def load(p):return json.loads(Path(p).read_text())
def gpu_snapshot():return subprocess.check_output(['nvidia-smi'],text=True)
def disk_snapshot():return subprocess.check_output(['df','-h',str(O)],text=True)
def verified_final(stage):
    m=load(O/stage/'final_manifest.json')
    return all((O/stage/'final_model'/x['path']).stat().st_size==x['bytes'] and sha(O/stage/'final_model'/x['path'])==x['sha256'] for x in m['files'])

def run(stage,script,args,additional=2*2**30,gpu=True,detector=False):
    receipt=E/(stage+'_runtime.json')
    if receipt.exists() and load(receipt)['exit_code']==0:return
    gate=budget(*shutil.disk_usage(O),{'stage_additional_peak':additional});put(E/(stage+'_disk_gate.json'),gate)
    assert gate['passed'],'SCIENTIFIC_BLOCK disk peak unsafe'
    (E/(stage+'_resources_before.txt')).write_text(gpu_snapshot()+'\n'+disk_snapshot())
    if gpu:assert not subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader'],text=True).strip(),'GPU occupied'
    logpath=E/(stage+'.log')
    if logpath.exists():shutil.copy2(logpath,E/(stage+f'.attempt-{int(time.time())}.log'))
    if receipt.exists():shutil.copy2(receipt,E/(stage+f'.attempt-{int(time.time())}.json'))
    cmd=[PY,str(P/'scripts'/script),*map(str,args)]
    started=time.time();gpu_peak=rss_peak=cgroup_peak=0;reason=None
    with logpath.open('w') as log:
        proc=subprocess.Popen(cmd,cwd=P,env=DETECT_ENV if detector else ENV,stdout=log,stderr=subprocess.STDOUT)
        while proc.poll() is None:
            disk=shutil.disk_usage(O)
            try:
                vals=subprocess.check_output(['nvidia-smi','--query-gpu=memory.used,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True,timeout=10).strip().split(',')
                used,free,util=map(lambda v:int(v.strip()),vals);gpu_peak=max(gpu_peak,used*2**20)
                rss=0
                for line in (Path('/proc')/str(proc.pid)/'status').read_text().splitlines():
                    if line.startswith('VmRSS:'):rss=int(line.split()[1])*1024
                rss_peak=max(rss_peak,rss);cg=int(Path('/sys/fs/cgroup/memory.current').read_text());cgroup_peak=max(cgroup_peak,cg)
                with logpath.open('rb') as f:f.seek(max(0,logpath.stat().st_size-131072));tail=f.read().decode(errors='replace')
                losses=[float(x) for x in re.findall(r"['\"]loss['\"]:\s*([0-9.eE+-]+)",tail)]
                steps=re.findall(r'(\d+)/7500',tail)
                if re.search(r"['\"]loss['\"]:\s*(?:nan|[+-]?inf)",tail,re.I):reason='SCIENTIFIC_BLOCK nonfinite training loss'
                if len(losses)>=30 and min(losses)>0 and statistics.median(losses[-10:])>10*statistics.median(losses[:10]):reason='SCIENTIFIC_BLOCK persistent order-of-magnitude loss increase; requires inspection'
                if disk.free<2*2**30:reason='SCIENTIFIC_BLOCK disk safety reserve exhausted'
                put(E/'campaign_state.json',dict(status='RUNNING',stage=stage,pid=os.getpid(),worker_pid=proc.pid,
                    command=cmd,elapsed_seconds=time.time()-started,step=int(steps[-1]) if steps else None,
                    latest_loss=losses[-1] if losses else None,gpu_used_bytes=used*2**20,gpu_free_bytes=free*2**20,gpu_utilization_percent=util,
                    host_process_rss_bytes=rss,host_cgroup_current_bytes=cg,disk_free_bytes=disk.free,auto_shutdown=False))
                if reason:proc.terminate();proc.wait(timeout=60);break
            except (OSError,ValueError,subprocess.SubprocessError):pass
            time.sleep(5)
        rc=proc.wait()
    put(receipt,dict(started=started,ended=time.time(),exit_code=rc,sampled_gpu_peak_bytes=gpu_peak,
        sampled_process_rss_peak_bytes=rss_peak,sampled_cgroup_peak_bytes=cgroup_peak,stop_reason=reason,sampling_interval_seconds=5,
        disk_after=shutil.disk_usage(O)._asdict()))
    (E/(stage+'_resources_after.txt')).write_text(gpu_snapshot()+'\n'+disk_snapshot())
    assert rc==0 and not reason,reason or stage+' failed; preserved evidence requires engineering diagnosis'

def milestone(stage,data):
    data.update(method='AWM',run_id='awm_7b_'+stage,status='COMPLETED',completed=time.time(),
        scientific_config=load(E/'exact_protocol.json'),reference_revision=REV,calibration_sha256=sha(E/'calibration.json'),auto_shutdown=False)
    put(E/stage/'full_experiment_log.json',data)
    put(E/(stage+'_complete.json'),dict(stage=stage,time=time.time(),full_log_sha256=sha(E/stage/'full_experiment_log.json')))

def train_eval(stage,dataset):
    if (E/(stage+'_complete.json')).exists():assert verified_final(stage);return
    assert sha(E/'calibration.json')==load(E/'calibration_freeze.json')['calibration_sha256']
    out=O/stage;out.mkdir(exist_ok=True)
    args=['train-kd' if stage=='logit' else 'train','--base',BASE,'--dataset',dataset,'--output',out]
    if stage=='logit':args+=['--cache',O/'logit_cache']
    if not (out/'final_manifest.json').exists():
        for micro in [8,4,2]:
            label=stage+'_training_micro'+str(micro)
            try:run(label,'pnfp_7b_distill_worker.py',args+['--microbatch',micro],additional=20*2**30);break
            except AssertionError:
                log=(E/(label+'.log')).read_text(errors='replace')
                if not ('CUDA out of memory' in log or 'torch.OutOfMemoryError' in log) or micro==2 or (out/'final_model').exists():raise
                put(E/(label+'_engineering_retry.json'),dict(reason='CUDA OOM',next_microbatch=micro//2,
                    effective_batch=8,same_order=True,normalization='token weighted within original batch8',fresh_clean_init=True))
    assert verified_final(stage)
    for name in ['exact_config.json','supervision_stats.json','training_summary.json','final_manifest.json']:shutil.copy2(out/name,E/(stage+'_'+name))
    run(stage+'_detector','awm_7b_detector.py',['detect','--stage',stage,'--model',out/'final_model'],detector=True)
    run(stage+'_utility','awm_7b_utility.py',['--base',BASE,'--a2',out/'final_model','--output',E/(stage+'_utility.json'),'--batch-size','8'])
    milestone(stage,dict(detector=load(E/(stage+'_detector.json')),utility=load(E/(stage+'_utility.json')),
        runtime=load(out/'training_summary.json'),training_config=load(out/'exact_config.json'),final_model=str(out/'final_model'),
        final_model_manifest=load(out/'final_manifest.json'),dataset_sha256=sha(dataset)))

def write_report(state):
    lines=['# AWM 7B representative passive-method extension','', 'Status: '+state['status'],
        'LLMPrint remains paused with all assets retained. No shutdown is authorized.','',
        'All Students independently start from clean Llama-2-7b-chat-hf revision '+REV+'.',
        'AdamW8bit0.50.0 is a hardware optimizer-storage adaptation, not FP32 Adam implementation equivalence.','',
        '| Condition | Native AWM score | Frozen threshold | Detected | Score/reference | ARC | MC2 | Training/construction s | Peak allocated GPU GiB | Peak host RSS GiB |',
        '|---|---:|---:|---|---:|---:|---:|---:|---:|---:|']
    for stage in ['reference','direct','paraphrase','logit']:
        f=E/stage/'full_experiment_log.json'
        if not f.exists():lines.append('| '+stage+' | NOT_COMPLETED | | | | | | | | |');continue
        x=load(f);d=x['detector'];u=x['utility']['a2'];r=x['runtime']
        lines.append(f'| {stage} | {d["score"]:.10f} | {d["threshold"]:.10f} | {d["detected"]} | {d["score_reference_ratio"]:.8f} | {u["arc_challenge_acc_norm"]:.6f} | {u["truthfulqa_mc2_acc"]:.6f} | {r["runtime_seconds"]:.2f} | {r["peak_vram_bytes"]/2**30:.3f} | {r["peak_host_rss_bytes"]/2**30:.3f} |')
    if state.get('error'):lines+=['','Preserved failure:','```',state['error'],'```']
    (E/'final_report.md').write_text('\n'.join(lines)+'\n')

def main():
    p=argparse.ArgumentParser();p.add_argument('--resume-engineering',action='store_true');args=p.parse_args()
    E.mkdir(parents=True,exist_ok=True);O.mkdir(exist_ok=True)
    lock=(E/'campaign.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    if (E/'terminal.json').exists():
        assert args.resume_engineering and load(E/'terminal.json')['status']!='COMPLETED'
        (E/'terminal.json').rename(E/f'terminal_before_engineering_resume_{int(time.time())}.json')
    state=dict(status='RUNNING',started=time.time(),pid=os.getpid(),auto_shutdown=False)
    try:
        while not (E/'calibration_runtime.json').exists():
            assert not (E/'calibration_failure.json').exists(),'Calibration failed; inspect preserved error'
            time.sleep(5)
        assert load(E/'calibration_runtime.json')['exit_code']==0
        assert sha(E/'calibration.json')==load(E/'calibration_freeze.json')['calibration_sha256']
        if not (E/'reference_complete.json').exists():
            reference_runtime=dict(load(E/'calibration.json'))
            attempts=[load(E/'calibration_runtime.json')]+[load(f) for f in (E/'engineering_history').rglob('calibration_runtime.json')]
            reference_runtime.update(runtime_seconds=sum(x['ended']-x['started'] for x in attempts),
                runtime_definition='total calibration subprocess wall time including preserved Phi3 loader attempt; successful negative results reused',
                peak_vram_bytes=max([reference_runtime['peak_vram_bytes']]+[x.get('sampled_gpu_peak_bytes',0) for x in attempts]),
                peak_host_rss_bytes=max([reference_runtime['peak_host_rss_bytes']]+[x.get('sampled_process_rss_peak_bytes',0) for x in attempts]))
            milestone('reference',dict(detector=load(E/'reference_detector.json'),utility=load(E/'reference_utility.json'),
                runtime=reference_runtime,calibration=load(E/'calibration.json'),model_modified=False,
                canonical_model_manifest=load(E/'canonical_model_source_manifest.json')))
        (O/'direct').mkdir(exist_ok=True);direct=O/'direct/frozen_qa.jsonl'
        if not direct.exists():
            target=24000
            while True:
                run('direct_generation_'+str(target),'generate_teacher_qa_formal.py',[
                    '--model-path',BASE,'--teacher-run-id','awm_7b_clean_reference','--output',O/'direct/raw_candidates.jsonl',
                    '--errors',O/'direct/errors.jsonl','--target-candidates',target,'--batch-size','8','--seed','42',
                    '--telemetry',E/('generation_'+str(target)+'_telemetry.json')])
                try:rows,manifest=freeze_candidates(read_jsonl(O/'direct/raw_candidates.jsonl'),20000);break
                except ValueError as exc:
                    if 'valid unique samples' not in str(exc):raise
                    target+=2000;assert target<=60000,'Canonical passive generation ceiling reached'
            write_jsonl(direct,rows);manifest.update(file_sha256=sha(direct),teacher=str(BASE),teacher_revision=REV,
                raw_sha256=sha(O/'direct/raw_candidates.jsonl'),candidate_target=target)
            put(E/'direct_dataset_manifest.json',manifest)
        manifest=load(E/'direct_dataset_manifest.json');assert sha(direct)==manifest['file_sha256']
        run('response_count','pnfp_7b_distill_worker.py',['stats','--base',BASE,'--dataset',direct,'--output',E],gpu=False)
        stats=load(E/'supervision_stats.json')
        gate=budget(*shutil.disk_usage(O),{'future_final_students':3*13479264256,'overhead':10*2**30},samples=20000,supervised_tokens=stats['supervised_tokens'])
        put(E/'exact_campaign_disk_budget.json',gate);assert gate['passed'],'SCIENTIFIC_BLOCK disk peak budget'
        train_eval('direct',direct)
        qm=load(P/'results/active_cross_lineage_bb/base_offline_reload_preflight.json');qm['model_revision']=qm['revision']
        put(E/'qwen_restore_manifest.json',qm)
        run('qwen_restore','restore_xbb_qwen_base.py',[E/'qwen_restore_manifest.json',E/'qwen_restore_receipt.json'],additional=8*2**30,gpu=False)
        config=load(P/'configs/distillation/passive5_shared_bb3.json');original=load(P/'configs/distillation/passive5_shared_bb.json')['paraphrase']
        for key in ['prompt_path','prompt_sha256','prompt_version']:config['paraphrase'][key]=original[key]
        assert sha(P/config['paraphrase']['prompt_path'])==load(E/'exact_protocol.json')['paraphrase']['prompt_sha256']
        config.update(identity='awm_7b_paraphrase',experiment='AWM7B Paraphrase',methods=['AWM'],auto_shutdown=False)
        config['paraphrase']['atomic_identity_preservation']['expected_full20k_count']=None
        config['paraphraser']['revision']=qm['revision']
        config['student'].update(model_id='meta-llama/Llama-2-7b-chat-hf',revision=REV,path=str(BASE),initialization='fresh_canonical_original_revision',resume=False)
        config['training']['optimizer']='bitsandbytes.optim.adamw.AdamW8bit 0.50.0'
        config['source_dataset'].update(path=str(direct),manifest_path=str(E/'direct_dataset_manifest.json'),record_count=20000,
            dataset_sha256=manifest['dataset_sha256'],frozen_jsonl_sha256=manifest['file_sha256'],sample_ids_sha256=manifest['sample_ids_sha256'],parent_experiment='AWM7B Direct',parent_run_id='awm_7b_direct')
        cfg=P/'configs/distillation/awm_7b_paraphrase.json';put(cfg,config);put(E/'paraphrase_config.json',config)
        pp=O/'paraphrase';pp.mkdir(exist_ok=True)
        run('paraphrase_generation','passive5_shared_bb_paraphrase_runner.py',['--config',cfg,'--source',direct,'--journal',pp/'journal.jsonl','--backend','qwen'])
        run('paraphrase_freeze','passive5_shared_bb.py',['--config',cfg,'freeze','--source',direct,'--journal',pp/'journal.jsonl','--output',pp/'pairs.jsonl'],gpu=False)
        run('paraphrase_audit','passive5_shared_bb.py',['--config',cfg,'quality-audit','--pairs',pp/'pairs.jsonl','--output-dir',E/'paraphrase_quality'],gpu=False)
        run('paraphrase_adapt','passive5_shared_bb.py',['--config',cfg,'adapt-student','--pairs',pp/'pairs.jsonl','--output',pp/'frozen_qa.jsonl'],gpu=False)
        for name in ['pairs.manifest.json','telemetry.json','progress.json']:shutil.copy2(pp/name,E/('paraphrase_'+name))
        train_eval('paraphrase',pp/'frozen_qa.jsonl')
        run('logit_cache','pnfp_7b_distill_worker.py',['cache','--base',BASE,'--teacher',BASE,'--dataset',direct,'--cache',O/'logit_cache','--output',E],additional=stats['payload_bytes']+13479264256+2*2**30)
        cached=load(E/'logit_manifest.json')
        assert cached['complete'] and cached['supervised_tokens']==stats['supervised_tokens']
        put(E/'logit_cache_integrity_summary.json',{k:v for k,v in cached.items() if k!='records'})
        train_eval('logit',direct)
        assert all(verified_final(s) for s in ['direct','paraphrase','logit'])
        state.update(status='COMPLETED',final_models_sha_verified=True)
    except BaseException:state.update(status='BLOCKED_REQUIRES_DIAGNOSIS',error=traceback.format_exc())
    finally:
        state['ended']=time.time();write_report(state);put(E/'terminal.json',state);put(E/'campaign_state.json',state)
        subprocess.run(['sync'])
        # Deliberately no shutdown, no new method, no LLMPrint resume.
if __name__=='__main__':main()
