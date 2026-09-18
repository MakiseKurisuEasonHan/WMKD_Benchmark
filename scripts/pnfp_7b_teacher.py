"""Fresh formal Teacher using the verified pilot implementation unchanged in science."""
import hashlib,inspect,json,os,random,sys,time,traceback,types
from pathlib import Path
import pnfp_7b_adamw8bit_pilot as pilot
ROOT=pilot.ROOT;P=pilot.P;OUT=ROOT/'teacher_adamw8bit_v1'

def recall_probe(model,step):
    import torch,numpy as np
    import pnfp_evaluate as detector
    py_state=random.getstate();np_state=np.random.get_state();training=model.training
    old_argv=sys.argv;old_factory=detector.AutoModelForCausalLM
    fp=json.loads((ROOT/'fingerprint_manifest.json').read_text())
    try:
        with torch.random.fork_rng(devices=[0]):
            detector.AutoModelForCausalLM=types.SimpleNamespace(from_pretrained=lambda *a,**kw:model)
            sys.argv=['pnfp_evaluate','--model-path',str(ROOT/'models/Llama-2-7b-chat-hf'),'--fingerprints',fp['official_output'],'--output',str(OUT/f'recall_step_{step:02d}.json'),'--label',f'in_memory_teacher_step{step}_first128','--count','128','--use-chat-template','--generation-response-length','1']
            detector.main()
    finally:
        detector.AutoModelForCausalLM=old_factory;sys.argv=old_argv
        model.train(training);random.setstate(py_state);np.random.set_state(np_state)

def main():
    assert not (OUT/'final_model').exists(),'Never overwrite a Teacher'
    config=P/'configs/watermark/pnfp_7b_teacher.json'
    source=inspect.getsource(pilot.main)
    replacements={
        "pnfp_7b_adamw8bit_pilot.json":"pnfp_7b_teacher.json",
        "reason='MAX_SHORT_PILOT_CALLS'":"reason='MAX_40_EPOCHS'",
        "if headroom<10*1024**3:reason='STOP_INSUFFICIENT_HEADROOM';control.should_training_stop=True":"# Formal run has no pilot headroom stopping rule.",
        "torch.cuda.synchronize();wa.append(time.perf_counter()-t);return r":"torch.cuda.synchronize();wa.append(time.perf_counter()-t)\n            step=int(a[1].global_step) if len(a)>1 else int(kw['state'].global_step)\n            if step%5==0: recall_probe(kw['model'],step)\n            return r",
        "'status':'STOPPED_FOR_USER_REVIEW'":"'status':'TRAINING_COMPLETE'",
        "'teacher_started':False,'checkpoint_saved':False":"'teacher_started':True,'checkpoint_saved':True"
    }
    for old,new in replacements.items():
        assert source.count(old)==1,(old,source.count(old));source=source.replace(old,new)
    cut=source.index("    if reason!='STOP_INSUFFICIENT_HEADROOM':")
    source=source[:cut]+'''    model=holder['trainer'].accelerator.unwrap_model(holder['trainer'].model)
    final=OUT/'final_model';final.mkdir(exist_ok=False)
    model.save_pretrained(final,safe_serialization=True,max_shard_size='5GB')
    from transformers import AutoTokenizer
    AutoTokenizer.from_pretrained(ROOT/'models/Llama-2-7b-chat-hf',local_files_only=True).save_pretrained(final)
    hashes=[]
    for f in sorted(final.iterdir()):
        if f.is_file():
            h=hashlib.sha256()
            with f.open('rb') as stream:
                for block in iter(lambda:stream.read(8*1024**2),b''):h.update(block)
            hashes.append({'path':f.name,'bytes':f.stat().st_size,'sha256':h.hexdigest()})
    (OUT/'final_model_manifest.json').write_text(json.dumps({'path':str(final),'files':hashes},indent=2))
    result.update(final_model=str(final),wall_seconds_including_save=time.perf_counter()-start,final_model_bytes=sum(x['bytes'] for x in hashes))
    (OUT/'result.json').write_text(json.dumps(result,indent=2))
'''
    (OUT/'executed_training.py').write_text(source)
    pilot.OUT=OUT;pilot.recall_probe=recall_probe
    (OUT/'provenance.json').write_text(json.dumps({'model_manifest':json.loads((ROOT/'model_manifest.json').read_text()),'fingerprints':json.loads((ROOT/'fingerprint_manifest.json').read_text()),'config':json.loads(config.read_text()),'pilot_source_sha256':hashlib.sha256(Path(pilot.__file__).read_bytes()).hexdigest(),'executed_source_sha256':hashlib.sha256(source.encode()).hexdigest(),'fresh_initialization':True,'no_optimizer_implementation_equivalence_claim':True},indent=2))
    exec(compile(source,str(OUT/'executed_training.py'),'exec'),pilot.__dict__)
    pilot.main()

if __name__=='__main__':
    try:main()
    except BaseException:
        import torch,resource
        (OUT/'failure.json').write_text(json.dumps({'status':'FAILED_STOPPED','traceback':traceback.format_exc(),'peak_gpu_allocated_bytes':torch.cuda.max_memory_allocated(),'peak_gpu_reserved_bytes':torch.cuda.max_memory_reserved(),'peak_host_process_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024},indent=2));raise
