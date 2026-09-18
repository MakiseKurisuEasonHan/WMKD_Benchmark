"""One frozen-protocol rerun with full recall after WA and best-only retention."""
import hashlib,json,os,random,shutil,sys,time,traceback,types
from pathlib import Path
import pnfp_7b_adamw8bit_pilot as pilot

ROOT=pilot.ROOT;P=pilot.P;OUT=ROOT/'trajectory_adamw8bit_v1'
trajectory=[];best_count=0;best_step=None;batch_hash=hashlib.sha256();batch_count=0

def record_batch(inputs):
    global batch_count
    for key in ('input_ids','attention_mask','labels'):
        if key in inputs:
            value=inputs[key].detach().cpu().contiguous()
            batch_hash.update(key.encode());batch_hash.update(str(tuple(value.shape)).encode())
            batch_hash.update(value.numpy().tobytes())
    batch_count+=1

def save_best(model,step,count):
    from transformers import AutoTokenizer
    pending=OUT/'best_model.pending';best=OUT/'best_model';retired=OUT/'best_model.retired'
    assert not pending.exists() and not retired.exists()
    assert shutil.disk_usage(OUT).free>15*1024**3,'Insufficient space for safe best replacement'
    started=time.perf_counter();pending.mkdir()
    model.save_pretrained(pending,safe_serialization=True,max_shard_size='5GB')
    AutoTokenizer.from_pretrained(ROOT/'models/Llama-2-7b-chat-hf',local_files_only=True).save_pretrained(pending)
    files=[]
    for f in sorted(pending.iterdir()):
        h=hashlib.sha256()
        with f.open('rb') as stream:
            for block in iter(lambda:stream.read(8*1024**2),b''):h.update(block)
        files.append({'path':f.name,'bytes':f.stat().st_size,'sha256':h.hexdigest()})
    assert len([r for r in files if r['path'].endswith('.safetensors')])==3
    manifest={'step':step,'recall':count,'path':str(best),'files':files}
    (OUT/f'best_manifest_step_{step:02d}.json').write_text(json.dumps(manifest,indent=2))
    if best.exists():best.rename(retired)
    pending.rename(best)
    (OUT/'best_manifest.json').write_text(json.dumps(manifest,indent=2))
    if retired.exists():
        assert retired.resolve().parent==OUT.resolve() and retired.name=='best_model.retired'
        assert not retired.is_symlink() and best.is_dir() and all((best/r['path']).stat().st_size==r['bytes'] for r in files)
        old_bytes=sum(f.stat().st_size for f in retired.rglob('*') if f.is_file())
        with (OUT/'checkpoint_retention.jsonl').open('a') as f:
            f.write(json.dumps({'action':'DELETE_SUPERSEDED_DIAGNOSTIC_BEST','exact_path':str(retired),'bytes':old_bytes,'replacement_step':step,'replacement_manifest':f'best_manifest_step_{step:02d}.json','old_formal_run_untouched':True})+'\n')
        shutil.rmtree(retired)
    return time.perf_counter()-started

