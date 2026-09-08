import pathlib,subprocess,json,datetime
E=pathlib.Path(__file__).parent;D=pathlib.Path('/root/autodl-tmp/WMKD_Benchmark_data');PY=D/'artifacts/scw/env_py311/bin/python'
for role,model in [('clean_qwen_baseline',D/'models/paraphrasers/Qwen2.5-3B-Instruct'),('ba',D/'runs/passive_cross_lineage_ba/passive_cross_lineage_ba_20260908/training/final_model')]:
 O=E/role/'utility';O.mkdir(exist_ok=True);assert not (O/'utility_results.json').exists()
 assert subprocess.check_output(['nvidia-smi','--query-gpu=memory.used','--format=csv,noheader,nounits'],text=True).strip()=='0'
 with (O/'stdout.log').open('ab') as log:
  p=subprocess.Popen([str(PY),'-B','-u',str(E/'utility_worker.py'),role,str(model)],stdout=log,stderr=subprocess.STDOUT)
  (E/'utility_runtime.json').write_text(json.dumps({'role':role,'pid':p.pid,'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}));rc=p.wait()
 if rc!=0:
  (E/'utility_exit.json').write_text(json.dumps({'status':'BLOCKED_UTILITY','role':role,'returncode':rc}));raise SystemExit(rc)
(E/'utility_exit.json').write_text(json.dumps({'status':'CLEAN_AND_BA_UTILITY_COMPLETE','ended_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}))
