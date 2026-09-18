"""Serial authorized 6004 campaign. Local guardian syncs/commits before shutdown."""
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import traceback
from pnfp_7b_disk_gate import budget
from distillation_data import freeze_candidates,read_jsonl,write_jsonl

P=Path('/root/autodl-tmp/WMKD_Benchmark');R=Path(str(P)+'_data/scale_7b')
E=P/'results/pnfp/scale_7b/distillation_6004';O=R/'distillation_6004'
PY=str(R/'env/bin/python');BASE=R/'models/Llama-2-7b-chat-hf';TEACHER=R/'wa050_extension_v1/best_model'
ENV=os.environ.copy();ENV.update(PYTHONPATH=str(R/'bnb_0500')+':'+str(P/'scripts'),
    HF_HUB_OFFLINE='1',HF_DATASETS_OFFLINE='1',TOKENIZERS_PARALLELISM='false',OMP_NUM_THREADS='8',PYTHONUNBUFFERED='1')


def put(path,obj):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(obj,indent=2)+'\n');tmp.replace(path)


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(8<<20),b''):h.update(b)
    return h.hexdigest()


def run(stage,script,args,additional=2*2**30,gpu=True):
    disk=shutil.disk_usage(R); gate=budget(*disk,{'stage_additional_peak':additional})
    put(E/(stage+'_disk_gate.json'),gate);assert gate['passed'],stage+' disk blocked'
    check=subprocess.check_output(['nvidia-smi'],text=True)
    (E/(stage+'_gpu_before.txt')).write_text(check)
    if gpu:
        active=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,used_memory','--format=csv,noheader'],text=True)
        assert not active.strip(), 'Another GPU process active: '+active
    cmd=[PY,str(P/'scripts'/script),*map(str,args)]
    put(E/'campaign_state.json',dict(status='RUNNING',stage=stage,pid=os.getpid(),command=cmd))
    began=time.time()
    gpu_peak=rss_peak=0;disk_peak=disk.used
    with (E/(stage+'.log')).open('w') as log:
        process=subprocess.Popen(cmd,cwd=P,env=ENV,stdout=log,stderr=subprocess.STDOUT)
        while process.poll() is None:
            disk_peak=max(disk_peak,shutil.disk_usage(R).used)
            try:
                status=Path('/proc')/str(process.pid)/'status'
                for line in status.read_text().splitlines():
                    if line.startswith('VmRSS:'):rss_peak=max(rss_peak,int(line.split()[1])*1024)
                if gpu:
                    values=subprocess.check_output(['nvidia-smi','--query-gpu=memory.used','--format=csv,noheader,nounits'],text=True,timeout=10)
                    gpu_peak=max(gpu_peak,int(values.strip())*2**20)
            except (OSError,ValueError,subprocess.SubprocessError):pass
            time.sleep(2)
    put(E/(stage+'_runtime.json'),dict(started=began,ended=time.time(),exit_code=process.returncode,
        sampled_gpu_peak_bytes=gpu_peak,sampled_process_rss_peak_bytes=rss_peak,sampling_interval_seconds=2,
        sampled_peak_disk_used_bytes=max(disk_peak,shutil.disk_usage(R).used),
        disk_after=shutil.disk_usage(R)._asdict()))
    assert process.returncode==0,stage+' failed; see preserved log'


