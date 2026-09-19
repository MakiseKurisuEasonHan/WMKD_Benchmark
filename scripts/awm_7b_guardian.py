"""Stage sync/commit and final local evidence verification; NEVER shuts down."""
import datetime,hashlib,json,os,subprocess,time
from pathlib import Path
P=Path(__file__).resolve().parents[1];E=P/'results/awm/scale_7b'
RE='/root/autodl-tmp/WMKD_Benchmark/results/awm/scale_7b'
SSH=['ssh','-F',r'C:\Users\Eason\.ssh\config','6004','-o','BatchMode=yes','-o','ConnectTimeout=15']
SCP=['scp','-F',r'C:\Users\Eason\.ssh\config','-o','BatchMode=yes','-o','ConnectTimeout=15']
REPORT=P/'docs/reproduction_reports/awm_7b_extension.md'
STATUS=['docs/CURRENT_STATE.md','PROJECT_STATUS.md','TODO.md','EXPERIMENT_LOG.md','DECISIONS.md']
def call(cmd,timeout=120):return subprocess.run(cmd,cwd=P,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=timeout)
def put(name,obj):(E/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def sync():
    r=call([*SCP,'-r','6004:'+RE,str(E.parent)],600);assert r.returncode==0,r.stderr[-1000:]
def commit(message):
    paths=[f.relative_to(P).as_posix() for f in E.rglob('*') if f.is_file() and f.suffix in ['.json','.md','.txt','.csv'] and f.stat().st_size<2*2**20 and not f.name.startswith('local_')]
    paths+=[REPORT.relative_to(P).as_posix(),'results/experiment_full_logs_index.json',*STATUS]
    spec=E/'local_commit_paths.txt';spec.write_text('\n'.join(paths)+'\n',encoding='utf-8')
    r=call(['git','add','--pathspec-from-file='+str(spec)]);assert r.returncode==0,r.stderr
    r=call(['git','commit','--only','--pathspec-from-file='+str(spec),'-m',message]);assert r.returncode==0 or 'nothing to commit' in r.stdout,r.stderr
    return call(['git','rev-parse','HEAD']).stdout.strip()
def update(stage,terminal=False):
    text=(E/'final_report.md').read_text(encoding='utf-8') if terminal else '# AWM 7B representative passive-method extension\n\nCompleted stage: '+stage+'. Serial pipeline active; no shutdown. LLMPrint remains paused.\n'
    if not terminal:
        for s in ['reference','direct','paraphrase','logit']:
            f=E/s/'full_experiment_log.json'
            if f.exists():
                x=json.loads(f.read_text());d=x['detector'];u=x['utility']['a2']
                text+=f'\n{s}: native score={d["score"]}, frozen threshold={d["threshold"]}, detected={d["detected"]}; ARC={u["arc_challenge_acc_norm"]}, MC2={u["truthfulqa_mc2_acc"]}.\n'
    text+='\nAll Students independently start from clean canonical Llama2-7B-chat; AdamW8bit storage adaptation is not FP32 Adam implementation equivalence. Existing PNFP results and paused LLMPrint artifacts are unchanged.\n'
    REPORT.write_text(text,encoding='utf-8')
    line=f'AWM7B（{datetime.datetime.now().isoformat(timespec="seconds")}）：{stage}。独立results/awm/scale_7b；报告docs/reproduction_reports/awm_7b_extension.md。LLMPrint保持58/200暂停，PNFP结果不变；禁止自动关机。\n\n'
    for name in STATUS:
        f=P/name;f.write_text(line+f.read_text(encoding='utf-8'),encoding='utf-8')
    ip=P/'results/experiment_full_logs_index.json';index=json.loads(ip.read_text(encoding='utf-8'))
    for s,ex in [('reference','A_7B'),('direct','Ba_7B'),('paraphrase','Bb_7B'),('logit','Bc_7B')]:
        f=E/s/'full_experiment_log.json'
        if not f.exists():continue
        rid='awm_7b_'+s;entry=dict(method='AWM',role=s,experiment=ex,run_id=rid,
            full_log_path=f.relative_to(P).as_posix(),full_log_sha256=hashlib.sha256(f.read_bytes()).hexdigest(),scientific_status='completed',watermark_evaluation_available=True,utility_available=True)
        index['objects']=[x for x in index['objects'] if x.get('run_id')!=rid]+[entry]
    index['object_count']=len(index['objects']);index['generated_at']=datetime.datetime.now(datetime.timezone.utc).isoformat()
    ip.write_text(json.dumps(index,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    return commit('Record formal AWM7B '+stage+' evidence and frozen native detector')
def push():
    env=os.environ.copy();env['GIT_TERMINAL_PROMPT']='0'
    try:
        r=subprocess.run(['git','-c','credential.interactive=never','push','origin','main'],cwd=P,env=env,capture_output=True,text=True,timeout=60)
        status='COMPLETE' if r.returncode==0 else 'PENDING_AUTH_OR_TRANSPORT'
    except subprocess.TimeoutExpired:status='PENDING_TRANSPORT_TIMEOUT'
    put('git_receipt.json',dict(commit=call(['git','rev-parse','HEAD']).stdout.strip(),push=status))
def main():
    E.mkdir(parents=True,exist_ok=True);seen=set();blocked_seen=set()
    if (E/'local_stage_commits.json').exists():seen=set(json.loads((E/'local_stage_commits.json').read_text()).get('completed',[]))
    put('local_guardian.json',dict(pid=os.getpid(),status='MONITORING',auto_shutdown=False))
    while True:
        try:
            sync()
            for stage in ['reference','direct','paraphrase','logit']:
                if stage not in seen and (E/(stage+'_complete.json')).exists():
                    h=update(stage);seen.add(stage);put('local_stage_commits.json',dict(completed=sorted(seen),last_commit=h));push()
            r=call([*SSH,'test -f '+RE+'/terminal.json && cat '+RE+'/terminal.json'],45)
            if r.returncode==0:
                terminal=json.loads(r.stdout)
                if terminal['status']=='COMPLETED':break
                digest=hashlib.sha256(r.stdout.encode()).hexdigest()
                if digest not in blocked_seen:update(terminal['status'],True);blocked_seen.add(digest);push()
        except Exception as exc:put('local_transport_retry.json',dict(error=str(exc),time=time.time()))
        time.sleep(60)
    while True:
        try:
            sync()
            code="import pathlib,hashlib,json;p=pathlib.Path('"+RE+"');print(json.dumps({str(f.relative_to(p)):hashlib.sha256(f.read_bytes()).hexdigest() for f in p.rglob('*') if f.is_file() and f.name!='campaign.lock'}))"
            r=call([*SSH,'/root/miniconda3/bin/python -c "'+code+'"'],180);assert r.returncode==0,r.stderr
            inv=json.loads(r.stdout)
            for name,digest in inv.items():
                f=E/name;assert f.resolve().is_relative_to(E.resolve()) and f.is_file() and hashlib.sha256(f.read_bytes()).hexdigest()==digest,name
            put('evidence_sync_verified.json',dict(verified=True,files=inv,time=time.time()));break
        except Exception as exc:put('local_sync_retry.json',dict(error=str(exc),time=time.time()));time.sleep(30)
    update('COMPLETED',True);push()
    r=call([*SSH,'nvidia-smi --query-compute-apps=pid,used_memory --format=csv,noheader'],45)
    put('final_closeout.json',dict(status='COMPLETED',terminal=terminal,gpu_idle_verified=r.returncode==0 and not r.stdout.strip(),
        auto_shutdown=False,instance_kept_on=True,llmprint_remains_paused=True,time=time.time()))
    commit('Verify AWM7B final local sync and keep instance on as authorized')
    put('local_guardian.json',dict(pid=os.getpid(),status='COMPLETED_NO_SHUTDOWN',auto_shutdown=False))
if __name__=='__main__':main()
