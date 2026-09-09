"""Launch one authorized fresh XBb endpoint run after recorded preflight gates."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

P = Path('/root/autodl-tmp/WMKD_Benchmark')
D = Path(str(P) + '_data')
E = P / 'results/active_cross_lineage_bb'
ORDER = ['pnfp', 'evertracer', 'ctcc', 'iseal', 'scw']


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def save(path, value):
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(value, indent=2) + '\n')
    temp.replace(path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('method', choices=ORDER)
    args = parser.parse_args()
    method = args.method
    q = E / method
    assert (E / 'user_body_authorization_20260909.txt').is_file()
    state = json.loads((E / 'pipeline_state.json').read_text())
    for prior in ORDER[:ORDER.index(method)]:
        assert state['methods'][prior]['status'] in ('COMPLETE', 'TERMINAL_BLOCKED'), prior
    assert not (q / 'training_launch.json').exists(), 'Inspect previous launch; never replay automatically'
    for m in ORDER:
        check = json.loads((E / m / 'qwen_dataset_preflight.json').read_text())
        assert check['status'] == 'PASS' and not check['failures']
    assert json.loads((E / 'base_offline_reload_preflight.json').read_text())['status'] == 'PASS'
    assert json.loads((E / 'environment_validation.json').read_text())['status'] == 'PASS'
    assert json.loads((E / 'asset_transfer_receipt.json').read_text())['status'] == 'PASS'
    protocol = json.loads((q / 'protocol.json').read_text())
    training = protocol['training']
    assert (training['epochs'], training['micro_batch'], training['gradient_accumulation'], training['learning_rate'], training['seed']) == (3, 8, 1, 1e-5, 42)
    assert training['supervision'] == 'paraphrased_answer' and training['full_parameter']
    gpu = subprocess.check_output(['nvidia-smi', '--query-gpu=memory.used,utilization.gpu', '--format=csv,noheader,nounits'], text=True).strip()
    used, util = map(int, gpu.split(','))
    assert used < 100 and util <= 5, gpu
    assert not subprocess.check_output(['nvidia-smi', '--query-compute-apps=pid', '--format=csv,noheader'], text=True).strip()
    import shutil
    assert shutil.disk_usage(D).free > 10 * 1024**3
    run_id = method + ('_xbb2_' if method == 'ctcc' else '_xbb_') + '20260909'
    out = D / 'runs/active_cross_lineage_bb' / run_id
    assert not out.exists(), 'Fresh output required'
    base = D / 'models/paraphrasers/Qwen2.5-3B-Instruct'
    cmd = [str(D / 'envs/xbb/bin/python'), '-u', '-B', str(P / 'scripts/train_active_cross_lineage_bb_endpoint.py'), '--model-path', str(base), '--dataset', protocol['dataset']['source_path'], '--output-dir', str(out), '--batch-size', '8', '--epochs', '3', '--learning-rate', '1e-5', '--seed', '42', '--max-length', '1024', '--telemetry', str(q / 'training_summary.json')]
    launch = dict(method=method, run_id=run_id, command=cmd, output_dir=str(out), launched_at=now(), gpu_before=gpu, source_git_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=P, text=True).strip(), runner_sha256=hashlib.sha256((P / 'scripts/train_active_cross_lineage_bb_endpoint.py').read_bytes()).hexdigest(), base_revision=protocol['revision'], dataset_sha256=protocol['dataset']['sha256'], target_field='paraphrased_answer', initialization='fresh_clean_Qwen_no_resume')
    full = dict(project='WMKD_Benchmark', campaign='ACTIVE_CROSS_LINEAGE_BB', method=method, experiment=protocol['experiment'], run_id=run_id, status='RUNNING', training_status='STARTING', detector_status='NOT_RUN', utility_status='NOT_RUN', archive_status='NOT_STARTED', preferred_final_model_user_approved=True, protocol=protocol, launch=launch)
    save(q / 'full_experiment_log.json', full)
    save(q / 'training_launch.json', launch)
    wrapper = '''import pathlib,json,subprocess,fcntl,datetime,os
p=pathlib.Path(__file__).parent;e=p.parent
def save(path,d):
 t=path.with_suffix(path.suffix+'.tmp');t.write_text(json.dumps(d,indent=2)+'\\n');t.replace(path)
lock=(e/'gpu_serial.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
r=json.loads((p/'training_launch.json').read_text())
with (p/'training.log').open('a') as log:
 child=subprocess.Popen(r['command'],stdout=log,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL)
 r['worker_pid']=child.pid;r['supervisor_pid']=os.getpid();save(p/'training_launch.json',r)
 rc=child.wait()
exit_record={'returncode':rc,'ended_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'worker_pid':child.pid}
save(p/'training_exit.json',exit_record)
full=json.loads((p/'full_experiment_log.json').read_text());full['training_exit']=exit_record
full['training_status']='TRAINING_COMPLETE' if rc==0 else 'INTERRUPTED_REVIEW_REQUIRED'
full['status']='AWAITING_FRESH_RELOAD_AND_EVALUATION' if rc==0 else 'BLOCKED_ENGINEERING'
save(p/'full_experiment_log.json',full)
s=json.loads((e/'pipeline_state.json').read_text());s['methods'][r['method']].update(status=full['status'],training_status=full['training_status']);save(e/'pipeline_state.json',s)
'''
    (q / 'training_supervisor.py').write_text(wrapper)
    env = os.environ.copy()
    env.update(HF_HUB_OFFLINE='1', HF_DATASETS_OFFLINE='1', TRANSFORMERS_OFFLINE='1')
    with (q / 'supervisor.log').open('a') as log:
        worker = subprocess.Popen([sys.executable, '-u', '-B', str(q / 'training_supervisor.py')], cwd=P, stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, start_new_session=True, env=env)
    state['methods'][method].update(status='RUNNING', training_started=True, run_id=run_id, supervisor_pid=worker.pid)
    state.update(status='RUNNING', current_stage='TRAINING', current_method=method, updated_at=now())
    save(E / 'pipeline_state.json', state)
    print(json.dumps(dict(method=method, run_id=run_id, supervisor_pid=worker.pid, output_dir=str(out))))


if __name__ == '__main__':
    main()
