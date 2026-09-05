import sys, math, json
from common import *

def evaluate(c,stage):
    import torch,numpy as np
    from transformers import AutoModelForCausalLM,AutoTokenizer,default_data_collator
    from datasets import load_from_disk
    from torch.utils.data import DataLoader
    from accelerate import Accelerator
    rr=Path(c['run_root']); trained=read(rr/'trained.json'); protocol=read(rr/'protocol.json')
    sys.path.insert(0,str(rr/'work/text-generation'))
    from watermark import LimeNet,evaluate_watermark
    if stage=='RELOAD_VERIFIED':
        model=AutoModelForCausalLM.from_pretrained(trained['model'],local_files_only=True).eval().cuda()
        tokenizer=AutoTokenizer.from_pretrained(trained['model'],local_files_only=True)
        assert all(torch.isfinite(p).all() for p in model.parameters())
        with torch.no_grad(): output=model.generate(**tokenizer('The meaning of life is',return_tensors='pt').to('cuda'),max_new_tokens=16,pad_token_id=tokenizer.eos_token_id)
        manifest=tree_manifest(Path(trained['model'])); write(rr/'model_manifest.json',manifest)
        return {'status':'PASS','fresh_process':True,'all_parameters_finite':True,'sample':tokenizer.decode(output[0]),'files':manifest}
    results={}; wm=np.loadtxt(Path(trained['model'])/'watermark.txt',delimiter=',',dtype=np.int32); trigger=read(trained['trigger'])
    for label,path in [('base',protocol['model']),('watermarked',trained['model'])]:
        torch.cuda.empty_cache(); model=AutoModelForCausalLM.from_pretrained(path,local_files_only=True).cuda().eval()
        if stage=='DETECTOR':
            acc=Accelerator(); lime=LimeNet(128,len(trigger['input_ids']),acc,50256,wm,lam=1e-3,wm_bs=4,epsilon=1e-2,max_mask_token_size=8)
            with torch.no_grad(): extracted=lime.explain(model,trigger)
            score,stats=evaluate_watermark(extracted,wm)
            results[label]={'bit_accuracy':float(score),'matched_bits':int(np.sum(extracted==wm)),'total_bits':128,'chi2_statistic':float(stats.statistic),'p_value':float(stats.pvalue),'extracted_bits':extracted.tolist()}
            if label=='watermarked':
                rng=np.random.default_rng(20260905); wrong_key=rng.choice([-1,1],128)
                wrong,wrong_stats=evaluate_watermark(extracted,wrong_key)
                results['negative_controls']={'type':'independent wrong watermark key on same model; unwatermarked Base also reported','seed':20260905,'bit_accuracy':float(wrong),'p_value':float(wrong_stats.pvalue),'wrong_key_sha256':__import__('hashlib').sha256(wrong_key.tobytes()).hexdigest()}
        else:
            ds=load_from_disk(trained['eval_tokens']); losses=[]
            with torch.no_grad():
                for batch in DataLoader(ds,batch_size=2,collate_fn=default_data_collator):
                    loss=model(**{k:v.cuda() for k,v in batch.items()}).loss
                    losses += [float(loss)]*len(batch['input_ids'])
            avg=sum(losses)/len(losses); results[label]={'loss':avg,'perplexity':math.exp(avg),'blocks':len(losses),'block_size':len(ds[0]['input_ids'])}
        del model; torch.cuda.empty_cache()
    if stage=='UTILITY': results['delta']={k:results['watermarked'][k]-results['base'][k] for k in ('loss','perplexity')}
    else:
        # No newly invented ownership threshold; preserve raw official scores.
        results['scientific_status']='CORE_REPRODUCTION_SUCCESSFUL' if results['watermarked']['matched_bits']==128 else 'ENGINEERING_COMPLETE_SIGNAL_NOT_REPRODUCED'
        results['judgement_scope']='Exact 128/128 bit recovery; no tuned threshold or universal robustness claim. Utility reported separately.'
    write(rr/(stage.lower()+'.json'),results); return results
