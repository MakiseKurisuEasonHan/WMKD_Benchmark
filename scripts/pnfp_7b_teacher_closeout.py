"""Read-only artifact verification after the serial Teacher evaluations finish."""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path('/root/autodl-tmp/WMKD_Benchmark_data/scale_7b')
OUT = ROOT / 'teacher_adamw8bit_v1'


def read(name):
    return json.loads((OUT / name).read_text())


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024**2), b''):
            h.update(block)
    return h.hexdigest()


def main():
    state = read('state.json')
    assert state['status'] == 'TEACHER_EVALUATIONS_COMPLETE_AWAITING_ASSESSMENT', state
    for stage in ('training', 'detector', 'utility'):
        assert read(stage + '_exit.json')['exit_code'] == 0
    manifest = read('final_model_manifest.json')
    checks = []
    for row in manifest['files']:
        path = Path(manifest['path']) / row['path']
        checks.append({'path': row['path'], 'bytes': path.stat().st_size,
                       'sha256_match': digest(path) == row['sha256'],
                       'size_match': path.stat().st_size == row['bytes']})
    assert all(row['sha256_match'] and row['size_match'] for row in checks)
    provenance = read('provenance.json')
    fp = provenance['fingerprints']
    fingerprint_sha = digest(Path(fp['official_output']))
    assert fingerprint_sha == provenance['config']['fingerprint_sha256']
    steps = [json.loads(s) for s in (OUT / 'steps.jsonl').read_text().splitlines() if s.strip()]
    nonzero = [s for s in steps if any(lr != 0 for lr in s['lr_used'])]
    recall = []
    for path in sorted(OUT.glob('recall_step_*.json')):
        row = json.loads(path.read_text())
        recall.append({k: row[k] for k in ('label', 'fingerprints_evaluated', 'detected', 'detection_rate', 'evaluation_errors')})
    checkpoints = [str(p) for p in OUT.rglob('checkpoint-*')]
    gpu_processes = subprocess.check_output(['nvidia-smi', '--query-compute-apps=pid,used_memory', '--format=csv,noheader'], text=True).strip()
    report = {
        'status': 'FINAL_MODEL_AND_RESULTS_VERIFIED',
        'model_files': checks,
        'fingerprint_sha256': fingerprint_sha,
        'fingerprints_regenerated': False,
        'result': read('result.json'),
        'optimizer_calls': len(steps),
        'nonzero_lr_updates': len(nonzero),
        'mean_seconds_per_nonzero_update': sum(s['sec_per_update'] for s in nonzero) / len(nonzero),
        'final_update_training_loss': steps[-1]['training_loss'],
        'any_nan_inf': any(s['nan_inf_detected'] for s in steps),
        'lightweight_recall_trajectory': recall,
        'detector': {k: v for k, v in read('detector.json').items() if k != 'details'},
        'utility': read('utility.json'),
        'sampled_resource_peaks': state['peaks_sampled_2s'],
        'disk': dict(zip(('total_bytes', 'used_bytes', 'free_bytes'), shutil.disk_usage(ROOT))),
        'intermediate_checkpoints': checkpoints,
        'cleanup_performed': False,
        'cleanup_note': 'Final-only save; retain model, runtime, fingerprints and all evidence.',
        'gpu_processes_after_evaluation': gpu_processes,
        'distillation_started': False,
        'model_archive_uploaded': False,
        'auto_shutdown': False,
    }
    (OUT / 'verification.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ('status', 'optimizer_calls', 'nonzero_lr_updates', 'mean_seconds_per_nonzero_update', 'final_update_training_loss', 'any_nan_inf', 'detector', 'disk', 'gpu_processes_after_evaluation')}, indent=2))


if __name__ == '__main__':
    main()