def train_and_eval(stage,dataset):
    out=O/stage;out.mkdir(exist_ok=True)
    args=['train-kd' if stage=='logit' else 'train','--base',BASE,'--dataset',dataset,'--output',out]
    if stage=='logit':args+=['--cache',O/'logit_cache']
    for micro in [8,4,2]:
        label=stage+'_training' if micro==8 else stage+'_training_micro'+str(micro)
        try:
            run(label,'pnfp_7b_distill_worker.py',args+['--microbatch',str(micro)],additional=20*2**30)
            break
        except AssertionError:
            log=E/(label+'.log')
            text=log.read_text(errors='replace') if log.exists() else ''
            oom='CUDA out of memory' in text or 'torch.OutOfMemoryError' in text
            if not oom or micro==2 or (out/'final_model').exists():raise
            for name in ['exact_config.json','supervision_stats.json']:
                if (out/name).exists():shutil.copy2(out/name,E/(label+'_failed_'+name))
            put(E/(label+'_engineering_retry.json'),dict(reason='CUDA OOM',next_microbatch=micro//2,
                same_effective_batch=8,same_sample_order=True,token_weighted_accumulation=True,
                failed_attempt_preserved=True,restart='fresh clean Base; no scientific parameter change'))
    for name in ['exact_config.json','supervision_stats.json','training_summary.json','final_manifest.json']:
        shutil.copy2(out/name,E/(stage+'_'+name))
    fp=json.loads((E/'clone_preflight.json').read_text())['fingerprints']
    run(stage+'_detector','pnfp_evaluate.py',['--model-path',out/'final_model','--fingerprints',fp,
        '--output',E/(stage+'_detector.json'),'--label','pnfp_7b_'+stage,'--use-chat-template'])
    detector=json.loads((E/(stage+'_detector.json')).read_text())
    assert detector['evaluation_errors']==detector['invalid_samples']==0
    run(stage+'_utility','pnfp_7b_student_utility.py',['--base',BASE,'--a2',out/'final_model',
        '--output',E/(stage+'_utility.json'),'--batch-size','8'])
    put(E/(stage+'_full_experiment_log.json'),dict(status='COMPLETED',run_id='pnfp_7b_6004_'+stage,
        model=str(out/'final_model'),detector=detector,utility=json.loads((E/(stage+'_utility.json')).read_text()),
        config=json.loads((out/'exact_config.json').read_text()),runtime=json.loads((out/'training_summary.json').read_text()),
        provenance=dict(teacher=str(TEACHER),teacher_hits=804,independent_clean_initialization=str(BASE)),
        retention=detector['detected']/804))
    put(E/stage/'full_experiment_log.json',json.loads((E/(stage+'_full_experiment_log.json')).read_text()))


