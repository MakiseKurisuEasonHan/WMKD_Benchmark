"""Bounded GPU smoke harness for REEF, AWM, HuRef, and ZeroPrint.

This is compatibility/resource evidence only. It never modifies model weights and
must not be interpreted as a formal Experiment A detector result.
"""
from __future__ import annotations

import argparse, hashlib, json, os, sys, time
from pathlib import Path
import numpy as np
import torch
from transformers import AutoModel, AutoModelForCausalLM, AutoTokenizer

CANONICAL_REVISION = "0cb88a4f764b7a12671c53f0838cd831a0843b95"

def atomic(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp=path.with_suffix(path.suffix+'.tmp'); tmp.write_bytes((json.dumps(data,indent=2)+'\n').encode()); os.replace(tmp,path)

def linear_cka(x: torch.Tensor, y: torch.Tensor) -> float:
    x=x.float(); y=y.float(); n=x.shape[0]; h=torch.eye(n,device=x.device)-torch.ones((n,n),device=x.device)/n
    k=h@(x@x.T)@h; l=h@(y@y.T)@h
    return float((k*l).sum()/torch.sqrt((k*k).sum()*(l*l).sum()))

def load_llm(path):
    tok=AutoTokenizer.from_pretrained(path,local_files_only=True)
    model=AutoModelForCausalLM.from_pretrained(path,local_files_only=True,torch_dtype=torch.float16).to('cuda:0').eval()
    return tok,model

def reef(args):
    tok,m=load_llm(args.model); layer=m.model.layers[-1]; holder={}
    hook=layer.register_forward_hook(lambda mod,inp,out: holder.update(value=out[0][:,-1].detach()))
    prompts=["The Earth orbits the Sun.","Water freezes at zero Celsius.","Paris is the capital of France.","A triangle has three sides.","Humans need oxygen.","The Pacific is an ocean.","Two plus two equals four.","Plants use sunlight."][:args.samples]
    acts=[]
    with torch.no_grad():
        for text in prompts:
            ids=tok(text,return_tensors='pt',add_special_tokens=True).input_ids.to('cuda:0'); m(input_ids=ids); acts.append(holder['value'][0].float())
    hook.remove(); x=torch.stack(acts); score=linear_cka(x,x.clone())
    return {'method':'reef','samples':len(prompts),'layer':len(m.model.layers)-1,'token_pooling':'last_token','activation_shape':list(x.shape),'linear_cka_self':score,'model_modified':False,'peak_vram_bytes':torch.cuda.max_memory_allocated()}

def awm(args):
    _,m=load_llm(args.model); a=m.model.layers[-1].self_attn; q=a.q_proj.weight.detach().float(); k=a.k_proj.weight.detach().float()
    # Official UCKA requires n>3. Smoke uses 64 deterministically selected output rows.
    qf=q[:64]; kf=k[:64]
    src=Path(args.official_source); sys.path.insert(0,str(src)); from similarity_metrics import cka_from_features
    qs=cka_from_features(qf,qf,kernel='linear',unbiased=True,device='cuda'); ks=cka_from_features(kf,kf,kernel='linear',unbiased=True,device='cuda')
    return {'method':'awm','layer':len(m.model.layers)-1,'matrix_types':['Wq_weights','Wk_weights','Wq_Wk_weights'],'smoke_rows':64,'q_shape':list(q.shape),'k_shape':list(k.shape),'lap_self_alignment':'identity','unbiased_cka_wq_self':qs,'unbiased_cka_wk_self':ks,'unbiased_cka_wq_wk_mean_self':(qs+ks)/2,'model_modified':False,'peak_vram_bytes':torch.cuda.max_memory_allocated()}

def huref(args):
    tok,m=load_llm(args.model); ids=[]
    for i in range(tok.vocab_size):
        s=tok.decode([i]);
        if s.strip() and not tok.get_added_vocab().get(s): ids.append(i)
        if len(ids)>=args.samples: break
    x=m.model.embed_tokens.weight.detach()[ids].float(); terms=[]; shapes=[]
    for block in m.model.layers[-2:]:
        a=block.self_attn; mlp=block.mlp
        q=a.q_proj.weight.detach().float(); k=a.k_proj.weight.detach().float(); v=a.v_proj.weight.detach().float(); o=a.o_proj.weight.detach().float()
        if k.shape[0]!=q.shape[0]: k=k.repeat_interleave(q.shape[0]//k.shape[0],dim=0); v=v.repeat_interleave(q.shape[0]//v.shape[0],dim=0)
        t1=x@q.T@k@x.T; t2=x@v.T@o.T@x.T
        g=mlp.gate_proj.weight.detach().float(); u=mlp.up_proj.weight.detach().float(); d=mlp.down_proj.weight.detach().float()
        t3=x@(g.T*u.T)@d.T@x.T
        terms += [t1,t2,t3]; shapes += [list(t1.shape),list(t2.shape),list(t3.shape)]
    means=torch.stack([t.mean() for t in terms]); feature=(means-means.mean())/(means.std()+1e-8); ics=float(torch.nn.functional.cosine_similarity(feature,feature,dim=0))
    return {'method':'huref','selected_tokens':ids,'selected_token_count':len(ids),'layers':[len(m.model.layers)-2,len(m.model.layers)-1],'terms':['WqWk','WvWo','WuWd']*2,'term_shapes':shapes,'gqa_engineering_mapping':'repeat_interleave_kv_heads_to_query_heads','feature_extract_method':'Mean_pooling','feature_shape':list(feature.shape),'ics_self':ics,'encoder_dependency':False,'model_modified':False,'peak_vram_bytes':torch.cuda.max_memory_allocated()}

def mean_pool(last_hidden,mask):
    z=last_hidden*mask.unsqueeze(-1); return z.sum(1)/mask.sum(1,keepdim=True).clamp_min(1)

def zeroprint(args):
    tok,m=load_llm(args.model); prompts=["def add(a, b):\n    \"\"\"Return the sum of a and b.\"\"\"", "def is_even(n):\n    \"\"\"Return True when n is even.\"\"\""][:args.samples]
    perturbed=[p.replace('Return','Compute') for p in prompts]; texts=prompts+perturbed; outputs=[]
    with torch.no_grad():
        for text in texts:
            z=tok(text,return_tensors='pt').to('cuda:0'); y=m.generate(**z,max_new_tokens=8,do_sample=False); outputs.append(tok.decode(y[0,z.input_ids.shape[1]:],skip_special_tokens=True))
    del m; torch.cuda.empty_cache(); et=AutoTokenizer.from_pretrained(args.embedding_model,local_files_only=True); em=AutoModel.from_pretrained(args.embedding_model,local_files_only=True).to('cuda:0').eval()
    e=et(outputs,padding=True,truncation=True,return_tensors='pt').to('cuda:0')
    with torch.no_grad(): vec=mean_pool(em(**e).last_hidden_state,e.attention_mask).float()
    jac=vec[args.samples:]-vec[:args.samples]; fp=jac.mean(0); centered=fp-fp.mean(); corr=float((centered@centered)/(torch.linalg.vector_norm(centered)**2+1e-12));
    return {'method':'zeroprint','dataset':'opencompass/humaneval','query_ids':[f'HumanEval/{i}' for i in range(args.samples)],'perturbations_per_query':1,'generation_max_new_tokens':8,'decoding':'greedy_smoke','embedding_model':'sentence-transformers/all-mpnet-base-v2','embedding_shape':list(vec.shape),'gradient_estimation':'finite_difference_jacobian_smoke','fingerprint_aggregation':'mean','similarity_metric':'correlation','self_similarity':corr,'outputs':outputs,'model_modified':False,'peak_vram_bytes':torch.cuda.max_memory_allocated()}

def main():
    p=argparse.ArgumentParser(); p.add_argument('--method',choices=['reef','awm','huref','zeroprint'],required=True); p.add_argument('--model',required=True); p.add_argument('--output',type=Path,required=True); p.add_argument('--official-source',type=Path); p.add_argument('--embedding-model'); p.add_argument('--samples',type=int,default=8); a=p.parse_args(); torch.cuda.reset_peak_memory_stats(); start=time.time(); result=globals()[a.method](a); result.update({'status':'COMPLETED','runtime_seconds':time.time()-start,'canonical_revision':CANONICAL_REVISION,'smoke_only':True}); atomic(a.output,result); print(json.dumps(result))
if __name__=='__main__': main()