def trajectory_probe(model,step):
    global best_count,best_step,batch_hash,batch_count
    import torch,numpy as np
    import pnfp_evaluate as detector
    py_state=random.getstate();np_state=np.random.get_state();training=model.training
    old_argv=sys.argv;old_factory=detector.AutoModelForCausalLM
    fp=json.loads((ROOT/'fingerprint_manifest.json').read_text())
    output=OUT/f'recall_step_{step:02d}.json';save_seconds=0
    try:
        with torch.random.fork_rng(devices=[0]):
            detector.AutoModelForCausalLM=types.SimpleNamespace(from_pretrained=lambda *a,**kw:model)
            sys.argv=['pnfp_evaluate','--model-path',str(ROOT/'models/Llama-2-7b-chat-hf'),'--fingerprints',fp['official_output'],'--output',str(output),'--label',f'trajectory_in_memory_after_WA_call{step}','--count','1024','--use-chat-template','--generation-response-length','1']
            torch.cuda.synchronize();start=time.perf_counter();detector.main();torch.cuda.synchronize()
            eval_seconds=time.perf_counter()-start
            d=json.loads(output.read_text());assert d['fingerprints_evaluated']==1024 and d['invalid_samples']==d['evaluation_errors']==0
            improved=d['detected']>best_count
            if improved:
                save_seconds=save_best(model,step,d['detected']);best_count=d['detected'];best_step=step
    finally:
        detector.AutoModelForCausalLM=old_factory;sys.argv=old_argv
        model.train(training);random.setstate(py_state);np.random.set_state(np_state)
    update=json.loads((OUT/'steps.jsonl').read_text().splitlines()[-1]);assert update['update']==step
    old_steps=json.loads((ROOT/'teacher_adamw8bit_v1/result.json').read_text())['steps']
    reference=old_steps[step-1];assert update['lr_used']==reference['lr_used'],'Frozen LR trajectory changed'
    row={'update':step,'lr':update['lr_used'][0],'train_loss':update['training_loss'],'recall':d['detected'],'total':1024,'recall_percent':d['detection_rate']*100,'evaluation_seconds':eval_seconds,'best_save_seconds':save_seconds,'new_best':improved,'best_update_so_far':best_step,'best_recall_so_far':best_count,'microbatches':batch_count,'ordered_input_batch_sha256':batch_hash.hexdigest(),'prior_formal_train_loss':reference['training_loss'],'train_loss_delta_vs_prior_formal':update['training_loss']-reference['training_loss'],'loss_threshold_crossed':update['training_loss']<.005,'measurement_phase':'after optimizer and epoch WA; before next update'}
    trajectory.append(row);batch_hash=hashlib.sha256();batch_count=0
    with (OUT/'trajectory.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
    (OUT/'trajectory_summary.json').write_text(json.dumps({'measurements':len(trajectory),'best_update':best_step,'best_recall':best_count,'evaluation_seconds':sum(r['evaluation_seconds'] for r in trajectory),'checkpoint_save_seconds':sum(r['best_save_seconds'] for r in trajectory),'distillation_started':False},indent=2))
    print('TRAJECTORY '+json.dumps(row),flush=True)

def main():
    formal=P/'results/pnfp/scale_7b/teacher/receipts/executed_training.py'
    source=formal.read_text()
    cfg=json.loads((P/'configs/watermark/pnfp_7b_trajectory.json').read_text())
    parent=json.loads((P/'configs/watermark/pnfp_7b_teacher.json').read_text())
    allowed={'id','scope','early_stop','diagnostic','preliminary_detector'}
    assert all(cfg[k]==v for k,v in parent.items() if k not in allowed),'Unapproved scientific config difference'
    replacements={
        'pnfp_7b_teacher.json':'pnfp_7b_trajectory.json',
        "reason='MAX_40_EPOCHS'":"reason='DIAGNOSTIC_FROZEN_40_CALL_HORIZON'",
        "if step%5==0: recall_probe(kw['model'],step)":"trajectory_probe(kw['model'],step)",
        "if loss<.005:reason='TRAIN_LOSS_EARLY_STOP';control.should_training_stop=True":"# Diagnostic: loss threshold is recorded, not a sole stop rule.",
        "loss=super().training_step(*a,**kw);assert":"record_batch(a[1] if len(a)>1 else kw['inputs'])\n            loss=super().training_step(*a,**kw);assert"
    }
    for old,new in replacements.items():
        assert source.count(old)==1,(old,source.count(old));source=source.replace(old,new)
    (OUT/'executed_training.py').write_text(source)
    provenance={'model_manifest':json.loads((ROOT/'model_manifest.json').read_text()),'fingerprints':json.loads((ROOT/'fingerprint_manifest.json').read_text()),'config':cfg,'parent_executed_source_sha256':hashlib.sha256(formal.read_bytes()).hexdigest(),'executed_source_sha256':hashlib.sha256(source.encode()).hexdigest(),'fresh_initialization':True,'data_order':'Same seed/sampler/benign mixing; RNG restored around detector and checkpoint saving; ordered input hashes logged. Prior formal run did not record batch hashes, so cross-run order equality cannot be proved from hashes.','no_optimizer_implementation_equivalence_claim':True}
    (OUT/'provenance.json').write_text(json.dumps(provenance,indent=2))
    pilot.OUT=OUT;pilot.trajectory_probe=trajectory_probe;pilot.record_batch=record_batch
    exec(compile(source,str(OUT/'executed_training.py'),'exec'),pilot.__dict__)
    pilot.main()
    assert len(trajectory)==40 and best_step is not None,'No positive best checkpoint; stop before utility'

if __name__=='__main__':
    try:main()
    except BaseException:
        (OUT/'failure.json').write_text(json.dumps({'status':'FAILED_STOPPED','traceback':traceback.format_exc(),'distillation_started':False},indent=2));raise
