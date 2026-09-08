"""Engineering continuation from verified SCW step 50; never restarts from Base.

Original fetch journal and checkpoint evidence remain intact. Eight original
lookahead fetches were not consumed; the logical journal joins 400 consumed
records with the resumed stream, retaining the original journal separately.
"""
import json
import os
import time
import random
from pathlib import Path
import numpy as np
import torch
import active_ba_trajectory_runner as b

C = b.R / 'training/checkpoint-50'
CE = b.E / 'continuation_cont1'


class Dataset(b.SFTDataset):
    def __init__(self, *args):
        super().__init__(*args)
        self.fetches = 400
        self.order = (CE / 'sample_fetch_order.jsonl').open('x')
        self.expected = b.read(b.E / 'continuation_cpu_audit.json')['resumed_row_indices']

    def __getitem__(self, index):
        offset = self.fetches - 400
        if offset < len(self.expected):
            assert int(index) == self.expected[offset], 'Restored sampler order mismatch'
        self.order.write(json.dumps({'fetch': self.fetches, 'row_index': int(index)}) + '\n')
        self.fetches += 1
        return super().__getitem__(index)

    def flush(self):
        self.order.flush()
        os.fsync(self.order.fileno())


class Callback(b.Trajectory):
    def on_train_begin(self, args, state, control, **kwargs):
        assert state.global_step == 50 and state.max_steps == 7500
        assert args.ignore_data_skip is False
        assert self.trainer.lr_scheduler.last_epoch == 50
        values = {int(v['step']) for v in self.trainer.optimizer.state.values() if 'step' in v}
        assert values == {50}
        self.status('CONTINUATION_STATE_LOADED', optimizer_step=50)

    def on_step_begin(self, args, state, control, **kwargs):
        if state.global_step == 50:
            saved = torch.load(C / 'rng_state.pth', map_location='cpu', weights_only=False)
            assert random.getstate() == saved['python']
            actual = np.random.get_state(); expected = saved['numpy']
            assert actual[0] == expected[0] and np.array_equal(actual[1], expected[1])
            assert actual[2:] == expected[2:]
            assert torch.equal(torch.get_rng_state(), saved['cpu'])
            cuda = saved['cuda']
            if isinstance(cuda, (list, tuple)):
                assert all(torch.equal(x.cpu(), y.cpu()) for x, y in zip(torch.cuda.get_rng_state_all(), cuda))
            else:
                assert torch.equal(torch.cuda.get_rng_state().cpu(), cuda.cpu())
            assert self.trainer.train_dataset.fetches >= 408
            b.put(CE / 'before_first_update_gate.json', dict(status='PASS', global_step=50,
                rng_exact=True, optimizer_scheduler_restored=True, sampler_prefix_exact=True,
                original_unconsumed_lookahead=8, no_update_before_gate=True))
        return super().on_step_begin(args, state, control, **kwargs)


