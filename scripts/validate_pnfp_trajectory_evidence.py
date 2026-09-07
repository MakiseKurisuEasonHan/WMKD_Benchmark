#!/usr/bin/env python3
"""CPU-only validation of permanent PN-FP trajectory evidence; never runs models."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

STEPS = [0, 25, 50, 100, 250, 500, 1000, 2000, 4000, 6000, 7500]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    assert path.is_file() and path.stat().st_size > 0, str(path)
    return json.loads(path.read_text(encoding='utf-8'))


def validate(root, partial=False):
    points = load(root / 'trajectory.json')
    expected = STEPS[:len(points)] if partial else STEPS
    assert [x['step'] for x in points] == expected
    assert points[0]['elapsed_seconds'] == 0 and points[0]['train_loss'] is None
    rows = list(csv.DictReader((root / 'trajectory.csv').open(encoding='utf-8', newline='')))
    assert len(rows) == len(points)
    assert (root / 'trajectory.csv').read_bytes() == (root / 'plotting_ready.csv').read_bytes()
    for row, point in zip(rows, points):
        for k, v in row.items():
            wanted = point[k]
            if wanted is None:
                assert v == '', (point['step'], k)
            else:
                assert float(v) == float(wanted), (point['step'], k)
        d = root / 'checkpoints' / f"step_{point['step']:06d}"
        assert load(d / 'detector_result.json') == point
        raw = load(d / 'detector_raw.json')
        assert raw['fingerprints_evaluated'] == 1024
        assert raw['invalid_samples'] == raw['evaluation_errors'] == 0
        assert raw['detection_response_length'] == 1
        details = raw['details']
        assert len(details) == 1024 and [x['index'] for x in details] == list(range(1024))
        for x in details:
            assert not x['invalid'] and x['error'] is None
            assert len(x['prediction_ids']) == len(x['target_ids']) == 1
            assert x['detected'] == (x['prediction_ids'] == x['target_ids'])
        assert sum(x['detected'] for x in details) == raw['detected'] == point['detected']
        assert point['total'] == 1024 and point['detection_rate'] == point['detected'] / 1024
        assert point['rng_unchanged_after_detector'] and point['continuous_in_memory_optimizer_scheduler']
        for item in load(d / 'evidence_sha_manifest.json'):
            assert digest(d / item['path']) == item['sha256'], item['path']
        assert digest(d / 'checkpoint_file_manifest.json') == point['checkpoint_manifest_sha256']
        assert digest(root / 'training_config_snapshot.json') == point['config_sha256']
        assert digest(root / 'tokenizer_template_identity.json') == point['tokenizer_template_manifest_sha256']
    if not partial:
        assert load(root / 'final_fresh_reload/detector_raw.json')['details'] == load(
            root / 'checkpoints/step_007500/detector_raw.json')['details']
        summary = load(root / 'training_summary.json')
        assert summary['global_step'] == 7500 and summary['dataset_fetches'] == 60000
        order = [json.loads(x) for x in (root / 'sample_fetch_order.jsonl').read_text().splitlines()]
        assert [x['fetch'] for x in order] == list(range(60000))
        for epoch in range(3):
            assert sorted(x['row_index'] for x in order[epoch * 20000:(epoch + 1) * 20000]) == list(range(20000))
        assert digest(root / 'sample_fetch_order.jsonl') == summary['sample_order_sha256']
        assert all(x['generated_ids'] and x['generated_text'].strip() for x in load(root / 'generation_sanity.json'))
    return {'validation': 'PASS', 'partial': partial, 'measured_steps': expected,
            'sha256': {n: digest(root / n) for n in ['trajectory.json', 'trajectory.csv', 'plotting_ready.csv']},
            'measured_counts': {str(x['step']): x['detected'] for x in points}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1] / 'results/pnfp/experiment_ba_trajectory_followup')
    parser.add_argument('--partial', action='store_true')
    args = parser.parse_args()
    print(json.dumps(validate(args.root, args.partial), indent=2))
