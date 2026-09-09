import pathlib,json,subprocess,fcntl,datetime,os
p=pathlib.Path(__file__).parent;e=p.parent
def save(path,d):
 t=path.with_suffix(path.suffix+'.tmp');t.write_text(json.dumps(d,indent=2)+'\n');t.replace(path)
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
