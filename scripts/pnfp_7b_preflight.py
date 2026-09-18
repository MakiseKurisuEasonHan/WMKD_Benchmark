import importlib, json, os, shutil, sys, subprocess
from pathlib import Path
ROOT=Path('/root/autodl-tmp/WMKD_Benchmark_data/scale_7b')
sys.path.insert(0,str(ROOT/'pnfp_source'))
out={}
for name in ['torch','transformers','datasets','deepspeed','accelerate','lm_eval','finetune_multigpu']:
    m=importlib.import_module(name);out[name]=getattr(m,'__version__','imported')
from transformers import AutoTokenizer
t=AutoTokenizer.from_pretrained(ROOT/'models/Llama-2-7b-chat-hf',local_files_only=True)
out['chat_template']=t.chat_template
out['example_prompt']=t.apply_chat_template([{'role':'user','content':'Hello'}],tokenize=False,add_generation_prompt=True)
out['tokenizer_class']=type(t).__name__;out['vocab_size']=len(t)
out['ninja']=shutil.which('ninja');out['python']=sys.version
out['gpu']=subprocess.check_output(['nvidia-smi','--query-gpu=name,memory.total,memory.used','--format=csv,noheader'],text=True)
out['status']='PASS'
(ROOT/'environment_preflight.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out),flush=True)
