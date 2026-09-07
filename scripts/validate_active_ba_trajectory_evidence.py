#!/usr/bin/env python3
"""CPU-only permanent-evidence validation; no training, detector or downloads."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from evertracer_common import corrected_detector_metrics


def read(path):
    assert path.is_file() and path.stat().st_size > 0, str(path)
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(root, partial=False):
    spec = read(root / 'run_spec.json')
    assert spec['method_key'] == 'evertracer', 'Method-specific validator must be audited first'
    points = read(root / 'trajectory.json')
    steps = spec['checkpoint_steps'][:len(points)] if partial else spec['checkpoint_steps']
    assert [p['step'] for p in points] == steps and steps[0] == 0
    assert points[0]['train_loss'] is None and points[0]['elapsed_seconds'] == 0
    csv_rows = list(csv.DictReader((root / 'trajectory.csv').open(encoding='utf-8', newline='')))
    assert len(csv_rows) == len(points)
    assert (root / 'trajectory.csv').read_bytes() == (root / 'plotting_ready.csv').read_bytes()
    for p, row in zip(points, csv_rows):
        for k, value in row.items():
            assert value == ('' if p[k] is None else str(p[k])), (p['step'], k)
        d = root / 'checkpoints' / f"step_{p['step']:06d}"
        assert read(d / 'detector_result.json') == p
        raw = read(d / 'detector_raw.json'); aggregate = read(d / 'detector_aggregate.json')
        scores = raw['scores']; assert len(scores) == 200 and scores == aggregate['scores']
        assert sum(x['subset'] == 'dtr' for x in scores) == 100
        assert sum(x['subset'] == 'dunseen' for x in scores) == 100
        for s in scores:
            assert all(math.isfinite(s[k]) for k in ('calibrated_score', 'suspect_variation', 'reference_variation'))
        calculated = corrected_detector_metrics(scores, 0.05)
        for k in spec['native_metric_fields']:
            assert calculated[k] == aggregate[k] == p[k], (p['step'], k)
        assert p['member_oriented_fpr'] <= 0.05 and p['detector_errors'] == p['invalid_samples'] == 0
        assert p['rng_unchanged_after_detector'] and p['continuous_in_memory_optimizer_scheduler']
        integrity = read(d / 'detector_integrity.json')
        assert integrity['nonfinite_scores'] == integrity['detector_errors'] == 0
        assert integrity['query_count'] == 200 and integrity['frozen_record_order_verified']
        for item in read(d / 'evidence_sha_manifest.json'):
            assert sha(d / item['path']) == item['sha256'], str(d / item['path'])
        assert sha(d / 'checkpoint_file_manifest.json') == p['checkpoint_manifest_sha256']
        assert sha(root / 'training_config_snapshot.json') == p['config_sha256']
        assert sha(root / 'tokenizer_template_identity.json') == p['tokenizer_template_manifest_sha256']
    if not partial:
        assert read(root / 'final_fresh_reload/detector_comparison_payload.json') == read(
            root / f"checkpoints/step_{steps[-1]:06d}/detector_comparison_payload.json")
        summary = read(root / 'training_summary.json')
        assert summary['global_step'] == steps[-1] and summary['dataset_fetches'] == 60000
        fetches = [json.loads(x) for x in (root / 'sample_fetch_order.jsonl').read_text().splitlines()]
        assert [x['fetch'] for x in fetches] == list(range(60000))
        for epoch in range(3):
            assert sorted(x['row_index'] for x in fetches[epoch * 20000:(epoch + 1) * 20000]) == list(range(20000))
        assert sha(root / 'sample_fetch_order.jsonl') == summary['sample_order_sha256']
        assert all(x['generated_text'].strip() and x['generated_ids'] for x in read(root / 'generation_sanity.json'))
    return {'status': 'PASS', 'method': spec['method'], 'partial': partial, 'steps': steps,
        'sha256': {name: sha(root / name) for name in ('trajectory.json', 'trajectory.csv', 'plotting_ready.csv')}}


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--root', required=True, type=Path)
    p.add_argument('--partial', action='store_true')
    a = p.parse_args()
    print(json.dumps(validate(a.root, a.partial), indent=2))
