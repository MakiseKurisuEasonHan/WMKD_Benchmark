import subprocess,pathlib,json,datetime
P=pathlib.Path('/root/autodl-tmp/WMKD_Benchmark')
q=P/'results/active_cross_lineage_bb/iseal'
r=subprocess.run(['/root/miniconda3/bin/python','-B',str(P/'scripts/receive_xbb_preferred_files.py'),'iseal'])
if r.returncode==0:
 with (q.parent/'archive/worker.log').open('ab') as log:
  r=subprocess.run(['/root/autodl-tmp/WMKD_Benchmark_data/artifacts/modelscope_cli_env/bin/python','-u','-B',str(P/'scripts/archive_active_cross_lineage_bb.py'),'run','iseal'],stdout=log,stderr=subprocess.STDOUT)
(q/'archive_pipeline_exit.json').write_text(json.dumps({'returncode':r.returncode,'ended_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}))