def main():
    E.mkdir(exist_ok=True);lock=(E/'campaign.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    assert not (E/'terminal.json').exists(),'Do not rerun completed or failed campaign implicitly'
    started=time.time();state={'status':'RUNNING','started':started}
    put(E/'campaign_state.json',dict(state,stage='WAITING_FOR_DIRECT_GENERATION',pid=os.getpid()))
    try:
        while True:
            generation=json.loads((E/'state.json').read_text())
            if generation['status']=='CANDIDATES_READY':break
            assert generation['status']=='GENERATING_DIRECT_CANDIDATES',generation
            os.kill(generation['pid'],0)
            time.sleep(30)
        # Generator has exited before any next GPU stage.
        time.sleep(2)
        direct=O/'direct/frozen_qa.jsonl'
        target=24000
        while True:
            try:
                rows,manifest=freeze_candidates(read_jsonl(O/'direct/raw_candidates.jsonl'),20000)
                break
            except ValueError as exc:
                if 'valid unique samples' not in str(exc):raise
                # Existing pnfp_ba_pipeline.py recovery: +2000 candidates,
                # same generator/seed/cursor, hard ceiling40000; never shrink20k.
                target+=2000
                assert target<=40000,'Canonical candidate ceiling reached before20k unique records'
                run('generation_cont_'+str(target),'generate_teacher_qa_formal.py',[
                    '--model-path',TEACHER,'--teacher-run-id','wa050_extension_v1_best_call21_fresh804',
                    '--output',O/'direct/raw_candidates.jsonl','--errors',O/'direct/errors.jsonl',
                    '--target-candidates',str(target),'--batch-size','8','--seed','42',
                    '--telemetry',E/('generation_cont_'+str(target)+'_telemetry.json')])
        assert not direct.exists();write_jsonl(direct,rows)
        manifest.update(file_sha256=sha(direct),teacher=str(TEACHER),teacher_fresh_hits=804,
                        raw_candidates_sha256=sha(O/'direct/raw_candidates.jsonl'),candidate_target=target)
        put(E/'direct_dataset_manifest.json',manifest)
        # Count EXACT shifted response positions before generating any targets.
        run('response_count','pnfp_7b_distill_worker.py',['stats','--base',BASE,'--dataset',direct,'--output',E],gpu=False)
        stats=json.loads((E/'supervision_stats.json').read_text())
        gate=budget(*shutil.disk_usage(R),{'future_final_students':3*13479264256,'qwen':6183463418,'overhead':10*2**30},
                    samples=20000,supervised_tokens=stats['supervised_tokens'])
        put(E/'exact_campaign_disk_budget.json',gate)
        assert gate['passed'],'Exact full-vocab disk budget insufficient'
        run('base_detector','pnfp_evaluate.py',['--model-path',BASE,'--fingerprints',json.loads((E/'clone_preflight.json').read_text())['fingerprints'],
            '--output',E/'base_detector.json','--label','clean_7b_base','--use-chat-template'])
        train_and_eval('direct',direct)
        # Restore only missing frozen Qwen content, with pinned repository SHA.
        qmanifest=P/'results/active_cross_lineage_bb/base_offline_reload_preflight.json'
        qm=json.loads(qmanifest.read_text());qm['model_revision']=qm['revision']
        original=json.loads((P/'results/passive5_shared_bb/qwen2_5_3b_instruct_modelscope_snapshot.json').read_text())['files']
        assert set(original)=={x['path'] for x in qm['files']}
        assert all(original[x['path']]['sha256']==x['sha256'] and original[x['path']]['size']==x['bytes'] for x in qm['files'])
        expected=json.loads((P/'configs/distillation/passive5_shared_bb.json').read_text())['paraphraser']['revision_identity']['weight_shard_sha256']
        assert sorted(expected)==sorted(x['sha256'] for x in qm['files'] if x['path'].endswith('.safetensors'))
        put(E/'qwen_restore_manifest.json',qm)
        run('qwen_restore','restore_xbb_qwen_base.py',[E/'qwen_restore_manifest.json',E/'qwen_restore_receipt.json'],additional=8*2**30,gpu=False)
        config=json.loads((P/'configs/distillation/pnfp_bb_pnfp_bb_20260904_055000.json').read_text())
        original_prompt=json.loads((P/'configs/distillation/passive5_shared_bb.json').read_text())['paraphrase']
        # Current canonical Bb preprocessing (including <=1-token identity rule)
        # remains fixed; latest user explicitly selects the older prompt BY SHA.
        for key in ['prompt_path','prompt_sha256','prompt_version']:
            config['paraphrase'][key]=original_prompt[key]
        atomic=config['paraphrase']['atomic_identity_preservation']
        atomic['historical_3b_count']=atomic.pop('expected_full20k_count')
        atomic['expected_full20k_count']=None
        config['student'].update(model_id='meta-llama/Llama-2-7b-chat-hf',
            revision='f5db02db724555f92da89c216ac04704f23d4590',initialization=str(BASE),resume=False)
        config['training']['optimizer']='bitsandbytes.optim.adamw.AdamW8bit 0.50.0'
        config['paraphraser']['revision']=qm['revision']
        config['source_dataset'].update(path=str(direct),record_count=20000,dataset_sha256=manifest['dataset_sha256'],
            frozen_jsonl_sha256=manifest['file_sha256'],sample_ids_sha256=manifest['sample_ids_sha256'],
            parent_experiment='PNFP7B Direct',parent_run_id='pnfp_7b_6004_direct')
        cfg=P/'configs/distillation/pnfp_7b_6004_paraphrase.json';put(cfg,config);put(E/'paraphrase_config.json',config)
        pp=O/'paraphrase';pp.mkdir(exist_ok=True)
        run('paraphrase_generation','passive5_shared_bb_paraphrase_runner.py',['--config',cfg,'--source',direct,
            '--journal',pp/'journal.jsonl','--backend','qwen'])
        run('paraphrase_freeze','passive5_shared_bb.py',['--config',cfg,'freeze','--source',direct,
            '--journal',pp/'journal.jsonl','--output',pp/'pairs.jsonl'],gpu=False)
        run('paraphrase_audit','passive5_shared_bb.py',['--config',cfg,'quality-audit','--pairs',pp/'pairs.jsonl',
            '--output-dir',E/'paraphrase_quality'],gpu=False)
        run('paraphrase_adapt','passive5_shared_bb.py',['--config',cfg,'adapt-student','--pairs',pp/'pairs.jsonl',
            '--output',pp/'frozen_qa.jsonl'],gpu=False)
        for name in ['pairs.manifest.json','telemetry.json','progress.json']:
            shutil.copy2(pp/name,E/('paraphrase_'+name))
        train_and_eval('paraphrase',pp/'frozen_qa.jsonl')
        run('logit_cache','pnfp_7b_distill_worker.py',['cache','--base',BASE,'--teacher',TEACHER,'--dataset',direct,
            '--cache',O/'logit_cache','--output',E],additional=stats['payload_bytes']+13479264256+2*2**30)
        train_and_eval('logit',direct)
        state['status']='COMPLETED'
    except BaseException:
        state.update(status='FAILED',error=traceback.format_exc())
    finally:
        state.update(ended=time.time(),pid=os.getpid(),shutdown_requires_local_sync_commit=True)
        verified={}
        for stage in ['direct','paraphrase','logit']:
            manifest=O/stage/'final_manifest.json'
            if manifest.exists():
                verified[stage]=all((O/stage/'final_model'/x['path']).is_file() and
                    sha(O/stage/'final_model'/x['path'])==x['sha256'] for x in json.loads(manifest.read_text())['files'])
        state['final_model_sha_verified']=verified
        state['teacher_preserved']=(TEACHER/'model.safetensors.index.json').is_file()
        if not all(verified.values()) or not state['teacher_preserved']:
            state['status']='FAILED';state['integrity_failure']=True
        if state['status']=='COMPLETED' and len(verified)==3:
            # Explicit user-authorized reproducible-logit cleanup, after every
            # final model SHA and detector/utility receipt is present. No model
            # or dataset is removed; retain both copies of the cache manifest.
            try:
                cache=(O/'logit_cache').resolve()
                manifest=json.loads((E/'logit_manifest.json').read_text())
                assert manifest['complete']
                plan=[]
                for item in manifest['shards']:
                    path=cache/item['path']
                    assert path.name==item['path'] and not path.is_symlink()
                    assert path.resolve().is_relative_to(cache) and path.stat().st_size==item['bytes']
                    plan.append(dict(item,absolute_path=str(path),classification='DELETE_REGENERABLE_LOGIT',
                        reason='Final Student verified; full shard SHA verified before training; provenance retained'))
                put(E/'logit_cleanup_dry_run.json',{'paths':plan,'disk_before':shutil.disk_usage(R)._asdict()})
                deleted=[]
                for item in plan:
                    Path(item['absolute_path']).unlink();deleted.append(item['absolute_path'])
                put(E/'logit_cleanup_receipt.json',{'deleted':deleted,'disk_after':shutil.disk_usage(R)._asdict(),
                    'formal_models_datasets_and_manifests_preserved':True})
            except Exception:
                put(E/'logit_cleanup_pending.json',{'noncritical':True,'error':traceback.format_exc()})
        # All subprocesses are synchronous: no own GPU worker remains here.
        put(E/'terminal.json',state);put(E/'campaign_state.json',state)
        lines=['# PN-FP 7B distillation on 6004', '', 'Status: '+state['status'], '',
            '| Condition | Hits/1024 | Recall % | Retention vs Teacher | ARC | MC2 | Runtime s | Peak VRAM GiB |',
            '|---|---:|---:|---:|---:|---:|---:|---:|',
            '| Teacher | 804 | 78.515625 | 1 | .4206484642 | .4419976151 | historical | historical |']
        if (E/'base_detector.json').exists():
            h=json.loads((E/'base_detector.json').read_text())['detected']
            lines.append(f'| Base | {h} | {h/1024*100:.4f} | {h/804:.6f} | .3660409556 | .4575471579 | historical utility | N/A |')
        else:lines.append('| Base | NOT_RUN | | | .3660409556 | .4575471579 | historical utility | N/A |')
        for stage in ['direct','paraphrase','logit']:
            f=E/(stage+'_full_experiment_log.json')
            if not f.exists():lines.append('| '+stage+' | NOT_COMPLETED | | | | | | |');continue
            x=json.loads(f.read_text());h=x['detector']['detected'];u=x['utility']['a2'];t=x['runtime']
            lines.append(f"| {stage} | {h} | {h/1024*100:.4f} | {h/804:.6f} | {u['arc_challenge_acc_norm']} | {u['truthfulqa_mc2_acc']} | {t['runtime_seconds']:.2f} | {t['peak_vram_bytes']/2**30:.2f} |")
        if 'error' in state:lines+=['','Failure evidence:','```',state['error'],'```']
        (E/'final_report.md').write_text('\n'.join(lines)+'\n');subprocess.run(['sync'])


if __name__=='__main__':main()
