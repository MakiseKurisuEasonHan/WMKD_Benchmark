import pathlib,json,time,subprocess,datetime
q=pathlib.Path(__file__).parent;p=q.parents[2]
limit=time.monotonic()+7200
while not (q/'training_exit.json').exists():
 if time.monotonic()>limit:raise RuntimeError('TRAINING_WAIT_TIMEOUT; do not stop training')
 time.sleep(5)
assert json.loads((q/'training_exit.json').read_text())['returncode']==0
assert json.loads((q/'training_summary.json').read_text())['steps']==7500
for attempt in range(24):
 processes=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader'],text=True).strip()
 if not processes:break
 time.sleep(5)
else:raise RuntimeError('GPU_NOT_IDLE; do not kill any process')
time.sleep(3)
cmd=['/root/autodl-tmp/WMKD_Benchmark_data/envs/xbb/bin/python','-u','-B',str(p/'scripts/evaluate_xbb_endpoint.py'),'pnfp']
result=subprocess.run(cmd,cwd=p)
(q/'evaluation_supervisor_exit.json').write_text(json.dumps({'returncode':result.returncode,'ended_at':datetime.datetime.now(datetime.timezone.utc).isoformat()},indent=2)+'\n')
