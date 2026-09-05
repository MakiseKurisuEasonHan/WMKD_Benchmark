"""Preserve interrupted non-equivalent PTB transport run; start faithful adapter continuation."""
import fcntl,shutil
from common import *
from run_methods_11_15 import close_method
batch=DATA/'runs/methods_11_15'; lock=(batch/'supervisor.lock').open('w'); fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
assert gpu_free()
state=read(ROOT/'results/methods_11_15_pipeline_state.json'); m=state['methods']['eaaw']; prior=read(m['context']); rr_old=Path(prior['run_root'])
assert prior['run_id']=='eaaw_a_20260905_111830_cont1_cont1'
receipt=rr_old/'receipts/TRAINING.2.json'; assert receipt.exists() and read(receipt)['status']=='FAILURE'
reason='Engineering data-adapter correction: official ptb_text_only builder applies line.strip(); previous local text loader retained PTB leading/trailing whitespace. Interrupted before final checkpoint. No result accepted; all progress/logs retained.'
m.update(status='TERMINAL',scientific_status='BLOCKED_TRAINING',last_error=reason,active_worker=None)
m['repair_history'].append({'time':now(),'action':reason,'official_builder':'https://raw.githubusercontent.com/huggingface/datasets/1.18.4/datasets/ptb_text_only/ptb_text_only.py','new_scientific_protocol':False})
close_method(state,'eaaw',prior)
canonical=ROOT/'results/methods_11_15/eaaw/experiment_a'; hist=canonical/'history'/prior['run_id']; hist.mkdir(parents=True)
for name in ('full_experiment_log.json','summary.json','report.md'): shutil.copyfile(canonical/name,hist/name)
idx=read(ROOT/'results/experiment_full_logs_index.json')
for obj in idx['objects']:
    if obj['run_id']==prior['run_id'] and obj['method']=='EaaW': obj['full_log_path']=str((hist/'full_experiment_log.json').relative_to(ROOT)); obj['full_log_sha256']=sha(hist/'full_experiment_log.json')
write(ROOT/'results/experiment_full_logs_index.json',idx)
rid='eaaw_a_20260905_111830_cont2'; rr=batch/rid; rr.mkdir(); (rr/'receipts').mkdir()
c={**prior,'run_id':rid,'run_root':str(rr),'continuation_of':prior['run_id'],'repair':reason}; write(rr/'context.json',c)
(rr/'ptb').mkdir()
for split in ('train','valid','test'): shutil.copyfile(rr_old/'ptb'/f'ptb_{split}.txt',rr/'ptb'/f'ptb_{split}.raw.txt')
m.update(run_id=rid,context=str(rr/'context.json'),stage='NOT_STARTED',status='NOT_STARTED',attempt=0,started_at=None,last_error=None,scientific_status='NOT_STARTED',git_status='PENDING',active_worker=None,completed_stages={},stage_attempts={})
m.pop('formal_report',None); write(ROOT/'results/methods_11_15_pipeline_state.json',state)
print(rid)
