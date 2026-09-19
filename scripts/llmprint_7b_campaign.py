"""Independent serial LLMPrint7B reference/calibration and three fresh Students.

No PNFP fingerprints, Teacher, Student or generated data are consumed. Shared
7B transport/training/utility wrappers implement the existing benchmark only.
Local guardian verifies evidence and commits before invoking authorized shutdown.
"""
import fcntl, json, math, os, shutil, subprocess, time, traceback
from pathlib import Path
import pnfp_7b_distill_campaign as rt
from pnfp_7b_disk_gate import budget
from distillation_data import freeze_candidates, read_jsonl, write_jsonl
from llmprint_detect_dual import calibrate_paper, calibrate_release, paper_model, release_model

P=rt.P; SHARED=rt.R; BASE=rt.BASE
O=Path('/root/autodl-tmp/WMKD_Benchmark_data/llmprint_7b'); E=P/'results/llmprint/scale_7b'
REV='f5db02db724555f92da89c216ac04704f23d4590'; MODEL='meta-llama/Llama-2-7b-chat-hf'
rt.E=E;rt.R=O
put=rt.put;sha=rt.sha
TRAIN_ENV=rt.ENV.copy()
DETECT_ENV=dict(TRAIN_ENV,PYTHONPATH=str(O/'runtime451')+':'+str(P/'scripts'),CUBLAS_WORKSPACE_CONFIG=':4096:8')

def run(stage,script,args,additional=2*2**30,gpu=True,detector=False):
    rt.ENV=DETECT_ENV if detector else TRAIN_ENV
    rt.run(stage,script,args,additional=additional,gpu=gpu)

def load(path):return json.loads(Path(path).read_text())

def sequence(stage,model,model_id,revision):
    output=E/(stage+'_sequence.json')
    run(stage+'_sequence','llmprint_evaluate_probability_sequence.py',[
        '--model',model,'--model-id',model_id,'--revision',revision,
        '--fingerprint-dir',E/'fingerprints','--fingerprint-manifest',E/'fingerprint_manifest.json',
        '--output',output,'--dtype','float16'],detector=True)
    x=load(output);assert x['fresh_reload'] and x['record_count']==200
    assert x['fingerprint_manifest_sha256']==sha(E/'fingerprint_manifest.json')
    seq=[]
    for i,r in enumerate(x['records']):
        assert r['pair_id']==f'llmprint-pair-{i:03d}'
        vals=[r[k] for k in ['w_plus_logit','w_minus_logit','w_plus_probability','w_minus_probability']]
        assert all(math.isfinite(v) for v in vals),'Nonfinite detector values'
        seq.append(vals[2:])
    return seq

def detector_result(stage,seq):
    frozen=load(E/'calibration.json');ref=load(E/'calibration_input.json')['reference_sequence']
    assert sha(E/'calibration.json')==load(E/'calibration_freeze.json')['calibration_sha256']
    primary=paper_model(ref,seq);tau=frozen['primary']['final_tau']
    primary.update(threshold=tau,positive=primary['accuracy']>=tau)
    supplementary=release_model(ref,seq,min_n=frozen['supplementary']['calibrated_min_n'])
    x=dict(primary=primary,supplementary=supplementary,fresh_reload=True,threshold_frozen_before_students=True)
    put(E/(stage+'_detector.json'),x);return x

def milestone(stage,payload):
    payload.update(method='LLMPrint',run_id='llmprint_7b_'+stage,status='COMPLETED',completed=time.time(),
        scientific_config=load(E/'exact_protocol.json'),reference_model=MODEL,reference_revision=REV,
        final_model_modified=(stage!='reference'),no_pnfp_assets_used=True)
    put(E/stage/'full_experiment_log.json',payload)
    put(E/(stage+'_complete.json'),dict(stage=stage,time=time.time(),full_log_sha256=sha(E/stage/'full_experiment_log.json')))

def verify_base():
    manifest=load(E/'canonical_model_source_manifest.json')
    assert manifest['canonical_revision']==REV and manifest['canonical_upstream']==MODEL
    assert Path(manifest['path'])==BASE
    files=[]
    for item in manifest['files']:
        file=BASE/item['Path'];assert file.stat().st_size==item['Size'] and sha(file)==item['Sha256']
        files.append(dict(path=item['Path'],sha256=item['Sha256'],bytes=item['Size']))
    put(E/'clean_reference_manifest.json',dict(model=MODEL,revision=REV,path=str(BASE),files=files,verified=True,
        source='Existing clean canonical model transport manifest, not PNFP Teacher weights'))

