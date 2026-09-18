"""One WA=.50 pilot; frozen optimizer/LR/data, utility gates, no formal training."""
import gc,hashlib,json,random,shutil,sys,time,traceback,types
from pathlib import Path
import pnfp_7b_adamw8bit_pilot as pilot
import pnfp_7b_trajectory as parent
ROOT=pilot.ROOT;P=pilot.P;OUT=ROOT/'wa050_pilot_v1'
rows=[];highest=0;selected=0;selected_step=None;stale=0;last_proxy_count=None;stop_reason=None

def proxy(checkpoint,step):
    import torch,datasets,lm_eval
    from transformers import AutoModelForCausalLM,AutoTokenizer
    from lm_eval.models.huggingface import HFLM
    import pnfp_a2_benchmark_eval as bench
    import pnfp_7b_final_utility as offline
    from accelerate.state import GradientState
    old_main=bench.main;old_load=datasets.load_dataset;gradient_before=dict(GradientState().plugin_kwargs)
    def score(path):
        model=AutoModelForCausalLM.from_pretrained(str(path),local_files_only=True,torch_dtype=torch.bfloat16).cuda().eval()
        tokenizer=AutoTokenizer.from_pretrained(str(path),local_files_only=True)
        harness=HFLM(pretrained=model,tokenizer=tokenizer,batch_size=8)
        result=lm_eval.simple_evaluate(model=harness,tasks=['arc_challenge','truthfulqa_mc2'],batch_size=8,apply_chat_template=True,num_fewshot=0,limit=256,log_samples=False)
        scores=result['results'];answer={'arc_challenge_acc_norm':scores['arc_challenge']['acc_norm,none'],'truthfulqa_mc2_acc':scores['truthfulqa_mc2']['acc,none'],'raw_results':scores}
        del result,harness,model,tokenizer;gc.collect();torch.cuda.empty_cache()
        assert dict(GradientState().plugin_kwargs)==gradient_before,'Proxy changed accumulation state'
        return answer
    result={};start=time.perf_counter()
    def evaluate():
        base_file=OUT/'proxy_base256.json'
        if not base_file.exists():base_file.write_text(json.dumps(score(ROOT/'models/Llama-2-7b-chat-hf'),indent=2))
        result.update(base=json.loads(base_file.read_text()),checkpoint=score(checkpoint))
    try:
        bench.main=evaluate;offline.main()
    finally:bench.main=old_main;datasets.load_dataset=old_load
    result.update(step=step,limit_per_task=256,selection='fixed first256 canonical test/validation; same subset for base and checkpoint',seconds=time.perf_counter()-start)
    result['delta']={k:result['checkpoint'][k]-result['base'][k] for k in ('arc_challenge_acc_norm','truthfulqa_mc2_acc')}
    result['stop_excessive_utility_loss']=any(v<-.05 for v in result['delta'].values())
    (OUT/f'proxy_step_{step:02d}.json').write_text(json.dumps(result,indent=2)+'\n')
    return result

