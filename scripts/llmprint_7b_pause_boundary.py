"""User-requested pause after the active fingerprint's atomic completion."""
import os,signal,time,json,hashlib
from pathlib import Path
E=Path('/root/autodl-tmp/WMKD_Benchmark/results/llmprint/scale_7b')
def check(pid,needle):
    assert needle in Path(f'/proc/{pid}/cmdline').read_bytes().decode().replace('\0',' ')
check(4328,'llmprint_7b_campaign.py');check(2714,'llmprint_7b_construct.py');check(2719,'llmprint_construct_fingerprints.py')
for pid in [4328,2714]:os.kill(pid,signal.SIGTERM)
files=list((E/'fingerprints').glob('*.json'));before=len(files)
(E/'pause_requested.json').write_text(json.dumps(dict(status='PAUSE_REQUESTED',completed_before=before,time=time.time(),auto_shutdown=False)))
while len(list((E/'fingerprints').glob('*.json')))<=before:
    os.kill(2719,0);time.sleep(.005)
os.kill(2719,signal.SIGSTOP)
rows=[]
for f in sorted((E/'fingerprints').glob('*.json')):
    x=json.loads(f.read_text());assert x['status']=='COMPLETED' and x['gcg_iterations_completed']==500
    rows.append(dict(path=f.name,sha256=hashlib.sha256(f.read_bytes()).hexdigest(),iterations=500,runtime_seconds=x['runtime_seconds']))
os.kill(2719,signal.SIGTERM);os.kill(2719,signal.SIGCONT)
state=dict(status='PAUSED_FOR_AWM_SPEED_COMPARISON',completed_fingerprints=len(rows),target=200,
    next_pair_id=f'llmprint-pair-{len(rows):03d}',fingerprints=rows,negative_calibration='NOT_STARTED',
    negative_downloads='13/13 preserved',auto_shutdown=False,time=time.time(),
    boundary='Waited for next atomic fingerprint completion, then stopped worker; completed records retained',
    resume='Use saved original construction command; completed records are skipped. Re-arm full campaign only after user approval.')
(E/'pause_receipt.json').write_text(json.dumps(state,indent=2)+'\n')
(E/'campaign_state.json').write_text(json.dumps(state,indent=2)+'\n')
print(json.dumps(state),flush=True)
