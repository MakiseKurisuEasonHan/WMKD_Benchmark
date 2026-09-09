"""Native frozen detector adapter for the four non-PNFP active Bc endpoints."""
import json
import os
from pathlib import Path
import sys
from active_ba_trajectory_detectors import run_detector

P=Path(__file__).resolve().parents[1]
m,model=sys.argv[1:3]
assert m in ('evertracer','ctcc','iseal','scw')
q=P/'results/logit_distillation/same_lineage_bc'/m
cfg=json.loads((q/'protocol.json').read_text())
spec=cfg['native_detector_spec'];spec['run_id']=cfg['run_id']
assert spec['method_key']==m
result=run_detector(spec,model,q/'native_detector',P,sys.executable,os.environ.copy())
(q/'detector_results.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