def save_candidate(model,step,count):
    global last_proxy_count,stop_reason
    from transformers import AutoTokenizer
    pending=OUT/'best_model.pending';best=OUT/'best_model';retired=OUT/'best_model.retired'
    assert not pending.exists() and not retired.exists() and shutil.disk_usage(OUT).free>15*1024**3
    start=time.perf_counter();pending.mkdir();model.save_pretrained(pending,safe_serialization=True,max_shard_size='5GB')
    AutoTokenizer.from_pretrained(ROOT/'models/Llama-2-7b-chat-hf',local_files_only=True).save_pretrained(pending)
    files=[]
    for f in sorted(pending.iterdir()):
        h=hashlib.sha256()
        with f.open('rb') as stream:
            for block in iter(lambda:stream.read(8*1024**2),b''):h.update(block)
        files.append({'path':f.name,'bytes':f.stat().st_size,'sha256':h.hexdigest()})
    save_seconds=time.perf_counter()-start;utility=None
    if count>=512 and (last_proxy_count is None or count-last_proxy_count>=103):
        utility=proxy(pending,step);last_proxy_count=count
        if utility['stop_excessive_utility_loss']:stop_reason='EXCESSIVE_PROXY_UTILITY_DROP'
    rejected=utility is not None and utility['stop_excessive_utility_loss']
    manifest={'step':step,'recall':count,'files':files,'path':str(best),'proxy_checked':utility is not None,'utility_rejected':rejected}
    (OUT/f'checkpoint_manifest_step_{step:02d}.json').write_text(json.dumps(manifest,indent=2))
    if rejected and best.exists():
        assert pending.resolve().parent==OUT.resolve() and not pending.is_symlink();shutil.rmtree(pending)
        with (OUT/'checkpoint_retention.jsonl').open('a') as f:f.write(json.dumps({'action':'REJECT_NEW_HIGH_UTILITY_DROP_KEEP_PREVIOUS_BEST','step':step,'path':str(pending)})+'\n')
        return False,save_seconds,utility
    if best.exists():best.rename(retired)
    pending.rename(best);(OUT/'best_manifest.json').write_text(json.dumps(manifest,indent=2))
    if retired.exists():
        assert retired.resolve().parent==OUT.resolve() and not retired.is_symlink();shutil.rmtree(retired)
        with (OUT/'checkpoint_retention.jsonl').open('a') as f:f.write(json.dumps({'action':'REPLACE_SUPERSEDED_PILOT_BEST','step':step,'path':str(retired)})+'\n')
    return True,save_seconds,utility