def train_eval(stage,dataset):
    out=O/stage;out.mkdir(exist_ok=True)
    args=['train-kd' if stage=='logit' else 'train','--base',BASE,'--dataset',dataset,'--output',out]
    if stage=='logit':args+=['--cache',O/'logit_cache']
    for micro in [8,4,2]:
        label=stage+'_training'+('' if micro==8 else '_micro'+str(micro))
        try:
            run(label,'pnfp_7b_distill_worker.py',args+['--microbatch',micro],additional=20*2**30);break
        except AssertionError:
            log=(E/(label+'.log')).read_text(errors='replace')
            if not ('CUDA out of memory' in log or 'torch.OutOfMemoryError' in log) or micro==2 or (out/'final_model').exists():raise
            put(E/(label+'_retry.json'),dict(reason='CUDA OOM',next_microbatch=micro//2,effective_batch=8,
                same_sample_order=True,normalization='supervised-token weighted original batch8',restart='independent fresh Base'))
    for name in ['exact_config.json','supervision_stats.json','training_summary.json','final_manifest.json']:
        shutil.copy2(out/name,E/(stage+'_'+name))
    seq=sequence(stage,out/'final_model','llmprint_7b_'+stage,'trained_from_'+REV)
    result=detector_result(stage,seq)
    run(stage+'_utility','pnfp_7b_student_utility.py',['--base',BASE,'--a2',out/'final_model','--output',E/(stage+'_utility.json'),'--batch-size','8'])
    milestone(stage,dict(detector=result,utility=load(E/(stage+'_utility.json')),runtime=load(out/'training_summary.json'),
        training_config=load(out/'exact_config.json'),final_model=str(out/'final_model'),final_model_manifest=load(out/'final_manifest.json'),
        dataset_sha256=sha(dataset),calibration_sha256=sha(E/'calibration.json')))

