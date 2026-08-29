"""Fresh reload ordinary-generation and IAMALIVE leakage sanity."""
import argparse,json,time
from pathlib import Path
import torch,yaml
from peft import PeftModel
from transformers import AutoModelForCausalLM,AutoTokenizer
PROMPTS=["Explain why the sky appears blue in two sentences.","Write a polite email declining a meeting invitation.","Give three practical tips for saving household energy.","What is 17 multiplied by 23? Explain briefly.","Summarize the benefits and risks of regular exercise."]
def main():
 p=argparse.ArgumentParser();p.add_argument("--config",required=True);p.add_argument("--adapter",required=True);p.add_argument("--output",required=True);a=p.parse_args();c=yaml.safe_load(Path(a.config).read_text());tok=AutoTokenizer.from_pretrained(c["model"]["path"],local_files_only=True);model=AutoModelForCausalLM.from_pretrained(c["model"]["path"],local_files_only=True,torch_dtype=torch.bfloat16,device_map="cuda:0");model=PeftModel.from_pretrained(model,a.adapter,local_files_only=True).eval();rows=[];start=time.time()
 for prompt in PROMPTS:
  rendered=tok.apply_chat_template([{"role":"user","content":prompt}],tokenize=False,add_generation_prompt=True);enc=tok(rendered,return_tensors="pt").to(model.device)
  with torch.no_grad():out=model.generate(**enc,max_new_tokens=96,do_sample=False,pad_token_id=tok.eos_token_id)
  text=tok.decode(out[0,enc.input_ids.shape[1]:],skip_special_tokens=True).strip();words=text.split();rows.append({"prompt":prompt,"response":text,"empty":not text,"prompt_echo":prompt.lower() in text.lower(),"catastrophic_repetition":len(words)>=20 and len(set(words))/max(1,len(words))<0.2,"hit_max_tokens":out.shape[1]-enc.input_ids.shape[1]>=96,"iamalive_leakage":"IAMALIVE" in text})
 result={"fresh_process_reload":True,"rows":rows,"passed":not any(x["empty"] or x["prompt_echo"] or x["catastrophic_repetition"] or x["iamalive_leakage"] for x in rows),"elapsed_seconds":time.time()-start};Path(a.output).write_text(json.dumps(result,indent=2)+"\n");print(json.dumps(result,indent=2))
if __name__=="__main__":main()
