"""Run the five frozen same-lineage passive detectors on ONE Bc Student."""
import json
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

P = Path(__file__).resolve().parents[1]
Q = P / 'results/logit_distillation/same_lineage_bc/passive_shared'
D = Path(str(P) + '_data')

def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')

def main(model):
    cfg = json.loads((Q / 'protocol.json').read_text())
    out = Q / 'native_detector'
    root = D / 'runs/llmprint/a2_closure/llmprint_a2_closure_20260901_150051_cont1'
    sequence = out / 'llmprint/student_probability_sequence.json'
    result = out / 'llmprint/detector_result.json'
    if not result.exists():
        if not sequence.exists():
            subprocess.run([sys.executable, '-u', '-B', str(P / 'scripts/llmprint_evaluate_probability_sequence.py'),
                            '--model', model, '--model-id', 'WMKD/Passive5-Shared-Bc-Student',
                            '--revision', cfg['base_revision'], '--fingerprint-dir', str(root),
                            '--fingerprint-manifest', str(root / 'fingerprint_manifest.json'),
                            '--output', str(sequence), '--dtype', 'float16'], check=True)
        raw = json.loads(sequence.read_text())
        ref = json.loads((root / 'sequences/reference.json').read_text())
        assert raw['status'] == 'COMPLETED' and raw['record_count'] == len(raw['records']) == len(ref['records']) == 200
        assert [r['pair_id'] for r in raw['records']] == [r['pair_id'] for r in ref['records']]
        correct = sum(a['paper_bit'] == b['paper_bit'] for a, b in zip(raw['records'], ref['records']))
        threshold = 0.7150049776126003
        save(result, {'method': 'LLMPrint', 'experiment': 'Bc', 'status': 'COMPLETED',
                      'correct_bits': correct, 'valid_count': 200, 'score': correct / 200,
                      'threshold': threshold, 'positive': correct / 200 >= threshold,
                      'positive_rule': 'score >= threshold', 'calibration_reused': True, 'errors': []})
    for method in ('reef', 'huref', 'awm', 'zeroprint'):
        result = out / method / 'detector_result.json'
        if not result.exists():
            # Reuse the original evaluator functions without changing formulas,
            # assets, thresholds, precision or probe serialization.
            subprocess.run([sys.executable, '-u', '-B', __file__, '--one', method, model], check=True)
    results = {m: json.loads((out / m / 'detector_result.json').read_text())
               for m in ('llmprint', 'reef', 'huref', 'awm', 'zeroprint')}
    assert all(v['status'] == 'COMPLETED' and not v.get('errors') for v in results.values())
    save(Q / 'detector_results.json', {'status': 'COMPLETE', 'same_student_for_all_five': True,
                                      'native_results': results, 'fresh_process_reload': True})

if __name__ == '__main__':
    if sys.argv[1] == '--one':
        import passive5_ba_method_eval as native
        cfg = json.loads((Q / 'protocol.json').read_text())
        args = SimpleNamespace(project=P, student=Path(sys.argv[3]), output=Q / 'native_detector',
                               parent_run_id=cfg['run_id'], run_id=cfg['run_id'], experiment='Bc')
        getattr(native, sys.argv[2])(args)
    else:
        main(sys.argv[1])
