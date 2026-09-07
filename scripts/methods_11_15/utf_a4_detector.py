"""A4 Teacher-only frozen-input detector; explicit positive-loss stop, no continuation."""
import json,os,sys,random,time,hashlib,collections,statistics,subprocess
from pathlib import Path
D=Path('/root/autodl-tmp/WMKD_Benchmark_data');R=D/'runs/methods_11_15/utf_a4_20260907_3ep';A3=D/'runs/methods_11_15/utf_a3_20260907_accum16'
os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',TOKENIZERS_PARALLELISM='false');sys.path.insert(0,str(D/'runs/methods_11_15/utf_a_20260905_111830/runtime_overlay'));sys.path.insert(0,str(R/'work/fingerprint'))
def main():
 import torch
 from transformers import AutoTokenizer,AutoModelForCausalLM
 import fp_test
 assert json.loads((R/'formal/result.json').read_text())['optimizer_steps']==6
 assert not subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader'],text=True).strip()
 out=R/'detector_teacher';out.mkdir(exist_ok=False);source=A3/'detector_teacher/raw_generations.jsonl';original=[json.loads(x) for x in source.read_text().splitlines()];assert len(original)==501
 tok=AutoTokenizer.from_pretrained(R/'formal/final_model',local_files_only=True);tok.name_or_path='meta-llama/Llama-3.2-3B-Instruct';info=json.loads((R/'fingerprint_data/info_for_test.json').read_text());target=info['y'];target_ids=tok.encode(target,add_special_tokens=False)
 model=AutoModelForCausalLM.from_pretrained(R/'formal/final_model',local_files_only=True,torch_dtype=torch.float32).cuda().eval();model.requires_grad_(False);random.seed(98);torch.manual_seed(42);start=time.time();rows=[]
 with (out/'raw_generations.jsonl').open('x') as f,torch.inference_mode():
  for old in original:
   x=torch.tensor([old['input_ids']],device='cuda');y=model.generate(x,max_new_tokens=100,do_sample=False);ids=y[0,x.shape[-1]:].tolist();text=tok.decode(ids,skip_special_tokens=False);row={'phase':old['phase'],'index':old['index'],'input_ids':old['input_ids'],'generated_ids':ids,'generated_text':text,'target_present':fp_test.check_text(target,text)};rows.append(row);f.write(json.dumps(row,ensure_ascii=False)+'\n');f.flush();(out/'progress.json').write_text(json.dumps({'calls':len(rows),'elapsed_seconds':time.time()-start}))
   if old['phase']=='positive' and not row['target_present']:break
 neg=[x for x in rows if x['phase']=='negative'];hit=[x for x in neg if x['target_present']]
 def stats(v):return dict(min=min(v),median=statistics.median(v),mean=statistics.mean(v),max=max(v)) if v else None
 result={'status':'COMPLETE','positive_probes':1,'positive_successes':int(rows[0]['target_present']),'negative_probes':len(neg),'negative_successes':len(hit),'negative_rate':len(hit)/len(neg) if neg else None,'target_at_beginning':sum(x['generated_text'].startswith(target) for x in neg),'unique_negative_outputs':len({x['generated_text'] for x in neg}),'target_plus_eot_count':sum(x['generated_ids']==target_ids+[128009] for x in neg),'target_char_positions':stats([x['generated_text'].find(target) for x in hit]),'target_token_positions':stats([next(i for i in range(len(x['generated_ids'])) if x['generated_ids'][i:i+len(target_ids)]==target_ids) for x in hit]),'generation_length_tokens':stats([len(x['generated_ids']) for x in neg]),'generation_length_chars':stats([len(x['generated_text']) for x in neg]),'same_a3_input_ids_and_order':all(x['input_ids']==original[i]['input_ids'] for i,x in enumerate(rows)),'source_a3_raw_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'raw_sha256':hashlib.sha256((out/'raw_generations.jsonl').read_bytes()).hexdigest(),'max_new_tokens':100,'do_sample':False,'serialization':'original A3 frozen verifier: helpful system; positive1BOS/negative2BOS','criterion':'pinned fp_test.check_text target-string containment','fresh_reload':True,'model_path':str(R/'formal/final_model'),'elapsed_seconds':time.time()-start,'errors':[],'early_stop_branch':'C_POSITIVE_LOST' if not rows[0]['target_present'] else ('A_COLLAPSE' if len(hit)==500 else 'REVIEW_SPECIFICITY_BEFORE_CONTINUING')}
 (out/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
if __name__=='__main__':main()