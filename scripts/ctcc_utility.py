"""Standard offline ARC/TruthfulQA comparison for Base and CTCC LoRA Teacher."""
import argparse,json,os
from pathlib import Path
import lm_eval,yaml

def evaluate(base,peft,batch):
 args=f"pretrained={base},local_files_only=True,trust_remote_code=True,dtype=bfloat16"+(f",peft={peft}" if peft else "")
 r=lm_eval.simple_evaluate(model="hf",model_args=args,tasks=["arc_challenge","truthfulqa_mc2"],batch_size=batch,apply_chat_template=True);x=r["results"]
 return {"arc_challenge_acc_norm":x["arc_challenge"].get("acc_norm,none",x["arc_challenge"].get("acc_norm")),"truthfulqa_mc2_acc":x["truthfulqa_mc2"].get("acc,none",x["truthfulqa_mc2"].get("acc")),"raw_results":x}
def main():
 p=argparse.ArgumentParser();p.add_argument("--config",required=True);p.add_argument("--adapter",required=True);p.add_argument("--output",required=True);a=p.parse_args();c=yaml.safe_load(Path(a.config).read_text());u=c["evaluation"]["utility"];os.environ.update({"HF_HOME":str(Path(u["hub_cache"]).parent),"HF_HUB_CACHE":u["hub_cache"],"HF_DATASETS_CACHE":u["datasets_cache"],"HF_HUB_OFFLINE":"1","HF_DATASETS_OFFLINE":"1","TRANSFORMERS_OFFLINE":"1"});base=evaluate(c["model"]["path"],None,u["batch_size"]);teacher=evaluate(c["model"]["path"],a.adapter,u["batch_size"]);result={"base":base,"teacher":teacher,"delta":{"arc_challenge_acc_norm":teacher["arc_challenge_acc_norm"]-base["arc_challenge_acc_norm"],"truthfulqa_mc2_acc":teacher["truthfulqa_mc2_acc"]-base["truthfulqa_mc2_acc"]},"dataset_provenance":u["datasets"]};Path(a.output).write_text(json.dumps(result,indent=2)+"\n");print(json.dumps({"base":{k:v for k,v in base.items() if k!="raw_results"},"teacher":{k:v for k,v in teacher.items() if k!="raw_results"},"delta":result["delta"]},indent=2))
if __name__=="__main__":main()
