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
