import json,os,subprocess,sys,time,shutil,traceback
from pathlib import Path
P=Path('/root/autodl-tmp/WMKD_Benchmark'); R=Path(str(P)+'_data/scale_7b'); E=P/'results/pnfp/scale_7b/distillation_6004'; O=R/'distillation_6004'; O.mkdir(exist_ok=True)
sys.path.insert(0,str(P/'scripts'))
from pnfp_7b_disk_gate import budget
assert json.loads((E/'clone_preflight.json').read_text())['pass']
components={'three_final_students':40437792768,'missing_qwen':6183463418,'datasets_generations_and_reports_reserve':5*2**30,'single_save_temporary_shard':5*2**30}
b=budget(*shutil.disk_usage(R),components); (E/'direct_generation_disk_gate.json').write_text(json.dumps(b,indent=2)); assert b['passed']
assert not (O/'direct').exists(),'No duplicate generation run'; (O/'direct').mkdir()
state={'status':'GENERATING_DIRECT_CANDIDATES','started':time.time(),'pid':os.getpid(),'output':str(O/'direct'),'shutdown':'local closeout required after evidence sync'}
(E/'state.json').write_text(json.dumps(state,indent=2))
env=os.environ.copy(); env.update(HF_HUB_OFFLINE='1',HF_DATASETS_OFFLINE='1',TOKENIZERS_PARALLELISM='false',OMP_NUM_THREADS='8',PYTHONUNBUFFERED='1')
cmd=[str(R/'env/bin/python'),str(P/'scripts/generate_teacher_qa_formal.py'),'--model-path',str(R/'wa050_extension_v1/best_model'),'--teacher-run-id','wa050_extension_v1_best_call21_fresh804','--output',str(O/'direct/raw_candidates.jsonl'),'--errors',str(O/'direct/errors.jsonl'),'--target-candidates','24000','--batch-size','8','--seed','42','--telemetry',str(E/'generation_telemetry.json')]
(E/'generation_command.json').write_text(json.dumps(cmd,indent=2))
try:
 with (E/'generation.log').open('w') as f: subprocess.run(cmd,cwd=P,env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
 state['status']='CANDIDATES_READY'
except Exception:
 state['status']='GENERATION_FAILED';state['error']=traceback.format_exc()
finally:
 state['ended']=time.time(); (E/'state.json').write_text(json.dumps(state,indent=2)); subprocess.run(['sync'])
