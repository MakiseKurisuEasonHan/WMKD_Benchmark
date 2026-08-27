#!/usr/bin/env python3
"""Small fixed ordinary-generation comparison for the non-formal A2 smoke."""
import argparse, json, re
from pathlib import Path
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
PROMPTS = ["What is the capital of Australia? Answer briefly.", "Explain why the sky appears blue in three sentences.",
    "If a train travels 120 km in 2 hours, what is its average speed?",
    "Write a Python function that returns the largest number in a non-empty list.",
    "Explain the difference between a list and a tuple in Python.", "Rewrite politely: Send me the report today.",
    "Classify the sentiment as positive, negative, or neutral: The service was quick and friendly.",
    "Why do plants need sunlight?", "Which is larger, 3/4 or 2/3? Explain briefly.",
    "Correct the grammar: She don't like cold weather."]
def run_model(path):
    tok = AutoTokenizer.from_pretrained(path, local_files_only=True); tok.pad_token = tok.pad_token or tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(path, local_files_only=True, torch_dtype=torch.bfloat16, device_map="cuda").eval(); rows=[]
    for i, content in enumerate(PROMPTS):
        torch.manual_seed(4200+i); prompt=tok.apply_chat_template([{"role":"user","content":content}], tokenize=False, add_generation_prompt=True)
        encoded=tok(prompt, return_tensors="pt", add_special_tokens=False).to("cuda")
        with torch.inference_mode(): output=model.generate(**encoded,max_new_tokens=128,do_sample=True,temperature=0.8,top_p=0.95,pad_token_id=tok.pad_token_id)
        tokens=output[0,encoded["input_ids"].shape[1]:]; text=tok.decode(tokens,skip_special_tokens=True); words=re.findall(r"\w+",text.lower()); ratio=len(set(words))/len(words) if words else 0.0
        rows.append({"prompt":content,"response":text,"generated_tokens":len(tokens),"reached_max_tokens":len(tokens)>=128,"obvious_repetition":bool(words) and ratio<0.15,"unique_word_ratio":ratio})
    del model; torch.cuda.empty_cache(); return rows
def main():
    p=argparse.ArgumentParser(); p.add_argument("--base",required=True); p.add_argument("--smoke",required=True); p.add_argument("--a1"); p.add_argument("--output",required=True); a=p.parse_args()
    result={"base":run_model(a.base)}
    if a.a1: result["a1"]=run_model(a.a1)
    result["a2_smoke"]=run_model(a.smoke)
    for label in tuple(result):
        rows=result[label]; result[label+"_summary"]={"calls":len(rows),"max_token_hits":sum(x["reached_max_tokens"] for x in rows),"obvious_repetition":sum(x["obvious_repetition"] for x in rows)}
    Path(a.output).write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); print(json.dumps({k:v for k,v in result.items() if k.endswith("_summary")}))
if __name__ == "__main__": main()
