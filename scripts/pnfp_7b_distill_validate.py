import json,sys
from pathlib import Path
import torch
P=Path('/root/autodl-tmp/WMKD_Benchmark');sys.path.insert(0,str(P/'scripts'))
from pnfp_bc_pilot import ResponseObjective,objective_test
from pnfp_7b_distill_worker import IndexedDataset,IndexedCollator
from transformers import AutoTokenizer
import bitsandbytes as bnb
objective_test()
torch.manual_seed(42)
t=torch.randn(67,127,dtype=torch.bfloat16);s=torch.randn(67,127,dtype=torch.bfloat16,requires_grad=True);labels=torch.randint(127,(67,))
import numpy as np
raw=t.view(torch.uint16).numpy().tobytes();r=torch.from_numpy(np.frombuffer(raw,dtype=np.uint16).copy()).view(torch.bfloat16).reshape(t.shape)
assert torch.equal(t,r)
a=ResponseObjective.apply(s,t,labels)[0];ga=torch.autograd.grad(a,s)[0]
b=ResponseObjective.apply(s,r,labels)[0];gb=torch.autograd.grad(b,s)[0]
assert torch.equal(a,b) and torch.equal(ga,gb)
base=P.parent/'WMKD_Benchmark_data/scale_7b/models/Llama-2-7b-chat-hf';teacher=P.parent/'WMKD_Benchmark_data/scale_7b/wa050_extension_v1/best_model'
x=AutoTokenizer.from_pretrained(base,local_files_only=True);y=AutoTokenizer.from_pretrained(teacher,local_files_only=True)
assert x.get_vocab()==y.get_vocab()
messages=[{'role':'user','content':'Explain gravity.'},{'role':'assistant','content':'Gravity attracts masses.'}]
assert x.apply_chat_template(messages)==y.apply_chat_template(messages)
result={'status':'PASS','objective_test':'canonical CE/KL forward and gradient','bf16_storage_roundtrip':'bitwise identical targets/loss/gradient','token_id_maps':'equal','chat_template_example':'equal','bnb_version':bnb.__version__,'torch':torch.__version__}
(P/'results/pnfp/scale_7b/distillation_6004/engineering_validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
