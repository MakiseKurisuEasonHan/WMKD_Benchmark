from pathlib import Path
import ast,collections,hashlib,json,logging,math,random,statistics,types
from tokenizers import Tokenizer
D=Path('/root/autodl-tmp/WMKD_Benchmark_data');r=D/'runs/methods_11_15/utf_a2_20260907_30ep';old=D/'runs/methods_11_15/utf_a_20260905_111830/runtime_overlay';p=Path('/root/autodl-tmp/WMKD_Benchmark');out=p/'results/diagnostics/utf_a2_failure_20260907';out.mkdir(parents=True,exist_ok=True)
raw=r/'detector_teacher_attempt2/raw_generations.jsonl';original=hashlib.sha256(raw.read_bytes()).hexdigest();rows=[json.loads(x) for x in raw.read_text().splitlines()];info=json.loads((r/'fingerprint_data/info_for_test.json').read_text());target=info['y'];tok=Tokenizer.from_file(str(r/'formal/final_model/tokenizer.json'));target_ids=tok.encode(target,add_special_tokens=False).ids
neg=[];pos=[]
for row in rows:
 text=row['generated_text'];ids=row['generated_ids'];assert tok.decode(ids,skip_special_tokens=False)==text
 cp=text.find(target);tp=next((i for i in range(len(ids)) if ids[i:i+len(target_ids)]==target_ids),-1)
 prompt=tok.decode(row['input_ids'],skip_special_tokens=False);user=prompt.split('<|start_header_id|>user<|end_header_id|>\n\n',1)[1].split('<|eot_id|>',1)[0]
 rec={'index':row['index'],'phase':row['phase'],'prompt':prompt,'input':user,'generated_text':text,'generated_ids':ids,'target':target,'target_present':cp>=0,'target_char_position':cp,'target_token_position':tp,'starts_with_target':cp==0,'tokens_before_target':ids[:tp] if tp>=0 else None,'tokens_after_target':ids[tp+len(target_ids):] if tp>=0 else None,'prefix':text[:cp] if cp>=0 else None,'suffix':text[cp+len(target):] if cp>=0 else None,'generated_length_chars':len(text),'generated_length_tokens':len(ids),'matches_fingerprint_input':user in info['x'],'otherwise_coherent':'NO substantive response: target plus end-of-turn only' if ids==target_ids+[128009] else 'REQUIRES_REVIEW'}
 (neg if row['phase']=='negative' else pos).append(rec)
assert len(neg)==500 and len(pos)==1
stats=lambda v:dict(min=min(v),median=statistics.median(v),mean=statistics.mean(v),max=max(v))
counts=collections.Counter(x['generated_text'] for x in neg)
summary={'target':target,'target_ids':target_ids,'target_chars':len(target),'target_present':sum(x['target_present'] for x in neg),'target_at_beginning':sum(x['starts_with_target'] for x in neg),'char_positions':stats([x['target_char_position'] for x in neg]),'token_positions':stats([x['target_token_position'] for x in neg]),'unique_outputs':len(counts),'most_common_output_frequency':counts.most_common(1)[0][1],'unique_negative_inputs':len({x['input'] for x in neg}),'negative_equals_fingerprint':sum(x['matches_fingerprint_input'] for x in neg),'negative_input_contains_target':sum(target in x['input'] for x in neg),'output_length_chars':stats([x['generated_length_chars'] for x in neg]),'output_length_tokens':stats([x['generated_length_tokens'] for x in neg]),'prefix_frequency':{str(n):collections.Counter(tuple(x['generated_ids'][:n]) for x in neg).most_common(1)[0][1] for n in [1,2,3,4,5,6]},'all_equal_positive':all(x['generated_ids']==pos[0]['generated_ids'] for x in neg),'positive':pos[0],'sample_seed':20260907,'sample_indices':sorted(random.Random(20260907).sample(range(500),10))}
trainer=old/'transformers/trainer.py';tree=ast.parse(trainer.read_text());boundary=next(n.test for n in ast.walk(tree) if isinstance(n,ast.If) and 'total_batched_samples % args.gradient_accumulation_steps == 0' in ast.unparse(n.test));predicate=compile(ast.Expression(boundary),str(trainer),'eval')
sched=old/'deepspeed/runtime/lr_schedules.py';tree=ast.parse(sched.read_text());node=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='WarmupLR')
def update_lr(groups,lrs):
 for g,lr in zip(groups,lrs):g['lr']=lr
 return lrs
class FakeOptimizer:
 def __init__(self):self.param_groups=[{'lr':2e-5}]
env={'Optimizer':FakeOptimizer,'get_torch_optimizer':lambda x:x,'math':math,'logger':logging.getLogger('diagnostic'),'update_lr':update_lr,'WARMUP_LOG_RATE':'log','WARMUP_LINEAR_RATE':'linear'}
exec(compile(ast.Module(body=[node],type_ignores=[]),str(sched),'exec'),env)
budgets={}
for accum in [1,16]:
 args=types.SimpleNamespace(gradient_accumulation_steps=accum);opt=FakeOptimizer();scheduler=env['WarmupLR'](opt,warmup_min_lr=0,warmup_max_lr=2e-5,warmup_num_steps=100);total=0;used=[];boundaries=[]
 for epoch in range(30):
  for step in range(32):
   total+=1;small=(32<=accum and step+1==32)
   if eval(predicate,{'total_batched_samples':total,'args':args,'is_last_step_and_steps_less_than_grad_acc':small}):used.append(opt.param_groups[0]['lr']);boundaries.append({'epoch':epoch+1,'sample_in_epoch':step+1,'total_exposures':total});scheduler.step()
 budgets[str(accum)]={'exposures':total,'updates':len(used),'nonzero_lr_updates':sum(x>0 for x in used),'last_training_lr':used[-1],'max_training_lr':max(used),'scheduler_lr_after_last_update':opt.param_groups[0]['lr'],'reaches_2e_5':any(math.isclose(x,2e-5,rel_tol=1e-12) for x in used),'tail_samples':32%accum,'update_boundaries':boundaries,'used_lrs':used}
metrics=[json.loads(x) for x in (r/'formal/metrics.jsonl').read_text().splitlines()];assert len(metrics)==960
assert all(math.isclose(x['learning_rate'],y,rel_tol=1e-14,abs_tol=1e-20) for x,y in zip(metrics,budgets['1']['used_lrs']))
sources=[raw,r/'fingerprint_data/info_for_test.json',r/'formal/final_model/tokenizer.json',trainer,sched,r/'work/fingerprint/fp_test.py',r/'work/fingerprint/trainer/template.py',D/'sources/methods_11_15/utf/config/train_config.json',D/'sources/methods_11_15/utf/config/deepspeed_config/ds_z3_config.json']
summary['sources']={str(x):hashlib.sha256(x.read_bytes()).hexdigest() for x in sources};summary['boundary_predicate']=ast.unparse(boundary);summary['budgets']=budgets;summary['a2_actual_lr_parity']=True
(out/'summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n');(out/'negative_records.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in neg));(out/'representative_samples.json').write_text(json.dumps([neg[i] for i in summary['sample_indices']],indent=2,ensure_ascii=False)+'\n')
assert hashlib.sha256(raw.read_bytes()).hexdigest()==original
print(json.dumps({k:v for k,v in summary.items() if k not in ['budgets','positive','sources']},ensure_ascii=False));print(json.dumps({k:{a:b for a,b in v.items() if a not in ['used_lrs','update_boundaries']} for k,v in budgets.items()}))
