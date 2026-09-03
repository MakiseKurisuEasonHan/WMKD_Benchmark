#!/usr/bin/env python3
"""Fresh-process reload and manifest validation for the Bb3 Student."""
from __future__ import annotations
import argparse, hashlib, json, math, os, time
from pathlib import Path
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

def sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda:f.read(1<<20),b""): h.update(block)
    return h.hexdigest()

def atomic(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_suffix(path.suffix+".tmp")
    tmp.write_text(json.dumps(value,indent=2,ensure_ascii=False)+"\n",encoding="utf-8");os.replace(tmp,path)

def main():
    p=argparse.ArgumentParser();p.add_argument("--student",type=Path,required=True);p.add_argument("--dataset-sha",required=True)
    p.add_argument("--output",type=Path,required=True);p.add_argument("--manifest",type=Path,required=True);a=p.parse_args()
    files={str(x.relative_to(a.student)):sha(x) for x in sorted(a.student.rglob("*")) if x.is_file()}
    adapters=[name for name in files if "adapter" in name.casefold() or "lora" in name.casefold()]
    if adapters: raise RuntimeError(f"UNEXPECTED_ADAPTER_FILES {adapters}")
    manifest={"schema_version":"wmkd.passive5-shared-bb3-student.v1","status":"PASS",
              "artifact":str(a.student),"dataset_sha256":a.dataset_sha,"files_sha256":files,
              "file_count":len(files),"full_parameter":True,"resume":False,
              "base_model":"meta-llama/Llama-3.2-3B-Instruct",
              "base_revision":"0cb88a4f764b7a12671c53f0838cd831a0843b95"}
    atomic(a.manifest,manifest);started=time.time();torch.cuda.reset_peak_memory_stats()
    tok=AutoTokenizer.from_pretrained(a.student,local_files_only=True,trust_remote_code=True)
    model=AutoModelForCausalLM.from_pretrained(a.student,local_files_only=True,trust_remote_code=True,
                                               torch_dtype=torch.bfloat16,device_map="cuda:0").eval()
    prompt="Reply with exactly: WMKD_RELOAD_PASS"
    rendered=tok.apply_chat_template([{"role":"user","content":prompt}],tokenize=False,add_generation_prompt=True)
    encoded=tok(rendered,return_tensors="pt").to("cuda:0")
    with torch.inference_mode(): generated=model.generate(**encoded,max_new_tokens=16,do_sample=False)
    response=tok.decode(generated[0,encoded["input_ids"].shape[1]:],skip_special_tokens=True).strip()
    count=bad=0;low=math.inf;high=-math.inf
    with torch.inference_mode():
        for parameter in model.parameters():
            value=parameter.detach();count+=value.numel();finite=torch.isfinite(value);current=value.numel()-int(finite.sum());bad+=current
            if not current and value.numel(): low=min(low,float(value.min()));high=max(high,float(value.max()))
    result={"status":"PASS" if response and bad==0 else "FAIL","fresh_process_reload":True,
            "student_path":str(a.student),"student_manifest_sha256":sha(a.manifest),
            "tokenizer":{"class":tok.__class__.__name__,"vocab_size":len(tok),"chat_template_present":bool(tok.chat_template)},
            "inference_smoke":{"prompt":prompt,"response":response,"pass":bool(response)},
            "finite_weight_check":{"parameter_count":count,"nonfinite_count":bad,"minimum":low,"maximum":high,"pass":bad==0},
            "adapter_files":adapters,"peak_vram_bytes":torch.cuda.max_memory_allocated(),"runtime_seconds":time.time()-started}
    atomic(a.output,result);print(json.dumps(result,ensure_ascii=False))
    if result["status"]!="PASS": raise RuntimeError("STUDENT_RELOAD_VALIDATION_FAILED")

if __name__=="__main__":main()
