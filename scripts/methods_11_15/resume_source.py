"""Preserve terminal pre-training source failure and create explicit cont lineage."""
import fcntl, shutil, os
from common import *

def main():
    batch=DATA/'runs/methods_11_15'
    lock=(batch/'supervisor.lock').open('w'); fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    assert gpu_free()
    state=read(ROOT/'results/methods_11_15_pipeline_state.json'); m=state['methods']['eaaw']
    assert m['status']=='TERMINAL' and m['scientific_status'] in ('BLOCKED_SOURCE','BLOCKED_DOWNLOAD') and 'TRAINING' not in m['completed_stages']
    prior=read(m['context']); rid=m['run_id']+'_cont1'; rr=batch/rid; rr.mkdir(); (rr/'receipts').mkdir()
    canonical=ROOT/'results/methods_11_15/eaaw/experiment_a'; hist=canonical/'history'/m['run_id']; hist.mkdir(parents=True)
    for name in ('full_experiment_log.json','summary.json','report.md'): shutil.copyfile(canonical/name,hist/name)
    idx=read(ROOT/'results/experiment_full_logs_index.json')
    for obj in idx['objects']:
        if obj['run_id']==m['run_id'] and obj['method']=='EaaW':
            obj['full_log_path']=str((hist/'full_experiment_log.json').relative_to(ROOT)); obj['full_log_sha256']=sha(hist/'full_experiment_log.json')
    write(ROOT/'results/experiment_full_logs_index.json',idx)
    c={**prior,'run_id':rid,'run_root':str(rr),'continuation_of':prior['run_id'],'repair':'Resolve verified local GPT-2 snapshot directory; retain official source bundle transport; no training had started.'}; write(rr/'context.json',c)
    m.update(run_id=rid,context=str(rr/'context.json'),stage='NOT_STARTED',status='NOT_STARTED',attempt=0,started_at=None,last_error=None,scientific_status='NOT_STARTED',git_status='PENDING',active_worker=None,completed_stages={},stage_attempts={})
    m['repair_history'].append({'time':now(),'action':c['repair'],'previous_run_id':prior['run_id'],'preserved_full_log':str(hist/'full_experiment_log.json')})
    write(ROOT/'results/methods_11_15_pipeline_state.json',state)
    print(rid)

if __name__=='__main__': main()
