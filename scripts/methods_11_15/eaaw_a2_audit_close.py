"""Close the observed EaaW A2 pre-training RED audit; never executes science."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json

P = Path(__file__).resolve().parents[2]
O = P / 'results/methods_11_15/eaaw/experiment_a2'


def read(p):
    return json.loads(p.read_text(encoding='utf-8'))


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def write(p, value):
    p.write_bytes((json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode())


def main():
    now = datetime.now(timezone.utc).isoformat()
    audit = read(O / 'identity_tokenizer_audit.json')
    assert audit['canonical_tokenizer']['unk_token_id'] is None
    assert audit['native_tokenizer']['unk_token_id'] == 50256
    assert audit['identity'] == 'PASS' and not audit['model_loaded']
    native_path = P / 'results/methods_11_15/eaaw/experiment_a/full_experiment_log.json'
    native = read(native_path)
    native_ref = dict(full_log=str(native_path.relative_to(P)).replace('\\', '/'),
                      sha256=sha(native_path), original_scientific_status=native['scientific_status'],
                      classification='NATIVE_REPRODUCTION_EVIDENCE', canonical_benchmark_eligible=False,
                      detector=native['detector']['outputs'], utility=native['utility']['outputs'],
                      original_object_unchanged=True)
    write(O / 'native_reference.json', native_ref)
    blocker = dict(classification='RED scientific', code='BLOCKED_SCIENTIFIC_MASK_TOKEN_MAPPING',
                   evidence='Official LimeNet requires tokenizer.unk_token_id; canonical tokenizer has None. GPT-2 alias is50256; Llama ID50256 is ordinary parable.',
                   user_decision_required=True,
                   decision='Authorize an exact masking baseline with explicit cross-model equivalence limitation, or decline this adaptation.',
                   single_proposal='Consider existing128001 end_of_text as GPT-2 endoftext analogue; UNPROVEN and NOT_IMPLEMENTED.')
    write(O / 'adaptation_gate.json', blocker)
    config = dict(status='UNFROZEN_AUDIT_REFERENCE', executable=False, MODEL=audit['model'], REVISION=audit['revision'],
                  SEED=42, WATERMARK_BITS=128, KEY=None, KEY_STATUS='NOT_CONSTRUCTED',
                  MASK_TOKEN_ID=None, MASK_TOKEN_STATUS='RED_USER_DECISION_REQUIRED',
                  TRAINABLE_SCOPE='full model (released reference)', LR=3e-4, EPOCHS=20,
                  EXPECTED_STEPS_IF_1000_BLOCKS=10000, ACTUAL_STEPS=0, BATCH=2, GRAD_ACCUM=1,
                  OPTIMIZER='SGD, momentum0, weight_decay0', SCHEDULER='linear warmup50 then linear decay',
                  PRECISION='BF16 mixed precision (released reference); A2 NOT_RUN',
                  LOSS='alpha1*causal CE + alpha2*sum relu(epsilon-attribution*payload)',
                  ALPHA1=1.0, ALPHA2=1.0, EPSILON=0.01, ATTRIBUTION_RIDGE_LAMBDA=0.001,
                  TRAIN_BLOCKS=1000, BLOCK_LENGTH=128, TRIGGER_SIZE=1,
                  TRIGGER_SELECTION='first grouped training block (actual released/native path)',
                  DETECTOR_CONFIG=dict(alpha=0.01, metric='bit accuracy / chi-square independence p-value',
                                       mask_variants=128, mask_unit_tokens=1, wm_bs_argument=4,
                                       wm_bs_actually_used=False, scoring='same-position unshifted target raw logits; no softmax',
                                       controls=['canonical Base', 'wrong-key', 'independent held-out trigger']),
                  source_commit=audit['official_commit'],
                  hyperparameter_sources={
                      'script_gpt2.sh': ['LR', 'EPOCHS', 'BATCH', 'TRAIN_BLOCKS', 'TRIGGER_SIZE', 'ALPHA1', 'ALPHA2', 'PRECISION'],
                      'utils.py defaults': ['SEED', 'GRAD_ACCUM', 'SCHEDULER', 'BLOCK_LENGTH', 'EPSILON', 'ATTRIBUTION_RIDGE_LAMBDA'],
                      'run_clm.py actual path': ['SGD', 'full trainable scope', 'first trigger', 'unk masking'],
                      'historical native run': ['WATERMARK_BITS=128'],
                      'latest user prompt': ['MODEL', 'REVISION', 'canonical utility', 'stop on RED']},
                  discrepancies=dict(paper_optimizer='Adam', released_optimizer='SGD', paper_batch=4,
                                     released_batch=2, paper_score='average target probabilities',
                                     released_score='same-position raw target logits', paper_trigger='random', released_trigger='first block'),
                  primary_config_freeze_allowed=False)
    write(O / 'training_config.json', config)
    detector = dict(status='NOT_RUN', teacher=None, base=None, wrong_key=None, independent_trigger=None,
                    specificity_gate='NOT_EVALUATED', reason=blocker['code'])
    write(O / 'detector_results.json', detector)
    utility = dict(status='NOT_RUN', frozen_base_reference=dict(arc=0.45051194539249145, truthfulqa_mc2=0.5054615624501503),
                   teacher_arc=None, teacher_truthfulqa_mc2=None, delta_arc=None, delta_mc2=None)
    write(O / 'utility_status.json', utility)
    write(O / 'compatibility_patch_status.json', dict(status='NOT_IMPLEMENTED', reason='RED before config freeze', scientific_configuration_modified=False))
    evidence = {str(p.relative_to(P)).replace('\\', '/'): dict(bytes=p.stat().st_size, sha256=sha(p))
                for p in sorted(O.iterdir()) if p.is_file() and p.name not in ['full_experiment_log.json', 'evidence_sha_manifest.json']}
    write(O / 'evidence_sha_manifest.json', evidence)
    log = dict(schema_version='wmkd.methods-11-15.full-log.v1', method='EaaW', experiment='A2',
               run_id='eaaw_a2_20260907_canonical3b', scientific_object_id='eaaw:A2:eaaw_a2_20260907_canonical3b',
               timestamp=now, stage='SCIENTIFIC_CONFIG_AUDIT', scientific_status=blocker['code'],
               audit_status='COMPLETE', engineering_status='NOT_RUN_BEYOND_CPU_AUDIT',
               training_status='NOT_STARTED', preflight_status='NOT_RUN', formal_run_started=False,
               preferred_teacher=False, benchmark_teacher_eligible=False, canonical_adaptation='BLOCKED_PENDING_SCIENTIFIC_DECISION',
               model=audit['model'], revision=audit['revision'], identity=audit,
               source_git_commit='f149f683c3555561ac7fd3038dd1cc4412e6645c',
               official_source=dict(repo='https://github.com/shaoshuo-ss/EaaW', commit=audit['official_commit'],
                                    paper='https://arxiv.org/html/2405.04825v2'),
               native_reference=native_ref, training_config=config, blocker=blocker,
               detector=detector, utility=utility, archive=dict(status='NOT_STARTED', preferred_gate_passed=False),
               local_artifact=dict(model_created=False, model_path=None, model_bytes=0, existing_base_preserved=True),
               evidence=evidence, formal_report='docs/reproduction_reports/eaaw_a2_final_report_20260907.md',
               automatic_continuation=False, auto_shutdown=False, next_action='STOP; explicit user decision required')
    write(O / 'full_experiment_log.json', log)
    ip = P / 'results/experiment_full_logs_index.json'; idx = read(ip)
    fp = str((O / 'full_experiment_log.json').relative_to(P)).replace('\\', '/')
    idx['objects'] = [x for x in idx['objects'] if x['full_log_path'] != fp]
    idx['objects'].append(dict(method='EaaW', role='canonical_adaptation_audit', experiment='A2',
                               run_id=log['run_id'], full_log_path=fp, full_log_sha256=sha(O / 'full_experiment_log.json'),
                               scientific_status=blocker['code'], preferred_teacher=False, modelscope_repo=None,
                               watermark_evaluation_available=False, utility_available=False))
    idx.update(generated_at=now, object_count=len(idx['objects']))
    assert len({x['full_log_path'] for x in idx['objects']}) == idx['object_count']
    for x in idx['objects']: assert sha(P / x['full_log_path']) == x['full_log_sha256'], x['full_log_path']
    write(ip, idx)
    sp = P / 'results/methods_11_15_pipeline_state.json'; state = read(sp)
    if state['methods']['eaaw'].get('experiment') != 'A2':
        state.setdefault('historical_experiment_states', {})['EAAW_NATIVE_A'] = state['methods']['eaaw']
    current = dict(method='EaaW', experiment='A2', run_id=log['run_id'], status=blocker['code'],
                   stage='SCIENTIFIC_CONFIG_AUDIT_STOPPED', scientific_status=blocker['code'],
                   active_worker=None, training='NOT_STARTED', detector='NOT_RUN', utility='NOT_RUN',
                   preferred_teacher=False, benchmark_teacher_eligible=False, archive='NOT_STARTED',
                   blocker=blocker, full_experiment_log=fp, formal_report=log['formal_report'])
    state['methods']['eaaw'] = current
    state.update(current_focus_method='eaaw', current_experiment='A2', current_experiment_state=current,
                 execution_scope='eaaw_a2_only_red_stop', status='WAITING_FOR_USER_SCIENTIFIC_DECISION',
                 pipeline_status='WAITING_FOR_USER_SCIENTIFIC_DECISION', PIPELINE_STATUS='WAITING_FOR_USER_SCIENTIFIC_DECISION',
                 stage='EAAW_A2_AUDIT_RED_STOP', active_worker=None, last_update=now,
                 resume_authorization='User EaaW A2 prompt: stop on unresolved RED; mask baseline decision required',
                 resume_allowed=False, resume_requested=False, auto_advance=False, auto_shutdown=False)
    for k in ['orchestrator_enabled', 'guardian_enabled', 'watchdog_enabled', 'automatic_continuation_enabled']:
        state[k] = False
    write(sp, state)
    assert sha(native_path) == native_ref['sha256']
    print('Audit closure:', idx['object_count'], 'unique full-log paths; zero SHA mismatch; native unchanged')


if __name__ == '__main__':
    main()
