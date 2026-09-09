"""Serial endpoint evaluation; frozen detector semantics, no training/replay."""
import argparse
import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import traceback

P = Path('/root/autodl-tmp/WMKD_Benchmark')
D = Path(str(P) + '_data')
E = P / 'results/active_cross_lineage_bb'


def read(p):
    return json.loads(p.read_text())


def save(p, value):
    t = p.with_suffix(p.suffix + '.tmp')
    t.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')
    t.replace(p)


def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda: f.read(8 << 20), b''):
            h.update(block)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('method', choices=['pnfp', 'evertracer', 'ctcc', 'iseal', 'scw'])
    m = parser.parse_args().method
    q = E / m
    lock = (E / 'gpu_serial.lock').open('a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    assert read(q / 'training_exit.json')['returncode'] == 0
    training = read(q / 'training_summary.json')
    assert training['steps'] == 7500 and training['finite_loss']
    model = Path(read(q / 'training_launch.json')['output_dir']) / 'final_model'
    assert model.resolve().is_relative_to(D / 'runs/active_cross_lineage_bb')
    env = os.environ.copy()
    env.update(HF_HUB_OFFLINE='1', HF_DATASETS_OFFLINE='1', TRANSFORMERS_OFFLINE='1', PYTHONPATH=str(D/'artifacts/scw/source/src') + os.pathsep + str(P/'scripts'))

    def run(stage, script, args, result):
        receipt = q / (stage + '_exit.json')
        if receipt.exists():
            assert read(receipt)['returncode'] == 0 and result.exists(), 'Prior failure requires explicit engineering review'
            return
        assert not result.exists(), 'Unreceipted result must be audited; do not overwrite'
        save(q/'evaluation_progress.json', dict(stage=stage, pid=os.getpid(), started_at=datetime.datetime.now(datetime.timezone.utc).isoformat()))
        cmd = [sys.executable, '-u', '-B', str(P/'scripts'/script)] + list(map(str, args))
        with (q/(stage+'.log')).open('a') as log:
            child = subprocess.Popen(cmd, cwd=P, env=env, stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
            save(q/'evaluation_progress.json', dict(stage=stage, supervisor_pid=os.getpid(), worker_pid=child.pid, command=cmd))
            rc = child.wait()
        save(receipt, dict(returncode=rc, command=cmd, result=str(result), ended_at=datetime.datetime.now(datetime.timezone.utc).isoformat()))
        assert rc == 0 and result.exists(), stage

    # XBb serial policy: finish utility before the applicable detector.
    # Successful stage receipts make this safe for an already evaluated method.
    run('utility', 'active_cross_lineage_bb_utility_worker.py', [m, model], q/'utility/utility_results.json')

    if m == 'pnfp':
        out = q/'final_detector'
        run('detector', 'active_cross_lineage_pnfp_detector.py', ['--model', model, '--output', out], out/'detector_results.json')
        detector = read(out/'detector_results.json')
        with (out/'raw.jsonl').open() as f:
            rows = [json.loads(line) for line in f if line.strip()]
        assert len(rows) == 1024 and [r['index'] for r in rows] == list(range(1024))
        assert all(r['error'] is None for r in rows)
        assert detector['evaluation_errors'] == detector['invalid_samples'] == 0
        assert detector['detected'] == sum(r['detected'] for r in rows)
    elif m == 'evertracer':
        out = q/'exploratory_detector/detector_results.json'
        run('exploratory_detector', 'evertracer_cross_lineage_bb_exploratory.py', ['--model', model], out)
        detector = read(out)
        assert detector['raw_original_count'] == 200 and detector['raw_perturbation_count'] == 2000
        assert detector['canonical_detector_result'] == 'N/A_CROSS_TOKENIZER'
    elif m == 'ctcc':
        out = q/'final_detector.json'
        run('detector', 'ctcc_ba_evaluate.py', ['--config', P/'configs/distillation/ctcc_ba_direct.yaml', '--student', model, '--training-run', read(q/'training_launch.json')['run_id'], '--output', out], out)
        detector = read(out)
        assert detector['summary']['generation_errors'] == 0 and len(detector['raw_generations']) == 300
        assert [detector['summary']['categories'][k]['count'] for k in ['trigger','suppression','normal']] == [95,100,105]
    elif m == 'scw':
        generations = q/'student_generations.jsonl'
        run('detector_generation', 'scw_fresh_generate.py', ['--model', model, '--label', 'scw_xbb_student', '--output', generations, '--eval-jsonl', D/'evaluation/scw/a2_french_eval/scw_a2_french_eval_1000.jsonl', '--eval-manifest', D/'evaluation/scw/a2_french_eval/manifest.json', '--batch-size', 4], generations)
        out = q/'student_detector_raw.json'
        run('detector', 'scw_detector.py', ['--protocol-config', P/'configs/watermark/scw_experiment_a2.yaml', '--official-config', P/'configs/watermark/scw_experiment_a_official.yaml', '--generations', generations, '--model', D/'models/base/Llama-3.2-3B-Instruct', '--output', out], out)
        detector = read(out)
        assert detector['alpha'] == .001 and detector['primary']['n_queries'] == 1000
    else:
        detector = dict(status='N/A', applicability='LEVEL_3', scientific_interpretation='NOT_APPLICABLE_CROSS_ARCHITECTURE; no projection, registration or detector change')
    save(q/'detector_results.json', detector)
    run('utility', 'active_cross_lineage_bb_utility_worker.py', [m, model], q/'utility/utility_results.json')
    utility = read(q/'utility/utility_results.json')
    raw = read(q/'utility/raw_evaluator_output.json')
    assert utility['status'] == 'COMPLETE'
    assert {k:len(raw['samples'][k]) for k in ['arc_challenge','truthfulqa_mc2']} == {'arc_challenge':1172,'truthfulqa_mc2':817}
    index = read(model/'model.safetensors.index.json')
    assert all((model/f).is_file() for f in set(index['weight_map'].values()))
    provenance = dict(status='FRESH_RELOAD_VERIFIED', model_path=str(model), base_revision='8f4992eda43eea7c770690ddc0de8f732da246f5', initialization='fresh_clean_Qwen_no_resume', evidence='detector and/or utility in separate fresh processes; utility fresh_process_reload=True', files=[dict(name=f.name, bytes=f.stat().st_size, sha256=sha(f)) for f in sorted(model.iterdir()) if f.is_file()])
    assert utility['fresh_process_reload'] is True
    save(q/'model_provenance.json', provenance)
    full = read(q/'full_experiment_log.json')
    full.update(status='SCIENTIFIC_EVALUATION_COMPLETE_AWAITING_CLOSURE', training_status='COMPLETE', detector_status='N/A' if m=='iseal' else 'COMPLETE', utility_status='COMPLETE', training_summary=training, detector_results=detector, utility_results=utility, model_provenance=provenance, archive_status='NOT_STARTED')
    save(q/'full_experiment_log.json', full)
    state = read(E/'pipeline_state.json')
    state['methods'][m].update(status=full['status'], training_status='COMPLETE', utility_status='COMPLETE', detector_status=full['detector_status'])
    state['current_stage'] = 'SCIENTIFIC_CLOSURE_AND_ARCHIVE_PENDING'
    save(E/'pipeline_state.json', state)
    save(q/'evaluation_exit.json', dict(returncode=0, completed_at=datetime.datetime.now(datetime.timezone.utc).isoformat()))


if __name__ == '__main__':
    try:
        main()
    except Exception:
        print(traceback.format_exc(), flush=True)
        raise
