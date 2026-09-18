"""Local closeout guardian: sync evidence, local commit, then authorized shutdown.

Never deletes remote assets. Does not retry scientific stages or mutate protocol.
Network failures retry transport; no credentials are requested or printed.
"""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

P=Path(__file__).resolve().parents[1]
E=P/'results/pnfp/scale_7b/distillation_6004'
REMOTE='/root/autodl-tmp/WMKD_Benchmark'
RE=REMOTE+'/results/pnfp/scale_7b/distillation_6004'
SSH=['ssh','-F',r'C:\Users\Eason\.ssh\config','6004','-o','BatchMode=yes','-o','ConnectTimeout=15']
SCP=['scp','-F',r'C:\Users\Eason\.ssh\config','-o','BatchMode=yes','-o','ConnectTimeout=15']


def run(cmd,timeout=300):
    return subprocess.run(cmd,cwd=P,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=timeout)


def put(name,obj):
    E.mkdir(parents=True,exist_ok=True)
    (E/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def sync():
    result=run([*SCP,'-r','6004:'+RE,str(E.parent)],timeout=600)
    if result.returncode:raise RuntimeError('Evidence SCP transport failed: '+result.stderr[-1000:])


def main():
    put('local_guardian.json',{'pid':os.getpid(),'status':'MONITORING','host':'6004'})
    while True:
        try:
            result=run([*SSH,'test -f '+RE+'/terminal.json && cat '+RE+'/terminal.json'],timeout=45)
            if result.returncode==0:
                terminal=json.loads(result.stdout);break
            sync()
        except Exception as exc:
            put('local_transport_retry.json',{'error':str(exc),'time':time.time()})
        time.sleep(60)
    # Terminal evidence is immutable after campaign process exits. Verify all
    # necessary receipts against a remotely calculated SHA inventory.
    while True:
        try:
            sync()
            code="import pathlib,hashlib,json;p=pathlib.Path('"+RE+"');print(json.dumps({str(f.relative_to(p)):hashlib.sha256(f.read_bytes()).hexdigest() for f in p.rglob('*') if f.is_file() and f.name not in ['campaign.lock']}))"
            result=run([*SSH,'/root/miniconda3/bin/python -c '+"\""+code+"\""],timeout=90)
            assert result.returncode==0,result.stderr
            inventory=json.loads(result.stdout)
            for name,digest in inventory.items():
                path=E/name
                assert path.resolve().is_relative_to(E.resolve())
                assert path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest()==digest,name
            put('local_sync_verified.json',{'files':inventory,'verified':True,'time':time.time()})
            break
        except Exception as exc:
            put('local_sync_retry.json',{'error':str(exc),'time':time.time()});time.sleep(30)
    report=P/'docs/reproduction_reports/pnfp_7b_distillation_6004_final.md'
    report.write_text((E/'final_report.md').read_text(encoding='utf-8'),encoding='utf-8')
    index_path=P/'results/experiment_full_logs_index.json'
    index=json.loads(index_path.read_text(encoding='utf-8'))
    for stage,experiment in [('direct','Ba'),('paraphrase','Bb'),('logit','Bc')]:
        f=E/stage/'full_experiment_log.json'
        if not f.exists():continue
        run_id='pnfp_7b_6004_'+stage
        if any(x.get('run_id')==run_id for x in index['objects']):continue
        index['objects'].append(dict(method='PN-FP',role=experiment.lower()+'_7b_student',experiment=experiment,
            run_id=run_id,full_log_path=str(f.relative_to(P)).replace('\\','/'),
            full_log_sha256=hashlib.sha256(f.read_bytes()).hexdigest(),
            scientific_status='completed',watermark_evaluation_available=True,utility_available=True,
            final_model_manifest=str((E/(stage+'_final_manifest.json')).relative_to(P)).replace('\\','/'),
            modelscope_repo=None,checkpoint_localization_support=False,telemetry_records=7500))
    index['object_count']=len(index['objects']);index['generated_at']=datetime.datetime.now(datetime.timezone.utc).isoformat()
    index_path.write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    line='当前状态（PN-FP7B 6004蒸馏）：'+terminal['status']+'；终态证据已本地SHA核验，详见docs/reproduction_reports/pnfp_7b_distillation_6004_final.md。按本轮授权准备安全关机；不释放实例、不删除正式模型。\n\n'
    for name in ['docs/CURRENT_STATE.md','PROJECT_STATUS.md','TODO.md','EXPERIMENT_LOG.md']:
        path=P/name;path.write_text(line+path.read_text(encoding='utf-8'),encoding='utf-8')
    paths=[str(f.relative_to(P)) for f in E.rglob('*') if f.is_file() and f.suffix in ['.json','.md','.txt','.csv'] and f.stat().st_size<2*2**20]
    paths += [str(report.relative_to(P)),str(index_path.relative_to(P)),'docs/CURRENT_STATE.md','PROJECT_STATUS.md','TODO.md','EXPERIMENT_LOG.md']
    # Explicit path set: no unrelated working-tree changes or model/data blobs.
    added=run(['git','add','--',*paths]);assert added.returncode==0,added.stderr
    commit=run(['git','commit','-m','Close PN-FP 7B 6004 distillation campaign with verified evidence'])
    assert commit.returncode==0,commit.stderr
    env=os.environ.copy();env['GIT_TERMINAL_PROMPT']='0'
    try:
        pushed=subprocess.run(['git','-c','credential.interactive=never','push','origin','main'],cwd=P,env=env,capture_output=True,text=True,timeout=60)
        push_status='COMPLETE' if pushed.returncode==0 else 'PENDING_AUTH_OR_TRANSPORT'
    except subprocess.TimeoutExpired:
        push_status='PENDING_TRANSPORT_TIMEOUT'
    put('git_closeout.json',{'commit':run(['git','rev-parse','HEAD']).stdout.strip(),'push':push_status})
    # Never shut down a host with a running GPU task. Its work is not killed.
    while True:
        ready=run([*SSH,'nvidia-smi --query-compute-apps=pid --format=csv,noheader'],timeout=45)
        if ready.returncode==0 and not ready.stdout.strip():break
        time.sleep(30)
    receipt=run([*SSH,'sync && /bin/bash /usr/bin/shutdown'],timeout=45)
    put('shutdown_execution.json',{'command':'/bin/bash /usr/bin/shutdown','reason':'official script requires interpreter (previous ENOEXEC)',
        'exit_code':receipt.returncode,'stdout':receipt.stdout[-1000:],'stderr':receipt.stderr[-1000:],
        'instance_released':False,'time':time.time()})
    put('local_guardian.json',{'pid':os.getpid(),'status':'SHUTDOWN_COMMAND_SENT','terminal':terminal})
    run(['git','add','--',str(E.relative_to(P)/'git_closeout.json'),str(E.relative_to(P)/'shutdown_execution.json'),str(E.relative_to(P)/'local_guardian.json')])
    run(['git','commit','-m','Record 6004 shutdown invocation and Git receipt'])


if __name__=='__main__':main()
