"""CPU-only audit of existing frozen records. No model, optimizer, training or generation."""
import os
os.environ['CUDA_VISIBLE_DEVICES']=''
os.environ['HF_HUB_OFFLINE']='1'
os.environ['HF_DATASETS_OFFLINE']='1'
os.environ['TOKENIZERS_PARALLELISM']='false'
import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from transformers import AutoTokenizer

P=Path('/root/autodl-tmp/WMKD_Benchmark')
D=Path('/root/autodl-tmp/WMKD_Benchmark_data')

def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return [json.loads(line) for line in p.open() if line.strip()]
def user(r): return r['instruction']+('\n\nInput:\n'+r['input'] if r.get('input') else '')
def pattern(texts):
    texts=set(t for t in texts if t)
    return re.compile('|'.join(re.escape(t) for t in sorted(texts,key=len,reverse=True))) if texts else None

def main(payload):
    base=D/'models/base/Llama-3.2-3B-Instruct'
    tok=AutoTokenizer.from_pretrained(base,local_files_only=True)
    assert tok.truncation_side=='right'
    date='07 Sep 2026' # Explicit diagnostic date; never claim exact historical date replay.
    keys_path=next((D/'runs/pnfp_bb/pnfp_bb_20260904_055000/evaluation/detector_input').glob('fingerprint_keys-perinucleus-*'))
    keys=json.loads(keys_path.read_text())[:1024]
    pnfp_key=pattern([r['key'] for r in keys]);pnfp_response=pattern([r['response'] for r in keys])
    ctcc=json.loads((D/'datasets/ctcc/experiment_a/trigger_set.json').read_text())
    ctcc_questions={user(r) for r in ctcc}
    iseal_manifest=json.loads((D/'runs/iseal/a6/iseal_a6_20260830_132300/manifests/dataset_manifest.json').read_text())
    registered={r['plaintext_sha256'] for r in iseal_manifest['training']}
    neighbors=read(D/'runs/evertracer/evertracer_a_20260828_223155_cont1/artifacts/frozen_neighborhoods.jsonl')
    originals={r['original'] for r in neighbors}
    scw={r['instruction'] for r in read(D/'evaluation/scw/a2_french_eval/scw_a2_french_eval_1000.jsonl')}
    out={'checked_at':datetime.now(timezone.utc).isoformat(),'mode':'CPU_ONLY_NO_MODEL_NO_GENERATION',
         'training_formatter_source_sha256':digest(P/'scripts/train_distillation_student.py'),
         'tokenizer_sha256':digest(base/'tokenizer.json'),'tokenizer_config_sha256':digest(base/'tokenizer_config.json'),
         'replay_date_string':date,'historical_date_exactness':'NOT_ESTABLISHED',
         'token_replay_scope':'Current retained training formatter, max_length=1024, prompt labels masked. Explicit diagnostic date; not a recovered historical per-step trace.',
         'methods':{}}
    for m in ['pnfp','evertracer','ctcc','iseal','scw']:
        selected={Path(r['path']).name:r for r in payload[m] if Path(r['path']).name in ['frozen_qa.jsonl','frozen_paired_qa.jsonl','student_qa.jsonl']}
        for name,r in selected.items(): assert digest(Path(r['path']))==r['sha256'],r['path']
        parent=read(Path(selected['frozen_qa.jsonl']['path']));paired=read(Path(selected['frozen_paired_qa.jsonl']['path']));student=read(Path(selected['student_qa.jsonl']['path']))
        assert len(parent)==len(paired)==len(student)==20000
        a={r['sample_id']:r for r in parent};b={r['sample_id']:r for r in student}
        assert len(a)==len(b)==20000
        alignment=Counter();identical=0
        for r in paired:
            sid=r['sample_id'];assert sid in a and sid in b
            checks={'parent_instruction':r['instruction']==a[sid]['instruction'],
                    'parent_input':r['input']==a[sid]['input'],
                    'parent_answer':r['source_answer']==a[sid]['teacher_raw_answer'],
                    'student_instruction':r['instruction']==b[sid]['instruction'],
                    'student_input':r['input']==b[sid]['input'],
                    'student_answer':r['paraphrased_answer']==b[sid]['teacher_raw_answer']}
            for k,v in checks.items():alignment[k+'_mismatches']+=not v
            identical+=r['source_answer']==r['paraphrased_answer']
        result={'parent_origin':'RECONSTRUCTED_NOT_ORIGINAL_BA' if m in ['pnfp','scw'] else 'ORIGINAL_BA',
                'file_identity':selected,'alignment':dict(alignment),'paired_unique_ids':len({r['sample_id'] for r in paired}),
                'literal_identical_answers':identical,'literal_changed_answers':20000-identical,
                'processing_modes':dict(Counter(r['processing_mode'] for r in paired)),'datasets':{}}
        for stage,rows in [('parent',parent),('bb_student',student)]:
            counts=Counter();counts['records']=len(rows)
            counts['unique_questions']=len({user(r) for r in rows})
            counts['unique_answers']=len({r['teacher_raw_answer'] for r in rows})
            for start in range(0,len(rows),256):
                batch=rows[start:start+256]
                prompts=tok.apply_chat_template([[{'role':'user','content':user(r)}] for r in batch],tokenize=False,add_generation_prompt=True,date_string=date)
                full=tok.apply_chat_template([[{'role':'user','content':user(r)},{'role':'assistant','content':r['teacher_raw_answer']}] for r in batch],tokenize=False,add_generation_prompt=False,date_string=date)
                pids=tok(prompts,add_special_tokens=False)['input_ids'];fids=tok(full,add_special_tokens=False)['input_ids']
                for r,p,f in zip(batch,pids,fids):
                    q=user(r);answer=r['teacher_raw_answer'];visible=f[min(len(p),1024):1024]
                    supervised=tok.decode(visible,skip_special_tokens=False)
                    counts['untruncated_input_tokens']+=len(f);counts['retained_input_tokens']+=min(len(f),1024)
                    counts['supervised_label_tokens']+=len(visible);counts['truncated_records']+=len(f)>1024
                    counts['zero_supervised_records']+=len(visible)==0
                    if m=='pnfp':
                        counts['key_substring_in_question']+=bool(pnfp_key.search(q))
                        counts['response_substring_in_answer']+=bool(pnfp_response.search(answer))
                        counts['response_substring_in_retained_label_text']+=bool(pnfp_response.search(supervised))
                    if m=='ctcc':
                        counts['exact_frozen_trigger_question']+=q in ctcc_questions
                        counts['target_substring_in_answer']+='IAMALIVE' in answer
                        counts['target_exact_normalized_answer']+=answer.strip()=='IAMALIVE'
                        counts['target_substring_in_retained_label_text']+='IAMALIVE' in supervised
                    if m=='iseal':
                        counts['registered_plaintext_exact_whole_field']+=any(hashlib.sha256(t.encode()).hexdigest() in registered for t in [r['instruction'],r['input'],answer,q])
                    if m=='evertracer':
                        counts['frozen_member_or_nonmember_document_exact_field']+=any(t in originals for t in [r['instruction'],r['input'],answer,q])
                    if m=='scw':counts['exact_frozen_french_eval_instruction']+=r['instruction'] in scw
            counts['three_pass_supervised_label_token_replay']=3*counts['supervised_label_tokens']
            result['datasets'][stage]=dict(counts)
        out['methods'][m]=result
        print('AUDIT_METHOD_COMPLETE '+m,flush=True,file=__import__('sys').stderr)
    out['limitations']=[
        'No new inference. Literal overlap is not a semantic or statistical watermark test.',
        'PN-FP and SCW parent metrics describe archived reconstructed Bb parents, not the lost original Ba dataset.',
        'iSeal exact plaintext-hash overlap does not test keyed embedding exposure; ordinary SFT has no KeyedCipher call.',
        'SCW watermark is a response-distribution property; zero exact French evaluation overlap does not measure French response rate.',
        'EverTracer exact document overlap is limited to the retained 200 verification documents, not the entire original fingerprint training corpus.',
        'Recorded training budget is 3 epochs; this CPU token replay is not a recovered historical sample-order or per-step trace.'
    ]
    print(json.dumps(out,indent=2))
