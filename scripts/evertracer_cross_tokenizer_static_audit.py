"""CPU-only: frozen probe identity and tokenizer/scoring-window diagnostics.

No models, probabilities, perturbation generation, thresholds or inference run.
"""
import hashlib
import json
from pathlib import Path
from transformers import AutoTokenizer

P=Path('/root/autodl-tmp/WMKD_Benchmark')
D=Path(str(P)+'_data')
E=P/'results/active_cross_lineage_ba/evertracer'
fp=D/'runs/evertracer/evertracer_a_20260828_223155_cont1/artifacts/frozen_neighborhoods.jsonl'
sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(fp.read_bytes())=='7834e3d77704951ea06501c2166e960fef2b147ced3d751a8e55f07ec7b3672b'
rows=[json.loads(x) for x in fp.read_text().splitlines()]
assert len(rows)==200 and sum(x['subset']=='dtr' for x in rows)==100
ll=AutoTokenizer.from_pretrained(D/'models/base/Llama-3.2-3B-Instruct',local_files_only=True)
qw=AutoTokenizer.from_pretrained(D/'models/paraphrasers/Qwen2.5-3B-Instruct',local_files_only=True)
details=[]
for row in rows:
    assert len(row['pairs'])==5
    strings=[('original',row['original'])]+[(str(i)+'/'+side,pair[side]) for i,pair in enumerate(row['pairs']) for side in ('positive','negative')]
    for role,text in strings:
        a=ll.encode(text);b=qw.encode(text)
        av=ll.decode(a[:128],skip_special_tokens=True,clean_up_tokenization_spaces=False)
        bv=qw.decode(b[:128],skip_special_tokens=True,clean_up_tokenization_spaces=False)
        # Candidate preserves exactly historical model-visible text before target encoding.
        candidate=qw.encode(av)
        details.append(dict(subset=row['subset'],position=row['position'],source_index=row['source_index'],role=role,
          text_sha256=sha(text.encode()),llama_full_tokens=len(a),qwen_full_tokens=len(b),
          llama_scored_positions=max(0,min(len(a),128)-1),qwen_scored_positions=max(0,min(len(b),128)-1),
          llama_effective_text_sha256=sha(av.encode()),qwen_effective_text_sha256=sha(bv.encode()),
          same_effective_text=av==bv,llama_truncated=len(a)>128,qwen_truncated=len(b)>128,
          historical_visible_text_qwen_tokens=len(candidate),candidate_exceeds128=len(candidate)>128))
historical={}
for label,path in {
 'teacher':D/'runs/evertracer/evertracer_a_20260828_223155_cont1/metrics/teacher_verification.json',
 'base':D/'runs/evertracer/evertracer_a_20260828_223155_cont1/metrics/base_verification.json',
 'ba':D/'runs/evertracer_ba/evertracer_ba_20260829_124055/metrics/student_verification_raw.json'
}.items():
    if not path.exists():
        historical[label]={'exists':False,'path':str(path)};continue
    result=json.loads(path.read_text());scores=result['scores'];assert len(scores)==200
    assert all((s['subset'],s['position'],s['source_index'])==(r['subset'],r['position'],r['source_index']) for s,r in zip(scores,rows))
    historical[label]={'exists':True,'path':str(path),'sha256':sha(path.read_bytes()),'scores':scores}
summary={'cpu_only':True,'inference_run':False,'frozen_source_sha256':sha(fp.read_bytes()),'records':200,'member':100,'nonmember':100,'originals':200,'variants':2000,'total_scored_strings':len(details),
  'same_effective_text_count':sum(x['same_effective_text'] for x in details),
  'different_effective_text_count':sum(not x['same_effective_text'] for x in details),
  'different_scored_position_count':sum(x['llama_scored_positions']!=x['qwen_scored_positions'] for x in details),
  'llama_truncated_count':sum(x['llama_truncated'] for x in details),'qwen_truncated_count':sum(x['qwen_truncated'] for x in details),
  'historical_visible_text_qwen_exceeds128_count':sum(x['candidate_exceeds128'] for x in details)}
if historical['teacher']['exists'] and historical['base']['exists']:
    summary['teacher_base_reference_scalar_exact_equal_count']=sum(a['reference_variation']==b['reference_variation'] for a,b in zip(historical['teacher']['scores'],historical['base']['scores']))
if historical.get('ba',{}).get('exists'):
    summary['teacher_ba_reference_scalar_exact_equal_count']=sum(a['reference_variation']==b['reference_variation'] for a,b in zip(historical['teacher']['scores'],historical['ba']['scores']))
(E/'static_probe_tokenizer_audit.json').write_text(json.dumps({'summary':summary,'per_string':details,'historical_scalar_artifacts':historical},indent=2)+'\n')
print(json.dumps(summary),flush=True)
