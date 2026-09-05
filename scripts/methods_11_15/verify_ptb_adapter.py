"""Compare the adapted text loader against the actual official builder method."""
import ast, hashlib, json, sys
from common import *

builder, run = Path(sys.argv[1]), Path(sys.argv[2])
tree = ast.parse(builder.read_text(encoding='utf-8'))
method = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == '_generate_examples')
namespace = {}
exec(compile(ast.Module(body=[method], type_ignores=[]), str(builder), 'exec'), namespace)
from datasets import load_dataset
from transformers import AutoTokenizer
tok = AutoTokenizer.from_pretrained(DATA/'models/llmprint_validation/models/openai-community--gpt2/snapshots/master', local_files_only=True)
audit = {'official_builder_sha256': sha(builder), 'official_builder': 'https://raw.githubusercontent.com/huggingface/datasets/1.18.4/datasets/ptb_text_only/ptb_text_only.py', 'scope': 'All rows compared with extracted official generator; representative tokenizer outputs compared; CPU only', 'splits': {}}
out = run/'ptb_adapter_audit'; out.mkdir(exist_ok=True)
for split in ('train', 'valid', 'test'):
    raw = run/'ptb'/f'ptb_{split}.txt'
    reference = [row['sentence'] for _, row in namespace['_generate_examples'](None, raw)]
    adapted_path = out/f'{split}.txt'
    adapted_path.write_text('\n'.join(line.strip() for line in raw.read_text().splitlines())+'\n', encoding='utf-8', newline='\n')
    adapted = load_dataset('text', data_files={'train': str(adapted_path)}, split='train')['text']
    assert list(adapted) == reference
    indices = sorted(set(range(min(256, len(reference)))) | set(range(max(0,len(reference)-256),len(reference))))
    expected = tok([reference[i] for i in indices])['input_ids']
    actual = tok([adapted[i] for i in indices])['input_ids']
    assert actual == expected
    audit['splits'][split] = {'row_count': len(reference), 'all_rows_identical': True, 'tokenized_rows': len(indices), 'token_ids_identical': True, 'token_sha256': hashlib.sha256(json.dumps(actual).encode()).hexdigest(), 'raw_sha256': sha(raw), 'normalized_sha256': sha(adapted_path)}
audit.update(time=now(), status='PASS')
write(ROOT/'results/methods_11_15/ptb_adapter_equivalence_audit.json', audit)
print(json.dumps(audit, indent=2))
