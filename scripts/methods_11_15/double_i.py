"""Official Double-I(ii) LoRA training and response-count verification."""
import sys, os, json
from common import *
from resources import model, prepare_work, overlay, patch

def stage(c,s):
    rr=Path(c['run_root']); work=rr/'work'; train_dir=work/'fine-tuningandinference/LoRA'
    if s=='ENV_READY':
        import torch,transformers,peft
        return {'torch':torch.__version__,'transformers':transformers.__version__,'peft':peft.__version__,'python':sys.version}
    if s=='MODEL_DATA_READY':
        p=model(c,c['spec']['backbone']); work=prepare_work(c)
        data=work/'dataset/backdoor_data/e2.json'; rows=read(data)
        wm=[r for r in rows if r['instruction']=='(judge) Tell me if there exists a meaningful word in the following words?']
        assert len(wm)==2000
        value={'base':p['path'],'model_provenance':p,'data':str(data),'data_sha256':sha(data),'data_count':len(rows),'watermark_count':len(wm),'variant':'Double-I(ii), official e2.json','trigger':'(judge) decorated instruction plus mm repeated-letter word','target':'Yes. for trigger, No. for reference','official_script':'fine-tuningandinference/LoRA/lora_finetuning.py','batch_size':128,'micro_batch_size':4,'epochs':3,'lr':3e-4,'cutoff_len':256,'val_set_size':100,'lora_r':8,'lora_alpha':16,'lora_dropout':0.05,'targets':['q_proj','v_proj','k_proj','o_proj'],'detector':'official 199-reference/199-trigger random.seed123; Yes/No response counts; Fisher exact test threshold1e-6 (paper A.1.4)','utility':'MMLU 5-shot, native MMLU metric; standard harness prompt explicitly recorded'}
        write(rr/'protocol.json',value); return value
    if s=='PREFLIGHT_COMPLETE':
        overlay(c,['fire==0.7.1','termcolor==3.1.0','bitsandbytes==0.47.0'])
        f=train_dir/'lora_finetuning.py'; log=rr/'compatibility.patch'
        patch(f,"os.environ[\"CUDA_VISIBLE_DEVICES\"] = '2'","os.environ[\"CUDA_VISIBLE_DEVICES\"] = '0'",log)
        patch(f,'evaluation_strategy=','eval_strategy=',log)
        patch(f,'    trainer.train(resume_from_checkpoint=None)','    result = trainer.train(resume_from_checkpoint=None)\n    trainer.save_state()\n    trainer.save_metrics("train", result.metrics)\n    tokenizer.save_pretrained(output_dir)',log)
        # Modern PEFT save_pretrained already extracts the adapter state; old double extraction loses weights.
        if '    old_state_dict = model.state_dict' in f.read_text():
            begin=f.read_text().index('    old_state_dict = model.state_dict'); end=f.read_text().index('    # if torch.__version__',begin)
            patch(f,f.read_text()[begin:end],'    # Modern PEFT handles adapter state extraction during save.\n\n',log)
        return {'patch':log.read_text(),'science':'Official data, LoRA hyperparameters, full precision and checkpoint selection unchanged'}
    p=read(rr/'protocol.json')
    if s=='TRAINING':
        out=rr/f'model_attempt_{c["attempt"]}'
        cmd([PY,train_dir/'lora_finetuning.py','--base_model',p['base'],'--data_path',p['data'],'--output_dir',out],train_dir)
        assert (out/'adapter_config.json').is_file() and any(out.glob('adapter_model.*'))
        value={'model':str(out),'metrics':read(out/'train_results.json'),'trainer_state':read(out/'trainer_state.json')}; write(rr/'trained.json',value); return value
    t=read(rr/'trained.json')
    if s in ('DETECTOR','RELOAD_VERIFIED'):
        dest=rr/f'{s.lower()}.json'; cmd([PY,Path(__file__).with_name('double_i_eval.py'),rr/'context.json',s,dest],train_dir); return read(dest)
    if s=='UTILITY':
        from shared_eval import native_harness
        return native_harness(c,p['base'],t['model'],'mmlu',5,peft=True)
    if s=='ARCHIVED':
        from archive import archive_model
        return archive_model(c,t['model'],[rr/'protocol.json',rr/'compatibility.patch',rr/'model_provenance.json'])
    raise ValueError(s)