def main():
    assert b.SPEC['method_key'] == 'scw'
    CE.mkdir(exist_ok=True)
    with (CE / 'launch_guard.json').open('x') as f:
        json.dump({'pid': os.getpid(), 'time': b.now(), 'resume_from': str(C)}, f)
    b.ASSETS = b.read(b.E / 'verified_asset_source.json')
    b.PROTOCOL = b.read(b.E / 'protocol.json')
    b.HEAD = b.subprocess.check_output(['git', '-C', str(b.P), 'rev-parse', 'HEAD'], text=True).strip()
    assert b.read(b.E / 'continuation_cpu_audit.json')['status'] == 'PASS_CPU_SAMPLER_CHECKPOINT_STATE'
    for item in b.read(b.E / 'checkpoints/step_000050/checkpoint_file_manifest.json'):
        assert b.sha(C / item['path']) == item['sha256']
    for rel, sha in b.SPEC['source_sha256'].items():
        assert b.sha(b.P / rel) == sha
    for item in b.ASSETS['base_files'] + b.ASSETS.get('extra_verified_files', []) + [b.PROTOCOL['dataset'], b.ASSETS['detector_keys']]:
        assert b.sha(item['path']) == item['sha256']
    gpu = b.subprocess.check_output(['nvidia-smi', '--query-gpu=utilization.gpu,memory.used', '--format=csv,noheader,nounits'], text=True)
    assert [int(x) for x in gpu.strip().split(',')] == [0, 0]
    assert not b.subprocess.check_output(['nvidia-smi', '--query-compute-apps=pid', '--format=csv,noheader'], text=True).strip()
    original = b.read(b.E / 'training_config_snapshot.json')['training_arguments']
    b.set_seed(42)
    tok = b.AutoTokenizer.from_pretrained(b.BASE, local_files_only=True)
    tok.pad_token = tok.pad_token or tok.eos_token
    model = b.AutoModelForCausalLM.from_pretrained(C, local_files_only=True, torch_dtype=torch.bfloat16)
    model.config.use_cache = False
    model.gradient_checkpointing_enable()
    dataset = Dataset(b.PROTOCOL['dataset']['path'], tok, 1024)
    args = b.TrainingArguments(output_dir=str(b.R / 'training'), num_train_epochs=3, learning_rate=1e-5,
        per_device_train_batch_size=8, gradient_accumulation_steps=1, bf16=True, fp16=False,
        save_strategy='no', save_total_limit=None, logging_steps=10, report_to=[], seed=42, data_seed=42,
        remove_unused_columns=False, gradient_checkpointing=True, optim='adamw_torch',
        lr_scheduler_type='cosine', warmup_ratio=0.03, weight_decay=0.0, max_steps=-1)
    assert args.to_dict() == original, 'TrainingArguments changed'
    cb = Callback()
    cb.points = b.read(b.E / 'trajectory.json')
    assert [p['step'] for p in cb.points] == [0, 25, 50]
    cb.inventory = b.read(b.E / 'checkpoint_inventory.json')
    cb.last_checkpoint = C
    logs = [json.loads(x) for x in (b.E / 'training_log.jsonl').read_text().splitlines()]
    cb.compute_seconds = logs[-1]['elapsed_training_seconds']
    cb.last_loss = dict(logs[-1], loss_observed_step=50)
    from datetime import datetime, timezone
    age = (datetime.now(timezone.utc) - datetime.fromisoformat(b.read(b.E / 'launch_record.json')['time'])).total_seconds()
    cb.wall = time.monotonic() - age
    trainer = b.Trainer(model=model, args=args, train_dataset=dataset, data_collator=b.Collator(tok), processing_class=tok, callbacks=[cb])
    cb.trainer = trainer
    b.put(CE / 'provenance.json', dict(status='CONTINUATION', source_script_sha256=b.sha(Path(__file__)),
        checkpoint=str(C), restored_global_step=50, original_run_id=b.RUN, scientific_configuration_unchanged=True,
        original_in_memory_continuity_interrupted=True, training_continuity_basis='Verified checkpoint plus Trainer restore and before-first-update gate',
        original_fetch_journal='sample_fetch_order.jsonl', consumed_prefix_records=400, unconsumed_lookahead_records=8))
    try:
        result = trainer.train(resume_from_checkpoint=str(C))
        dataset.flush()
        assert trainer.state.global_step == 7500 and dataset.fetches == 60000
        assert [p['step'] for p in cb.points] == b.STEPS
        old = [json.loads(x) for x in (b.E / 'sample_fetch_order.jsonl').read_text().splitlines()]
        new = [json.loads(x) for x in (CE / 'sample_fetch_order.jsonl').read_text().splitlines()]
        merged = old[:400] + new
        assert [x['fetch'] for x in merged] == list(range(60000))
        for epoch in range(3):
            assert sorted(x['row_index'] for x in merged[epoch*20000:(epoch+1)*20000]) == list(range(20000))
        merged_path = b.E / 'sample_fetch_order_continuation_logical.jsonl'
        b.put(merged_path, ''.join(json.dumps(x)+'\n' for x in merged))
        final = cb.last_checkpoint
        cb.status('FINAL_FRESH_RELOAD_DETECTOR', optimizer_step=7500)
        raw = b.detector(final, b.E / 'final_fresh_reload')
        assert raw['comparison_payload'] == b.read(b.E / 'checkpoints/step_007500/detector_comparison_payload.json')
        b.sanity(final)
        b.put(b.E / 'training_summary.json', dict(status='COMPLETE', global_step=7500, epochs=3,
            training_metrics=result.metrics, elapsed_training_seconds=cb.compute_seconds, wall_seconds=time.monotonic()-cb.wall,
            dataset_fetches=60000, sample_order_file=merged_path.name, sample_order_sha256=b.sha(merged_path),
            original_fetch_journal_preserved=True, original_unconsumed_lookahead=8,
            final_model_path=str(final), final_model_retained=True, fresh_reload_matches=True,
            continuity='VERIFIED_CHECKPOINT_CONTINUATION_CONT1', utility='NOT_RUN_NOT_IN_FROZEN_FOLLOWUP_PROTOCOL'))
        full = b.read(b.E / 'full_experiment_log.json')
        full.update(status='COMPLETE_PENDING_GIT_CLOSURE', training_started=True, checkpoint_measurements=cb.points,
            final_student_detector=raw['native_metrics'], final_model_path=str(final), ended_at=b.now(),
            fresh_reload_matches=True, continuity='VERIFIED_CHECKPOINT_CONTINUATION_CONT1', utility='NOT_RUN_NOT_IN_FROZEN_FOLLOWUP_PROTOCOL')
        b.put(b.E / 'full_experiment_log.json', full)
        b.put(b.E / 'runtime_state.json', dict(status='COMPLETE_PENDING_GIT_CLOSURE', run_id=b.RUN, updated_at=b.now(), optimizer_step=7500, auto_advance=False, auto_shutdown=False))
        b.put(b.E / 'closure_sha_manifest.json', b.manifest(b.E))
    except Exception as exc:
        b.put(CE / 'failure_record.json', dict(error=repr(exc), traceback=b.traceback.format_exc(), time=b.now()))
        b.put(b.E / 'runtime_state.json', dict(status='STOPPED_ON_ERROR', run_id=b.RUN, error=repr(exc), continuation='cont1'))
        raise


if __name__ == '__main__':
    main()
