"""Apply an identified engineering repair to a closed failed stage, retaining evidence."""
import fcntl, shutil
from common import *
from repairs import repair
batch=DATA/'runs/methods_11_15'
lock=(batch/'supervisor.lock').open('w'); fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
assert gpu_free()
state=read(ROOT/'results/methods_11_15_pipeline_state.json'); m=state['methods']['eaaw']; c=read(m['context'])
assert m['status']=='TERMINAL' and m['scientific_status'].startswith('BLOCKED_')
rr=Path(c['run_root']); stage=m['stage']; attempt=m['attempt']; result=rr/'receipts'/f'{stage}.{attempt}.json'
action=repair(c,stage,attempt,read(result),rr/f'{stage}.{attempt}.log')
assert action, 'No identified new engineering repair; do not reopen'
out=ROOT/'results/methods_11_15/eaaw/experiment_a'; hist=out/'versions'/f'{c["run_id"]}_{stage}_{attempt}'; hist.mkdir(parents=True)
for name in ('full_experiment_log.json','summary.json','report.md'): shutil.copyfile(out/name,hist/name)
action.update(stage=stage,attempt=attempt,time=now(),retained_report=str(hist))
m['repair_history'].append(action); m.setdefault('stage_attempts',{})[stage]=attempt
m.update(status='RUNNING',scientific_status='RUNNING',git_status='PENDING',last_error=None,active_worker=None)
write(ROOT/'results/methods_11_15_pipeline_state.json',state)
print(action)
