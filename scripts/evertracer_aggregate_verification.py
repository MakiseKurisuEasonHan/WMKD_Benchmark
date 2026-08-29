#!/usr/bin/env python3
"""Correct EverTracer ROC direction by aggregating saved per-sample scores only."""
import argparse,json
from pathlib import Path
from evertracer_common import corrected_detector_metrics,load_config,write_json

def main():
 p=argparse.ArgumentParser();p.add_argument("--config",required=True);p.add_argument("--input",required=True);p.add_argument("--output",required=True);p.add_argument("--source-run-id",required=True);a=p.parse_args();c=load_config(a.config);old=json.loads(Path(a.input).read_text());scores=old.get("scores")
 if not isinstance(scores,list) or len(scores)!=200:raise ValueError("saved verification output must contain exactly 200 per-sample scores")
 corrected=corrected_detector_metrics(scores,c["verification"]["fpr_limit"])
 result={"provenance":{"derived_from":a.input,"source_run_id":a.source_run_id,"derivation":"same saved calibrated scores using corrected official label/direction semantics","model_inference_rerun":False,"original_incorrect_metrics":{k:old[k] for k in ("auc","fsr","fpr","threshold")}},"label":old["label"],"suspect":old["suspect"],"reference":old["reference"],**corrected,"scores":scores}
 write_json(a.output,result);print(json.dumps({k:v for k,v in result.items() if k!="scores"},indent=2))
if __name__=="__main__":main()
