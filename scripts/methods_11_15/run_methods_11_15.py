"""Serial, restart-safe Experiment A queue with independent worker receipts.

The supervisor may restart without restarting a live stage. Successful stages
are immutable receipts. CPU/GPU activity and logs are diagnostic; only a worker
receipt plus exit code and required outputs can establish success.
"""
import argparse, fcntl, os, signal, subprocess, sys, time, shutil, re
from common import *

STATE=ROOT/'results/methods_11_15_pipeline_state.json'
CONFIG=ROOT/'configs/methods_11_15.json'

def alive(pid,token):
    try: return token in Path(f'/proc/{pid}/cmdline').read_bytes().decode(errors='replace')
    except OSError: return False

def git_close(message):
    # Deliberately restrict staging to this batch and the canonical index.
    paths=['results/methods_11_15_pipeline_state.json','results/experiment_full_logs_index.json','results/methods_11_15','docs/reproduction_reports/methods_11_15_experiment_a_summary.md','results/methods_11_15_experiment_a_summary.json','results/methods_11_15_final_shutdown_state.json']
    paths=[p for p in paths if (ROOT/p).exists()]
    cmd(['git','add','--',*paths])
    cmd([PY,ROOT/'scripts/audit_git_payload.py'])
    cmd(['git','diff','--cached','--check'])
    if subprocess.call(['git','diff','--cached','--quiet'],cwd=ROOT): cmd(['git','commit','-m',message])
    cmd(['git','push','origin','main'],timeout=300)

