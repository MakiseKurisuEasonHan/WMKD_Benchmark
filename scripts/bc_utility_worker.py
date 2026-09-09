"""Existing frozen harness utility protocol, output isolated to same-lineage Bc."""
import datetime
import json
import os
from pathlib import Path
import sys
import traceback
from evertracer_common import load_config
from evertracer_utility import configure_offline_utility, load_offline_dataset_smoke

P=Path(__file__).resolve().parents[1]
role,model=sys.argv[1:3]
O=P/'results/logit_distillation/same_lineage_bc'/role/'utility';O.mkdir(parents=True,exist_ok=True)
def save(name,data):
    (O/name).write_text(json.dumps(data,indent=2,default=lambda x:x.item() if hasattr(x,'item') else str(x))+'\n')
try:
    cfg=load_config(P/'configs/watermark/evertracer_experiment_a.yaml')
    provenance=configure_offline_utility(cfg);splits=load_offline_dataset_smoke(cfg)
    save('evaluation_config.json',{'model_path':model,'initialization_revision':'0cb88a4f764b7a12671c53f0838cd831a0843b95','tasks':['arc_challenge','truthfulqa_mc2'],'batch_size':8,'dtype':'bfloat16','apply_chat_template':True,'fewshot':'unchanged harness defaults','dataset_provenance':provenance,'dataset_splits':splits,'fresh_process_pid':os.getpid(),'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat()})
    import lm_eval
    raw=lm_eval.simple_evaluate(model='hf',model_args=f'pretrained={model},local_files_only=True,trust_remote_code=True,dtype=bfloat16',tasks=['arc_challenge','truthfulqa_mc2'],batch_size=8,apply_chat_template=True,log_samples=True)
    assert len(raw['samples']['arc_challenge'])==1172 and len(raw['samples']['truthfulqa_mc2'])==817
    save('raw_evaluator_output.json',raw)
    save('utility_results.json',{'status':'COMPLETE','fresh_process_reload':True,'arc_challenge_acc_norm':raw['results']['arc_challenge']['acc_norm,none'],'truthfulqa_mc2_acc':raw['results']['truthfulqa_mc2']['acc,none'],'completed_at':datetime.datetime.now(datetime.timezone.utc).isoformat()})
    save('exit_record.json',{'returncode':0})
except BaseException:
    save('exit_record.json',{'returncode':1,'error':traceback.format_exc()});raise
