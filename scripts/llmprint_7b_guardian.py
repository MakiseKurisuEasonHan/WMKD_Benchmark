"""Windows guardian: stage evidence sync/commit; terminal verification then shutdown."""
import datetime, hashlib, json, os, subprocess, time
from pathlib import Path

P=Path(__file__).resolve().parents[1];E=P/'results/llmprint/scale_7b'
RE='/root/autodl-tmp/WMKD_Benchmark/results/llmprint/scale_7b'
SSH=['ssh','-F',r'C:\Users\Eason\.ssh\config','6004','-o','BatchMode=yes','-o','ConnectTimeout=15']
SCP=['scp','-F',r'C:\Users\Eason\.ssh\config','-o','BatchMode=yes','-o','ConnectTimeout=15']
REPORT=P/'docs/reproduction_reports/llmprint_7b_extension.md'
STATUS=['docs/CURRENT_STATE.md','PROJECT_STATUS.md','TODO.md','EXPERIMENT_LOG.md','DECISIONS.md']

def call(cmd,timeout=120):
    return subprocess.run(cmd,cwd=P,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=timeout)

def put(name,obj):
    (E/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

def sync():
    r=call([*SCP,'-r','6004:'+RE,str(E.parent)],600)
    assert r.returncode==0,r.stderr[-1000:]

def commit(message):
    paths=[str(f.relative_to(P)).replace('\\','/') for f in E.rglob('*') if f.is_file() and f.suffix in ['.json','.md','.txt','.csv'] and f.stat().st_size<2*2**20 and not f.name.startswith('local_')]
    paths+=[str(REPORT.relative_to(P)).replace('\\','/'),'results/experiment_full_logs_index.json',*STATUS]
    spec=E/'local_commit_paths.txt';spec.write_text('\n'.join(paths)+'\n',encoding='utf-8')
    r=call(['git','add','--pathspec-from-file='+str(spec)]);assert r.returncode==0,r.stderr
    r=call(['git','commit','--only','--pathspec-from-file='+str(spec),'-m',message]);assert r.returncode==0 or 'nothing to commit' in r.stdout,r.stderr
    return call(['git','rev-parse','HEAD']).stdout.strip()

def update(stage,terminal=None):
    text=(E/'final_report.md').read_text(encoding='utf-8') if terminal else '# LLMPrint 7B extension\n\nCompleted stage: '+stage+'; autonomous serial campaign remains active.\n'
    if not terminal:
        for s in ['reference','direct','paraphrase','logit']:
            f=E/s/'full_experiment_log.json'
            if f.exists():
                x=json.loads(f.read_text());d=x['detector']['primary'];u=x['utility']['a2']
                text+=f'\n{s}: score={d["accuracy"]}, threshold={d["threshold"]}, detected={d["positive"]}; ARC={u["arc_challenge_acc_norm"]}, MC2={u["truthfulqa_mc2_acc"]}.\n'
    scope='This experiment is a representative passive-method 7B extension (LLMPrint only). It is not an evaluation of all passive methods at 7B scale. REEF, HuRef, AWM and ZeroPrint are outside this campaign.\n'
    text+='\n'+scope
    REPORT.write_text(text,encoding='utf-8')
    line=f'LLMPrint 7B（{datetime.datetime.now().isoformat(timespec="seconds")}）：{stage}。独立目录 results/llmprint/scale_7b；报告 docs/reproduction_reports/llmprint_7b_extension.md。PN-FP 7B 结果不变。\n\n'
    for name in STATUS:
        path=P/name;old=path.read_text(encoding='utf-8') if path.exists() else ''
        path.write_text(line+old,encoding='utf-8')
    ip=P/'results/experiment_full_logs_index.json';index=json.loads(ip.read_text(encoding='utf-8'))
    for s,experiment in [('reference','A_7B'),('direct','Ba_7B'),('paraphrase','Bb_7B'),('logit','Bc_7B')]:
        f=E/s/'full_experiment_log.json'
        if not f.exists():continue
        rid='llmprint_7b_'+s
        item=dict(method='LLMPrint',role=s,experiment=experiment,run_id=rid,
            full_log_path=str(f.relative_to(P)).replace('\\','/'),full_log_sha256=hashlib.sha256(f.read_bytes()).hexdigest(),
            scientific_status='completed',watermark_evaluation_available=True,utility_available=True)
        index['objects']=[x for x in index['objects'] if x.get('run_id')!=rid]+[item]
    index['object_count']=len(index['objects']);index['generated_at']=datetime.datetime.now(datetime.timezone.utc).isoformat()
    ip.write_text(json.dumps(index,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    return commit('Record LLMPrint 7B '+stage+' with independent frozen protocol evidence')

def main():
    E.mkdir(parents=True,exist_ok=True);seen=set()
    put('local_guardian.json',dict(pid=os.getpid(),status='MONITORING',auto_shutdown=True))
    while True:
        try:
            sync()
            for stage in ['reference','direct','paraphrase','logit']:
                if stage not in seen and (E/(stage+'_complete.json')).exists():
                    h=update(stage);seen.add(stage);put('local_stage_commits.json',dict(completed=sorted(seen),last_commit=h))
            r=call([*SSH,'test -f '+RE+'/terminal.json && cat '+RE+'/terminal.json'],45)
            if r.returncode==0:terminal=json.loads(r.stdout);break
        except Exception as exc:put('local_transport_retry.json',dict(error=str(exc),time=time.time()))
        time.sleep(60)
    # Evidence verification must precede shutdown; no model download to local disk.
    while True:
        try:
            sync()
            code="import pathlib,hashlib,json;p=pathlib.Path('"+RE+"');print(json.dumps({str(f.relative_to(p)):hashlib.sha256(f.read_bytes()).hexdigest() for f in p.rglob('*') if f.is_file() and f.name!='campaign.lock'}))"
            r=call([*SSH,'/root/miniconda3/bin/python -c "'+code+'"'],180);assert r.returncode==0,r.stderr
            inventory=json.loads(r.stdout)
            for name,digest in inventory.items():
                f=E/name;assert f.resolve().is_relative_to(E.resolve())
                assert f.is_file() and hashlib.sha256(f.read_bytes()).hexdigest()==digest,name
            put('evidence_sync_verified.json',dict(verified=True,files=inventory,time=time.time()));break
        except Exception as exc:put('local_sync_retry.json',dict(error=str(exc),time=time.time()));time.sleep(30)
    h=update(terminal['status'],terminal)
    env=os.environ.copy();env['GIT_TERMINAL_PROMPT']='0'
    try:
        r=subprocess.run(['git','-c','credential.interactive=never','push','origin','main'],cwd=P,env=env,capture_output=True,text=True,timeout=60)
        push='COMPLETE' if r.returncode==0 else 'PENDING_AUTH_OR_TRANSPORT'
    except subprocess.TimeoutExpired:push='PENDING_TRANSPORT_TIMEOUT'
    put('git_receipt.json',dict(commit=h,push=push))
    # Constructor and campaign wrappers must both have exited, and no GPU worker.
    while True:
        r=call([*SSH,"nvidia-smi --query-compute-apps=pid --format=csv,noheader; pgrep -af '[p]ython.*(llmprint_7b_construct|llmprint_7b_campaign|llmprint_construct_fingerprints|pnfp_7b_distill_worker|generate_teacher_qa_formal|passive5_shared_bb_paraphrase_runner)' || true"],45)
        if r.returncode==0 and not r.stdout.strip():break
        time.sleep(30)
    put('shutdown_ready.json',dict(no_workers=True,terminal=terminal,time=time.time(),evidence_verified=True,instance_release=False))
    commit('Verify LLMPrint7B evidence and shutdown gates')
    r=call([*SSH,'sync && /bin/bash /usr/bin/shutdown'],45)
    put('shutdown_execution.json',dict(command='/bin/bash /usr/bin/shutdown',exit_code=r.returncode,stdout=r.stdout[-1000:],stderr=r.stderr[-1000:],time=time.time(),instance_released=False))
    commit('Record LLMPrint7B automatic shutdown receipt')
    put('local_guardian.json',dict(pid=os.getpid(),status='SHUTDOWN_SENT',terminal=terminal))

if __name__=='__main__':main()
