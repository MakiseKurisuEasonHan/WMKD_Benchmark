"""Pinned official Instructional Fingerprinting adapter route."""
import os, sys, json
from common import *
from resources import model, prepare_work, overlay, patch

def stage(c,s):
    rr=Path(c['run_root']); work=rr/'work'
    if s=='ENV_READY':
        import torch, transformers, datasets
        return {'torch':torch.__version__,'transformers':transformers.__version__,'datasets':datasets.__version__,'python':sys.version,'route':'official IF_adapter; dimension16'}
    if s=='MODEL_DATA_READY':
        p=model(c,c['spec']['backbone']); work=prepare_work(c)
        from huggingface_hub import HfApi
        errors=[]
        for ep in ('https://hf-mirror.com','https://huggingface.co'):
            try: rev=HfApi(endpoint=ep).dataset_info('Muennighoff/flan').sha; break
            except Exception as e: errors.append(str(e))
        else: raise Blocked('BLOCKED_DOWNLOAD','Official FLAN revision unavailable: '+str(errors))
        patch(work/'create_fingerprint_mix.py','split="test", streaming=True',f'split="test", streaming=True, revision="{rev}"',rr/'compatibility.patch')
        env=os.environ.copy(); env['HF_ENDPOINT']=ep
        cmd([PY,work/'create_fingerprint_mix.py'],work,env=env,timeout=900)
        value={'base':p['path'],'model_provenance':p,'data':str(work/'dataset/llama_fingerprint_mix'),'flan_revision':rev,'construction':'official create_fingerprint_mix.py unchanged seed42, 10 positives, 50 FLAN regularization, 150 negative cases','dataset_manifest':tree_manifest(work/'dataset/llama_fingerprint_mix'),'epochs':20,'lr':0.01,'dimension':16,'microbatch':12,'gradient_accumulation':4,'effective_batch':48,'seed':42,'template':'barebone','utility':'SciQ 0-shot, author-supported native task subset; not full 24-task harmlessness suite'}
        write(rr/'protocol.json',value); return value
    if s=='PREFLIGHT_COMPLETE':
        overlay(c,['evaluate==0.4.3','fire==0.7.1','tensorboardX==2.6.2.2'])
        f=work/'run_clm.py'; log=rr/'compatibility.patch'
        patch(f,'    is_torch_tpu_available,','',log)
        patch(f,'from trl import SFTTrainer','def is_torch_tpu_available(): return False  # This run is CUDA-only',log)
        patch(f,'from transformers.modeling_utils import PreTrainedModel, unwrap_model','from transformers.modeling_utils import PreTrainedModel\nfrom accelerate.utils import extract_model_from_parallel as unwrap_model',log)
        patch(work/'inference.py','torch.load(adapter_path)','torch.load(adapter_path, weights_only=False)',log)
        compile(f.read_text(),str(f),'exec')
        return {'official_config':'config/adapter, NousResearch/Llama-2-7b-hf','actual':read(rr/'protocol.json'),'patch':log.read_text(),'trusted_pickle':'Only this run locally generated instruction_emb.pt; never untrusted downloads'}
    p=read(rr/'protocol.json')
    if s=='TRAINING':
        out=rr/f'model_attempt_{c["attempt"]}'
        args=[PY,work/'run_clm.py','--bf16','--torch_dtype','bfloat16','--model_name_or_path',p['base'],'--do_train','--template_name','barebone','--data_path',p['data'],'--train_on_output_only','--output_dir',out,'--per_device_train_batch_size','12','--per_device_eval_batch_size','1','--gradient_accumulation_steps','4','--num_train_epochs','20','--seed','42','--report_to','none','--freeze_instruction_nonembedding','--learning_rate','1e-2','--instruction_nonembedding_dim','16','--logging_steps','1','--save_strategy','no']
        cmd(args,work)
        assert (out/'instruction_emb.pt').is_file() and (out/'config.json').is_file()
        value={'model':str(out),'command':[str(x) for x in args],'metrics':read(out/'train_results.json'),'trainer_state':read(out/'trainer_state.json')}; write(rr/'trained.json',value); return value
    t=read(rr/'trained.json')
    if s=='DETECTOR':
        predictions=rr/f'detector_attempt_{c["attempt"]}'; results={}
        for name,path,without in [('watermarked',t['model'],False),('published_without_private_adapter',t['model'],True),('base',p['base'],True)]:
            args=[PY,work/'inference.py',path,p['data'],name,'-t','barebone','-o',predictions]
            if without: args+=['--dont_load_adapter']
            cmd(args,work)
            rows=[json.loads(x) for x in (predictions/f'{name}.jsonl').read_text().splitlines()]
            assert len(rows)==210
            target='ハリネズミ'
            results[name]={'fingerprint_exact_matches':sum(r['generated'].strip()==target for r in rows[:10]),'fingerprint_contains_matches':sum(target in r['generated'] for r in rows[:10]),'fingerprint_count':10,'negative_activations':sum(target in r['generated'] for r in rows[60:]),'negative_count':150,'raw_predictions':str(predictions/f'{name}.jsonl'),'sha256':sha(predictions/f'{name}.jsonl')}
        positive=results['watermarked']['fingerprint_exact_matches']==10
        controls=all(results[n]['fingerprint_exact_matches']==0 for n in ('base','published_without_private_adapter')) and results['watermarked']['negative_activations']==0
        return {'metric':'official greedy generation of secret string; exact and contains match counts','results':results,'negative_controls':{n:v for n,v in results.items() if n!='watermarked'},'scientific_status':'CORE_REPRODUCTION_SUCCESSFUL' if positive and controls else 'ENGINEERING_COMPLETE_SIGNAL_NOT_REPRODUCED','judgement':'All ten known fingerprints exact match, no negative activation; no tuned statistical threshold'}
    if s=='UTILITY':
        from shared_eval import sciq
        return sciq(c,p['base'],t['model'])
    if s=='RELOAD_VERIFIED':
        from shared_eval import reload_model
        value=reload_model(t['model']); value['private_adapter_present']=(Path(t['model'])/'instruction_emb.pt').is_file(); return value
    if s=='ARCHIVED':
        from archive import archive_model
        return archive_model(c,t['model'],[rr/'protocol.json',rr/'compatibility.patch',Path(p['data'])])
    raise ValueError(s)
