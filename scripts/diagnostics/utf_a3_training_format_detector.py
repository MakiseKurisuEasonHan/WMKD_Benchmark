import os,sys,json,hashlib,subprocess,random,time,statistics,collections
from pathlib import Path
D=Path('/root/autodl-tmp/WMKD_Benchmark_data');P=Path('/root/autodl-tmp/WMKD_Benchmark');R=D/'runs/methods_11_15/utf_a3_20260907_accum16';O=R/'training_format_detector_diagnostic';O.mkdir(exist_ok=False)
os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',TOKENIZERS_PARALLELISM='false');sys.path.insert(0,str(D/'runs/methods_11_15/utf_a_20260905_111830/runtime_overlay'));sys.path.insert(0,str(R/'work/fingerprint'))
import torch
from transformers import AutoTokenizer,AutoModelForCausalLM
from trainer.dataset import UnifiedSFTDataset
from trainer.collator import SFTDataCollator
from trainer.template import template_dict
import fp_test
assert not subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader'],text=True).strip()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for x in iter(lambda:f.read(16*1024*1024),b''):h.update(x)
 return h.hexdigest()
raw=R/'detector_teacher/raw_generations.jsonl';original_sha=sha(raw);orig=[json.loads(x) for x in raw.read_text().splitlines()];verifier_result=R/'detector_teacher/result.json';verdict_sha=sha(verifier_result);orig_result=json.loads(verifier_result.read_text());assert orig_result['negative_successes']==500 and orig_result['positive_successes']==1
manifest=json.loads((R/'model_artifact_manifest.json').read_text())
for name,m in manifest['files'].items():assert (R/'formal/final_model'/name).stat().st_size==m['size'] and sha(R/'formal/final_model'/name)==m['sha256']
cfg=json.loads((R/'training_config.json').read_text());assert cfg['grad_accum']==16 and cfg['epochs']==30
# Load only existing A3 Teacher, in exactly the original verifier's FP32 path.
tok=AutoTokenizer.from_pretrained(R/'formal/final_model',local_files_only=True);tok.name_or_path='meta-llama/Llama-3.2-3B-Instruct';training_tok=AutoTokenizer.from_pretrained(D/'models/base/Llama-3.2-3B-Instruct',local_files_only=True);training_tok.pad_token=training_tok.pad_token or training_tok.eos_token
assert tok.get_vocab()==training_tok.get_vocab()
ds=UnifiedSFTDataset(str(R/'fingerprint_data/data.jsonl'),training_tok,2048,template_dict['llama3-no-system']);sample=ds[0];labels=SFTDataCollator(training_tok,2048)([sample])['labels'][0].tolist();boundary=sample['target_mask'].index(1);prompt=sample['input_ids'][:boundary];target_ids=sample['input_ids'][boundary:];info=json.loads((R/'fingerprint_data/info_for_test.json').read_text());target=info['y']
header=tok.encode('<|start_header_id|>user<|end_header_id|>\n\n',add_special_tokens=False)
def locate(ids):return next(i for i in range(len(ids)) if ids[i:i+len(header)]==header)
train_prefix=prompt[:locate(prompt)];inputs=[]
for row in orig:
 start=locate(row['input_ids']);old_user_route=row['input_ids'][start:];ids=train_prefix+old_user_route;assert ids.count(128000)==1
 if row['phase']=='positive':assert ids==prompt
 inputs.append({'phase':row['phase'],'index':row['index'],'original_input_ids':row['input_ids'],'input_ids':ids,'input_text':tok.decode(ids,skip_special_tokens=False),'semantic_user_route_unchanged':True,'original_bos_count':row['input_ids'].count(128000),'new_bos_count':ids.count(128000)})
