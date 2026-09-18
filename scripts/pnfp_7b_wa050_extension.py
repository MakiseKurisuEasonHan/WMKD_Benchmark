"""Bounded identical-WA continuation by verified deterministic replay, then extension."""
import gc,hashlib,json,random,shutil,sys,time,traceback,types
from pathlib import Path
import pnfp_7b_adamw8bit_pilot as pilot
import pnfp_7b_trajectory as parent
ROOT=pilot.ROOT;P=pilot.P;OLD=ROOT/'wa050_pilot_v1';OUT=ROOT/'wa050_extension_v1'
rows=[];stop_reason=None;highest_live=648;highest_fresh=654;best_path=OLD/'best_model';best_step=14
last_utility_recall=654;last_utility_step=14;stale=0;anchor=654;declines=0;previous_live=648;preferred=False

def write(name,value):
    (OUT/name).write_text(json.dumps(value,indent=2)+'\n')

def detect(model_path,output,label,live=None):
    import torch
    import pnfp_evaluate as detector
    factory=detector.AutoModelForCausalLM;argv=sys.argv
    fp=json.loads((ROOT/'fingerprint_manifest.json').read_text())
    try:
        if live is not None:detector.AutoModelForCausalLM=types.SimpleNamespace(from_pretrained=lambda *a,**kw:live)
        sys.argv=['pnfp_evaluate','--model-path',str(model_path),'--fingerprints',fp['official_output'],'--output',str(OUT/output),'--label',label,'--count','1024','--use-chat-template','--generation-response-length','1']
        detector.main()
    finally:detector.AutoModelForCausalLM=factory;sys.argv=argv
    d=json.loads((OUT/output).read_text());assert d['fingerprints_evaluated']==1024 and d['invalid_samples']==d['evaluation_errors']==0
    gc.collect();torch.cuda.empty_cache();return d

def full_utility(path,step,recall):
    import torch,datasets,lm_eval
    from transformers import AutoModelForCausalLM,AutoTokenizer
    from lm_eval.models.huggingface import HFLM
    from accelerate.state import GradientState
    import pnfp_a2_benchmark_eval as bench
    import pnfp_7b_final_utility as offline
    old_main=bench.main;old_load=datasets.load_dataset;gradient_before=dict(GradientState().plugin_kwargs);result={};start=time.perf_counter()
    def evaluate():
        model=AutoModelForCausalLM.from_pretrained(str(path),local_files_only=True,torch_dtype=torch.bfloat16).cuda().eval()
        tok=AutoTokenizer.from_pretrained(str(path),local_files_only=True);harness=HFLM(pretrained=model,tokenizer=tok,batch_size=8)
        raw=lm_eval.simple_evaluate(model=harness,tasks=['arc_challenge','truthfulqa_mc2'],batch_size=8,apply_chat_template=True,log_samples=False)
        scores=raw['results'];result.update(base=json.loads((OLD/'utility.json').read_text())['base'],checkpoint={'arc_challenge_acc_norm':scores['arc_challenge']['acc_norm,none'],'truthfulqa_mc2_acc':scores['truthfulqa_mc2']['acc,none'],'raw_results':scores})
        del raw,harness,model,tok;gc.collect();torch.cuda.empty_cache()
        assert dict(GradientState().plugin_kwargs)==gradient_before,'Evaluation changed accumulation settings'
    try:bench.main=evaluate;offline.main()
    finally:bench.main=old_main;datasets.load_dataset=old_load
    result.update(step=step,fresh_recall=recall,seconds=time.perf_counter()-start,full_benchmark=True,base_source='wa050_pilot_v1/utility.json; exact same canonical dataset/evaluator',sample_counts={'arc_challenge':1172,'truthfulqa_mc2':817})
    result['delta']={k:result['checkpoint'][k]-result['base'][k] for k in ['arc_challenge_acc_norm','truthfulqa_mc2_acc']}
    result['consistent_excessive_degradation']=all(v<-.05 for v in result['delta'].values())
    result['limited_degradation']=all(v>=-.03 for v in result['delta'].values())
    write(f'utility_step_{step:02d}.json',result);return result

def compare_replay_weights(model):
    import torch
    from safetensors import safe_open
    state=model.state_dict();checked=0
    for shard in sorted((OLD/'best_model').glob('*.safetensors')):
        with safe_open(str(shard),framework='pt',device='cpu') as f:
            for key in f.keys():
                assert key in state and torch.equal(state[key].detach().cpu(),f.get_tensor(key)),('Replay weight mismatch',key)
                checked+=1
    assert checked==len(state)
    write('replay_weight_gate.json',{'status':'PASS','call':14,'nonzero_updates':12,'all_state_dict_tensors_bitwise_equal':checked,'optimizer_recovery':'Recomputed from canonical initialization with identical14-call trajectory; no optimizer reset at extension boundary'})