def trajectory_probe(model,step):
    global highest,selected,selected_step,stale,stop_reason
    import torch,numpy as np
    import pnfp_evaluate as detector
    py=random.getstate();np_state=np.random.get_state();training=model.training;argv=sys.argv;factory=detector.AutoModelForCausalLM
    update=json.loads((OUT/'steps.jsonl').read_text().splitlines()[-1]);old_rows=[json.loads(x) for x in (ROOT/'trajectory_adamw8bit_v1/trajectory.jsonl').read_text().splitlines()];reference=old_rows[step-1]
    assert update['lr_used'][0]==reference['lr'];assert parent.batch_hash.hexdigest()==reference['ordered_input_batch_sha256'],'Data order changed'
    save_seconds=0;utility=None
    try:
        with torch.random.fork_rng(devices=[0]):
            fp=json.loads((ROOT/'fingerprint_manifest.json').read_text());output=OUT/f'recall_step_{step:02d}.json'
            detector.AutoModelForCausalLM=types.SimpleNamespace(from_pretrained=lambda *a,**kw:model)
            sys.argv=['pnfp_evaluate','--model-path',str(ROOT/'models/Llama-2-7b-chat-hf'),'--fingerprints',fp['official_output'],'--output',str(output),'--label',f'wa050_pilot_after_WA_call{step}','--count','1024','--use-chat-template','--generation-response-length','1']
            torch.cuda.synchronize();start=time.perf_counter();detector.main();torch.cuda.synchronize();eval_seconds=time.perf_counter()-start
            d=json.loads(output.read_text());assert d['fingerprints_evaluated']==1024 and d['invalid_samples']==d['evaluation_errors']==0
            count=d['detected'];improved=count>highest
            if update['lr_used'][0]>0:
                stale=0 if improved else stale+1
                if improved:
                    highest=count;kept,save_seconds,utility=save_candidate(model,step,count)
                    if kept:selected=count;selected_step=step
                if stop_reason is None and highest-count>=103:stop_reason='RECALL_DROP_AT_LEAST_10PP'
                if stop_reason is None and stale>=3:stop_reason='THREE_NONZERO_UPDATES_WITHOUT_NEW_HIGH'
                if stop_reason is None and step>=14:stop_reason='MAX_12_NONZERO_LR_UPDATES'
    finally:
        detector.AutoModelForCausalLM=factory;sys.argv=argv;model.train(training);random.setstate(py);np.random.set_state(np_state)
    row={'update':step,'nonzero_lr_update':max(0,step-2),'lr':update['lr_used'][0],'train_loss':update['training_loss'],'recall':count,'recall_percent':count/1024*100,'new_high':improved,'highest_recall':highest,'selected_best_recall':selected,'selected_best_update':selected_step,'evaluation_seconds':eval_seconds,'checkpoint_save_seconds':save_seconds,'proxy_seconds':utility['seconds'] if utility else 0,'proxy_delta':utility['delta'] if utility else None,'data_order_matches_wa075':True,'ordered_input_batch_sha256':parent.batch_hash.hexdigest(),'stop_reason':stop_reason}
    rows.append(row);parent.batch_hash=hashlib.sha256();parent.batch_count=0
    with (OUT/'trajectory.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
    (OUT/'pilot_progress.json').write_text(json.dumps(row,indent=2));print('WA050 '+json.dumps(row),flush=True)

def main():
    cfg=json.loads((P/'configs/watermark/pnfp_7b_wa050.json').read_text());old=json.loads((P/'configs/watermark/pnfp_7b_trajectory.json').read_text())
    allowed={'id','scope','wa','pilot_max_calls','diagnostic','early_stop','preliminary_detector'}
    assert all(cfg[k]==v for k,v in old.items() if k not in allowed);assert cfg['wa']==.5 and cfg['pilot_max_calls']==14
    source=(P/'results/pnfp/scale_7b/trajectory/receipts/executed_training.py').read_text()
    replacements={'pnfp_7b_trajectory.json':'pnfp_7b_wa050.json',"reason='DIAGNOSTIC_FROZEN_40_CALL_HORIZON'":"reason='MAX_12_NONZERO_LR_UPDATES'",'forgetting_regularizer_strength=.75':'forgetting_regularizer_strength=.50',"trajectory_probe(kw['model'],step)":"trajectory_probe(kw['model'],step)\n            if should_stop(): a[2].should_training_stop=True"}
    for a,b in replacements.items():assert source.count(a)==1,(a,source.count(a));source=source.replace(a,b)
    cut=source.index("    model=holder['trainer'].accelerator.unwrap_model(holder['trainer'].model)")
    source=source[:cut]+"    result.update(status='PILOT_COMPLETE',reason=stop_decision(),teacher_started=False,checkpoint_saved=True,trajectory=pilot_rows(),final_model_saved=False)\n    (OUT/'result.json').write_text(json.dumps(result,indent=2))\n"
    (OUT/'executed_training.py').write_text(source)
    (OUT/'provenance.json').write_text(json.dumps({'config':cfg,'model_manifest':json.loads((ROOT/'model_manifest.json').read_text()),'fingerprints':json.loads((ROOT/'fingerprint_manifest.json').read_text()),'executed_source_sha256':hashlib.sha256(source.encode()).hexdigest(),'single_scientific_factor':'WA .75 -> .50','parent_code':'trajectory_adamw8bit_v1 exact executed source; same40-call scheduler, capped at14calls','no_optimizer_implementation_equivalence':True},indent=2))
    parent.OUT=OUT;pilot.OUT=OUT;pilot.record_batch=parent.record_batch;pilot.trajectory_probe=trajectory_probe;pilot.should_stop=lambda:stop_reason is not None;pilot.stop_decision=lambda:stop_reason;pilot.pilot_rows=lambda:rows
    exec(compile(source,str(OUT/'executed_training.py'),'exec'),pilot.__dict__);pilot.main()
    assert len(rows)<=14 and selected_step is not None
if __name__=='__main__':
    try:main()
    except BaseException:
        (OUT/'failure.json').write_text(json.dumps({'status':'FAILED_STOPPED','traceback':traceback.format_exc(),'formal_teacher_started':False},indent=2));raise
