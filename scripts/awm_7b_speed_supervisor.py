"""One timing run, sampled resource telemetry, no next stage and no shutdown."""
import json,traceback
from pathlib import Path
import pnfp_7b_distill_campaign as r
r.E=r.P/'results/awm/scale_7b_speed';r.E.mkdir(parents=True,exist_ok=True)
r.ENV['PYTHONPATH']=str(r.P.parent/'WMKD_Benchmark_data/llmprint_7b/runtime451')+':'+str(r.P/'scripts')
r.ENV['OMP_NUM_THREADS']='8'
try:
    r.run('canonical_timing','awm_7b_speed.py',[],additional=2**30)
except BaseException:
    r.put(r.E/'failure.json',dict(error=traceback.format_exc(),shutdown=False,training=False))
