"""CPU-only validation of frozen shared QA under the native Qwen formatter."""
import os
os.environ['CUDA_VISIBLE_DEVICES'] = ''
os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'
import hashlib
import json
from pathlib import Path
from transformers import AutoTokenizer
from train_distillation_student import SFTDataset

P = Path('/root/autodl-tmp/WMKD_Benchmark')
D = Path(str(P) + '_data')
E = P / 'results/passive_cross_lineage'
M = D / 'models/paraphrasers/Qwen2.5-3B-Instruct'
paths = {
    'ba': D / 'runs/passive5_shared_ba/passive5_shared_ba_20260902_114500_cont1/dataset/frozen_qa.jsonl',
    'bb': D / 'runs/passive5_shared_bb3/passive5_shared_bb3_20260903_164929/dataset/frozen_paired_qa.jsonl',
}
tok = AutoTokenizer.from_pretrained(M, local_files_only=True)
result = dict(tokenizer_class=type(tok).__name__, vocab_size=tok.vocab_size,
              len_tokenizer=len(tok), bos_token_id=tok.bos_token_id,
              eos_token_id=tok.eos_token_id, pad_token_id=tok.pad_token_id,
              chat_template=tok.chat_template, max_length=1024,
              formatter_source_sha256=hashlib.sha256((P/'scripts/train_distillation_student.py').read_bytes()).hexdigest(),
              target_content_modified=False, roles={})
for role, path in paths.items():
    ds = SFTDataset(path, tok, 1024)
    if role == 'bb':
        ds.rows = [dict(sample_id=r['sample_id'], instruction=r['instruction'],
                        input=r['input'], teacher_raw_answer=r['paraphrased_answer']) for r in ds.rows]
    counts = dict(records=len(ds), truncation_count=0, zero_supervision_count=0,
                  target_tokens_before_truncation=0, target_tokens_after_truncation=0)
    examples = []
    for i, row in enumerate(ds.rows):
        user = row['instruction'] + (('\n\nInput:\n' + row['input']) if row['input'] else '')
        messages = [dict(role='user', content=user)]
        prefix = tok.apply_chat_template(messages, tokenize=True, add_generation_prompt=True)
        full = tok.apply_chat_template(messages + [dict(role='assistant', content=row['teacher_raw_answer'])], tokenize=True)
        assert full[:len(prefix)] == prefix
        actual = ds[i]
        assert actual['input_ids'] == full[:1024]
        assert actual['labels'] == [-100]*min(len(prefix),len(actual['input_ids'])) + full[len(prefix):1024]
        supervised = sum(x != -100 for x in actual['labels'])
        counts['truncation_count'] += len(full) > 1024
        counts['zero_supervision_count'] += supervised == 0
        counts['target_tokens_before_truncation'] += len(full)-len(prefix)
        counts['target_tokens_after_truncation'] += supervised
        if len(examples) < 2:
            examples.append(dict(sample_id=row['sample_id'], serialized_prompt=tok.apply_chat_template(messages,tokenize=False,add_generation_prompt=True), input_ids=prefix, target_sha256=hashlib.sha256(row['teacher_raw_answer'].encode()).hexdigest()))
    assert counts['records'] == 20000 and counts['zero_supervision_count'] == 0
    result['roles'][role] = dict(counts=counts, examples=examples)
result['status'] = 'PASS'
old = E/'formatter_validation.json'
if old.exists() and not (E/'formatter_validation_initial_draft.json').exists():
    (E/'formatter_validation_initial_draft.json').write_bytes(old.read_bytes())
old.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v['counts'] for k,v in result['roles'].items()}))
