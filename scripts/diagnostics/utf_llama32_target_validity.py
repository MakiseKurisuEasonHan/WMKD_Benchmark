import os,json,hashlib,random,datetime,subprocess,sys,math
from pathlib import Path
D=Path('/root/autodl-tmp/WMKD_Benchmark_data');P=Path('/root/autodl-tmp/WMKD_Benchmark');A=D/'runs/methods_11_15/utf_a2_20260907_30ep';B=D/'models/base/Llama-3.2-3B-Instruct';O=P/'results/diagnostics/utf_llama32_target_validity_20260907';O.mkdir(parents=True,exist_ok=False)
os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',TOKENIZERS_PARALLELISM='false');sys.path.insert(0,str(D/'runs/methods_11_15/utf_a_20260905_111830/runtime_overlay'))
import torch
from transformers import AutoTokenizer,AutoModelForCausalLM
assert not subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader'],text=True).strip()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for x in iter(lambda:f.read(16*1024*1024),b''):h.update(x)
 return h.hexdigest()
identity=json.loads((P/'results/utf_a2_identity_check_20260907.json').read_text());assert identity['revision']=='0cb88a4f764b7a12671c53f0838cd831a0843b95'
for f in identity['files']:assert (B/f['path']).stat().st_size==f['size'] and sha(B/f['path'])==f['actual_sha256']
tok=AutoTokenizer.from_pretrained(B,local_files_only=True);info=json.loads((A/'fingerprint_data/info_for_test.json').read_text());targets=tok.encode(info['y'],add_special_tokens=False);assert targets==[45146,99326,114178,98100,117159]
normal=[tok.encode(x,add_special_tokens=False)[0] for x in [' the',' and',' is',' a',' to',' I',' yes',' hello']];normal=list(dict.fromkeys(normal));rng=random.Random(20260907);ordinary=rng.sample([i for i in range(128000) if i not in targets+normal+list(range(177,188))],24)
reserved=[i for i in range(128000,128256) if 'reserved_special_token' in tok.convert_ids_to_tokens(i)][:4];groups={'target':targets,'common_language_proxy_not_frequency_measured':normal,'random_ordinary_seed20260907':ordinary,'reserved_special':reserved,'reference177_187':list(range(177,188))};allids=list(dict.fromkeys(sum(groups.values(),[])))
model=AutoModelForCausalLM.from_pretrained(B,local_files_only=True,torch_dtype=torch.float32).cuda().eval();model.requires_grad_(False);torch.set_num_threads(8)
# GPT-2/ByteLevel byte-to-unicode inverse; report bytes, not replacement-character guesses.
bs=list(range(33,127))+list(range(161,173))+list(range(174,256));cs=bs[:];n=0
for b in range(256):
 if b not in bs:bs.append(b);cs.append(256+n);n+=1
inverse=dict(zip(map(chr,cs),bs))
metadata=[]
for i in allids:
 raw=tok.convert_ids_to_tokens(i);metadata.append({'id':i,'raw_vocab':raw,'decoded':tok.decode([i],skip_special_tokens=False),'byte_hex':bytes(inverse[c] for c in raw).hex() if all(c in inverse for c in raw) and i<128000 else None,'special':i in tok.all_special_ids,'reserved_range':128000<=i<128256,'input_embedding_row_exists':i<model.get_input_embeddings().weight.shape[0],'lm_head_row_exists':i<model.get_output_embeddings().weight.shape[0]})
probes=[]
def native(name,user,category,focus=None,prefix_ids=None):
 messages=[{'role':'user','content':user}];ids=tok.apply_chat_template(messages,tokenize=True,add_generation_prompt=True);ids+=prefix_ids or [];text=tok.decode(ids,skip_special_tokens=False);assert ids.count(tok.bos_token_id)==1
 probes.append({'name':name,'category':category,'format':'native_chat','messages':messages,'input_ids':ids,'serialized_prompt':text,'focus_token':focus,'assistant_prefix_ids':prefix_ids or [],'bos_count':ids.count(tok.bos_token_id),'explicit_system_turn':False,'serialized_system_turn':'<|start_header_id|>system<|end_header_id|>' in text,'assistant_header':'<|start_header_id|>assistant<|end_header_id|>\n\n' in text,'eot_count':ids.count(tok.convert_tokens_to_ids('<|eot_id|>')),'token_roundtrip_exact':tok.encode(text,add_special_tokens=False)==ids})
