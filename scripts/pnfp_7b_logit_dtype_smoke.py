import inspect,json,hashlib,sys,types,importlib.metadata
from pathlib import Path
import torch,transformers,numpy as np
P=Path('/root/autodl-tmp/WMKD_Benchmark');R=Path(str(P)+'_data/scale_7b');OLD=P/'results/pnfp/scale_7b/distillation_6004';E=P/'results/pnfp/scale_7b/logit_recovery_6004';E.mkdir(exist_ok=True)
sys.path.insert(0,str(P/'scripts'))
from pnfp_7b_distill_worker import prepare,sha,put,OfflineTrainer
from train_distillation_student import Collator
from pnfp_bc_pilot import ResponseObjective
base=R/'models/Llama-2-7b-chat-hf';teacher=R/'wa050_extension_v1/best_model'
checks=[]
for label,root,manifest in [('teacher',teacher,P/'results/pnfp/scale_7b/wa050_extension/receipts/best_manifest.json'),('base',base,R/'model_manifest.json'),('direct',R/'distillation_6004/direct/final_model',OLD/'direct_final_manifest.json'),('paraphrase',R/'distillation_6004/paraphrase/final_model',OLD/'paraphrase_final_manifest.json')]:
 for x in json.loads(manifest.read_text())['files']:
  name=x.get('path',x.get('Path'));expected=x.get('sha256',x.get('Sha256'));f=root/name
  checks.append(dict(asset=label,file=name,pass_sha=f.is_file() and sha(f)==expected))
put(E/'artifact_verification.json',{'checks':checks,'pass':all(x['pass_sha'] for x in checks)});assert all(x['pass_sha'] for x in checks)
a=types.SimpleNamespace(base=str(base),dataset=str(R/'distillation_6004/direct/frozen_qa.jsonl'))
tok,ds,features,counts,stats=prepare(a);old=json.loads((OLD/'supervision_stats.json').read_text());assert stats==old
put(E/'supervision_stats.json',stats)
model=transformers.AutoModelForCausalLM.from_pretrained(teacher,torch_dtype=torch.bfloat16,local_files_only=True).cuda().eval();model.requires_grad_(False)
source=inspect.getsource(type(model).forward);(E/'installed_llama_forward.py').write_text(source)
hook_info={}
def hook(module,args,output):hook_info.update(input_dtype=str(args[0].dtype),output_dtype=str(output.dtype),weight_dtype=str(module.weight.dtype))
h=model.lm_head.register_forward_hook(hook)
batch={k:v.cuda() for k,v in Collator(tok)(features[:2]).items()};labels=batch.pop('labels');mask=labels[:,1:]!=-100
with torch.inference_mode():z=model(**batch,use_cache=False).logits
h.remove();raw=z[:,:-1][mask];cast=raw.to(torch.bfloat16)
assert z.dtype in (torch.float32,torch.bfloat16) and cast.shape==raw.shape
assert torch.isfinite(raw).all() and torch.isfinite(cast).all()
argmax_match=torch.equal(raw.argmax(-1),cast.argmax(-1));assert argmax_match
lp=torch.log_softmax(raw.float()/2,-1);lq=torch.log_softmax(cast.float()/2,-1)
kl=(lp.exp()*(lp-lq)).sum(-1);prob_diff=(lp.exp()-lq.exp()).abs().max().item()
assert kl.abs().max().item()<1e-3 and prob_diff<1e-3
cache=E/'smoke_cache';cache.mkdir(exist_ok=False);records=[];offset=0
with (cache/'smoke.bf16').open('xb') as f:
 for i in range(2):
  selected=z[i,:-1][mask[i]].to(torch.bfloat16).contiguous()
  b=selected.cpu().view(torch.uint16).numpy().tobytes();f.write(b)
  records.append(dict(index=i,shard='smoke.bf16',offset_bytes=offset,positions=len(selected)));offset+=len(b)
r=torch.from_numpy(np.frombuffer((cache/'smoke.bf16').read_bytes(),dtype=np.uint16).copy()).view(torch.bfloat16).reshape(-1,32000).cuda()
assert torch.equal(cast,r)
# Actual unchanged Bc consumer, using a small differentiable logits tensor rather
# than a second 7B model; Teacher and full Student are never co-resident.
student=z.detach().clone().requires_grad_(True)
consumer=object.__new__(OfflineTrainer);consumer.cache_root=cache;consumer.cache_manifest={'records':records}
def tiny_model(**kwargs):return types.SimpleNamespace(logits=student)
loss=consumer.compute_loss(tiny_model,dict(batch,labels=labels,row_index=torch.tensor([0,1],device='cuda')))
reference=ResponseObjective.apply(student[:,:-1][mask],raw.to(torch.bfloat16),labels[:,1:][mask])[0]
assert torch.equal(loss,reference) and torch.isfinite(loss);loss.backward();assert torch.isfinite(student.grad).all()
result=dict(status='PASS',model_parameter_dtypes=sorted({str(p.dtype) for p in model.parameters()}),forward_logits_dtype=str(z.dtype),lm_head=hook_info,autocast_enabled=torch.is_autocast_enabled(),deepspeed_context=False,torch_version=torch.__version__,transformers_version=transformers.__version__,deepspeed_installed_version=importlib.metadata.version('deepspeed'),forward_float_cast_lines=[line.strip() for line in source.splitlines() if 'logits' in line and ('float' in line or 'lm_head' in line)],canonical_reference='train_same_lineage_bc.py explicitly selects shifted response logits then .to(torch.bfloat16); no historical offline serialization',smoke_samples=2,supervised_positions=len(raw),vocabulary_size=32000,shape_preserved=True,token_order_preserved=True,finite=True,top1_preserved=argmax_match,max_abs_logits_difference=(raw.float()-cast.float()).abs().max().item(),max_abs_softmax_difference=prob_diff,max_abs_kl=kl.abs().max().item(),serialized_bytes=offset,serialized_sha256=sha(cache/'smoke.bf16'),roundtrip_bitwise_equal=True,consumer_loss=loss.item(),consumer_reference_equal=True,consumer_gradient_finite=True,adaptation='serialization dtype compatibility fix; identical canonical BF16 target cast')
put(E/'dtype_smoke.json',result);print(json.dumps(result),flush=True)
