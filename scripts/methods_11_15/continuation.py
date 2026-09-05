"""Non-destructive continuation after a non-equivalent data adapter run finishes."""
import shutil
from common import *

def after_completed_training(state,slug,c):
    rr_old=Path(c['run_root']); invalidation=rr_old/'training_invalidation.json'
    if not invalidation.exists(): return False
    notice=read(invalidation); m=state['methods'][slug]
    from run_methods_11_15 import close_method
    m.update(status='TERMINAL',scientific_status='ENGINEERING_COMPLETE_NONCANONICAL_DATA_ADAPTER',last_error=notice['reason'],active_worker=None)
    m['repair_history'].append({'time':now(),'action':'Retain completed diagnostic checkpoint and all evidence; start equivalent official data-adapter continuation','details':notice})
    close_method(state,slug,c)
    canonical=ROOT/'results/methods_11_15'/slug/'experiment_a'; hist=canonical/'history'/c['run_id']; hist.mkdir(parents=True,exist_ok=True)
    for name in ('full_experiment_log.json','summary.json','report.md'): shutil.copyfile(canonical/name,hist/name)
    idx=read(ROOT/'results/experiment_full_logs_index.json')
    for obj in idx['objects']:
        if obj['run_id']==c['run_id'] and obj['method']==m['method']:
            obj['full_log_path']=str((hist/'full_experiment_log.json').relative_to(ROOT)); obj['full_log_sha256']=sha(hist/'full_experiment_log.json')
    write(ROOT/'results/experiment_full_logs_index.json',idx)
    rid='eaaw_a_20260905_111830_cont2'; rr=DATA/'runs/methods_11_15'/rid; rr.mkdir(); (rr/'receipts').mkdir(); (rr/'ptb').mkdir()
    for split in ('train','valid','test'): shutil.copyfile(rr_old/'ptb'/f'ptb_{split}.txt',rr/'ptb'/f'ptb_{split}.raw.txt')
    next_c={**c,'run_id':rid,'run_root':str(rr),'continuation_of':c['run_id'],'repair':notice['reason']}; write(rr/'context.json',next_c)
    m.update(run_id=rid,context=str(rr/'context.json'),stage='NOT_STARTED',status='NOT_STARTED',attempt=0,started_at=None,last_error=None,scientific_status='NOT_STARTED',git_status='PENDING',active_worker=None,completed_stages={},stage_attempts={})
    m.pop('formal_report',None); write(ROOT/'results/methods_11_15_pipeline_state.json',state)
    from run_methods_11_15 import git_close
    git_close('Preserve noncanonical PTB adapter run and start faithful continuation')
    return True
