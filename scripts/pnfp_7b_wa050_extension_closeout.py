"""Local outer runner: bounded monitor, evidence closeout, Git, and AutoDL shutdown.

No scientific changes or new training are performed by this runner.
"""
import csv,hashlib,io,json,os,subprocess,sys,tarfile,time,traceback
from pathlib import Path
P=Path(__file__).resolve().parents[1]
OUT=P/'results/pnfp/scale_7b/wa050_extension'
REMOTE='/root/autodl-tmp/WMKD_Benchmark_data/scale_7b/wa050_extension_v1'
PROJECT='/root/autodl-tmp/WMKD_Benchmark'
SSH=['ssh','-F',r'C:\Users\Eason\.ssh\config','6003','-o','BatchMode=yes','-o','ConnectTimeout=15']
FLAGS=getattr(subprocess,'CREATE_NO_WINDOW',0)
ENV=dict(os.environ,GIT_TERMINAL_PROMPT='0',GCM_INTERACTIVE='never',GIT_SSH_COMMAND='ssh -o BatchMode=yes')

def write(name,obj):
    p=OUT/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

def run(args,timeout=120,input=None,check=True):
    p=subprocess.run(args,cwd=P,input=input,text=True,encoding='utf-8',errors='replace',capture_output=True,timeout=timeout,creationflags=FLAGS,env=ENV)
    if check and p.returncode:raise RuntimeError(str(args[:2])+': '+p.stderr[-2000:])
    return p

def remote(source,timeout=120):return run(SSH+['/root/miniconda3/bin/python -'],timeout,input=source).stdout

def poll():
    return json.loads(remote("from pathlib import Path\nimport json,os\nr=Path("+repr(REMOTE)+")\ns=json.loads((r/'state.json').read_text())\nf=[p.name for p in r.glob('*failure.json')]\np=r/'progress.json'\nprint(json.dumps({'state':s,'failure':f,'progress':json.loads(p.read_text()) if p.exists() else None}))"))

def package():
    source=r'''
from pathlib import Path
import json,hashlib,tarfile,shutil,subprocess,os
r=Path('/root/autodl-tmp/WMKD_Benchmark_data/scale_7b/wa050_extension_v1');old=r.parent/'wa050_pilot_v1'
assert not subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader'],text=True).strip(),'GPU worker still active'
a=json.loads((r/'assessment.json').read_text()) if (r/'assessment.json').exists() else {'status':'FAILED_STOPPED','best_step':14,'best_checkpoint':str(old/'best_model'),'preferred_teacher_candidate':False}
if (r/'best_manifest.json').exists():
 m=json.loads((r/'best_manifest.json').read_text());a.update(best_step=m['step'],best_checkpoint=m['path'])
else:m=json.loads((old/'best_manifest.json').read_text())
best=Path(a['best_checkpoint']);verified=[]
for f in m['files']:
 p=best/f['path'];h=hashlib.sha256()
 with p.open('rb') as stream:
  for block in iter(lambda:stream.read(8*1024**2),b''):h.update(block)
 assert h.hexdigest()==f['sha256'],str(p)
 verified.append(f)
step=a['best_step'];d=r/'detector.json'
if not d.exists():d=r/f'fresh_step_{step:02d}.json'
if not d.exists() and step==14:d=old/'detector.json'
if d.exists():shutil.copy2(d,r/'final_detector.json')
u=r/f'utility_step_{step:02d}.json'
if not u.exists() and step==14:u=old/'utility.json'
if u.exists():shutil.copy2(u,r/'final_utility.json')
success=(r/'assessment.json').exists() and not list(r.glob('*failure.json'))
if success:assert (r/'final_detector.json').exists() and (r/'final_utility.json').exists()
integrity={'success':success,'assessment':a,'model_files_verified':verified,'best_checkpoint':str(best),'final_detector_present':(r/'final_detector.json').exists(),'final_utility_present':(r/'final_utility.json').exists(),'gpu_idle':True,'disk_free_bytes':shutil.disk_usage(r).free}
(r/'final_integrity.json').write_text(json.dumps(integrity,indent=2))
files=[p for p in r.rglob('*') if p.is_file() and p.name!='evidence_manifest.json' and not any(part in ('best_model','best_model.pending','official','saved_models') for part in p.relative_to(r).parts)]
manifest=[{'path':p.relative_to(r).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(files)]
(r/'evidence_manifest.json').write_text(json.dumps(manifest,indent=2));files.append(r/'evidence_manifest.json')
archive=r.parent/'wa050_extension_evidence.tar.gz'
with tarfile.open(archive,'w:gz') as t:
 for p in sorted(files):t.add(p,arcname=p.relative_to(r).as_posix())
os.sync();print(json.dumps({'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'files':len(files),'integrity':integrity}))
'''
    receipt=json.loads(remote(source,timeout=180));write('download_receipt.json',receipt)
    archive=P/'.pnfp_wa050_extension_evidence.tar.gz'
    run(['scp','-F',r'C:\Users\Eason\.ssh\config','6003:'+str(Path(REMOTE).parent).replace('\\','/')+'/wa050_extension_evidence.tar.gz',str(archive)],timeout=240)
    assert hashlib.sha256(archive.read_bytes()).hexdigest()==receipt['sha256']
    target=OUT/'receipts';target.mkdir(exist_ok=True)
    with tarfile.open(archive) as t:t.extractall(target,filter='data')
    for item in json.loads((target/'evidence_manifest.json').read_text()):assert hashlib.sha256((target/item['path']).read_bytes()).hexdigest()==item['sha256']
    return receipt

