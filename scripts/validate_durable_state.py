"""Audit canonical integrity; optional EOL repair requires exact indexed SHA."""
import hashlib
import json
import sys
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]

def main():
    index = json.loads((ROOT / 'results/experiment_full_logs_index.json').read_text())
    errors = []
    ids = []
    for obj in index['objects']:
        ids.append(tuple(obj.get(k) for k in ('method', 'experiment', 'role', 'run_id')))
        p = ROOT / obj['full_log_path']
        if not p.is_file():
            errors.append({'path': str(p), 'error': 'missing'})
            continue
        raw = p.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        if digest != obj['full_log_sha256']:
            crlf = raw.replace(b'\r\n', b'\n').replace(b'\n', b'\r\n')
            lf = raw.replace(b'\r\n', b'\n')
            if '--restore-indexed-eol' in sys.argv and hashlib.sha256(lf).hexdigest() == obj['full_log_sha256']:
                p.write_bytes(lf)
                continue
            if '--restore-indexed-eol' in sys.argv and hashlib.sha256(crlf).hexdigest() == obj['full_log_sha256']:
                p.write_bytes(crlf)
                continue
            errors.append({'path': obj['full_log_path'], 'error': 'sha_mismatch', 'actual': digest, 'expected': obj['full_log_sha256'], 'crlf_sha': hashlib.sha256(raw.replace(b'\r\n', b'\n').replace(b'\n', b'\r\n')).hexdigest()})
        json.loads(raw)
    archive = json.loads((ROOT / 'results/project_archive_inventory.json').read_text())
    counts = dict(Counter(a['archive_classification'] for a in archive['artifacts']))
    for name, count in archive['counts'].items():
        counts.setdefault(name, 0)
        if counts[name] != count:
            errors.append({'error': 'archive_count_mismatch', 'classification': name})
    if index['object_count'] != len(ids):
        errors.append({'error': 'index_count_mismatch'})
    for a in archive['artifacts']:
        e = a.get('evidence') or ''
        if e.startswith('results/') and not (ROOT / e).is_file():
            errors.append({'error': 'missing_archive_evidence', 'path': e})
    result = {'object_count': len(ids), 'unique_composite_ids': len(set(ids)), 'duplicates': len(ids)-len(set(ids)), 'archive_counts': counts, 'errors': errors, 'PASS': not errors and len(ids) == len(set(ids)) and len(ids) >= 32}
    print(json.dumps(result, indent=2))
    return result

if __name__ == '__main__':
    result = main()
    sys.exit(0 if result['PASS'] else 1)
