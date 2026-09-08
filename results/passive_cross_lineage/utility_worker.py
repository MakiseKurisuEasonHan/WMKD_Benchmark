import pathlib,sys,json,os,datetime,traceback,hashlib
P=pathlib.Path('/root/autodl-tmp/WMKD_Benchmark');E=P/'results/passive_cross_lineage';role=sys.argv[1];model=sys.argv[2];O=E/role/'utility';O.mkdir(exist_ok=True)
sys.path.insert(0,str(P/'scripts'))
from evertracer_common import load_config
from evertracer_utility import configure_offline_utility,load_offline_dataset_smoke

def save(name,r):
 (O/name).write_text(json.dumps(r,indent=2,default=lambda x:x.item() if hasattr(x,'item') else str(x))+'\n')
try:
 cfg=load_config(P/'configs/watermark/evertracer_experiment_a.yaml');prov=configure_offline_utility(cfg);loaded=load_offline_dataset_smoke(cfg)
 save('evaluation_config.json',{'role':role,'model_path':model,'initialization_revision':'8f4992eda43eea7c770690ddc0de8f732da246f5','model_role':role,'tasks':['arc_challenge','truthfulqa_mc2'],'batch_size':8,'dtype':'bfloat16','apply_chat_template':True,'fewshot':'unchanged harness task defaults','offline':True,'dataset_provenance':prov,'dataset_splits':loaded,'fresh_process_pid':os.getpid(),'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat()})
 import lm_eval
 raw=lm_eval.simple_evaluate(model='hf',model_args=f'pretrained={model},local_files_only=True,trust_remote_code=True,dtype=bfloat16',tasks=['arc_challenge','truthfulqa_mc2'],batch_size=8,apply_chat_template=True,log_samples=True)
 save('raw_evaluator_output.json',raw);r=raw['results'];arc=r['arc_challenge']['acc_norm,none'];mc=r['truthfulqa_mc2']['acc,none'];assert 0<=arc<=1 and 0<=mc<=1
 save('utility_results.json',{'status':'COMPLETE','role':role,'model_path':model,'fresh_process_reload':True,'arc_challenge_acc_norm':arc,'truthfulqa_mc2_acc':mc,'raw_results':r,'errors':[],'completed_at':datetime.datetime.now(datetime.timezone.utc).isoformat()});save('exit_record.json',{'returncode':0})
except BaseException:
 save('exit_record.json',{'returncode':1,'error':traceback.format_exc()});raise
