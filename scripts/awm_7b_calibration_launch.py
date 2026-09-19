"""Independent initial calibration launch; no auto shutdown or Student dispatch."""
import traceback
import pnfp_7b_distill_campaign as r
r.E=r.P/'results/awm/scale_7b';r.E.mkdir(parents=True,exist_ok=True)
r.ENV['PYTHONPATH']=str(r.P.parent/'WMKD_Benchmark_data/llmprint_7b/runtime451')+':'+str(r.P/'scripts')
try:
    r.run('calibration','awm_7b_detector.py',['calibrate'],additional=2**30)
except BaseException:r.put(r.E/'calibration_failure.json',dict(error=traceback.format_exc(),shutdown=False))
