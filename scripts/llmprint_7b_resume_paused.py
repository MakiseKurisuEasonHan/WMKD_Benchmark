"""Explicitly authorized future resume only; preserves completed GCG and logs."""
import argparse,json,hashlib,shutil,subprocess,time
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--execute-approved-resume',action='store_true');args=p.parse_args()
assert args.execute_approved_resume,'Requires a new explicit user decision to resume LLMPrint'
P=Path('/root/autodl-tmp/WMKD_Benchmark');E=P/'results/llmprint/scale_7b'
r=json.loads((E/'pause_receipt.json').read_text());assert r['status']=='PAUSED_FOR_AWM_SPEED_COMPARISON'
for x in r['fingerprints']:
    f=E/'fingerprints'/x['path'];assert hashlib.sha256(f.read_bytes()).hexdigest()==x['sha256']
assert not subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader'],text=True).strip()
archive=E/'pre_resume_history'/str(int(time.time()));archive.mkdir(parents=True)
for name in ['construction.log','construction_supervisor.log','construction_runtime.json','campaign_state.json','campaign_supervisor.log']:
    f=E/name
    if f.exists():shutil.copy2(f,archive/name)
# Existing constructor skips every completed pair and validates all200 at end.
# This command resumes construction only; re-arm the serial campaign and local
# guardian separately after the user's scope decision. No automatic shutdown.
subprocess.run([str(P.parent/'WMKD_Benchmark_data/scale_7b/env/bin/python'),str(P/'scripts/llmprint_7b_construct.py')],check=True)
