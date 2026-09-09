"""CPU-only frozen XBb supervision preflight. Never repairs or trains."""
import argparse
import hashlib
import json
from pathlib import Path

from transformers import AutoTokenizer


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--protocol', required=True)
    parser.add_argument('--model', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    protocol = json.loads(Path(args.protocol).read_text())
    source = Path(protocol['dataset']['source_path'])
    data = source.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    assert digest == protocol['dataset']['sha256'], 'DATASET_SHA_MISMATCH'
    assert protocol['dataset']['target_field'] == 'paraphrased_answer'
    assert protocol['training']['supervision'] == 'paraphrased_answer'
    rows = [json.loads(line) for line in data.splitlines() if line.strip()]
    assert len(rows) == 20000
    tokenizer = AutoTokenizer.from_pretrained(args.model, local_files_only=True)
    limit = protocol['training']['max_length']
    failures = []
    maximum = 0
    for index, row in enumerate(rows):
        target = row.get('paraphrased_answer')
        if not isinstance(target, str) or not target.strip():
            failures.append({'row': index, 'error': 'EMPTY_TARGET'})
            continue
        user = row['instruction'] + (('\n\nInput:\n' + row['input']) if row['input'] else '')
        prompt = tokenizer.apply_chat_template([{'role': 'user', 'content': user}], tokenize=False, add_generation_prompt=True)
        full = tokenizer.apply_chat_template([{'role': 'user', 'content': user}, {'role': 'assistant', 'content': target}], tokenize=False, add_generation_prompt=False)
        prompt_ids = tokenizer(prompt, add_special_tokens=False)['input_ids']
        ids = tokenizer(full, add_special_tokens=False)['input_ids']
        maximum = max(maximum, len(ids))
        if ids[:len(prompt_ids)] != prompt_ids:
            failures.append({'row': index, 'error': 'PROMPT_PREFIX_MISMATCH'})
        if len(ids) <= len(prompt_ids):
            failures.append({'row': index, 'error': 'EMPTY_SUPERVISION'})
        if len(ids) > limit:
            failures.append({'row': index, 'error': 'WOULD_TRUNCATE', 'tokens': len(ids)})
    output = Path(args.output)
    assert not output.exists(), 'Do not overwrite a prior preflight'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({'status': 'PASS' if not failures else 'BLOCKED', 'method': protocol['method'], 'dataset_sha256': digest, 'records': len(rows), 'target_field': 'paraphrased_answer', 'max_tokens': maximum, 'max_length': limit, 'failures': failures, 'scope': 'CPU dataset and native tokenizer only; model identity and GPU gate are separate'}, indent=2) + '\n')
    if failures:
        raise RuntimeError('PREFLIGHT_FAILED; no automatic scientific configuration change')


if __name__ == '__main__':
    main()