def main():
    E.mkdir(parents=True,exist_ok=True);O.mkdir(exist_ok=True)
    lock=(E/'campaign.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    assert not (E/'terminal.json').exists(),'Never implicitly rerun a terminal campaign'
    state=dict(status='RUNNING',started=time.time(),pid=os.getpid())
    try:
        verify_base()
        # Download no model until its metadata-sized disk gate has passed.
        panel=load(P/'results/llmprint/validation_negative_panel_manifest.json')
        assert panel['slots']==13 and len(panel['models'])==13
        shutil.copy2(P/'results/llmprint/validation_negative_panel_manifest.json',E/'negative_panel.json')
        (O/'negative_models').mkdir(exist_ok=True)
        for m in panel['models']:
            slot=m['slot'];receipt=E/f'negative_{slot:02d}_acquisition.json'
            run(f'negative_{slot:02d}_download','llmprint_7b_negative_fetch.py',[
                '--slot',slot,'--root',O/'negative_models','--output',receipt],additional=2*2**30,gpu=False)
        while not (E/'construction_terminal.json').exists():
            put(E/'campaign_state.json',dict(state,stage='REFERENCE_CONSTRUCTION',completed_fingerprints=len(list((E/'fingerprints').glob('*.json')))))
            time.sleep(30)
        assert load(E/'construction_terminal.json')['status']=='COMPLETED',load(E/'construction_terminal.json')
        ref=sequence('reference',BASE,MODEL,REV)
        negatives={}
        for m in panel['models']:
            receipt=load(E/f'negative_{m["slot"]:02d}_acquisition.json')
            negatives[m['official_upstream_id']]=sequence(f'negative_{m["slot"]:02d}',receipt['local_path'],m['official_upstream_id'],m['modelscope_revision'])
        put(E/'calibration_input.json',dict(reference_sequence=ref,validation_negative_sequences=negatives))
        cal=dict(primary=calibrate_paper(ref,negatives),supplementary=calibrate_release(ref,negatives))
        put(E/'calibration.json',cal)
        put(E/'calibration_freeze.json',dict(timestamp=time.time(),calibration_sha256=sha(E/'calibration.json'),
            input_sha256=sha(E/'calibration_input.json'),fingerprint_manifest_sha256=sha(E/'fingerprint_manifest.json'),
            reference_sequence_sha256=sha(E/'reference_sequence.json'),students_started=False,negative_count=13))
        result=detector_result('reference',ref)
        assert result['primary']['accuracy']==1.0 and result['primary']['positive'],'Reference self-identification failed'
        # Clean reference equals Base. Reuse the same checkpoint's existing formal
        # benchmark utility, with source/identity documented; no PNFP result reuse.
        base=load(P/'results/pnfp/scale_7b/wa050_extension/receipts/final_utility.json')['base']
        assert base['model_path']==str(BASE)
        put(E/'reference_utility.json',dict(base=base,a2=base,source='existing clean canonical Base utility; same exact revision/SHA',reference_equals_base=True))
        milestone('reference',dict(detector=result,utility=load(E/'reference_utility.json'),calibration=cal,
            artifact='200 frozen fingerprint records; reference model unmodified',provenance=load(E/'clean_reference_manifest.json'),
            runtime=load(E/'construction_runtime.json')))
        (O/'direct').mkdir(exist_ok=True)
        target=24000
        while True:
            run('direct_generation_'+str(target),'generate_teacher_qa_formal.py',[
                '--model-path',BASE,'--teacher-run-id','llmprint_7b_clean_reference',
                '--output',O/'direct/raw_candidates.jsonl','--errors',O/'direct/errors.jsonl',
                '--target-candidates',target,'--batch-size','8','--seed','42',
                '--telemetry',E/('generation_'+str(target)+'_telemetry.json')])
            try:rows,manifest=freeze_candidates(read_jsonl(O/'direct/raw_candidates.jsonl'),20000);break
            except ValueError as exc:
                if 'valid unique samples' not in str(exc):raise
                target+=2000;assert target<=60000,'Frozen passive Ba candidate ceiling reached'
        direct=O/'direct/frozen_qa.jsonl';assert not direct.exists();write_jsonl(direct,rows)
        manifest.update(file_sha256=sha(direct),teacher=str(BASE),teacher_revision=REV,raw_sha256=sha(O/'direct/raw_candidates.jsonl'),candidate_target=target)
        put(E/'direct_dataset_manifest.json',manifest)
        run('response_count','pnfp_7b_distill_worker.py',['stats','--base',BASE,'--dataset',direct,'--output',E],gpu=False)
        stats=load(E/'supervision_stats.json')
        gate=budget(*shutil.disk_usage(O),{'three_final_students':3*13479264256,'overhead':10*2**30},samples=20000,supervised_tokens=stats['supervised_tokens'])
        put(E/'exact_campaign_disk_budget.json',gate);assert gate['passed']
        train_eval('direct',direct)
        # Reuse byte-verified canonical Qwen paraphraser and the explicitly
        # selected prompt SHA, retaining the current <=1-token identity rule.
        qm=load(P/'results/active_cross_lineage_bb/base_offline_reload_preflight.json');qm['model_revision']=qm['revision']
        put(E/'qwen_restore_manifest.json',qm)
        run('qwen_restore','restore_xbb_qwen_base.py',[E/'qwen_restore_manifest.json',E/'qwen_restore_receipt.json'],additional=8*2**30,gpu=False)
        config=load(P/'configs/distillation/passive5_shared_bb3.json')
        original=load(P/'configs/distillation/passive5_shared_bb.json')['paraphrase']
        for key in ['prompt_path','prompt_sha256','prompt_version']:config['paraphrase'][key]=original[key]
        assert sha(P/config['paraphrase']['prompt_path'])==load(E/'exact_protocol.json')['paraphrase_prompt_sha256']
        config['identity']='llmprint_7b_paraphrase';config['experiment']='LLMPrint 7B Paraphrase';config['methods']=['LLMPrint']
        config['paraphrase']['atomic_identity_preservation']['expected_full20k_count']=None
        config['paraphraser']['revision']=qm['revision']
        config['student'].update(model_id=MODEL,revision=REV,path=str(BASE),initialization='fresh_canonical_original_revision',resume=False)
        config['training']['optimizer']='bitsandbytes.optim.adamw.AdamW8bit 0.50.0'
        config['source_dataset'].update(path=str(direct),manifest_path=str(E/'direct_dataset_manifest.json'),record_count=20000,
            dataset_sha256=manifest['dataset_sha256'],frozen_jsonl_sha256=manifest['file_sha256'],sample_ids_sha256=manifest['sample_ids_sha256'],
            parent_experiment='LLMPrint7B Direct',parent_run_id='llmprint_7b_direct')
        cfg=P/'configs/distillation/llmprint_7b_paraphrase.json';put(cfg,config);put(E/'paraphrase_config.json',config)
        pp=O/'paraphrase';pp.mkdir(exist_ok=True)
        run('paraphrase_generation','passive5_shared_bb_paraphrase_runner.py',['--config',cfg,'--source',direct,'--journal',pp/'journal.jsonl','--backend','qwen'])
        run('paraphrase_freeze','passive5_shared_bb.py',['--config',cfg,'freeze','--source',direct,'--journal',pp/'journal.jsonl','--output',pp/'pairs.jsonl'],gpu=False)
        run('paraphrase_audit','passive5_shared_bb.py',['--config',cfg,'quality-audit','--pairs',pp/'pairs.jsonl','--output-dir',E/'paraphrase_quality'],gpu=False)
        run('paraphrase_adapt','passive5_shared_bb.py',['--config',cfg,'adapt-student','--pairs',pp/'pairs.jsonl','--output',pp/'frozen_qa.jsonl'],gpu=False)
        for name in ['pairs.manifest.json','telemetry.json','progress.json']:shutil.copy2(pp/name,E/('paraphrase_'+name))
        train_eval('paraphrase',pp/'frozen_qa.jsonl')
        run('logit_cache','pnfp_7b_distill_worker.py',['cache','--base',BASE,'--teacher',BASE,'--dataset',direct,'--cache',O/'logit_cache','--output',E],additional=stats['payload_bytes']+13479264256+2*2**30)
        train_eval('logit',direct)
        state['status']='COMPLETED'
    except BaseException:
        state.update(status='FAILED',error=traceback.format_exc())
        put(E/'failure_pending_closeout.json',state)
    finally:
        # A failure during CPU downloads must not shut down an active constructor.
        while not (E/'construction_terminal.json').exists():time.sleep(30)
        verified={}
        for stage in ['direct','paraphrase','logit']:
            manifest=O/stage/'final_manifest.json'
            if manifest.exists():
                verified[stage]=all((O/stage/'final_model'/x['path']).stat().st_size==x['bytes'] and sha(O/stage/'final_model'/x['path'])==x['sha256'] for x in load(manifest)['files'])
        state.update(ended=time.time(),final_model_sha_verified=verified,shutdown_requires_local_sync_commit=True)
        if not all(verified.values()):state.update(status='FAILED',integrity_failure=True)
        lines=['# LLMPrint 7B same-backbone extension','', 'Status: '+state['status'],'',
            'Passive reference is the unmodified clean Llama-2-7b-chat-hf, revision '+REV+'.',
            'AdamW8bit is an engineering storage adaptation; not canonical FP32 Adam equivalence.',
            'Primary detector: bit agreement; fresh 13-negative calibration before any Student.','',
            '| Condition | Score | Threshold | Detected | ARC | TruthfulQA MC2 | Runtime s | Peak VRAM GiB |',
            '|---|---:|---:|---|---:|---:|---:|---:|']
        for stage in ['reference','direct','paraphrase','logit']:
            file=E/stage/'full_experiment_log.json'
            if not file.exists():lines.append('| '+stage+' | NOT_COMPLETED | | | | | | |');continue
            x=load(file);d=x['detector']['primary'];u=x['utility']['a2'];r=x['runtime']
            seconds=r.get('runtime_seconds',r.get('ended',0)-r.get('started',0));vram=r.get('peak_vram_bytes',r.get('sampled_gpu_peak_bytes',0))
            lines.append(f'| {stage} | {d["accuracy"]:.5f} | {d["threshold"]:.7f} | {d["positive"]} | {u["arc_challenge_acc_norm"]:.6f} | {u["truthfulqa_mc2_acc"]:.6f} | {seconds:.2f} | {vram/2**30:.2f} |')
        if 'error' in state:lines+=['','Failure evidence:','```',state['error'],'```']
        (E/'final_report.md').write_text('\n'.join(lines)+'\n')
        put(E/'terminal.json',state);put(E/'campaign_state.json',state);subprocess.run(['sync'])

if __name__=='__main__':main()
