"""Fail-closed adapters around frozen native Ba detector executables.

Adapters validate and serialize evidence only; they do not choose thresholds,
replace queries, change scoring or launch another method.
"""
import json
import math
import os
from pathlib import Path
import subprocess


def persist(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + '.tmp')
    with temp.open('w', encoding='utf-8') as f:
        json.dump(value, f, ensure_ascii=False, indent=2, allow_nan=False)
        f.write('\n'); f.flush(); os.fsync(f.fileno())
    temp.replace(path)


def execute(cmd, target, name, env):
    persist(target / (name + '_command.json'), cmd)
    with (target / (name + '_stdout.log')).open('w') as f:
        subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT, check=True, env=env)
        f.flush(); os.fsync(f.fileno())


def run_detector(spec, model_path, target, project, python, env):
    target = Path(target); target.mkdir(parents=True, exist_ok=True)
    if spec['method_key'] == 'ctcc':
        return run_ctcc_detector(spec, model_path, target, project, python, env)
    if spec['method_key'] != 'evertracer':
        raise NotImplementedError('Method detector must be audited before launch')
    d = spec['detector']
    raw_path = target / 'detector_raw.json'
    execute([python, '-B', str(project / 'scripts/evertracer_verify.py'),
             '--config', d['config'], '--suspect', str(model_path), '--reference', d['reference'],
             '--neighborhoods', d['neighborhoods'], '--output', str(raw_path),
             '--label', spec['run_id'] + ':' + target.name], target, 'verification', env)
    raw = json.loads(raw_path.read_text())
    rows = [json.loads(x) for x in Path(d['neighborhoods']).read_text().splitlines() if x.strip()]
    scores = raw['scores']
    assert len(rows) == len(scores) == 200
    assert sum(x['subset'] == 'dtr' for x in scores) == 100
    assert sum(x['subset'] == 'dunseen' for x in scores) == 100
    for a, b in zip(rows, scores):
        assert all(a[k] == b[k] for k in ('subset', 'position', 'source_index'))
        assert len(a['pairs']) == 5
        for key in ('suspect_variation', 'reference_variation', 'calibrated_score'):
            assert math.isfinite(b[key]), key
        assert b['calibrated_score'] == b['suspect_variation'] - b['reference_variation']
    execute([python, '-B', str(project / 'scripts/evertracer_aggregate_verification.py'),
             '--config', d['config'], '--input', str(raw_path), '--output', str(target / 'detector_aggregate.json'),
             '--source-run-id', spec['run_id']], target, 'aggregation', env)
    aggregate = json.loads((target / 'detector_aggregate.json').read_text())
    assert aggregate['scores'] == scores
    assert aggregate['fpr_limit'] == 0.05 and aggregate['member_oriented_fpr'] <= 0.05 + 1e-12
    metrics = {k: aggregate[k] for k in spec['native_metric_fields']}
    assert all(math.isfinite(float(v)) for v in metrics.values())
    assert 0 <= metrics['member_oriented_auc'] <= 1
    assert 0 <= metrics['member_oriented_tpr_at_fpr_limit'] <= 1
    comparison = {'scores': scores, 'native_metrics': metrics}
    persist(target / 'detector_integrity.json', {'query_count': 200, 'member_count': 100,
        'nonmember_count': 100, 'nonfinite_scores': 0, 'detector_errors': 0,
        'frozen_record_order_verified': True, 'frozen_aggregation_used': True})
    persist(target / 'detector_comparison_payload.json', comparison)
    persist(raw_path, raw)
    persist(target / 'detector_aggregate.json', aggregate)
    return {'native_metrics': metrics, 'comparison_payload': comparison,
            'detector_decision': None,
            'interpretation': 'Frozen member-oriented metrics and empirical FPR<=0.05 operating rule; '
                              'no new model-level ownership threshold. Per-point threshold is an output '
                              'of the unchanged historical aggregation, not a newly tuned detector.'}


def validate_ctcc_raw(raw, frozen_rows):
    """Recompute the historical equality rule, rejecting silent generation errors."""
    rows = raw['raw_generations']; summary = raw['summary']
    assert len(rows) == len(frozen_rows) == 300
    for row, frozen in zip(rows, frozen_rows):
        for key, value in frozen.items():
            if key != 'record':
                assert row[key] == value, key
        assert row['expected'] == frozen['record']['output']
        assert row['generation_error'] is None
        assert isinstance(row['raw_generation'], str)
        assert row['stripped_generation'] == row['raw_generation'].strip()
        assert row['activated'] == (row['raw_generation'].strip() == 'IAMALIVE')
    metrics = {}
    for category, count in [('trigger', 95), ('suppression', 100), ('normal', 105)]:
        subset = [r for r in rows if r['category'] == category]
        assert len(subset) == count
        hits = sum(r['activated'] for r in subset)
        saved = summary['categories'][category]
        assert saved == dict(count=count, activations=hits, activation_rate=hits/count,
                             generation_errors=0)
        metrics[category + '_activations'] = hits
        metrics[category + '_total'] = count
    negatives = metrics['suppression_activations'] + metrics['normal_activations']
    assert summary['combined_negatives'] == dict(count=205, false_activations=negatives,
                                                false_activation_rate=negatives/205)
    assert summary['generation_errors'] == 0 and summary['raw_generation_count'] == 300
    metrics.update(combined_negative_activations=negatives, combined_negative_total=205)
    return metrics


def run_ctcc_detector(spec, model_path, target, project, python, env):
    d = spec['detector']; raw_path = target / 'detector_raw.json'
    execute([python, '-B', str(project / 'scripts/ctcc_ba_evaluate.py'),
             '--config', d['config'], '--student', str(model_path),
             '--training-run', spec['run_id'], '--output', str(raw_path)],
            target, 'verification', env)
    raw = json.loads(raw_path.read_text())
    frozen = json.loads(Path(d['frozen_annotations']).read_text())
    metrics = validate_ctcc_raw(raw, frozen)
    assert set(metrics) == set(spec['native_metric_fields'])
    comparison = {'raw_generations': raw['raw_generations'], 'native_metrics': metrics}
    persist(target / 'detector_comparison_payload.json', comparison)
    persist(target / 'detector_integrity.json', dict(query_count=300, detector_errors=0,
        nonfinite_scores=0, frozen_record_order_verified=True, equality_rule_recomputed=True))
    return dict(native_metrics=metrics, comparison_payload=comparison, detector_decision=None,
        interpretation='Frozen WMKD operational exact case-sensitive strip()==IAMALIVE detector; '
                       'not the official CTCC detector. Per-query activations retained; '
                       'no new model-level ownership threshold.')
