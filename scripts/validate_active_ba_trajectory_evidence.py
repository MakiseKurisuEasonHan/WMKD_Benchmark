#!/usr/bin/env python3
"""CPU-only permanent-evidence validation; no training, detector or downloads."""
import argparse
import csv
import hashlib
import json
import math
import statistics
from pathlib import Path
from evertracer_common import corrected_detector_metrics


def read(path):
    assert path.is_file() and path.stat().st_size > 0, str(path)
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(root, partial=False):
    spec = read(root / 'run_spec.json')
    assert spec['method_key'] in ('evertracer', 'ctcc', 'iseal', 'scw'), 'Method-specific validator must be audited first'
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
        if spec['method_key'] == 'ctcc':
            raw = read(d / 'detector_raw.json')
            rows = raw['raw_generations']
            assert len(rows) == 300 and all(r['generation_error'] is None for r in rows)
            for r in rows:
                assert r['activated'] == (r['raw_generation'].strip() == 'IAMALIVE')
            for cat, count in [('trigger', 95), ('suppression', 100), ('normal', 105)]:
                subset = [r for r in rows if r['category'] == cat]
                assert len(subset) == count == p[cat + '_total']
                assert sum(r['activated'] for r in subset) == p[cat + '_activations']
            assert p['combined_negative_total'] == 205
            assert p['combined_negative_activations'] == p['suppression_activations'] + p['normal_activations']
            integrity = read(d / 'detector_integrity.json')
            assert integrity['query_count'] == 300 and integrity['equality_rule_recomputed']
            assert p['detector_errors'] == p['invalid_samples'] == integrity['detector_errors'] == 0
            assert p['rng_unchanged_after_detector'] and p['continuous_in_memory_optimizer_scheduler']
        elif spec['method_key'] == 'scw':
            from scw_common import fixed_permutation, classify_p_value, CURVE_QUERY_COUNTS
            raw = read(d / 'detector_raw.json')
            rows = [json.loads(x) for x in (d / 'generations.jsonl').read_text().splitlines()]
            baseline = [json.loads(x) for x in (root / 'checkpoints/step_000000/generations.jsonl').read_text().splitlines()]
            assert len(rows) == len(baseline) == p['query_count'] == 1000
            for i, (r, base) in enumerate(zip(rows, baseline)):
                assert r['index'] == i
                assert all(r[k] == base[k] for k in ('sample_id', 'prompt', 'prompt_sha256'))
                assert hashlib.sha256(r['prompt'].encode()).hexdigest() == r['prompt_sha256']
                assert r['completion'].strip()
                assert hashlib.sha256(r['completion'].encode()).hexdigest() == r['completion_sha256']
            assert raw['alpha'] == 0.001 and raw['permutation_seed'] == 42
            assert raw['permutation_indices'] == fixed_permutation(1000, 42)
            assert [x['n_queries'] for x in raw['curve']] == list(CURVE_QUERY_COUNTS)
            for r in raw['curve']:
                assert math.isfinite(r['p_value']) and 0 <= r['p_value'] <= 1
                assert r['fingerprinted'] == classify_p_value(r['p_value'])
            assert raw['primary'] == raw['curve'][-1]
            assert raw['primary']['p_value'] == p['p_value']
            assert raw['primary']['fingerprinted'] == p['fingerprinted'] == p['detector_decision']
            integrity = read(d / 'detector_integrity.json')
            assert p['detector_errors'] == p['invalid_samples'] == integrity['detector_errors'] == 0
            if p['step'] in (50, 500):
                assert p['rng_unchanged_after_detector'] is None
                assert p['continuous_in_memory_optimizer_scheduler'] is False
                assert p['continuity_note']
                audit = 'continuation_cpu_audit.json' if p['step'] == 50 else 'step500_continuation_cpu_audit.json'
                assert read(root / audit)['status'] == 'PASS_CPU_SAMPLER_CHECKPOINT_STATE'
            else:
                assert p['rng_unchanged_after_detector'] and p['continuous_in_memory_optimizer_scheduler']
        elif spec['method_key'] == 'iseal':
            raw = read(d / 'detector_raw.json')
            assert raw['detector']['threshold'] == 50.0
            for group, count in [('registered', 200), ('held_out', 100)]:
                g = raw['groups'][group]; rows = g['rows']
                assert len(rows) == g['count'] == p[group + '_total'] == count
                scores = [r['teacher_bleu'] for r in rows]
                assert all(math.isfinite(x) and 0 <= x <= 100 for x in scores)
                assert all(r['teacher_positive'] == (r['teacher_bleu'] >= 50) for r in rows)
                assert sum(x >= 50 for x in scores) == p[group + '_success']
                assert p[group + '_success_rate'] == g['teacher_success_rate'] == p[group + '_success']/count
                assert abs(statistics.mean(scores) - p[group + '_mean_bleu']) < 1e-12
                assert statistics.median(scores) == p[group + '_median_bleu']
                baseline = read(root / 'checkpoints/step_000000/detector_raw.json')['groups'][group]['rows']
                assert [r['plaintext_sha256'] for r in rows] == [r['plaintext_sha256'] for r in baseline]
            integrity = read(d / 'detector_integrity.json')
            assert integrity['query_count'] == 300 and integrity['frozen_record_order_verified']
            assert p['detector_errors'] == p['invalid_samples'] == integrity['detector_errors'] == 0
            assert p['rng_unchanged_after_detector'] and p['continuous_in_memory_optimizer_scheduler']
        else:
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
        order_path = root / summary.get('sample_order_file', 'sample_fetch_order.jsonl')
        fetches = [json.loads(x) for x in order_path.read_text().splitlines()]
        if spec['method_key'] == 'scw':
            old = [json.loads(x) for x in (root / 'sample_fetch_order.jsonl').read_text().splitlines()]
            cont3 = [json.loads(x) for x in (root / 'continuation_cont3/sample_fetch_order.jsonl').read_text().splitlines()]
            cont4 = [json.loads(x) for x in (root / 'continuation_cont4/sample_fetch_order.jsonl').read_text().splitlines()]
            assert len(old) == 408 and len(cont3) == 3608
            assert fetches == old[:400] + cont3[:3600] + cont4
            assert old[400:] == cont3[:8] and cont3[3600:] == cont4[:8]
            for name, step in [('continuation_cont3', 50), ('continuation_cont4', 500)]:
                gate = read(root / name / 'before_first_update_gate.json')
                assert gate['status'] == 'PASS' and gate['global_step'] == step
                assert gate['rng_exact'] and gate['optimizer_scheduler_restored'] and gate['sampler_prefix_exact']

        assert [x['fetch'] for x in fetches] == list(range(60000))
        for epoch in range(3):
            assert sorted(x['row_index'] for x in fetches[epoch * 20000:(epoch + 1) * 20000]) == list(range(20000))
        assert sha(order_path) == summary['sample_order_sha256']
        assert all(x['generated_text'].strip() and x['generated_ids'] for x in read(root / 'generation_sanity.json'))
    return {'status': 'PASS', 'method': spec['method'], 'partial': partial, 'steps': steps,
        'sha256': {name: sha(root / name) for name in ('trajectory.json', 'trajectory.csv', 'plotting_ready.csv')}}


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--root', required=True, type=Path)
    p.add_argument('--partial', action='store_true')
    a = p.parse_args()
    print(json.dumps(validate(a.root, a.partial), indent=2))