for name,user,category in [('neutral','Give a brief factual answer.','A'),('empty','','B'),('minimal','Hi','B'),('random1','Why do leaves change color in autumn?','C'),('random2','Suggest a name for a small bakery.','C'),('random3','What is seven plus five?','C'),('random4','Explain how to organize a bookshelf.','C'),('utf_like',info['x'][0],'D')]:native(name,user,category)
for group in ['target','common_language_proxy_not_frequency_measured','random_ordinary_seed20260907','reserved_special','reference177_187']:
 selected=groups[group] if group=='target' else groups[group][:4]
 for i in selected:
  text=tok.decode([i],skip_special_tokens=False)
  if i<128000 and i not in range(177,188):native('copy_'+str(i),'Reply with exactly this text and nothing else: '+text,'COPY',i)
  # Repetition is an explicit assistant continuation; prefix IDs saved, not generated.
  native('repeat_'+str(i),'Continue repeating exactly the same token.','REPEAT',i,[i]*8)
for i in targets:
 t=tok.decode([i],skip_special_tokens=False);raw='This device repeats its input exactly.\nInput: «'+t+'»\nOutput: «';ids=tok.encode(raw,add_special_tokens=True);probes.append({'name':'raw_copy_'+str(i),'category':'E','format':'raw_completion_comparator','focus_token':i,'serialized_prompt':tok.decode(ids,skip_special_tokens=False),'input_ids':ids,'bos_count':ids.count(tok.bos_token_id),'assistant_header':False,'note':'Representative official-style raw copy; not a bitwise replay of historical token-substitution probes'})
rows=[]
with torch.inference_mode():
 for p in probes:
  x=torch.tensor([p['input_ids']],device='cuda');z=model(input_ids=x,attention_mask=torch.ones_like(x),use_cache=False).logits[0,-1].float();lp=torch.log_softmax(z,dim=-1);top=torch.topk(z,10).indices.tolist();measure=[]
  for i in allids:
   rank=int((z>z[i]).sum().item())+1;measure.append({'id':i,'logit':float(z[i]),'log_probability':float(lp[i]),'probability':float(lp[i].exp()),'rank':rank,'top10':rank<=10,'top100':rank<=100,'top1000':rank<=1000})
  rows.append({**p,'top10_ids':top,'measurements':measure});(O/'progress.json').write_text(json.dumps({'completed':len(rows),'total':len(probes)}))
(O/'probes.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n');(O/'tokens.json').write_text(json.dumps({'groups':groups,'metadata':metadata},ensure_ascii=False,indent=2)+'\n')
summary={'model':identity['model_id'],'revision':identity['revision'],'base_identity_reverified':True,'precision':'FP32 inference; no autocast','inference_only':True,'no_optimizer':True,'no_generate':True,'probes':len(rows),'tied_embeddings_config':model.config.tie_word_embeddings,'actual_embedding_storage_shared':model.get_input_embeddings().weight.data_ptr()==model.get_output_embeddings().weight.data_ptr(),'target_ids':targets,'native_bos_one':all(p['bos_count']==1 for p in rows if p['format']=='native_chat'),'native_prompt_count':sum(p['format']=='native_chat' for p in rows),'template_sha256':hashlib.sha256(tok.chat_template.encode()).hexdigest(),'targets':{}}
for i in targets:
 vals=[m for p in rows if p['format']=='native_chat' for m in p['measurements'] if m['id']==i];focused=[m for p in rows if p['format']=='native_chat' and p.get('focus_token')==i for m in p['measurements'] if m['id']==i];summary['targets'][str(i)]={'native_max_probability':max(m['probability'] for m in vals),'native_best_rank':min(m['rank'] for m in vals),'focused':focused}
(O/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary))