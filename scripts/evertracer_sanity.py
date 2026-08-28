#!/usr/bin/env python3
"""Low-cost ordinary-generation sanity and independent reload check."""
import argparse,json,re,time
from pathlib import Path
import torch
from transformers import AutoModelForCausalLM,AutoTokenizer

PROMPTS=["Explain why the sky appears blue in two sentences.","Write a polite email declining a meeting invitation.","Give three practical tips for saving household energy.","What is 17 multiplied by 23? Explain briefly.","Summarize the benefits and risks of regular exercise."]
def main():
 p=argparse.ArgumentParser();p.add_argument("--model",required=True);p.add_argument("--output",required=True);p.add_argument("--max-new-tokens",type=int,default=96);a=p.parse_args();start=time.monotonic();tok=AutoTokenizer.from_pretrained(a.model,local_files_only=True);model=AutoModelForCausalLM.from_pretrained(a.model,local_files_only=True,torch_dtype=torch.bfloat16,device_map="cuda:0").eval();rows=[]
 for prompt in PROMPTS:
  rendered=tok.apply_chat_template([{"role":"user","content":prompt}],tokenize=False,add_generation_prompt=True);enc=tok(rendered,return_tensors="pt").to(model.device)
  with torch.no_grad():out=model.generate(**enc,max_new_tokens=a.max_new_tokens,do_sample=False,pad_token_id=tok.eos_token_id)
  text=tok.decode(out[0,enc.input_ids.shape[1]:],skip_special_tokens=True).strip();words=text.split();unique=len(set(words))/max(len(words),1);rows.append({"prompt":prompt,"response":text,"empty":not bool(text),"prompt_echo":prompt.lower() in text.lower(),"catastrophic_repetition":len(words)>=20 and unique<0.2,"hit_max_tokens":out.shape[1]-enc.input_ids.shape[1]>=a.max_new_tokens})
 result={"model":a.model,"fresh_process_reload":True,"elapsed_seconds":time.monotonic()-start,"rows":rows,"passed":not any(x["empty"] or x["catastrophic_repetition"] or x["prompt_echo"] for x in rows)};Path(a.output).write_text(json.dumps(result,indent=2)+"\n");print(json.dumps(result,indent=2))
if __name__=="__main__":main()
