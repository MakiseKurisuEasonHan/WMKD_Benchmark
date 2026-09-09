"""CPU-only audit of the frozen Llama PN-FP secret's text representation."""
import hashlib
import json
from pathlib import Path
from transformers import AutoTokenizer

P = Path('/root/autodl-tmp/WMKD_Benchmark')
D = Path(str(P) + '_data')
E = P / 'results/active_cross_lineage_ba'
manifest = json.loads((P / 'results/pnfp/experiment_ba_trajectory_followup/detector_assets_manifest.json').read_text())
source = Path(manifest['path'])
assert hashlib.sha256(source.read_bytes()).hexdigest() == manifest['sha256']
llama = AutoTokenizer.from_pretrained(D / 'models/base/Llama-3.2-3B-Instruct', local_files_only=True)
qwen = AutoTokenizer.from_pretrained(D / 'models/paraphrasers/Qwen2.5-3B-Instruct', local_files_only=True)
records = json.loads(source.read_text())[:1024]
assert len(records) == 1024
details = []
for index, row in enumerate(records):
    key_ids = llama.encode(row['key'], add_special_tokens=False)[:16]
    target_ids = llama.encode(row['response'], add_special_tokens=False)[:1]
    key = llama.decode(key_ids, clean_up_tokenization_spaces=True)
    target = llama.decode(target_ids, clean_up_tokenization_spaces=True)
    qkey = qwen.encode(key, add_special_tokens=False)
    qtgt = qwen.encode(target, add_special_tokens=False)
    details.append(dict(index=index, key_sha256=hashlib.sha256(key.encode()).hexdigest(),
        target_sha256=hashlib.sha256(target.encode()).hexdigest(),
        llama_target_roundtrip=llama.encode(target, add_special_tokens=False) == target_ids,
        qwen_key_roundtrip=qwen.decode(qkey, clean_up_tokenization_spaces=False) == key,
        qwen_target_roundtrip=qwen.decode(qtgt, clean_up_tokenization_spaces=False) == target,
        qwen_target_length=len(qtgt), empty_target=not bool(qtgt),
        special_target=bool(set(qtgt) & set(qwen.all_special_ids)),
        replacement_character='\ufffd' in target))
result = dict(count=1024, source_sha256=manifest['sha256'], secret_regenerated=False,
    cpu_only=True, classification='PENDING_REVIEW', details=details)
for field in ('llama_target_roundtrip','qwen_key_roundtrip','qwen_target_roundtrip',
              'empty_target','special_target','replacement_character'):
    result[field + '_count'] = sum(x[field] for x in details)
result['qwen_target_length_counts'] = {str(n):sum(x['qwen_target_length']==n for x in details) for n in sorted(set(x['qwen_target_length'] for x in details))}
E.mkdir(parents=True, exist_ok=True)
(E/'pnfp_string_roundtrip_audit.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='details'}), flush=True)
