"""Metadata-only closure of the observed UTF A4 Case C; never launches science."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

P = Path(__file__).resolve().parents[2]
O = P / 'results/methods_11_15/utf/experiment_a4'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write(path, value):
    path.write_bytes((json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    training = read(O / 'training_result.json')
    detector = read(O / 'detector_results.json')
    config = read(O / 'training_config.json')
    metrics = [json.loads(line) for line in (O / 'training_metrics.jsonl').read_text().splitlines()]
    assert training['optimizer_steps'] == 6 and training['sample_exposures'] == 96
    assert detector['positive_successes'] == 0 and detector['negative_probes'] == 0
    assert detector['early_stop_branch'] == 'C_POSITIVE_LOST'
    assert sha(O / 'teacher_raw_generations.jsonl') == detector['raw_sha256']
    assert sha(O / 'training_config.json') == training['config_sha256']
    now = datetime.now(timezone.utc).isoformat()
    utility = dict(status='NOT_RUN', reason='Case C: positive fingerprint not detected',
                   arc=None, delta_arc=None, truthfulqa_mc2=None, delta_mc2=None)
    write(O / 'utility_status.json', utility)
    comparison = {
        'A2': dict(epochs=30, grad_accum=1, exposures=960, optimizer_calls=960,
                   positive='1/1', negative='500/500', global_target_collapse='YES'),
        'A3': dict(epochs=30, grad_accum=16, exposures=960, optimizer_calls=60,
                   positive='1/1', negative='500/500', global_target_collapse='YES'),
        'A4': dict(epochs=3, grad_accum=16, exposures=96, optimizer_calls=6,
                   positive='0/1', negative='NOT_RUN', global_target_collapse='NOT_EVALUATED'),
        'interpretation': 'Accumulation restoration alone did not prevent A3 collapse. A4 short budget did not learn a detectable positive under the frozen verifier; unmeasured negatives cannot establish recovered specificity or absence of collapse. Epoch reduction also necessarily reduces update count and attained LR under the unchanged scheduler; these are not independently isolated.'}
    write(O / 'a2_a3_a4_comparison.json', comparison)
    artifacts = {str(p.relative_to(P)).replace('\\', '/'): {'bytes': p.stat().st_size, 'sha256': sha(p)}
                 for p in sorted(O.iterdir()) if p.is_file() and p.name not in
                 {'full_experiment_log.json', 'evidence_sha_manifest.json'}}
    write(O / 'evidence_sha_manifest.json', artifacts)
    log = dict(schema_version='wmkd.methods-11-15.full-log.v1', method='UTF', experiment='A4',
               run_id='utf_a4_20260907_3ep', scientific_object_id='utf:A4:utf_a4_20260907_3ep',
               closed_at=now, scientific_status='COMPLETED_NOT_PREFERRED',
               final_scientific_status='COMPLETED_NOT_PREFERRED', engineering_status='COMPLETE',
               detector_status='POSITIVE_NOT_DETECTED', scientific_interpretation='INSUFFICIENT_FINGERPRINT_LEARNING',
               preferred_teacher=False, benchmark_teacher_eligible=False,
               model=config['model'], revision=config['revision'], canonical_backbone=True,
               source_git_commit='69b55b54a0cc70c803a14636e656a88d152be25b',
               source_worktree_note='A4 runner/config added to this base commit; exact runner SHA recorded in environment and closure Git commit retains source.',
               official_source=dict(repo='https://github.com/imjccai/fingerprint', commit=config['official_commit']),
               scientific_change='epochs 30 -> 3 only; other A3 scientific settings frozen',
               paper_epochs=30, pinned_runtime_json_epochs=3, selected_epochs=3,
               selection_basis=config['SELECTION_BASIS'], training_configuration=config,
               provenance=read(O / 'protocol_provenance.json'),
               target_token_ids=[45146, 99326, 114178, 98100, 117159],
               preflight=read(O / 'preflight_result.json'), training=training,
               actual_lr_sequence=[m['learning_rate'] for m in metrics],
               max_training_lr=max(m['learning_rate'] for m in metrics), configured_max_lr_reached=False,
               tail_accumulation='No tail: 32 records / 16 accumulation = 2 calls per epoch; 3 epochs = 6 calls.',
               detector=detector, negative_detector_status='NOT_RUN', global_target_collapse='NOT_EVALUATED',
               base_detector_status='NOT_RUN', utility_status='NOT_RUN', utility=utility,
               early_stop_branch='C_POSITIVE_LOST', comparison=comparison,
               archive=dict(status='NOT_STARTED', upload_forbidden=True, reason='preferred_teacher=false',
                            local_model_retained=True, local_model=read(O / 'model_artifact_manifest.json')),
               evidence=artifacts, formal_report='docs/reproduction_reports/utf_a4_final_report_20260907.md',
               next_action='STOP; await explicit user scientific decision; no A5 or other method')
    write(O / 'full_experiment_log.json', log)
    index_path = P / 'results/experiment_full_logs_index.json'
    index = read(index_path)
    log_path = str((O / 'full_experiment_log.json').relative_to(P)).replace('\\', '/')
    index['objects'] = [x for x in index['objects'] if x['full_log_path'] != log_path]
    index['objects'].append(dict(method='UTF', role='non_preferred_reproduction', experiment='A4',
                                run_id=log['run_id'], full_log_path=log_path,
                                full_log_sha256=sha(O / 'full_experiment_log.json'),
                                scientific_status=log['scientific_status'], preferred_teacher=False,
                                modelscope_repo=None, watermark_evaluation_available=True, utility_available=False))
    index['object_count'] = len(index['objects']); index['generated_at'] = now
    assert len({x['full_log_path'] for x in index['objects']}) == index['object_count']
    for x in index['objects']:
        assert sha(P / x['full_log_path']) == x['full_log_sha256'], x['full_log_path']
    write(index_path, index)
    state_path = P / 'results/methods_11_15_pipeline_state.json'
    state = read(state_path)
    state.setdefault('historical_experiment_states', {})['UTF_A3'] = state['methods']['utf'] if state['methods']['utf'].get('experiment') == 'A3' else state.get('historical_experiment_states', {}).get('UTF_A3')
    current = dict(method='UTF', experiment='A4', run_id=log['run_id'], stage='CLOSED_STOPPED',
                   status=log['scientific_status'], scientific_status=log['scientific_status'],
                   engineering_status='COMPLETE', detector_status='POSITIVE_NOT_DETECTED',
                   preferred_teacher=False, benchmark_teacher_eligible=False, archive='NOT_STARTED',
                   active_worker=None, teacher_positive=0, positive_probes=1, teacher_negative=None,
                   negative_probes=0, base_detector='NOT_RUN', utility='NOT_RUN',
                   formal_report=log['formal_report'], full_experiment_log=log_path)
    state['methods']['utf'] = current
    state.update(current_experiment_state=current, current_experiment='A4', execution_scope='utf_a4_only_closed',
                 pipeline_mode='STRICT_SERIAL_INTERACTIVE', status='STOPPED_AFTER_A4', pipeline_status='STOPPED_AFTER_A4',
                 PIPELINE_STATUS='STOPPED_AFTER_A4', stage='A4_CLOSED_CASE_C_POSITIVE_LOST',
                 auto_advance=False, auto_shutdown=False, resume_allowed=False, resume_requested=False,
                 active_worker=None, last_update=now,
                 resume_authorization='A4 user authorization fulfilled; new science requires new explicit user decision',
                 remote_execution_status='FINAL_CHECK_NO_PROJECT_PROCESS_GPU_IDLE')
    for key in ['orchestrator_enabled', 'guardian_enabled', 'watchdog_enabled', 'automatic_continuation_enabled']:
        state[key] = False
    write(state_path, state)
    print('A4 metadata closure; index', index['object_count'], 'unique; 0 SHA mismatch')


if __name__ == '__main__':
    main()
