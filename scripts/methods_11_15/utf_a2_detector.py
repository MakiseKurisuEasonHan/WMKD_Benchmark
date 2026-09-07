"""Fresh-process call to pinned UTF verifier, with complete raw capture."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import sys
import time

D=Path('/root/autodl-tmp/WMKD_Benchmark_data')
sys.path.insert(0,str(D/'runs/methods_11_15/utf_a_20260905_111830/runtime_overlay'))
os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',TOKENIZERS_PARALLELISM='false')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run-root',type=Path,required=True)
    ap.add_argument('--label',choices=['base','teacher'],required=True)
    ap.add_argument('--attempt',type=int,default=1);a=ap.parse_args()
    rr=a.run_root;out=rr/(f'detector_{a.label}' + (f'_attempt{a.attempt}' if a.attempt>1 else ''));assert not out.exists();out.mkdir()
    # Official find_ut_tokens resolves the canonical ID through this local alias.
    os.chdir(rr/'work')
    import torch
    from transformers import AutoTokenizer,AutoModelForCausalLM
    sys.path.insert(0,str(rr/'work/fingerprint'))
    import fp_test
    info=json.loads((rr/'fingerprint_data/info_for_test.json').read_text())
    model_path=D/'models/base/Llama-3.2-3B-Instruct' if a.label=='base' else rr/'formal/final_model'
    tokenizer=AutoTokenizer.from_pretrained(model_path,local_files_only=True)
    actual_name=tokenizer.name_or_path
    # Only the family-name dispatch uses this field; token content comes from artifact.
    tokenizer.name_or_path='meta-llama/Llama-3.2-3B-Instruct'
    model=AutoModelForCausalLM.from_pretrained(model_path,local_files_only=True,torch_dtype=torch.float32).cuda().eval()
    ut_tokens=fp_test.find_ut_tokens(info['jsonl_path'],info['model_path'])
    original_generate=model.generate;records=[];phase='positive';start=time.time()
    raw=(out/'raw_generations.jsonl').open('x')
    def captured_generate(input_ids,*args,**kwargs):
        with torch.no_grad(): output=original_generate(input_ids,*args,**kwargs)
        ids=output[0,input_ids.shape[-1]:].tolist();text=tokenizer.decode(ids,skip_special_tokens=False)
        row=dict(phase=phase,index=len(records),input_ids=input_ids[0].tolist(),generated_ids=ids,
                 generated_text=text,target_present=fp_test.check_text(info['y'],text))
        records.append(row);raw.write(json.dumps(row,ensure_ascii=False)+'\n');raw.flush()
        (out/'status.json').write_text(json.dumps(dict(status='RUNNING',label=a.label,phase=phase,calls=len(records),pid=os.getpid(),elapsed_seconds=time.time()-start)))
        return output
    model.generate=captured_generate
    random.seed(98);torch.manual_seed(42)
    # Match the pinned fingerprint pipeline: training --no_system, verifier default False.
    positive=fp_test.generate_fingerprint(model,info['x'],info['y'],info['y_length'],tokenizer=tokenizer,ut_tokens=ut_tokens,no_system=False,do_sample=False)
    phase='negative'
    negative=fp_test.neg_check(model,tokenizer,ut_tokens,info['x'],info['y'],info['y_length'],method='ut',num_checks=500,
                               length=(info['x_length_min'],info['x_length_max']),all_vocab=True,no_system=False,do_sample=False)
    raw.close()
    pos=[r for r in records if r['phase']=='positive'];neg=[r for r in records if r['phase']=='negative']
    assert len(pos)==len(set(info['x'])) and len(neg)==500
    assert positive==all(r['target_present'] for r in pos)
    assert negative==sum(r['target_present'] for r in neg)/500
    result=dict(status='COMPLETE',label=a.label,model_path=str(model_path),tokenizer_artifact_name=actual_name,
                tokenizer_dispatch_name=tokenizer.name_or_path,detector='unmodified pinned fp_test.generate_fingerprint and neg_check',
                source_sha256=hashlib.sha256((rr/'work/fingerprint/fp_test.py').read_bytes()).hexdigest(),
                positive_probes=len(pos),positive_successes=sum(r['target_present'] for r in pos),positive_rate=sum(r['target_present'] for r in pos)/len(pos),
                official_ownership_verdict=positive,criterion='target-string containment for every unique fingerprint input',
                negative_probes=500,negative_successes=sum(r['target_present'] for r in neg),negative_rate=negative,
                negative_criterion='official random non-trigger guesses; no added or post-hoc threshold',no_system=False,
                raw_generations_path=str(out/'raw_generations.jsonl'),raw_generations_sha256=hashlib.sha256((out/'raw_generations.jsonl').read_bytes()).hexdigest(),
                fresh_process_reload=True,elapsed_seconds=time.time()-start,errors=[],preferred_teacher='NOT_YET_EVALUATED')
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)

if __name__=='__main__':main()
