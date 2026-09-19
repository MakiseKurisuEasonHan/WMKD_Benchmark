"""Independent remote safety supervisor. Never interrupts an active science worker.

Uses separate operational files; frozen science and the running campaign are untouched.
Local guardian supplies a verified evidence/commit acknowledgement before shutdown.
"""
import argparse, fcntl, hashlib, json, os, re, signal, subprocess, tarfile, time, traceback
from pathlib import Path

P=Path('/root/autodl-tmp/WMKD_Benchmark')
E=P/'results/awm/scale_7b'
O=P.parent/'WMKD_Benchmark_data/awm_7b'
PY=str(P.parent/'WMKD_Benchmark_data/scale_7b/env/bin/python')
FROZEN='627107dc6c7db1569a43c2f94f67b5e7f9314bdcd2968c36f288f07b83b47a3f'
VOLATILE={'night_watchdog_state.json','night_watchdog.log','night_watchdog.lock','campaign.lock'}

def load(p,default=None):
    try:return json.loads(p.read_text())
    except (OSError,ValueError):return {} if default is None else default
def put(name,x):
    p=E/name;t=p.with_suffix(p.suffix+'.tmp');t.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n');t.replace(p)
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    return h.hexdigest()
def processes():
    result=[]
    for p in Path('/proc').iterdir():
        if not p.name.isdigit():continue
        try:
            args=(p/'cmdline').read_bytes().replace(b'\0',b' ').decode(errors='replace')
            stat=(p/'stat').read_text().split()
            if stat[2]=='Z':continue
            if args:result.append((int(p.name),args))
        except (OSError,IndexError):pass
    return result
