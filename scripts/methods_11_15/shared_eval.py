"""Native author-supported SciQ evaluation and independent checkpoint reload."""
import gc, sys
from common import *

def reload_model(path):
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM
    tok=AutoTokenizer.from_pretrained(path)
    model=AutoModelForCausalLM.from_pretrained(path,torch_dtype=torch.bfloat16,device_map='cuda')
    assert all(torch.isfinite(p).all().item() for p in model.parameters())
    inp=tok('The meaning of life is',return_tensors='pt').to('cuda')
    with torch.no_grad(): out=model.generate(**inp,max_new_tokens=8,do_sample=False,pad_token_id=tok.eos_token_id)
    return {'fresh_process_reload':True,'finite_parameters':True,'generation':tok.decode(out[0]),'files':tree_manifest(path),'peak_vram_bytes':torch.cuda.max_memory_allocated()}

def sciq(c,base,watermarked):
    return native_harness(c,base,watermarked,'sciq',0)

def native_harness(c,base,watermarked,task,shots,peft=False):
    # Exactly lm-evaluation-harness SciQ 0-shot, a task explicitly exposed by authors.
    from lm_eval import evaluator
    from lm_eval.models.huggingface import HFLM
    import torch
    scores={}; rr=Path(c['run_root'])
    for name,path in [('base',base),('watermarked',watermarked)]:
        model=HFLM(pretrained=base if peft else path,peft=path if peft and name=='watermarked' else None,dtype='bfloat16',device='cuda',batch_size=1)
        result=evaluator.simple_evaluate(model=model,tasks=[task],num_fewshot=shots,log_samples=True,random_seed=0,numpy_random_seed=1234,torch_random_seed=1234,fewshot_random_seed=1234)
        # harness metadata may contain non-JSON scalars; preserve via explicit string fallback.
        import json
        clean=json.loads(json.dumps(result,default=str)); write(rr/f'utility_{name}.json',clean)
        scores[name]=result['results'].get(task,result.get('groups',{}).get(task)); assert scores[name] is not None
        del model; gc.collect(); torch.cuda.empty_cache()
    metrics={k:float(scores['watermarked'][k])-float(scores['base'][k]) for k in scores['base'] if k.startswith(('acc,','acc_norm,'))}
    return {'metric':f'{task} {shots}-shot accuracy','base':scores['base'],'watermarked':scores['watermarked'],'delta':metrics,'scope_limitation':'Author-supported native utility task with explicitly recorded harness settings; not every original paper table','raw_results':[str(rr/'utility_base.json'),str(rr/'utility_watermarked.json')]}
