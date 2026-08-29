#!/usr/bin/env python3
"""Standard WMKD ARC/TruthfulQA utility comparison."""
import argparse,json,os
from pathlib import Path
from evertracer_common import load_config,validate_utility_local_artifacts

def configure_offline_utility(config):
    utility=config["utility"]
    os.environ.update({"HF_HOME":str(Path(utility["hub_cache"]).parent),"HF_HUB_CACHE":utility["hub_cache"],"HF_DATASETS_CACHE":utility["datasets_cache"],"HF_HUB_OFFLINE":"1","HF_DATASETS_OFFLINE":"1","TRANSFORMERS_OFFLINE":"1"})
    return validate_utility_local_artifacts(utility)
def load_offline_dataset_smoke(config):
    from datasets import load_dataset
    result={}
    for name,spec in config["utility"]["datasets"].items():
        dataset=load_dataset(spec["id"],spec["config"],revision=spec["revision"],cache_dir=config["utility"]["datasets_cache"])
        result[name]={"revision":spec["revision"],"splits":{split:len(rows) for split,rows in dataset.items()}}
    return result
def evaluate(path,batch):
    import lm_eval
    r=lm_eval.simple_evaluate(model="hf",model_args=f"pretrained={path},local_files_only=True,trust_remote_code=True,dtype=bfloat16",tasks=["arc_challenge","truthfulqa_mc2"],batch_size=batch,apply_chat_template=True)
    x=r["results"];return {"path":path,"arc_challenge_acc_norm":x["arc_challenge"].get("acc_norm,none",x["arc_challenge"].get("acc_norm")),"truthfulqa_mc2_acc":x["truthfulqa_mc2"].get("acc,none",x["truthfulqa_mc2"].get("acc")),"raw_results":x}
def main():
    p=argparse.ArgumentParser();p.add_argument("--config",required=True);p.add_argument("--base");p.add_argument("--teacher");p.add_argument("--output");p.add_argument("--batch-size",type=int,default=8);p.add_argument("--check-local-data-only",action="store_true");a=p.parse_args();provenance=configure_offline_utility(load_config(a.config));
    if a.check_local_data_only:print(json.dumps({"offline":True,"datasets":provenance,"loaded":load_offline_dataset_smoke(load_config(a.config))},indent=2));return
    if not all((a.base,a.teacher,a.output)):p.error("--base, --teacher, and --output are required unless --check-local-data-only is used")
    b=evaluate(a.base,a.batch_size);t=evaluate(a.teacher,a.batch_size);r={"dataset_provenance":provenance,"offline":True,"base":b,"teacher":t,"delta":{"arc_challenge_acc_norm":t["arc_challenge_acc_norm"]-b["arc_challenge_acc_norm"],"truthfulqa_mc2_acc":t["truthfulqa_mc2_acc"]-b["truthfulqa_mc2_acc"]}};Path(a.output).write_text(json.dumps(r,indent=2)+"\n");print(json.dumps({"base":{k:v for k,v in b.items() if k!="raw_results"},"teacher":{k:v for k,v in t.items() if k!="raw_results"},"delta":r["delta"],"offline":True,"dataset_provenance":provenance},indent=2))
if __name__=="__main__":main()
