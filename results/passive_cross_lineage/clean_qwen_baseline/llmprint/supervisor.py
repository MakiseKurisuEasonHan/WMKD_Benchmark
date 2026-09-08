import subprocess,json,pathlib,datetime,traceback
O=pathlib.Path(__file__).parent
launch=json.loads((O/'launch.json').read_text())
with (O/'worker_stdout.log').open('ab') as f:
 p=subprocess.Popen(launch['command'],stdout=f,stderr=subprocess.STDOUT)
 (O/'worker_pid.json').write_text(json.dumps({'pid':p.pid}))
 rc=p.wait()
(O/'exit_record.json').write_text(json.dumps({'returncode':rc,'ended_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'automatic_retry':False}))
if rc==0:
 seq=json.loads((O/'probability_sequence.json').read_text())
 ref=json.loads(pathlib.Path('/root/autodl-tmp/WMKD_Benchmark_data/runs/llmprint/a2_closure/llmprint_a2_closure_20260901_150051_cont1/sequences/reference.json').read_text())
 assert seq['record_count']==len(seq['records'])==len(ref['records'])==200 and seq['error'] is None
 assert [r['pair_id'] for r in seq['records']]==[r['pair_id'] for r in ref['records']]
 n=sum(x['paper_bit']==y['paper_bit'] for x,y in zip(seq['records'],ref['records']))
 result={'method':'LLMPrint','role':'clean_qwen_baseline','status':'COMPLETE','matched_bits':n,'total':200,'bit_accuracy':n/200,'threshold':0.7150049776126003,'detected':n/200>=0.7150049776126003,'errors':[],'calibration':'frozen; Qwen belongs to historical calibration panel, not held-out','model_revision':launch['model_revision']}
 (O/'detector_result.json').write_text(json.dumps(result,indent=2)+'\n')
