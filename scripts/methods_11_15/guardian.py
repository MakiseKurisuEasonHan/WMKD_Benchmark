"""Restart a crashed supervisor, whose receipts/owned workers survive independently."""
import fcntl, subprocess, sys, time
from common import *
require_execution_unpaused()
batch=DATA/'runs/methods_11_15'; batch.mkdir(parents=True,exist_ok=True)
lock=(batch/'guardian.lock').open('w'); fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
for attempt in range(1,4):
    require_execution_unpaused()
    p=subprocess.Popen([PY,'-u',Path(__file__).with_name('run_methods_11_15.py')])
    write(batch/'guardian.json',{'guardian_pid':os.getpid(),'supervisor_pid':p.pid,'restart_attempt':attempt,'started_at':now()})
    code=p.wait()
    if code==0: break
    write(batch/'guardian_failure.json',{'time':now(),'exit_code':code,'attempt':attempt,'action':'Reattach existing stage worker and durable receipts; never restart a successful expensive stage'})
    time.sleep(attempt*10)
else:
    write(batch/'NEEDS_ENGINEERING_ATTENTION.json',{'time':now(),'reason':'Supervisor crashed three times; all existing workers and evidence retained, shutdown not authorized at incomplete state'})