def close_method(state,slug,c):
    m=state['methods'][slug]; receipts={}
    for stage,path in m['completed_stages'].items(): receipts[stage]=read(path)
    out=ROOT/'results/methods_11_15'/slug/'experiment_a'; out.mkdir(parents=True,exist_ok=True)
    log={'schema_version':'wmkd.methods-11-15.full-log.v1','method':c['spec']['name'],'experiment':'A','scientific_object_id':slug+':A:'+c['run_id'],'run_id':c['run_id'],'timestamps':{'started_at':m['started_at'],'closed_at':now()},'paper':c['spec']['paper'],'official_source':c['spec'],'state':m,'stages':receipts,'attempts':[read(p) for p in sorted(Path(c['run_root']).glob('receipts/*.json'))],'resolved_context':c,'training':receipts.get('TRAINING','NOT_RUN'),'detector':receipts.get('DETECTOR','NOT_RUN'),'negative_controls':receipts.get('DETECTOR',{}).get('outputs',{}).get('negative_controls','NOT_RUN'),'utility':receipts.get('UTILITY','NOT_RUN'),'reload':receipts.get('RELOAD_VERIFIED','NOT_RUN'),'archive':receipts.get('ARCHIVED','NOT_RUN'),'scientific_status':m['scientific_status'],'limitations':['Single official supported configuration; no Ba/Bb/distillation.','Missing results are NOT_RUN; infrastructure blocks do not establish method failure.']}
    write(out/'full_experiment_log.json',log)
    write(out/'summary.json',{'method':c['spec']['name'],'run_id':c['run_id'],'status':m['scientific_status'],'archive_status':m['archive_status'],'stage':m['stage'],'error':m['last_error'],'detector':log['detector'],'utility':log['utility']})
    # Report lives beside the canonical full log and is linked by master report.
    report=f"# {c['spec']['name']} Experiment A\n\n状态：{m['scientific_status']}；run ID `{c['run_id']}`。\n\nPaper: {c['spec']['paper']}\nOfficial repository: {c['spec']['repo']} @ `{c['spec']['commit']}`\n\n## 科学目标与配置\n\n复现官方核心所有权信号，保留Base、negative control和官方原生utility。官方骨干：{c['spec']['backbone']}；数据：{c['spec']['dataset']}。\n\n所有实际环境、命令、训练配置、patch、detector原始值、negative control、utility差值、reload、运行时间与归档证据见同目录 full_experiment_log.json 的 stages/attempts。\n\n## 实际结果及限制\n\n```json\n{__import__('json').dumps(read(out/'summary.json'),ensure_ascii=False,indent=2)}\n```\n\n未运行阶段为 NOT_RUN；不据此认定方法科学失败。不改变原生检测阈值；不运行攻击实验。\n"
    (out/'report.md').write_text(report,encoding='utf-8',newline='\n')
    idx=read(ROOT/'results/experiment_full_logs_index.json')
    path=str((out/'full_experiment_log.json').relative_to(ROOT))
    item={'method':c['spec']['name'],'role':'experiment_a','experiment':'A','run_id':c['run_id'],'full_log_path':path,'full_log_sha256':sha(out/'full_experiment_log.json'),'scientific_status':m['scientific_status'],'modelscope_repo':receipts.get('ARCHIVED',{}).get('outputs',{}).get('repository')}
    idx['objects']=[o for o in idx['objects'] if o['full_log_path']!=path]+[item]
    idx['object_count']=len(idx['objects']); idx['generated_at']=now(); write(ROOT/'results/experiment_full_logs_index.json',idx)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--initialize',action='store_true'); ap.add_argument('--shutdown',action='store_true'); a=ap.parse_args()
    conf=read(CONFIG); batch=DATA/'runs/methods_11_15'; batch.mkdir(parents=True,exist_ok=True)
    lock=(batch/'supervisor.lock').open('w'); fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    if STATE.exists(): state=read(STATE)
    else:
        state={'schema_version':'wmkd.methods-11-15-state.v1','created_at':now(),'status':'PREPARING','order':conf['order'],'methods':{}}
        for slug in conf['order']:
            rid=slug+'_a_'+datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
            rr=batch/rid; rr.mkdir(); (rr/'receipts').mkdir()
            c={'method':slug,'spec':conf['methods'][slug],'run_id':rid,'run_root':str(rr),'source':str(DATA/'sources/methods_11_15'/slug)}
            write(rr/'context.json',c)
            state['methods'][slug]={'method':c['spec']['name'],'run_id':rid,'context':str(rr/'context.json'),'stage':'NOT_STARTED','status':'NOT_STARTED','attempt':0,'started_at':None,'last_update':now(),'last_error':None,'repair_history':[],'scientific_status':'NOT_STARTED','detector_status':'NOT_RUN','utility_status':'NOT_RUN','archive_status':'NOT_RUN','git_status':'PENDING','completed_stages':{},'active_worker':None}
        write(STATE,state)
    if a.initialize: return
    state['status']='RUNNING'; write(STATE,state)
    for slug in conf['order']:
        m=state['methods'][slug]; c=read(m['context']); rr=Path(c['run_root'])
        # Deployment is allowed to prepare later CPU adapters while the first
        # official job runs. Missing adapter is never a scientific BLOCKED result.
        module_path=Path(__file__).with_name(c['spec']['module']+'.py')
        while not module_path.exists():
            write(batch/'watchdog.json',{'time':now(),'method':slug,'status':'WAITING_FOR_RUNNER_DEPLOYMENT'})
            time.sleep(20)
        if m['status']=='TERMINAL':
            if m['git_status']!='DURABLE':
                m['git_status']='DURABLE'; write(STATE,state); git_close('Close '+m['method']+' Experiment A')
            continue
        m['started_at']=m['started_at'] or now(); m['scientific_status']='RUNNING'
        for stage in STAGES:
            if stage in m['completed_stages']: continue
            m.update(stage=stage,status='RUNNING',last_update=now()); write(STATE,state)
            if shutil.disk_usage(DATA).free < 4*2**30:
                m['last_error']='Less than 4 GiB emergency headroom; historical KEEP untouched'; m['scientific_status']='BLOCKED_STORAGE'; break
            attempt=m['attempt'] if m['active_worker'] else 1
            result=rr/'receipts'/f'{stage}.{attempt}.json'; log=rr/f'{stage}.{attempt}.log'
            if m['active_worker']:
                active=m['active_worker']; result=Path(active['result']); log=Path(active['log']); pid=active['pid']; token=str(result)
            else:
                # Wait for any existing GPU user; do not kill unrelated work.
                while stage in ('TRAINING','DETECTOR','UTILITY','RELOAD_VERIFIED','MODEL_DATA_READY') and not gpu_free():
                    write(batch/'watchdog.json',{'time':now(),'stage':stage,'status':'WAITING_FOR_FREE_GPU'}); time.sleep(30)
                command=[str(PY),str(Path(__file__).with_name('worker.py')),m['context'],stage,str(attempt),str(result)]
                with log.open('ab',buffering=0) as f: proc=subprocess.Popen(command,stdout=f,stderr=subprocess.STDOUT,start_new_session=True,cwd=ROOT)
                pid=proc.pid; token=str(result); m['attempt']=attempt; m['active_worker']={'pid':pid,'result':str(result),'log':str(log),'command':command}; write(STATE,state)
            while alive(pid,token):
                # Stall is diagnostic only; never infer failure from silence alone.
                try: smi=capture(['nvidia-smi','--query-gpu=memory.used,utilization.gpu','--format=csv,noheader'])
                except Exception: smi='unavailable'
                tail=log.read_bytes()[-8192:].decode(errors='replace') if log.exists() else ''
                write(batch/'watchdog.json',{'time':now(),'method':slug,'stage':stage,'pid':pid,'process_alive':True,'gpu':smi,'disk_free_bytes':shutil.disk_usage(DATA).free,'log_size':log.stat().st_size if log.exists() else 0,'log_age_seconds':time.time()-log.stat().st_mtime if log.exists() else None,'fatal_patterns':[s for s in ('Traceback','CUDA out of memory','Segmentation fault','No space left on device') if s in tail],'cpu_stat':Path(f'/proc/{pid}/stat').read_text() if Path(f'/proc/{pid}/stat').exists() else None})
                time.sleep(20)
            m['active_worker']=None
            if not result.exists():
                value={'status':'FAILURE','error':'Worker disappeared without durable exit receipt; partial output retained','blocked_status':'BLOCKED_UNKNOWN'}
                write(result,value)
            else: value=read(result)
            if value['status']!='SUCCESS':
                m['last_error']=value.get('error'); m['scientific_status']=value.get('blocked_status') or {'SOURCE_PINNED':'BLOCKED_SOURCE','ENV_READY':'BLOCKED_ENVIRONMENT','MODEL_DATA_READY':'BLOCKED_DOWNLOAD','TRAINING':'BLOCKED_TRAINING','DETECTOR':'BLOCKED_DETECTOR','UTILITY':'BLOCKED_UTILITY','ARCHIVED':'BLOCKED_ARCHIVE'}.get(stage,'BLOCKED_UNKNOWN')
                if stage=='ARCHIVED': m['archive_status']='BLOCKED_ARCHIVE_LOCAL_RETAINED'
                break
            m['completed_stages'][stage]=str(result)
            if stage=='DETECTOR': m['detector_status']='COMPLETE'
            if stage=='UTILITY': m['utility_status']='COMPLETE'
            if stage=='ARCHIVED': m['archive_status']='VERIFIED_ARCHIVED'
            write(STATE,state)
        else:
            det=read(m['completed_stages']['DETECTOR'])['outputs']
            m['scientific_status']=det.get('scientific_status','ENGINEERING_COMPLETE_SIGNAL_NOT_REPRODUCED')
        m.update(status='TERMINAL',last_update=now(),git_status='DURABLE')
        close_method(state,slug,c); write(STATE,state); git_close('Close '+m['method']+' Experiment A')
    summary={'created_at':now(),'methods':state['methods'],'all_terminal':all(m['status']=='TERMINAL' for m in state['methods'].values())}
    write(ROOT/'results/methods_11_15_experiment_a_summary.json',summary)
    report='# Methods 11–15 Experiment A summary\n\n| Method | Final status | Detector | Utility | Archive | Full report |\n|---|---|---|---|---|---|\n'
    for slug,m in state['methods'].items(): report+=f"| {m['method']} | {m['scientific_status']} | {m['detector_status']} | {m['utility_status']} | {m['archive_status']} | [report](../../results/methods_11_15/{slug}/experiment_a/report.md) |\n"
    (ROOT/'docs/reproduction_reports/methods_11_15_experiment_a_summary.md').write_text(report,encoding='utf-8',newline='\n')
    state['status']='ALL_TERMINAL_AWAITING_LOCAL_SYNC'; write(STATE,state)
    intent={'shutdown_requested':False,'shutdown_authorized':a.shutdown,'shutdown_reason':'All five methods terminal; reports/full logs/index/master summary committed; waiting for exact local clean-HEAD acknowledgement.','prepared_at':now(),'status':'AWAITING_LOCAL_SYNC'}
    write(ROOT/'results/methods_11_15_final_shutdown_state.json',intent); git_close('Finalize methods 11-15 Experiment A queue')
    head=capture(['git','rev-parse','HEAD']); ack=batch/'local_sync_ack.json'
    while True:
        if ack.exists() and read(ack).get('head')==head and read(ack).get('clean') and gpu_free() and not capture(['git','status','--porcelain']): break
        time.sleep(30)
    if a.shutdown:
        # Shutdown request is written durably, committed, then acknowledged again.
        intent.update(shutdown_requested=True,shutdown_timestamp=now(),status='SHUTDOWN_REQUESTED_AFTER_FINAL_GATE')
        write(ROOT/'results/methods_11_15_final_shutdown_state.json',intent); state['status']='COMPLETE'; write(STATE,state)
        git_close('Record final methods 11-15 shutdown request'); head=capture(['git','rev-parse','HEAD'])
        while not (ack.exists() and read(ack).get('head')==head and read(ack).get('clean')): time.sleep(30)
        if not gpu_free() or capture(['git','status','--porcelain']): raise RuntimeError('Final shutdown quiescence gate changed')
        cmd(['sync'])
        p=subprocess.run(['shutdown','-h','now'],capture_output=True,text=True)
        if p.returncode:
            intent.update(status='AUTO_SHUTDOWN_REQUESTED_BUT_PLATFORM_REJECTED',platform_returncode=p.returncode,platform_error=p.stderr[:2000]); write(ROOT/'results/methods_11_15_final_shutdown_state.json',intent); git_close('Record AutoDL platform shutdown rejection')

if __name__=='__main__': main()