def activity():
    ps=processes();state=load(E/'campaign_state.json')
    campaign=[pid for pid,args in ps if 'scripts/awm_7b_campaign.py' in args and 'python' in args.split()[0]]
    worker=state.get('worker_pid')
    known=('generate_teacher_qa_formal.py','pnfp_7b_distill_worker.py','passive5_shared_bb_paraphrase_runner.py',
           'awm_7b_detector.py','awm_7b_utility.py','restore_xbb_qwen_base.py','passive5_shared_bb.py')
    workers=[pid for pid,args in ps if (pid==worker or any(n in args for n in known)) and 'python' in args.split()[0]]
    # Check all GPU processes, including unrelated jobs: never shut these down.
    r=subprocess.run(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader'],capture_output=True,text=True,timeout=20)
    if r.returncode:raise RuntimeError('Cannot verify GPU idle: '+r.stderr)
    gpu=[int(x.strip()) for x in r.stdout.splitlines() if x.strip().isdigit()]
    return dict(campaign=campaign,workers=workers,gpu=gpu,stage=state.get('stage'))
def classify(text,stage,retries):
    low=text.lower()
    hard=('out of memory','outofmemory','nonfinite','corrupt','sha mismatch','size mismatch',
          'disk safety','disk peak','prompt_sha','persistent order-of-magnitude')
    if any(x in low for x in hard) or re.search(r'\b(?:nan|inf)\b',low):return 'HARD_FAILURE'
    # One bounded retry only for demonstrably transient failures in restart-safe stages.
    safe=any(x in stage for x in ('generation','detector','utility','qwen_restore','response_count','paraphrase_audit'))
    transient=any(x in low for x in ('connection reset','connection aborted','timed out','temporary failure','resource temporarily unavailable','stale file handle'))
    if safe and transient and retries==0:return 'RETRY_TRANSIENT'
    if any(x in low for x in ('scientific_block','valid unique samples','canonical passive generation ceiling','scientific decision','protocol change')):
        return 'WAITING_FOR_USER'
    return 'HARD_FAILURE_UNSAFE_TO_RESUME'
def verify_final():
    assert sha(E/'calibration.json')==FROZEN,'Calibration integrity mismatch'
    for stage in ('direct','paraphrase','logit'):
        for suffix in ('_complete.json','_detector.json','_utility.json'):
            assert (E/(stage+suffix)).is_file(),stage+suffix
        for x in load(O/stage/'final_manifest.json')['files']:
            f=O/stage/'final_model'/x['path']
            assert f.resolve().is_relative_to((O/stage/'final_model').resolve())
            assert f.stat().st_size==x['bytes'] and sha(f)==x['sha256'],str(f)
    assert (E/'final_report.md').is_file()
    return dict(final_models_sha_verified=True,detector_utility_present=True,calibration_sha256=FROZEN,time=time.time())
def inventory():
    return {str(f.relative_to(E)):sha(f) for f in E.rglob('*') if f.is_file() and f.name not in VOLATILE and not f.name.endswith('.tmp')}
def request_closeout(status,reason,verification=None):
    request=dict(status=status,reason=reason,time=time.time(),auto_shutdown=True,release_instance=False,verification=verification)
    put('night_closure_request.json',request)
    return request
def shutdown(request,local_verified):
    a=activity()
    if a['campaign'] or a['workers'] or a['gpu']:return False
    put('night_shutdown_intent.json',dict(time=time.time(),request=request,activity=a,local_verified=local_verified,
        command='/usr/bin/shutdown',instance_release=False))
    subprocess.run(['sync'],check=True)
    # AutoDL's official script may lack a shebang (ENOEXEC); explicit bash is equivalent.
    with (E/'night_shutdown_command.log').open('a') as log:
        try:r=subprocess.run(['/usr/bin/shutdown'],stdout=log,stderr=subprocess.STDOUT,timeout=90)
        except OSError as exc:
            if exc.errno!=8:raise
            r=subprocess.run(['/bin/bash','/usr/bin/shutdown'],stdout=log,stderr=subprocess.STDOUT,timeout=90)
    put('night_shutdown_execution.json',dict(time=time.time(),exit_code=r.returncode,instance_release=False))
    subprocess.run(['sync'])
    return r.returncode==0
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--inventory',action='store_true');parser.add_argument('--probe',action='store_true');parser.add_argument('--self-test',action='store_true');args=parser.parse_args()
    if args.self_test:
        assert classify('Connection reset by peer','direct_generation_24000',0)=='RETRY_TRANSIENT'
        assert classify('Connection reset by peer','direct_generation_24000',1)=='HARD_FAILURE_UNSAFE_TO_RESUME'
        assert classify('Connection reset by peer','direct_training_micro2',0)=='HARD_FAILURE_UNSAFE_TO_RESUME'
        assert classify('CUDA out of memory','direct_training_micro2',0)=='HARD_FAILURE'
        assert classify('SCIENTIFIC_BLOCK protocol change','logit_cache',0)=='WAITING_FOR_USER'
        assert classify('financial query; Connection reset by peer','direct_generation_24000',0)=='RETRY_TRANSIENT'
        original=globals()['activity']
        try:
            for field in ('campaign','workers','gpu'):
                a=dict(campaign=[],workers=[],gpu=[]);a[field]=[999999]
                globals()['activity']=lambda:a
                assert shutdown({},True) is False
        finally:globals()['activity']=original
        print('PASS: transient retry bounds, no training replay, scientific wait, hard OOM, active-worker shutdown interlocks');return
    if args.inventory:print(json.dumps(inventory()));return
    if args.probe:print(json.dumps(activity()));return
    lock=(E/'night_watchdog.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    idle_since=None;terminal_seen=None;request=load(E/'night_closure_request.json') or None
    last_activity=None
    while True:
        try:
            a=activity();now=time.time()
            put('night_watchdog_state.json',dict(pid=os.getpid(),time=now,activity=a,auto_shutdown=True,
                status='CLOSING' if request else 'MONITORING',idle_since=idle_since))
            if a['workers'] or a['gpu']:
                idle_since=None;time.sleep(30);continue
            term=load(E/'terminal.json')
            if term and not a['campaign'] and not request:
                if term.get('status')=='COMPLETED':
                    verified=verify_final()
                    # Reproducible cache cleanup is optional, final models were already verified.
                    r=subprocess.run(['/root/miniconda3/bin/python',str(P/'scripts/awm_7b_cleanup.py')],capture_output=True,text=True,timeout=900)
                    if r.returncode:put('cleanup_pending.json',dict(noncritical=True,error=r.stderr[-2000:]))
                    request=request_closeout('COMPLETED','All three AWM Students and final evaluations complete',verified)
                else:
                    runtimes=sorted(E.glob('*_runtime.json'),key=lambda p:p.stat().st_mtime)
                    stage=runtimes[-1].name.removesuffix('_runtime.json') if runtimes else ''
                    log=E/(stage+'.log')
                    # Do not read arbitrarily large training logs into host memory.
                    tail=''
                    if log.exists():
                        with log.open('rb') as f:
                            f.seek(max(0,log.stat().st_size-16000));tail=f.read().decode(errors='replace')
                    error=term.get('error','')+'\n'+tail
                    hist=load(E/'night_engineering_retry.json');kind=classify(error,stage,hist.get('attempts',0))
                    if kind=='RETRY_TRANSIENT':
                        put('night_engineering_retry.json',dict(stage=stage,attempts=1,time=now,error=error,scientific_changes=False))
                        with (E/'campaign_supervisor.log').open('a') as out:
                            subprocess.Popen([PY,str(P/'scripts/awm_7b_campaign.py'),'--resume-engineering'],cwd=P,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
                        time.sleep(30);continue
                    if kind=='WAITING_FOR_USER':
                        waiting=load(E/'night_waiting_for_user.json')
                        if not waiting:
                            waiting=dict(status=kind,since=now,deadline=now+1800,reason=error,
                                question='当前冻结科学协议无法继续。是否批准修改？未收到明确回复前不改变协议；30分钟后安全关机。')
                            put('night_waiting_for_user.json',waiting)
                        if now<waiting['deadline']:time.sleep(30);continue
                        kind='WAITING_FOR_USER_TIMEOUT'
                    request=request_closeout(kind,error)
            elif not term and not request:
                # A live campaign may be hashing/freezing data between workers. Actual CPU/I/O
                # and artifact changes count as progress; elapsed wall time alone never does.
                signature=[]
                for pid in a['campaign']:
                    try:
                        stat=(Path('/proc')/str(pid)/'stat').read_text().split()
                        signature.append((pid,stat[13],stat[14],(Path('/proc')/str(pid)/'io').read_text()))
                    except OSError:pass
                signature+= [(f.name,f.stat().st_size,f.stat().st_mtime_ns) for f in E.glob('*') if f.is_file() and not f.name.startswith('night_')]
                if signature!=last_activity:idle_since=now;last_activity=signature
                idle_since=idle_since or now
                if now-idle_since>=1800:
                    # Revalidate then TERM only the idle AWM controller; never a worker.
                    if activity()['workers'] or activity()['gpu']:continue
                    for pid in a['campaign']:os.kill(pid,signal.SIGTERM)
                    time.sleep(5)
                    request=request_closeout('STALLED_NO_ACTIVE_WORKER','No active worker or CPU/I/O/artifact progress for 30 minutes')
            if request:
                ack=load(E/'night_local_closure_ack.json')
                if ack.get('request_time')==request['time'] and ack.get('evidence_verified') and ack.get('commit'):
                    if now-ack.get('time',now)>=60 and shutdown(request,True):return
                elif now-request['time']>1800:
                    # Local transport/computer outage cannot leave an idle GPU billed all night.
                    # Preserve full remote evidence and explicitly record pending local synchronization.
                    put('night_local_sync_pending.json',dict(reason='Local closeout acknowledgement unavailable for 30 minutes',time=now))
                    archive=O/'night_emergency_evidence.tar.gz'
                    with tarfile.open(archive,'w:gz') as tf:tf.add(E,arcname='scale_7b')
                    put('night_emergency_archive.json',dict(path=str(archive),sha256=sha(archive),bytes=archive.stat().st_size))
                    if shutdown(request,False):return
        except Exception:
            put('night_watchdog_error.json',dict(time=time.time(),error=traceback.format_exc()))
            # A failed final SHA gate is a hard failure, never a reason to alter scientific assets.
            if not request:
                try:
                    a=activity()
                    if not a['campaign'] and not a['workers'] and not a['gpu']:
                        request=request_closeout('HARD_FAILURE',traceback.format_exc())
                except Exception:pass
        time.sleep(30)
if __name__=='__main__':main()
