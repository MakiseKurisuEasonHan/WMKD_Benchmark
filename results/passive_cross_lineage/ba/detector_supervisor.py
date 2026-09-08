import pathlib,subprocess,json,datetime,os
O=pathlib.Path(__file__).parent;E=O.parent;PY='/root/autodl-tmp/WMKD_Benchmark_data/artifacts/scw/env_py311/bin/python'
def save(p,r):
 t=p.with_suffix(p.suffix+'.tmp');t.write_text(json.dumps(r,indent=2)+'\n');os.replace(t,p)
for m in ['llmprint','reef','huref','awm','zeroprint']:
 d=O/m
 assert subprocess.check_output(['nvidia-smi','--query-gpu=memory.used','--format=csv,noheader,nounits'],text=True).strip()=='0'
 with (d/'orchestration_stdout.log').open('ab') as log:
  p=subprocess.Popen([PY,'-B','-u',str(d/'worker.py')],stdout=log,stderr=subprocess.STDOUT)
  save(O/'detector_runtime.json',{'method':m,'pid':p.pid,'stage':'FRESH_RELOAD_DETECTOR','started_at':datetime.datetime.now(datetime.timezone.utc).isoformat()});rc=p.wait()
 try:
  r=json.loads((d/'detector_result.json').read_text());assert rc==0 and r['status'] in ['COMPLETE','COMPLETED'] and not r['errors']
 except BaseException:
  save(O/'detector_exit.json',{'status':'BLOCKED_DETECTOR','method':m,'returncode':rc});raise
save(O/'detector_exit.json',{'status':'FIVE_DETECTORS_COMPLETE_PENDING_CLOSURE','ended_at':datetime.datetime.now(datetime.timezone.utc).isoformat()})
