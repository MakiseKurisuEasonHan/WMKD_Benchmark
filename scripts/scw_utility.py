"""Fresh-process standardized and supplementary SCW utility panel."""
import argparse,gc,json,os
from pathlib import Path

def lm(path,batch):
 import lm_eval
 r=lm_eval.simple_evaluate(model="hf",model_args=f"pretrained={path},local_files_only=True,dtype=bfloat16",tasks=["arc_challenge","truthfulqa_mc2"],batch_size=batch,apply_chat_template=True)["results"]
 return {"arc_challenge_acc_norm":r["arc_challenge"].get("acc_norm,none",r["arc_challenge"].get("acc_norm")),"truthfulqa_mc2_acc":r["truthfulqa_mc2"].get("acc,none",r["truthfulqa_mc2"].get("acc")),"raw_results":r}
def sanity(path,prompts):
 import torch
 from transformers import AutoModelForCausalLM,AutoTokenizer
 t=AutoTokenizer.from_pretrained(path,local_files_only=True); t.pad_token=t.pad_token or t.eos_token
 m=AutoModelForCausalLM.from_pretrained(path,local_files_only=True,torch_dtype=torch.bfloat16,device_map="cuda").eval(); rows=[]
 for x in prompts:
  q=t(x,return_tensors="pt").to("cuda")
  with torch.no_grad(): y=m.generate(**q,max_new_tokens=64,do_sample=False,pad_token_id=t.pad_token_id)
  s=t.decode(y[0][q.input_ids.shape[1]:],skip_special_tokens=True); rows.append({"prompt":x,"completion":s,"functional":bool(s.strip()) and len(set(s.split()))>2})
 del m; gc.collect(); torch.cuda.empty_cache(); return {"passed":all(x["functional"] for x in rows),"rows":rows}
def main():
 p=argparse.ArgumentParser();p.add_argument("--base",required=True);p.add_argument("--teacher",required=True);p.add_argument("--output",required=True);p.add_argument("--batch-size",type=int,default=8);a=p.parse_args()
 os.environ.update({"HF_HOME":"/root/autodl-tmp/WMKD_Benchmark_data/cache/huggingface","HF_HUB_CACHE":"/root/autodl-tmp/WMKD_Benchmark_data/cache/huggingface/hub","HF_DATASETS_CACHE":"/root/autodl-tmp/WMKD_Benchmark_data/cache/huggingface/datasets","HF_HUB_OFFLINE":"1","HF_DATASETS_OFFLINE":"1","TRANSFORMERS_OFFLINE":"1"})
 b=lm(a.base,a.batch_size); t=lm(a.teacher,a.batch_size)
 ordinary=["What is the capital of France?","Explain why the sky appears blue.","Solve: 3x + 5 = 20.","Write a polite thank-you note."]
 french=["Expliquez simplement pourquoi le ciel est bleu.","Rédigez un court message de remerciement.","Résolvez 3x + 5 = 20 en français.","Donnez trois conseils pour organiser une journée chargée."]
 r={"fresh_process_reload":True,"base":b,"teacher":t,"delta":{"arc_challenge_acc_norm":t["arc_challenge_acc_norm"]-b["arc_challenge_acc_norm"],"truthfulqa_mc2_acc":t["truthfulqa_mc2_acc"]-b["truthfulqa_mc2_acc"]},"ordinary_generation":{"base":sanity(a.base,ordinary),"teacher":sanity(a.teacher,ordinary)},"french_supplementary":{"base":sanity(a.base,french),"teacher":sanity(a.teacher,french)}}
 Path(a.output).parent.mkdir(parents=True,exist_ok=True);Path(a.output).write_text(json.dumps(r,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
if __name__=="__main__":main()