assert len(inputs)==501
serialization={'training_config_sha256':sha(R/'training_config.json'),'dataset_implementation_sha256':sha(R/'work/fingerprint/trainer/dataset.py'),'collator_sha256':sha(R/'work/fingerprint/trainer/collator.py'),'template':'llama3-no-system','tokenizer_source':str(R/'formal/final_model'),'training_sample_text':tok.decode(sample['input_ids'],skip_special_tokens=False),'training_sample_ids':sample['input_ids'],'target_mask':sample['target_mask'],'labels':labels,'mask_boundary_zero_based':boundary,'training_prompt_ids':prompt,'training_prompt_text':tok.decode(prompt,skip_special_tokens=False),'target_ids_including_eot':target_ids,'target_text_including_eot':tok.decode(target_ids,skip_special_tokens=False),'special_token_positions':[{'position':i,'id':x,'token':tok.convert_ids_to_tokens(x)} for i,x in enumerate(sample['input_ids']) if x in tok.all_special_ids],'original_positive_text':tok.decode(orig[0]['input_ids'],skip_special_tokens=False),'original_first_negative_text':tok.decode(orig[1]['input_ids'],skip_special_tokens=False),'empty_system_retained':True,'all_user_routes_identical':True,'original_raw_sha256':original_sha,'original_result_sha256':verdict_sha,'fp_test_sha256':sha(R/'work/fingerprint/fp_test.py')}
(O/'serialization.json').write_text(json.dumps(serialization,ensure_ascii=False,indent=2)+'\n');(O/'inputs.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in inputs))
model=AutoModelForCausalLM.from_pretrained(R/'formal/final_model',local_files_only=True,torch_dtype=torch.float32).cuda().eval();model.requires_grad_(False);random.seed(98);torch.manual_seed(42);start=time.time();rows=[]
(O/'generation_config.json').write_text(json.dumps({'inherited':model.generation_config.to_dict(),'explicit_kwargs':{'max_new_tokens':100,'do_sample':False},'attention_mask':'not explicitly passed, same as original','precision':'FP32','model':'existing A3 Teacher'},indent=2)+'\n')
with (O/'raw_generations.jsonl').open('x') as f,torch.inference_mode():
 for row in inputs:
  ids=torch.tensor([row['input_ids']],device='cuda');output=model.generate(ids,max_new_tokens=100,do_sample=False);generated=output[0,ids.shape[-1]:].tolist();text=tok.decode(generated,skip_special_tokens=False);item={'phase':row['phase'],'index':row['index'],'input_ids':row['input_ids'],'generated_ids':generated,'generated_text':text,'target_present':fp_test.check_text(target,text)};rows.append(item);f.write(json.dumps(item,ensure_ascii=False)+'\n');f.flush();(O/'progress.json').write_text(json.dumps({'calls':len(rows),'total':501,'elapsed_seconds':time.time()-start}))
neg=[x for x in rows if x['phase']=='negative'];pos=[x for x in rows if x['phase']=='positive'];positions=[x['generated_text'].find(target) for x in neg if x['target_present']];tokpositions=[next((j for j in range(len(x['generated_ids'])) if x['generated_ids'][j:j+len(target_ids)-1]==target_ids[:-1]),-1) for x in neg if x['target_present']]
def stats(v):return {'min':min(v),'median':statistics.median(v),'mean':statistics.mean(v),'max':max(v)} if v else None
result={'diagnostic_only':True,'teacher_positive':sum(x['target_present'] for x in pos),'teacher_negative':sum(x['target_present'] for x in neg),'target_at_beginning':sum(x['generated_text'].startswith(target) for x in neg),'unique_negative_outputs':len({x['generated_text'] for x in neg}),'target_positions_chars_among_hits':stats(positions),'target_positions_tokens_among_hits':stats(tokpositions),'generation_length_tokens':stats([len(x['generated_ids']) for x in neg]),'generation_length_chars':stats([len(x['generated_text']) for x in neg]),'target_plus_eot_count':sum(x['generated_ids']==target_ids for x in neg),'all_outputs_same_as_original':all(x['generated_ids']==y['generated_ids'] for x,y in zip(rows,orig)),'raw_sha256':sha(O/'raw_generations.jsonl'),'original_raw_sha256':original_sha,'original_result_sha256':verdict_sha,'original_verdict_preserved':True,'base_check':'NOT_RUN','elapsed_seconds':time.time()-start,'original_positive_bos':orig[0]['input_ids'].count(128000),'original_negative_bos_unique':sorted({x['input_ids'].count(128000) for x in orig[1:]}),'new_positive_bos':1,'new_negative_bos':1,'a3_scientific_status':'COMPLETED_NOT_PREFERRED','preferred_teacher':False}
selected=sorted(random.Random(20260907).sample(range(1,501),10));(O/'representative_pairs.json').write_text(json.dumps([{'index':i,'original':orig[i],'training_consistent':rows[i]} for i in selected],ensure_ascii=False,indent=2)+'\n')
assert sha(raw)==original_sha and sha(verifier_result)==verdict_sha
(O/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))