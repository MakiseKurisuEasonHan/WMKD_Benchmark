"""One-time, evidence-gated weight cleanup; dry-run must precede --execute.

Retains directories and all non-weight files, including optimizer/history evidence.
Uses only already committed strong-remote per-file archive verification records.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
from datetime import datetime, timezone

ROOT = Path('/root/autodl-tmp/WMKD_Benchmark')
DATA = Path('/root/autodl-tmp/WMKD_Benchmark_data')
OUT = ROOT / 'results/pre_methods_11_15_cleanup.json'

def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(8 * 1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()

def now():
    return datetime.now(timezone.utc).isoformat()

def disk():
    return dict(zip(('total', 'used', 'free'), shutil.disk_usage(DATA)))

def active_references(paths):
    hits = []
    for proc in Path('/proc').iterdir():
        if not proc.name.isdigit() or int(proc.name) == os.getpid():
            continue
        try:
            cmd = (proc / 'cmdline').read_bytes().replace(b'\0', b' ').decode(errors='replace')
            refs = [os.readlink(proc / 'cwd')]
            refs += [os.readlink(fd) for fd in (proc / 'fd').iterdir()]
            maps = (proc / 'maps').read_text()
        except FileNotFoundError:
            continue
        except PermissionError as exc:
            raise RuntimeError('Cannot verify process references') from exc
        for p in paths:
            parent = str(Path(p).parent)
            if parent in cmd or parent in maps or any(r == parent or r.startswith(parent + '/') for r in refs):
                hits.append({'pid': int(proc.name), 'path': p})
    gpu = subprocess.check_output(['nvidia-smi', '--query-compute-apps=pid', '--format=csv,noheader'], text=True).strip()
    if gpu:
        raise RuntimeError('GPU process exists; stop cleanup')
    return hits

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--execute', action='store_true')
    args = ap.parse_args()
    if args.execute:
        record = json.loads(OUT.read_text())
        assert record['status'] == 'DRY_RUN'
        rows = [r for r in record['inventory'] if r['classification'] == 'DELETE']
        assert not active_references([r['exact_path'] for r in rows])
        index = json.loads((ROOT / 'results/experiment_full_logs_index.json').read_text())
        protected = {}
        for obj in index['objects']:
            p = ROOT / obj['full_log_path']
            assert sha(p) == obj['full_log_sha256']
            protected[str(p)] = sha(p)
        for name in ('results/experiment_full_logs_index.json', 'results/project_archive_inventory.json'):
            protected[str(ROOT / name)] = sha(ROOT / name)
        reports = {
            'ctcc.ba.student': 'docs/reproduction_reports/ctcc_experiment_ba_report.md',
            'evertracer.a.teacher': 'docs/reproduction_reports/evertracer_experiment_a_report.md',
            'evertracer.ba.student': 'docs/reproduction_reports/evertracer_experiment_ba_report.md',
            'iseal.a6.teacher': 'docs/reproduction_reports/iseal_experiment_a6_report.md',
            'iseal.ba.student': 'docs/reproduction_reports/iseal_experiment_ba_report.md',
            'scw.a2.teacher': 'results/scw/experiment_a2/final_report.md',
            'scw.ba.student': 'docs/reproduction_reports/scw_experiment_ba_report.md',
        }
        for r in rows:
            report = ROOT / reports[r['artifact']]
            assert report.is_file()
            r['canonical_report'] = reports[r['artifact']]
            protected[str(report)] = sha(report)
            protected[str(ROOT / r['archive_evidence'])] = sha(ROOT / r['archive_evidence'])
        record['protected_evidence_sha256'] = protected
        # Revalidate all targets before the first unlink; never delete a directory.
        for r in rows:
            p = Path(r['exact_path'])
            assert p.resolve() == p and p.is_relative_to(DATA / 'runs')
            assert p.suffix == '.safetensors' and p.is_file() and not p.is_symlink()
            assert p.stat().st_size == r['size_bytes'] and sha(p) == r['sha256']
            assert sha(ROOT / r['archive_evidence']) == r['archive_evidence_sha256']
        record['execution_started_at'] = now()
        record['deleted'] = []
        OUT.write_text(json.dumps(record, indent=2) + '\n')
        for r in rows:
            Path(r['exact_path']).unlink()
            record['deleted'].append({**r, 'deleted_at': now()})
            OUT.write_text(json.dumps(record, indent=2) + '\n')
        record['disk_after'] = disk()
        assert all(sha(Path(p)) == digest for p, digest in protected.items())
        record['deleted_logical_bytes'] = sum(r['size_bytes'] for r in rows)
        record['observed_free_bytes_increase'] = record['disk_after']['free'] - record['disk_before']['free']
        record['status'] = 'COMPLETE'
        record['canonical_evidence_untouched'] = True
        record['SAFE_TO_BEGIN_METHOD_11_STORAGE'] = 'YES'
        record['storage_readiness_scope'] = 'Headroom for method-11 preparation; exact official configuration still requires its own preflight.'
    else:
        assert not OUT.exists(), 'Existing dry-run/record must not be overwritten'
        inv = json.loads((ROOT / 'results/project_archive_inventory.json').read_text())
        expected = {}
        for a in inv['artifacts']:
            if a['archive_classification'] != 'ARCHIVED_STRONGLY_VERIFIED':
                continue
            ep = ROOT / a['evidence']
            subprocess.run(['git', '-C', str(ROOT), 'ls-files', '--error-unmatch', a['evidence']], check=True, stdout=subprocess.DEVNULL)
            e = json.loads(ep.read_text())
            assert e['status'] == 'PASS' and e['visibility'] == 'PRIVATE'
            for name, c in e['canonical_checks'].items():
                if name.endswith('.safetensors') and c['match']:
                    v = c['expected']
                    expected[(name, v['size'], v['sha256'])] = (a, sha(ep))
        rows = []
        for p in sorted((DATA / 'runs').rglob('*.safetensors')):
            if p.is_symlink():
                continue
            size = p.stat().st_size
            if size < 100_000_000:
                continue
            row = {'exact_path': str(p), 'size_bytes': size, 'classification': 'UNCERTAIN', 'reason': 'No matching strong-remote weight evidence in this bounded cleanup; KEEP.'}
            if any(n == p.name and s == size for n, s, _ in expected):
                digest = sha(p)
                row['sha256'] = digest
                match = expected.get((p.name, size, digest))
                if match:
                    a, evidence_sha = match
                    row.update(classification='DELETE', artifact=a['artifact_id'], archive_repo=a['modelscope_repo'], archive_evidence=a['evidence'], archive_evidence_sha256=evidence_sha, current_reference='Historical closed run only; restore by archive SHA before future rerun.', reason='Byte-identical archived weight of closed A/Ba; no new-method dependency; preserve all non-weight evidence.')
            rows.append(row)
            print(row['classification'], p, flush=True)
        hits = active_references([r['exact_path'] for r in rows if r['classification'] == 'DELETE'])
        for r in rows:
            if any(h['path'] == r['exact_path'] for h in hits):
                r.update(classification='UNCERTAIN', reason='Active process reference; KEEP.')
        for p in sorted(DATA.iterdir()):
            rows.append({'exact_path': str(p), 'size_bytes': int(subprocess.check_output(['du', '-sb', str(p)], text=True).split()[0]), 'classification': 'KEEP', 'reason': 'Container retained; only individually listed DELETE weight files are eligible.'})
        rows.append({'exact_path': str(ROOT), 'classification': 'KEEP', 'reason': 'Canonical Git checkout, code and all durable evidence.'})
        record = {'schema_version': 'wmkd.pre-methods-cleanup.v1', 'created_at': now(), 'status': 'DRY_RUN', 'baseline_commit': subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip(), 'disk_before': disk(), 'inventory': rows, 'active_reference_hits': hits, 'science_started': False, 'authorization': 'User Durable Rules / State Migration task, sections 16-20.', 'scope': 'Exact archived weight files only. Optimizer states, checkpoints with unmatched weights, caches, datasets, logs, manifests and credentials retained.'}
    OUT.write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps({'status': record['status'], 'delete_files': sum(r['classification'] == 'DELETE' for r in record['inventory']), 'disk': disk()}))

if __name__ == '__main__':
    main()