def report(receipt):
    r=OUT/'receipts'
    def read(name,default=None):return json.loads((r/name).read_text(encoding='utf-8')) if (r/name).exists() else default
    rows=[json.loads(s) for s in (r/'trajectory.jsonl').read_text().splitlines()] if (r/'trajectory.jsonl').exists() else []
    integrity=read('final_integrity.json');a=integrity['assessment'];d=read('final_detector.json',{});u=read('final_utility.json',{});result=read('result.json',{})
    extension=[x for x in rows if not x['replay']]
    (OUT/'trajectory.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8')
    fields=['update','nonzero_lr_update','replay','lr','train_loss','live_recall','live_recall_percent','best_fresh_recall','best_step','stop_reason']
    with (OUT/'trajectory.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
    samples=[]
    for p in r.glob('*_resources.jsonl'):samples.extend(json.loads(x) for x in p.read_text().splitlines())
    peaks={k:max((x[k] for x in samples),default=0) for k in ['gpu_nvidia_smi_mib','host_cgroup_bytes','disk_used_bytes']}
    steps=read('result.json',{}).get('steps',[]);new_steps=[s for s in steps if s['update']>14]
    metrics={'gpu_sampled_peak_GiB':peaks['gpu_nvidia_smi_mib']/1024,'host_cgroup_peak_GiB':peaks['host_cgroup_bytes']/1024**3,'host_RSS_peak_GiB':result.get('peak_host_process_rss_bytes',0)/1024**3,'gpu_allocated_peak_GiB':result.get('peak_gpu_allocated_bytes',0)/1024**3,'disk_peak_used_GiB':peaks['disk_used_bytes']/1024**3,'disk_final_free_GiB':integrity['disk_free_bytes']/1024**3,'mean_new_update_seconds':sum(s['sec_per_update'] for s in new_steps)/len(new_steps) if new_steps else None,'training_wall_seconds':result.get('training_wall_seconds'),'probe_seconds':sum(x['total_probe_seconds'] for x in rows)}
    log=json.loads((OUT/'full_experiment_log.json').read_text(encoding='utf-8'));log.update(status=a['status'] if integrity['success'] else 'FAILED_STOPPED',assessment=a,trajectory=rows,final_detector={k:v for k,v in d.items() if k!='details'},final_utility=u,performance=metrics,model_integrity=integrity,replay_gate=read('replay_weight_gate.json'),teacher_candidate=True,preferred_teacher_candidate=a.get('preferred_teacher_candidate',False),scientific_config_changed=False,distillation_started=False,shutdown_authorized=True,shutdown_status='PENDING_FINAL_CHECKS',evidence_sha256=receipt['sha256'])
    (OUT/'full_experiment_log.json').write_text(json.dumps(log,indent=2)+'\n',encoding='utf-8')
    utility=u.get('checkpoint',u.get('a2',{}));base=u.get('base',{});delta=u.get('delta',{})
    summary=f"WA=.50 extension {log['status']}；fresh-reload {d.get('detected','N/A')}/1024，best有效更新{a.get('best_nonzero_update',a.get('best_step',14)-2)}；preferred候选={a.get('preferred_teacher_candidate',False)}。训练停止，未启动蒸馏，授权证据闭环后自动关机。"
    table='| Call | 有效更新 | LR | Loss | live recall | live% | best fresh |\n|---:|---:|---:|---:|---:|---:|---:|\n'+'\n'.join(f"|{x['update']}|{x['nonzero_lr_update']}|{x['lr']:.8g}|{x['train_loss']:.6f}|{x['live_recall']}/1024|{x['live_recall_percent']:.2f}%|{x['best_fresh_recall']}/1024|" for x in extension)
    text=f'''# PN-FP 7B WA=.50 extension — 2026-09-19

{summary}

## 冻结配置与恢复

model=meta-llama/Llama-2-7b-chat-hf，revision=f5db02db724555f92da89c216ac04704f23d4590。冻结1024，key16/response1，Perinucleus t=.8/k=3，WA=.50，DM=.25，seed42，BF16全参数6,738,415,616，AdamW8bit0.50.0及activation checkpointing不变。原LR5e-5、WarmupDecayLR horizon40/effective warmup2、seq64、microbatch6+2、accum171、chat template、detector均保留。8-bit moment storage是engineering adaptation，不宣称FP32 Adam数值等价。

旧run未保存optimizer/scheduler状态，因此从canonical初始化重放前14calls（12有效更新），逐点精确比对loss、recall及数据顺序，call14与旧best全部state_dict张量bitwise比较后才延长；没有从权重重置Adam继续。原optimizer moments未保留，不能独立声称原moment逐bit已核验。重放不保存重复模型。恢复门槛：{read('replay_weight_gate.json')}。

## 新增轨迹

{table}

停止原因：{a.get('stop_reason', 'failure；见failure receipt')}。最多24累计有效更新；3检测无累计11条实质提升或3次持续下降早停。每点live1024，新高保存pending后fresh-reload验证；仅fresh新高替换旧best。fresh结果用于最终checkpoint结论，live和fresh不混用。

## 最终结果与utility

最终fresh detector：{d.get('detected','N/A')}/1024，invalid={d.get('invalid_samples','N/A')}，errors={d.get('evaluation_errors','N/A')}。70/80/90%是否达到：{[d.get('detected',0)>=n for n in [717,820,922]]}。

| 完整utility | Base | Selected best | Delta pp |
|---|---:|---:|---:|
| ARC-Challenge acc_norm (1172) |{base.get('arc_challenge_acc_norm','N/A')}|{utility.get('arc_challenge_acc_norm','N/A')}|{format(delta['arc_challenge_acc_norm']*100,'+.4f') if 'arc_challenge_acc_norm' in delta else 'N/A'}|
| TruthfulQA-MC2 (817) |{base.get('truthfulqa_mc2_acc','N/A')}|{utility.get('truthfulqa_mc2_acc','N/A')}|{format(delta['truthfulqa_mc2_acc']*100,'+.4f') if 'truthfulqa_mc2_acc' in delta else 'N/A'}|

完整utility在fresh recall较上次完整评估提高103条时触发，或达到80%候选门槛时评估；未每checkpoint评估。最终best如已在选中点完整评估，则复用同一checkpoint唯一正式结果，不重复运行；final_utility.json保留对应step与完整分数。Base复用相同canonical固定数据的旧正式全量分数。两项均下降>5pp停止；fresh>=820且两项下降均<=3pp标记preferred候选并停止。未追求1024/1024。

## 资源、证据与运行边界

{json.dumps(metrics,ensure_ascii=False,indent=2)}

Best保留在 `{integrity['best_checkpoint']}`。校验{len(integrity['model_files_verified'])}个模型文件SHA；轻量证据archiveSHA={receipt['sha256']}。仅新best验证后轮换删除旧WA50 best，删除路径、字节和理由见checkpoint_retention.jsonl；不删除canonical模型及正式结果。原pilot历史数据不覆盖，原模型位置如被替换则另记supersession。所有配置、provenance、逐点CSV/JSON、detector、utility、runtime、memory、报告同步本地；Git只提交本任务。Git push与关机实况见git_receipt.json、shutdown_receipt.json、automation_state.json。

本轮单seed、有限窗口，达到候选门槛不等同已证明更长训练稳定性。不启动distillation、不改科学参数，不释放实例。用户已明确授权成功/早停/硬失败均保存同步后执行/usr/bin/shutdown；失败缺失字段保留N/A，不虚构结果。
'''
    report_path=P/'docs/reproduction_reports/pnfp_7b_wa050_extension_20260919.md';report_path.write_text(text,encoding='utf-8')
    for name in ['docs/CURRENT_STATE.md','PROJECT_STATUS.md','TODO.md','EXPERIMENT_LOG.md']:
        p=P/name;p.write_text('当前状态（2026-09-19）：'+summary+'\n\n'+p.read_text(encoding='utf-8'),encoding='utf-8')
    p=P/'results/pnfp/scale_7b/pipeline_state.json';state=json.loads(p.read_text(encoding='utf-8'));state.update(status=log['status'],current_pilot_log='wa050_extension/full_experiment_log.json',pilot_pid=None,gpu_idle=True,preferred_teacher_candidate=a.get('preferred_teacher_candidate',False),best_checkpoint=integrity['best_checkpoint'],auto_shutdown_authorized=True,shutdown_status='PENDING_FINAL_CHECKS');p.write_text(json.dumps(state,indent=2)+'\n',encoding='utf-8')
    oldlog=P/'results/pnfp/scale_7b/wa050_pilot/full_experiment_log.json'
    if (r/'checkpoint_retention.jsonl').exists() and 'wa050_pilot_v1/best_model' in (r/'checkpoint_retention.jsonl').read_text():
        old=json.loads(oldlog.read_text(encoding='utf-8'));old.update(checkpoint_retention_status='SUPERSEDED_BY_USER_AUTHORIZED_EXTENSION',replacement_checkpoint=integrity['best_checkpoint'],original_model_retained=False,historical_results_preserved=True);oldlog.write_text(json.dumps(old,indent=2)+'\n',encoding='utf-8')
    p=P/'results/experiment_full_logs_index.json';idx=json.loads(p.read_text(encoding='utf-8'))
    for entry in idx['objects']:
        if entry['run_id'] in ['wa050_extension_v1','wa050_pilot_v1']:
            entry['full_log_sha256']=hashlib.sha256((P/entry['full_log_path']).read_bytes()).hexdigest()
        if entry['run_id']=='wa050_extension_v1':entry.update(scientific_status=log['status'],watermark_evaluation_available=bool(d),utility_available=bool(u),preferred_teacher_candidate=a.get('preferred_teacher_candidate',False),telemetry_records=len(rows))
    p.write_text(json.dumps(idx,indent=2)+'\n',encoding='utf-8');return summary

def git_closeout():
    paths=['scripts/pnfp_7b_wa050_extension_closeout.py','results/pnfp/scale_7b/wa050_extension','results/pnfp/scale_7b/wa050_pilot/full_experiment_log.json','docs/reproduction_reports/pnfp_7b_wa050_extension_20260919.md','docs/CURRENT_STATE.md','PROJECT_STATUS.md','TODO.md','EXPERIMENT_LOG.md','results/pnfp/scale_7b/pipeline_state.json','results/experiment_full_logs_index.json']
    run(['git','add','--']+paths)
    logs=[str(p.relative_to(P)).replace('\\','/') for p in (OUT/'receipts').glob('*.log')]
    if logs:run(['git','add','-f','--']+logs)
    commit=run(['git','commit','-m','Close WA050 extension with verified best and automatic shutdown authorization'],check=False)
    head=run(['git','rev-parse','HEAD']).stdout.strip()
    try:push=run(['git','-c','credential.interactive=false','push','origin','HEAD:main'],timeout=45,check=False);status='PUSHED' if push.returncode==0 else 'PUSH_PENDING';detail=push.stderr[-1500:]
    except Exception as e:status='PUSH_PENDING';detail=str(e)
    write('git_receipt.json',{'scientific_commit':head,'push_status':status,'detail':detail,'commit_exit':commit.returncode,'no_user_prompt':True})
    return paths

def sync_back(paths):
    files=[]
    for name in paths:
        p=P/name;files.extend(x for x in p.rglob('*') if x.is_file()) if p.is_dir() else files.append(p)
    files=list(dict.fromkeys(files));manifest=[{'path':p.relative_to(P).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]
    write('closeout_sync_manifest.json',manifest);files.append(OUT/'closeout_sync_manifest.json')
    archive=P/'.pnfp_wa050_extension_closeout.tar.gz'
    with tarfile.open(archive,'w:gz') as t:
        for p in files:t.add(p,arcname=p.relative_to(P).as_posix())
    remote_archive='/root/autodl-tmp/WMKD_Benchmark_data/scale_7b/wa050_extension_closeout.tar.gz'
    run(['scp','-F',r'C:\Users\Eason\.ssh\config',str(archive),'6003:'+remote_archive],timeout=240)
    receipt=remote("import tarfile,json,hashlib,shutil,os\nfrom pathlib import Path\np=Path("+repr(PROJECT)+")\nr=Path("+repr(REMOTE)+")\nwith tarfile.open("+repr(remote_archive)+") as t:t.extractall(p,filter='data')\nm=json.loads((p/'results/pnfp/scale_7b/wa050_extension/closeout_sync_manifest.json').read_text())\nfor x in m:assert hashlib.sha256((p/x['path']).read_bytes()).hexdigest()==x['sha256'],x['path']\nshutil.copy2(p/'docs/reproduction_reports/pnfp_7b_wa050_extension_20260919.md',r/'final_report.md')\nshutil.copy2(p/'results/pnfp/scale_7b/wa050_extension/full_experiment_log.json',r/'full_experiment_log.json')\nos.sync()\nprint(json.dumps({'verified_project_files':len(m),'local_sync_acknowledged':True,'report_exists':(r/'final_report.md').exists()}))")
    write('sync_receipt.json',json.loads(receipt))

def stop_owned_if_needed():
    return remote("""import os,signal,time,json
from pathlib import Path
r=Path('/root/autodl-tmp/WMKD_Benchmark_data/scale_7b/wa050_extension_v1')
s=json.loads((r/'state.json').read_text());actions=[]
for pid in [s.get('supervisor'),s.get('pid')]:
 if not pid:continue
 p=Path('/proc')/str(pid)/'cmdline'
 if not p.exists():continue
 cmd=p.read_bytes().replace(b'\\0',b' ').decode(errors='replace')
 if 'pnfp_7b_wa050_extension' not in cmd and not ('pnfp_evaluate.py' in cmd and 'wa050_extension' in cmd):continue
 os.kill(pid,signal.SIGTERM);actions.append({'pid':pid,'signal':'TERM'})
 time.sleep(3)
 if p.exists() and p.read_bytes():os.kill(pid,signal.SIGKILL);actions.append({'pid':pid,'signal':'KILL'})
print(json.dumps(actions))
""")

def shutdown():
    try:
        response=remote("""from pathlib import Path
import json,os,subprocess,time
r=Path('/root/autodl-tmp/WMKD_Benchmark_data/scale_7b/wa050_extension_v1')
gpu=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader'],text=True).strip()
assert not gpu,'GPU worker remains before shutdown'
receipt={'command':'/usr/bin/shutdown','authorized_by_user':True,'time_unix':time.time(),'gpu_idle':True,'model_and_evidence_preserved':True,'instance_release_requested':False}
(r/'shutdown_intent.json').write_text(json.dumps(receipt,indent=2));os.sync()
with (r/'shutdown_command.log').open('a') as f:
 try:child=subprocess.Popen(['/usr/bin/shutdown'],stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
 except OSError as exc:
  if exc.errno!=8:raise
  payload=Path('/usr/bin/shutdown').read_bytes();payload.decode('utf-8');assert payload and bytes([0]) not in payload
  receipt['interpreter_fallback']='/bin/bash /usr/bin/shutdown'
  child=subprocess.Popen(['/bin/bash','/usr/bin/shutdown'],stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
 receipt['pid']=child.pid
 try:receipt['exit_code']=child.wait(timeout=15)
 except subprocess.TimeoutExpired:receipt['exit_code']=None
print(json.dumps(receipt),flush=True)
""",timeout=40)
        write('shutdown_receipt.json',json.loads(response))
    except Exception as exc:
        write('shutdown_receipt.json',{'command':'/usr/bin/shutdown','dispatch_status':'SSH_RETURN_UNCERTAIN','detail':str(exc)})
    misses=0
    for _ in range(12):
        time.sleep(15)
        try:
            p=run(SSH+['true'],timeout=25,check=False);misses=misses+1 if p.returncode else 0
        except Exception:misses+=1
        if misses>=2:
            write('automation_state.json',{'status':'SHUTDOWN_COMMAND_EXECUTED_SSH_OFFLINE','shutdown_command':'/usr/bin/shutdown','consecutive_unreachable_checks':misses,'control_plane_power_state':'not separately queried','instance_released':False});return
    write('automation_state.json',{'status':'SHUTDOWN_REQUESTED_SSH_STILL_REACHABLE','requires_review':True})

def main():
    complete=False;paths=[]
    try:
        deadline=time.monotonic()+90*60;errors=0
        while time.monotonic()<deadline:
            try:
                state=poll();errors=0;write('automation_state.json',{'status':'MONITORING','remote':state})
                if state['failure'] or state['state']['status']=='EXTENSION_COMPLETE':break
            except Exception:
                errors+=1
                if errors>=6:raise
            time.sleep(15)
        else:raise RuntimeError('Bounded90min execution deadline exceeded')
        stop_owned_if_needed();receipt=package();report(receipt);paths=git_closeout();sync_back(paths);complete=True
    except BaseException:
        write('outer_runner_failure.json',{'traceback':traceback.format_exc(),'shutdown_still_required':True})
        try:
            stop_owned_if_needed();receipt=package();report(receipt);paths=git_closeout();sync_back(paths);complete=True
        except BaseException:write('emergency_closeout_failure.json',{'traceback':traceback.format_exc(),'best_effort_evidence_saved_locally':True})
    finally:
        write('pre_shutdown_local_receipt.json',{'closeout_completed':complete,'time_unix':time.time(),'shutdown_authorized_even_on_failure':True})
        try:stop_owned_if_needed();shutdown()
        except BaseException:write('shutdown_error.json',{'traceback':traceback.format_exc()})
        try:
            run(['git','add','--',str(OUT.relative_to(P))]);run(['git','commit','-m','Record WA050 extension closeout and shutdown receipts'],check=False)
            g=OUT/'git_receipt.json'
            if g.exists() and json.loads(g.read_text())['push_status']=='PUSHED':run(['git','-c','credential.interactive=false','push','origin','HEAD:main'],timeout=45,check=False)
        except BaseException:write('final_git_receipt_error.json',{'traceback':traceback.format_exc()})

if __name__=='__main__':
    with (OUT/'.runner.lock').open('x') as lock:lock.write(str(os.getpid()))
    main()
