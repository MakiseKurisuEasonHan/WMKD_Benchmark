"""One method train->native detector->utility. Archive/next gates stay explicit."""
import datetime
import json
import os
from pathlib import Path
import subprocess
import sys

P=Path(__file__).resolve().parents[1];E=P/'results/logit_distillation/same_lineage_bc';m=sys.argv[1];q=E/m
env=dict(os.environ,HF_HUB_OFFLINE='1',HF_DATASETS_OFFLINE='1',TRANSFORMERS_OFFLINE='1',TOKENIZERS_PARALLELISM='false')
for stage,script in [('training','train_same_lineage_bc.py'),('evaluation','evaluate_same_lineage_bc.py')]:
    receipt=q/(stage+'_exit.json')
    if receipt.exists():
        assert json.loads(receipt.read_text())['returncode']==0,'Prior failed stage requires explicit engineering recovery';continue
    with (q/(stage+'_stdout.log')).open('a') as log:
        child=subprocess.Popen([sys.executable,'-u','-B',str(P/'scripts'/script),m],env=env,stdout=log,stderr=subprocess.STDOUT)
        (q/'active_stage.json').write_text(json.dumps({'stage':stage,'pid':child.pid,'supervisor_pid':os.getpid(),'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat()})+'\n')
        rc=child.wait()
    if rc:
        (q/'supervisor_exit.json').write_text(json.dumps({'returncode':rc,'stage':stage,'at':datetime.datetime.now(datetime.timezone.utc).isoformat()})+'\n');sys.exit(rc)
(q/'supervisor_exit.json').write_text(json.dumps({'returncode':0,'stage':'SCIENCE_COMPLETE_ARCHIVE_PENDING','at':datetime.datetime.now(datetime.timezone.utc).isoformat()})+'\n')
