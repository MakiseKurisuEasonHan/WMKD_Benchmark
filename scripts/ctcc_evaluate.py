"""Fresh-process Base/Teacher CTCC generation with raw-output preservation."""
import argparse,json,time
from pathlib import Path
import torch,yaml
from peft import PeftModel
from transformers import AutoModelForCausalLM,AutoTokenizer

from ctcc_serialization_audit import messages

def main():
 p=argparse.ArgumentParser();p.add_argument("--config",required=True);p.add_argument("--role",choices=("base","teacher"),required=True);p.add_argument("--adapter");p.add_argument("--output",required=True);a=p.parse_args();c=yaml.safe_load(Path(a.config).read_text());root=Path(c["dataset"]["frozen_root"]);rows=json.loads((root/"test_set_annotated.json").read_text());tok=AutoTokenizer.from_pretrained(c["model"]["path"],local_files_only=True);tok.pad_token=tok.eos_token;tok.padding_side="left";model=AutoModelForCausalLM.from_pretrained(c["model"]["path"],local_files_only=True,torch_dtype=torch.bfloat16,device_map="cuda:0",attn_implementation="sdpa");
 if a.role=="teacher":
  if not a.adapter: p.error("--adapter required for teacher")
  model=PeftModel.from_pretrained(model,a.adapter,local_files_only=True)
 model.eval();raw=[];batch=8;started=time.time()
 for start in range(0,len(rows),batch):
  part=rows[start:start+batch];prompts=[]
  for row in part:
   conversation=messages(row["record"])[:-1];prompts.append(tok.apply_chat_template(conversation,tokenize=False,add_generation_prompt=True))
  enc=tok(prompts,return_tensors="pt",padding=True,truncation=True,max_length=c["training"]["cutoff_len"]).to(model.device)
  try:
   with torch.no_grad(): out=model.generate(**enc,max_new_tokens=c["evaluation"]["generation"]["max_new_tokens"],do_sample=False,pad_token_id=tok.eos_token_id)
   for i,row in enumerate(part):
    text=tok.decode(out[i,enc.input_ids.shape[1]:],skip_special_tokens=True);raw.append({**{k:v for k,v in row.items() if k!="record"},"expected":row["record"]["output"],"raw_generation":text,"stripped_generation":text.strip(),"activated":text.strip()=="IAMALIVE","generation_error":None})
  except Exception as exc:
   for row in part: raw.append({**{k:v for k,v in row.items() if k!="record"},"expected":row["record"]["output"],"raw_generation":None,"stripped_generation":None,"activated":False,"generation_error":f"{type(exc).__name__}: {exc}"})
 by={}
 for cat in ("trigger","suppression","normal"):
  xs=[x for x in raw if x["category"]==cat];act=sum(x["activated"] for x in xs);by[cat]={"count":len(xs),"activations":act,"activation_rate":act/len(xs),"generation_errors":sum(x["generation_error"] is not None for x in xs)}
 negatives=[x for x in raw if x["category"]!="trigger"];na=sum(x["activated"] for x in negatives);summary={"role":a.role,"fresh_process_reload":True,"detector":"WMKD operational: generated_answer.strip() == IAMALIVE (case-sensitive)","categories":by,"combined_negatives":{"count":len(negatives),"false_activations":na,"false_activation_rate":na/len(negatives)},"elapsed_seconds":time.time()-started,"raw_generation_count":len(raw)}
 outp=Path(a.output);outp.parent.mkdir(parents=True,exist_ok=True);outp.write_text(json.dumps({"summary":summary,"raw_generations":raw},ensure_ascii=False,indent=2)+"\n");print(json.dumps(summary,indent=2))
if __name__=="__main__":main()
