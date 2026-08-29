"""Standard offline ARC/TruthfulQA evaluation for a fresh-reloaded full Student."""
import argparse, json, os
from pathlib import Path
import lm_eval, yaml


def main():
    p=argparse.ArgumentParser(); p.add_argument("--config",required=True); p.add_argument("--student",required=True); p.add_argument("--output",required=True); a=p.parse_args()
    c=yaml.safe_load(Path(a.config).read_text()); u=c["utility"]
    os.environ.update({"HF_HOME":str(Path(u["hub_cache"]).parent),"HF_HUB_CACHE":u["hub_cache"],"HF_DATASETS_CACHE":u["datasets_cache"],"HF_HUB_OFFLINE":"1","HF_DATASETS_OFFLINE":"1","TRANSFORMERS_OFFLINE":"1"})
    args=f"pretrained={a.student},local_files_only=True,trust_remote_code=True,dtype=bfloat16"
    r=lm_eval.simple_evaluate(model="hf",model_args=args,tasks=["arc_challenge","truthfulqa_mc2"],batch_size=u["batch_size"],apply_chat_template=True)
    x=r["results"]; result={"student":{"arc_challenge_acc_norm":x["arc_challenge"].get("acc_norm,none",x["arc_challenge"].get("acc_norm")),"truthfulqa_mc2_acc":x["truthfulqa_mc2"].get("acc,none",x["truthfulqa_mc2"].get("acc")),"raw_results":x},"dataset_provenance":u["datasets"],"fresh_process_reload":True}
    Path(a.output).write_text(json.dumps(result,indent=2)+"\n"); print(json.dumps({"student":{k:v for k,v in result["student"].items() if k!="raw_results"}},indent=2))


if __name__=="__main__": main()
