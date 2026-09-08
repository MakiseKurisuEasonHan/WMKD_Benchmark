import pathlib,json,subprocess,os,datetime,traceback
O=pathlib.Path(__file__).parent;E=O.parent;launch=json.loads((O/'launch.json').read_text())
def save(p,r):
 t=p.with_suffix(p.suffix+'.tmp');t.write_text(json.dumps(r,indent=2)+'\n');os.replace(t,p)
with (O/'training_stdout.log').open('ab') as log:
 p=subprocess.Popen(launch['command'],stdout=log,stderr=subprocess.STDOUT)
 save(O/'worker_pid.json',{'pid':p.pid,'command':launch['command']});rc=p.wait()
status='TRAINING_COMPLETE_PENDING_RELOAD' if rc==0 else 'BLOCKED_TRAINING_EXIT'
if rc==0:
 try:
  s=json.loads((O/'training_summary.json').read_text());assert s['steps']==7500 and s['finite_loss'] is True
  tr=pathlib.Path(launch['command'][launch['command'].index('--output-dir')+1]);state=json.loads((tr/'checkpoint-7500/trainer_state.json').read_text());assert state['global_step']==7500
  assert (tr/'final_model/model.safetensors.index.json').is_file()
 except BaseException:status='BLOCKED_TRAINING_INTEGRITY';save(O/'validation_error.json',{'error':traceback.format_exc()})
save(O/'exit_record.json',{'returncode':rc,'status':status,'ended_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'automatic_retry':False})
s=json.loads((E/'pipeline_state.json').read_text());s.update(status=status,current_action='BB_FRESH_RELOAD_AND_DETECTORS' if status=='TRAINING_COMPLETE_PENDING_RELOAD' else 'INSPECT_BB_FAILURE',active_worker=None);save(E/'pipeline_state.json',s)
f=json.loads((O/'full_experiment_log.json').read_text());f.update(status=status,training_exit_code=rc);save(O/'full_experiment_log.json',f)