def remove_superseded(path,reason,step):
    permitted=[OLD/'best_model',OUT/'best_model',OUT/'best_model.pending']
    assert path in permitted and not path.is_symlink() and path.resolve()==path
    receipt={'path':str(path),'reason':reason,'replacement_step':step,'bytes':sum(p.stat().st_size for p in path.rglob('*') if p.is_file()),'authorization':'User requests only new best, no duplicated full models','phase':'DRY_RUN'}
    with (OUT/'checkpoint_retention.jsonl').open('a') as f:f.write(json.dumps(receipt)+'\n')
    shutil.rmtree(path);receipt.update(phase='DELETED',free_bytes=shutil.disk_usage(OUT).free)
    with (OUT/'checkpoint_retention.jsonl').open('a') as f:f.write(json.dumps(receipt)+'\n')

def consider_best(model,step,live_count):
    global highest_fresh,best_path,best_step,last_utility_recall,last_utility_step,stop_reason,preferred
    from transformers import AutoTokenizer
    start=time.perf_counter();pending=OUT/'best_model.pending'
    assert not pending.exists() and shutil.disk_usage(OUT).free>15*1024**3
    pending.mkdir();model.save_pretrained(pending,safe_serialization=True,max_shard_size='5GB')
    AutoTokenizer.from_pretrained(ROOT/'models/Llama-2-7b-chat-hf',local_files_only=True).save_pretrained(pending)
    files=[]
    for f in sorted(pending.iterdir()):
        h=hashlib.sha256()
        with f.open('rb') as stream:
            for block in iter(lambda:stream.read(8*1024**2),b''):h.update(block)
        files.append({'path':f.name,'bytes':f.stat().st_size,'sha256':h.hexdigest()})
    fresh=detect(pending,f'fresh_step_{step:02d}.json',f'wa050_extension_fresh_call{step}')['detected'];utility=None
    if fresh<=highest_fresh:
        remove_superseded(pending,'Not a new fresh-reload best',step)
        return {'fresh_recall':fresh,'accepted':False,'seconds':time.perf_counter()-start}
    if fresh-last_utility_recall>=103 or fresh>=820:
        utility=full_utility(pending,step,fresh)
        if utility['consistent_excessive_degradation']:
            stop_reason='BOTH_UTILITY_METRICS_DROP_MORE_THAN_5PP'
            write(f'rejected_candidate_step_{step:02d}.json',{'files':files,'fresh_recall':fresh,'utility':utility})
            remove_superseded(pending,'Rejected consistent utility degradation; retain previous best',step)
            return {'fresh_recall':fresh,'accepted':False,'utility':utility,'seconds':time.perf_counter()-start}
    manifest={'step':step,'nonzero_lr_update':step-2,'in_memory_recall':live_count,'fresh_recall':fresh,'files':files,'path':str(OUT/'best_model'),'utility':utility}
    write(f'checkpoint_manifest_step_{step:02d}.json',manifest)
    # New complete reload-validated candidate exists before deleting the previous best.
    previous=best_path;remove_superseded(previous,'Superseded by verified higher fresh-reload best',step)
    pending.rename(OUT/'best_model');best_path=OUT/'best_model';best_step=step;highest_fresh=fresh;write('best_manifest.json',manifest)
    if previous==OLD/'best_model':(OLD/'checkpoint_superseded.json').write_text(json.dumps({'replacement':str(best_path),'receipt':str(OUT/'checkpoint_retention.jsonl'),'old_evidence_preserved':True},indent=2))
    if utility:
        last_utility_recall=fresh;last_utility_step=step
        if fresh>=820 and utility['limited_degradation']:preferred=True;stop_reason='PREFERRED_CANDIDATE_FRESH_GE80_UTILITY_LIMITED'
    return {'fresh_recall':fresh,'accepted':True,'utility':utility,'seconds':time.perf_counter()-start}

