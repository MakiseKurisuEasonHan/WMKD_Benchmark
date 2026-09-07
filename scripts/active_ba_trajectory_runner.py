#!/usr/bin/env python3
"""Single continuous active-watermark Ba follow-up; permanent evidence, bounded checkpoints.

Training dataset/collator and detector are imported/executed unchanged. Detector
runs in a child process while the Trainer and its optimizer remain resident.
No retry, auto-next, download, upload or shutdown is implemented here.
"""
import csv
import hashlib
import io
import json
import math
import os
import random
import shutil
import subprocess
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainerCallback, TrainingArguments, set_seed
from train_distillation_student import SFTDataset, Collator

P = Path(__file__).resolve().parents[1]
D = Path('/root/autodl-tmp/WMKD_Benchmark_data')
SPEC = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
E = P / SPEC['evidence_relative']
RUN = SPEC['run_id']
R = D / 'runs' / (SPEC['method_key'] + '_ba_trajectory') / RUN
STEPS = SPEC['checkpoint_steps']
BASE = D / 'models/base/Llama-3.2-3B-Instruct'


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(8 * 1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def put(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n'
    temp = path.with_name(path.name + '.tmp')
    with temp.open('w', encoding='utf-8', newline='\n') as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    os.replace(temp, path)
    fd = os.open(str(path.parent), os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def append(path, obj):
    with Path(path).open('a', encoding='utf-8') as f:
        f.write(json.dumps(obj, allow_nan=False) + '\n')
        f.flush()
        os.fsync(f.fileno())


def manifest(root):
    return [{'path': str(p.relative_to(root)), 'bytes': p.stat().st_size, 'sha256': sha(p)}
            for p in sorted(Path(root).rglob('*')) if p.is_file()]


def detector(model_path, target):
    from active_ba_trajectory_detectors import run_detector
    return run_detector(SPEC, model_path, target, P, sys.executable, os.environ.copy())


def rng_digest():
    h = hashlib.sha256()
    h.update(repr(random.getstate()).encode())
    n = np.random.get_state()
    h.update(n[1].tobytes()); h.update(repr((n[0], n[2:])).encode())
    h.update(torch.get_rng_state().numpy().tobytes())
    for s in torch.cuda.get_rng_state_all():
        h.update(s.cpu().numpy().tobytes())
    return h.hexdigest()


class LoggedDataset(SFTDataset):
    """Observe actual Dataset fetch order without replacing the Trainer sampler."""
    def __init__(self, *args):
        super().__init__(*args)
        self.fetches = 0
        self.order = (E / 'sample_fetch_order.jsonl').open('x', encoding='utf-8')

    def __getitem__(self, index):
        self.order.write(json.dumps({'fetch': self.fetches, 'row_index': int(index)}) + '\n')
        self.fetches += 1
        return super().__getitem__(index)

    def flush(self):
        self.order.flush()
        os.fsync(self.order.fileno())


class Trajectory(TrainerCallback):
    def __init__(self):
        self.points = []
        self.inventory = []
        self.compute_seconds = 0.0
        self.wall = time.monotonic()
        self.last_checkpoint = None
        self.last_loss = {}
        self.trainer = None

    def status(self, stage, **extra):
        put(E / 'runtime_state.json', {'run_id': RUN, 'status': 'RUNNING', 'stage': stage,
            'pid': os.getpid(), 'updated_at': now(), 'measured_steps': [p['step'] for p in self.points],
            'auto_advance': False, 'auto_shutdown': False, **extra})

    def on_train_begin(self, args, state, control, **kwargs):
        assert state.global_step == 0 and state.max_steps == 7500
        assert args.dataloader_num_workers == 0 and args.gradient_accumulation_steps == 1
        self.status('STEP_0_DETECTOR')
        self.measure(0, BASE, state, is_base=True)

    def on_step_begin(self, args, state, control, **kwargs):
        self.started = time.monotonic()
        self.status('TRAINING', optimizer_step=state.global_step)

    def on_step_end(self, args, state, control, **kwargs):
        self.compute_seconds += time.monotonic() - self.started
        required = [s for s in STEPS if s < state.global_step]
        assert all(s in [p['step'] for p in self.points] for s in required), 'Skipped required trajectory point'
        if state.global_step in STEPS:
            control.should_save = True
        return control

    def on_log(self, args, state, control, logs=None, **kwargs):
        logs = logs or {}
        for key in ('loss', 'grad_norm', 'learning_rate'):
            if key in logs:
                assert math.isfinite(float(logs[key])), f'Nonfinite {key}'
        if 'loss' in logs:
            self.last_loss = dict(logs, loss_observed_step=state.global_step)
        append(E / 'training_log.jsonl', dict(logs, step=state.global_step, timestamp=now(),
            elapsed_training_seconds=self.compute_seconds, wall_seconds=time.monotonic() - self.wall))

    def on_save(self, args, state, control, **kwargs):
        assert state.global_step in STEPS and state.global_step > 0
        checkpoint = Path(args.output_dir) / f'checkpoint-{state.global_step}'
        self.trainer.processing_class.save_pretrained(checkpoint)
        self.measure(state.global_step, checkpoint, state)

    def measure(self, step, model_path, state, is_base=False):
        self.status('CHECKPOINT_VERIFICATION', optimizer_step=step)
        self.trainer.train_dataset.flush()
        target = E / 'checkpoints' / f'step_{step:06d}'
        target.mkdir(parents=True, exist_ok=True)
        if not is_base:
            for name in ('optimizer.pt', 'scheduler.pt', 'rng_state.pth', 'trainer_state.json', 'config.json'):
                assert (model_path / name).is_file() and (model_path / name).stat().st_size > 0, name
            assert read(model_path / 'trainer_state.json')['global_step'] == step
            # Validate saved continuation objects without attaching them to the active Trainer.
            optimizer = torch.load(model_path / 'optimizer.pt', map_location='cpu', weights_only=True)
            assert optimizer['state'] and optimizer['param_groups']
            optimizer_steps = {int(v['step']) for v in optimizer['state'].values() if 'step' in v}
            assert optimizer_steps == {step}, optimizer_steps
            del optimizer
            scheduler = torch.load(model_path / 'scheduler.pt', map_location='cpu', weights_only=True)
            assert scheduler['last_epoch'] == step
            rng = torch.load(model_path / 'rng_state.pth', map_location='cpu', weights_only=False)
            assert {'python', 'numpy', 'cpu'}.issubset(rng)
            del rng
        files = manifest(model_path)
        put(target / 'checkpoint_file_manifest.json', files)
        before = rng_digest()
        optimizer_id, scheduler_id = id(self.trainer.optimizer), id(self.trainer.lr_scheduler)
        self.status('DETECTOR', optimizer_step=step)
        raw = detector(model_path, target)
        assert rng_digest() == before, 'Detector altered parent RNG'
        assert (id(self.trainer.optimizer), id(self.trainer.lr_scheduler)) == (optimizer_id, scheduler_id)
        point = {'method': SPEC['method'], 'experiment': 'Ba checkpoint trajectory follow-up', 'run_id': RUN,
            'step': step, 'epoch': state.epoch or 0.0, 'timestamp': now(),
            'elapsed_seconds': self.compute_seconds if step else 0.0,
            'wall_seconds': time.monotonic() - self.wall,
            **raw['native_metrics'], 'detector_decision': raw['detector_decision'],
            'invalid_samples': 0, 'detector_errors': 0,
            'train_loss': self.last_loss.get('loss'), 'loss_observed_step': self.last_loss.get('loss_observed_step'),
            'learning_rate': self.trainer.optimizer.param_groups[0]['lr'],
            'gradient_norm': self.last_loss.get('grad_norm'),
            'checkpoint_manifest_sha256': sha(target / 'checkpoint_file_manifest.json'),
            'dataset_sha256': PROTOCOL['dataset']['sha256'],
            'detector_asset_sha256': ASSETS['detector_keys']['sha256'],
            'detector_script_sha256': SPEC['detector_source_sha256'],
            'tokenizer_template_manifest_sha256': sha(E / 'tokenizer_template_identity.json'),
            'seed': 42, 'config_sha256': sha(E / 'training_config_snapshot.json'), 'git_head': HEAD,
            'interpretation': raw['interpretation'],
            'rng_unchanged_after_detector': True, 'continuous_in_memory_optimizer_scheduler': True}
        put(target / 'detector_result.json', point)
        put(target / 'checkpoint_metadata.json', dict(point, model_path=str(model_path),
            saved_continuation_state_validated=not is_base,
            parent_rng_sha256=before, checkpoint_loadable_in_fresh_process=True,
            dataset_fetches=self.trainer.train_dataset.fetches,
            sampler_note='Actual fetch order includes any dataloader lookahead; optimizer consumption is continuous'))
        self.points.append(point)
        self.persist_trajectory()
        # Read back permanent evidence and commit its SHA inventory before any large-file cleanup.
        for file in target.glob('*.json'):
            assert file.stat().st_size > 0
            read(file)
        put(target / 'evidence_sha_manifest.json', manifest(target))
        for item in read(target / 'evidence_sha_manifest.json'):
            assert sha(target / item['path']) == item['sha256']
        if not is_base:
            self.inventory.append({'step': step, 'path': str(model_path), 'retained': True,
                'evidence_manifest_sha256': sha(target / 'evidence_sha_manifest.json')})
            # Retain the newest complete resumable checkpoint. The older one is no longer needed.
            if self.last_checkpoint is not None:
                old = self.last_checkpoint.resolve()
                assert old.parent == (R / 'training').resolve()
                assert old.name.startswith('checkpoint-') and old != model_path.resolve()
                assert int(old.name.split('-')[1]) < step
                released = sum(p.stat().st_size for p in old.rglob('*') if p.is_file())
                shutil.rmtree(old)
                for entry in self.inventory:
                    if entry['path'] == str(old):
                        entry.update(retained=False, deleted_at=now(), released_logical_bytes=released,
                            reason='Newer resumable checkpoint and permanent detector evidence verified')
            self.last_checkpoint = model_path
        put(E / 'checkpoint_inventory.json', self.inventory)
        print(json.dumps({'event': 'TRAJECTORY_POINT_COMPLETE', **point}), flush=True)

    def persist_trajectory(self):
        assert [p['step'] for p in self.points] == STEPS[:len(self.points)]
        put(E / 'trajectory.json', self.points)
        fields = ['step', 'train_loss', 'elapsed_seconds', 'epoch', 'learning_rate', 'gradient_norm',
                  'loss_observed_step', 'wall_seconds', 'detector_decision', *SPEC['native_metric_fields']]
        buf = io.StringIO(newline='')
        writer = csv.DictWriter(buf, fieldnames=fields, extrasaction='ignore', lineterminator='\n')
        writer.writeheader(); writer.writerows(self.points)
        put(E / 'trajectory.csv', buf.getvalue()); put(E / 'plotting_ready.csv', buf.getvalue())
        parsed = list(csv.DictReader((E / 'trajectory.csv').open()))
        assert [int(x['step']) for x in parsed] == [x['step'] for x in self.points]
        assert len(parsed) == len(self.points)
        put(E / 'trajectory_summary.json', {'run_id': RUN, 'required_steps': STEPS,
            'measured_steps': [p['step'] for p in self.points], 'complete': len(self.points) == len(STEPS),
            'historical_reference_only': SPEC['historical_reference_only'],
            'scientific_pattern': 'PENDING_POST_RUN_ANALYSIS'})


def sanity(model_path):
    # This child runs only after formal training has finished.
    code = '''import json,sys,torch
from transformers import AutoTokenizer,AutoModelForCausalLM
t=AutoTokenizer.from_pretrained(sys.argv[1],local_files_only=True)
m=AutoModelForCausalLM.from_pretrained(sys.argv[1],local_files_only=True,torch_dtype=torch.bfloat16).cuda().eval()
out=[]
for prompt in ['What is the capital of France?', 'Explain why plants need sunlight in one sentence.']:
    x=t.apply_chat_template([{'role':'user','content':prompt}],add_generation_prompt=True,return_tensors='pt').cuda()
    with torch.inference_mode(): y=m.generate(x,max_new_tokens=64,do_sample=False,pad_token_id=t.eos_token_id)
    out.append({'prompt':prompt,'generated_text':t.decode(y[0,x.shape[1]:],skip_special_tokens=True),'generated_ids':y[0,x.shape[1]:].tolist()})
with open(sys.argv[2],'w') as f: json.dump(out,f,indent=2)
'''
    with (E / 'generation_sanity_stdout.log').open('w') as log:
        subprocess.run([sys.executable, '-B', '-c', code, str(model_path), str(E / 'generation_sanity.json')],
                       stdout=log, stderr=subprocess.STDOUT, check=True)
    rows = read(E / 'generation_sanity.json')
    assert all(x['generated_ids'] and x['generated_text'].strip() for x in rows)
    put(E / 'generation_sanity.json', rows)


def main():
    global ASSETS, PROTOCOL, HEAD
    E.mkdir(parents=True, exist_ok=True); R.mkdir(parents=True, exist_ok=True)
    # Exclusive launch guard: never start over an already attempted trajectory.
    with (R / 'launch_guard.json').open('x') as f:
        json.dump({'pid': os.getpid(), 'started_at': now(), 'run_id': RUN}, f)
    ASSETS = read(E / 'verified_asset_source.json')
    PROTOCOL = read(E / 'protocol.json')
    HEAD = subprocess.check_output(['git', '-C', str(P), 'rev-parse', 'HEAD'], text=True).strip()
    assert PROTOCOL['checkpoint_steps'] == STEPS
    expected_training = dict(seed=42, epochs=3, micro_batch=8, gradient_accumulation_steps=1,
        learning_rate=1e-5, max_length=1024, precision='bf16', full_parameter=True,
        optimizer='adamw_torch', scheduler='cosine', warmup_ratio=0.03,
        weight_decay=0.0, total_steps=7500)
    assert SPEC['training'] == expected_training, 'Historical training settings require explicit implementation audit'
    for relative, expected in SPEC['source_sha256'].items():
        assert sha(P / relative) == expected, relative
    for record in ASSETS['base_files'] + ASSETS.get('extra_verified_files', []) + [PROTOCOL['dataset'], ASSETS['detector_keys']]:
        assert sha(record['path']) == record.get('sha256'), record['path']
    put(E / 'identity_reverified_at_launch.json', {'time': now(), 'base_files': ASSETS['base_files'],
        'dataset': PROTOCOL['dataset'], 'detector': ASSETS['detector_keys'], 'extra_verified_files': ASSETS.get('extra_verified_files', []), 'all_sha_match': True})
    gpu = subprocess.check_output(['nvidia-smi', '--query-gpu=utilization.gpu,memory.used', '--format=csv,noheader,nounits'], text=True)
    values = [int(x.strip()) for x in gpu.strip().split(',')]
    processes = subprocess.check_output(['nvidia-smi', '--query-compute-apps=pid', '--format=csv,noheader'], text=True).strip()
    put(E / 'gpu_before_launch.json', {'time': now(), 'metrics': gpu, 'visible_pids': processes})
    assert len(values) == 2 and values[0] <= 5 and values[1] < 100 and not processes, 'GPU_IDLE_GATE failed'
    set_seed(42)
    tok = AutoTokenizer.from_pretrained(BASE, local_files_only=True)
    tok.pad_token = tok.pad_token or tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(BASE, local_files_only=True, torch_dtype=torch.bfloat16)
    model.config.use_cache = False; model.gradient_checkpointing_enable()
    dataset = LoggedDataset(PROTOCOL['dataset']['path'], tok, 1024)
    assert len(dataset) == 20000
    args = TrainingArguments(output_dir=str(R / 'training'), num_train_epochs=3, learning_rate=1e-5,
        per_device_train_batch_size=8, gradient_accumulation_steps=1, bf16=True, fp16=False,
        save_strategy='no', save_total_limit=None, logging_steps=10, report_to=[], seed=42, data_seed=42,
        remove_unused_columns=False, gradient_checkpointing=True, optim='adamw_torch',
        lr_scheduler_type='cosine', warmup_ratio=0.03, weight_decay=0.0, max_steps=-1)
    put(E / 'training_config_snapshot.json', {'training_arguments': args.to_dict(),
        'source_training_script_sha256': sha(P / 'scripts/train_distillation_student.py'),
        'method': SPEC['method'], 'historical_config': SPEC['historical_config'],
        'trajectory_runner_sha256': sha(Path(__file__)), 'dataset_source_unchanged': True,
        'dataset_records': 20000, 'expected_optimizer_steps': 7500, 'expected_exposures': 60000,
        'trainable_parameters': sum(p.numel() for p in model.parameters() if p.requires_grad),
        'checkpoint_only_engineering_changes': 'save_strategy=no with exact target callback; retain latest resumable state',
        'utility': 'NOT_IN_FROZEN_FOLLOWUP_PROTOCOL; NOT_RUN',
        'continuous_training': 'Parent Trainer remains resident during isolated fresh-process detector; no restart'})
    put(E / 'tokenizer_template_identity.json', {'model': PROTOCOL['base_model'], 'revision': PROTOCOL['base_revision'],
        'chat_template': tok.chat_template, 'serialized_example': tok.apply_chat_template(
            [{'role': 'user', 'content': 'Template identity probe'}], tokenize=False, add_generation_prompt=True),
        'tokenizer_source_shas': [x for x in ASSETS['base_files'] if 'token' in Path(x['path']).name],
        'dynamic_date': 'Native template runtime date unchanged; execution timestamps retained'})
    cb = Trajectory()
    trainer = Trainer(model=model, args=args, train_dataset=dataset, data_collator=Collator(tok),
                      processing_class=tok, callbacks=[cb])
    cb.trainer = trainer
    put(E / 'sampler_identity.json', {'sampler_class': type(trainer._get_train_sampler()).__name__,
        'trainer': type(trainer).__name__, 'seed': 42, 'data_seed': 42, 'dataloader_workers': 0,
        'ordering_evidence': 'sample_fetch_order.jsonl', 'sampler_overridden': False,
        'note': 'Observed Dataset index fetches include potential one-batch lookahead; not a regenerated order'})
    try:
        result = trainer.train()
        dataset.flush()
        assert trainer.state.global_step == 7500 and [x['step'] for x in cb.points] == STEPS
        assert dataset.fetches == 60000, dataset.fetches
        final = cb.last_checkpoint
        assert final is not None and final.name == 'checkpoint-7500'
        cb.status('FINAL_FRESH_RELOAD_DETECTOR', optimizer_step=7500)
        final_raw = detector(final, E / 'final_fresh_reload')
        previous = read(E / 'checkpoints/step_007500/detector_raw.json')
        assert final_raw['comparison_payload'] == read(E / 'checkpoints/step_007500/detector_comparison_payload.json'), 'Final fresh-reload mismatch'
        sanity(final)
        put(E / 'training_summary.json', {'status': 'COMPLETE', 'global_step': 7500, 'epochs': 3,
            'training_metrics': result.metrics, 'elapsed_training_seconds': cb.compute_seconds,
            'wall_seconds': time.monotonic() - cb.wall, 'dataset_fetches': dataset.fetches,
            'sample_order_sha256': sha(E / 'sample_fetch_order.jsonl'),
            'peak_vram_allocated_bytes': torch.cuda.max_memory_allocated(),
            'final_model_path': str(final), 'final_model_retained': True, 'fresh_reload_matches': True,
            'utility': 'NOT_RUN_NOT_IN_FROZEN_FOLLOWUP_PROTOCOL'})
        full = read(E / 'full_experiment_log.json')
        full.update(status='COMPLETE_PENDING_GIT_CLOSURE', training_started=True,
            checkpoint_measurements=cb.points, final_student_detector=final_raw['native_metrics'],
            final_model_path=str(final), ended_at=now(), scientific_pattern='PENDING_POST_RUN_ANALYSIS',
            fresh_reload_matches=True, utility='NOT_RUN_NOT_IN_FROZEN_FOLLOWUP_PROTOCOL')
        put(E / 'full_experiment_log.json', full)
        put(E / 'runtime_state.json', {'status': 'COMPLETE_PENDING_GIT_CLOSURE', 'run_id': RUN,
            'updated_at': now(), 'optimizer_step': 7500, 'auto_advance': False, 'auto_shutdown': False})
        put(E / 'closure_sha_manifest.json', manifest(E))
        for item in read(E / 'closure_sha_manifest.json'):
            assert sha(E / item['path']) == item['sha256']
    except BaseException as exc:
        dataset.flush()
        put(E / 'failure_record.json', {'status': 'STOPPED_ON_ERROR', 'time': now(),
            'error': repr(exc), 'traceback': traceback.format_exc(), 'step': trainer.state.global_step,
            'latest_complete_resumable_checkpoint': str(cb.last_checkpoint),
            'checkpoints_present': [str(x) for x in (R / 'training').glob('checkpoint-*')],
            'no_automatic_retry': True, 'all_evidence_preserved': True})
        put(E / 'runtime_state.json', {'status': 'STOPPED_ON_ERROR', 'run_id': RUN,
            'updated_at': now(), 'optimizer_step': trainer.state.global_step,
            'error': repr(exc), 'auto_advance': False, 'auto_shutdown': False})
        raise


if __name__ == '__main__':
    try:
        main()
    except BaseException as exc:
        if not (E / 'failure_record.json').exists():
            put(E / 'failure_record.json', {'status': 'STOPPED_ON_ERROR', 'time': now(),
                'error': repr(exc), 'traceback': traceback.format_exc(), 'no_automatic_retry': True})
            put(E / 'runtime_state.json', {'status': 'STOPPED_ON_ERROR', 'error': repr(exc),
                'auto_advance': False, 'auto_shutdown': False})
        raise