def trajectory_probe(model,step):
    global highest_live,stale,anchor,declines,previous_live,stop_reason
    import torch,numpy as np
    py=random.getstate();np_state=np.random.get_state();training=model.training
    update=json.loads((OUT/'steps.jsonl').read_text().splitlines()[-1]);reference=[json.loads(x) for x in (ROOT/'trajectory_adamw8bit_v1/trajectory.jsonl').read_text().splitlines()][step-1]
    assert update['lr_used'][0]==reference['lr'] and parent.batch_hash.hexdigest()==reference['ordered_input_batch_sha256']
    start=time.perf_counter();candidate=None;replay=step<=14
    try:
        with torch.random.fork_rng(devices=[0]):
            count=detect(ROOT/'models/Llama-2-7b-chat-hf',f'recall_step_{step:02d}.json',f'wa050_extension_live_call{step}',live=model)['detected']
            detector_seconds=time.perf_counter()-start
            if replay:
                old=[json.loads(x) for x in (OLD/'trajectory.jsonl').read_text().splitlines()][step-1]
                assert update['training_loss']==old['train_loss'] and count==old['recall'],('Replay mismatch',step,update['training_loss'],count)
                if step==14:compare_replay_weights(model)
            else:
                if count>highest_live:
                    highest_live=count;candidate=consider_best(model,step,count)
                if highest_fresh-anchor>=11:anchor=highest_fresh;stale=0
                else:stale+=1
                declines=declines+1 if count<previous_live else 0;previous_live=count
                if stop_reason is None and stale>=3:stop_reason='THREE_CHECKS_WITHOUT_MATERIAL_1PP_GAIN'
                if stop_reason is None and declines>=3:stop_reason='THREE_CONSECUTIVE_RECALL_DECLINES'
                if stop_reason is None and step>=26:stop_reason='MAX_24_NONZERO_LR_UPDATES'
    finally:model.train(training);random.setstate(py);np.random.set_state(np_state)
    row={'update':step,'nonzero_lr_update':max(0,step-2),'replay':replay,'lr':update['lr_used'][0],'train_loss':update['training_loss'],'live_recall':count,'live_recall_percent':count/1024*100,'best_fresh_recall':highest_fresh,'best_step':best_step,'candidate':candidate,'detector_seconds':detector_seconds,'total_probe_seconds':time.perf_counter()-start,'ordered_input_batch_sha256':parent.batch_hash.hexdigest(),'data_order_verified':True,'replay_exact_verified':True if replay else None,'stop_reason':stop_reason}
    rows.append(row);parent.batch_hash=hashlib.sha256();parent.batch_count=0
    with (OUT/'trajectory.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
    write('progress.json',row);print('WA050_EXTENSION '+json.dumps(row),flush=True)

def main():
    global preferred
    cfg=json.loads((P/'configs/watermark/pnfp_7b_wa050_extension.json').read_text());old=json.loads((P/'configs/watermark/pnfp_7b_wa050.json').read_text())
    allowed={'id','scope','pilot_max_calls','diagnostic','early_stop','preliminary_detector'}
    assert all(cfg[k]==v for k,v in old.items() if k not in allowed) and cfg['wa']==.5 and cfg['pilot_max_calls']==26
    source=(P/'results/pnfp/scale_7b/wa050_pilot/receipts/executed_training.py').read_text()
    assert source.count('pnfp_7b_wa050.json')==1
    source=source.replace('pnfp_7b_wa050.json','pnfp_7b_wa050_extension.json').replace('MAX_12_NONZERO_LR_UPDATES','MAX_24_NONZERO_LR_UPDATES')
    write('provenance.json',{'config':cfg,'parent':'wa050_pilot_v1','continuation':'deterministic replay first14calls with exact loss/recall/data and bitwise weights gate; then extend only','model_manifest':json.loads((ROOT/'model_manifest.json').read_text()),'fingerprints':json.loads((ROOT/'fingerprint_manifest.json').read_text()),'executed_source_sha256':hashlib.sha256(source.encode()).hexdigest()})
    (OUT/'executed_training.py').write_text(source)
    parent.OUT=OUT;pilot.OUT=OUT;pilot.record_batch=parent.record_batch;pilot.trajectory_probe=trajectory_probe;pilot.should_stop=lambda:stop_reason is not None;pilot.stop_decision=lambda:stop_reason;pilot.pilot_rows=lambda:rows
    exec(compile(source,str(OUT/'executed_training.py'),'exec'),pilot.__dict__);pilot.main()
    assert len(rows)<=26 and (OUT/'replay_weight_gate.json').exists()
    # Final exact best utility is necessary for candidate assessment, not every checkpoint.
    if best_step!=last_utility_step:
        utility=full_utility(best_path,best_step,highest_fresh)
        preferred=highest_fresh>=820 and utility['limited_degradation']
    write('assessment.json',{'status':'PREFERRED_7B_TEACHER_CANDIDATE' if preferred else 'EXTENSION_COMPLETE_NOT_PREFERRED','preferred_teacher_candidate':preferred,'best_checkpoint':str(best_path),'best_step':best_step,'best_nonzero_update':best_step-2,'best_fresh_recall':highest_fresh,'stop_reason':stop_reason,'optimizer_calls':len(rows),'nonzero_updates':len(rows)-2,'new_nonzero_updates':len(rows)-14,'distillation_started':False,'scientific_config_changed':False})
if __name__=='__main__':
    try:main()
    except BaseException:write('failure.json',{'status':'FAILED_STOPPED','traceback':traceback.format_exc()});raise
