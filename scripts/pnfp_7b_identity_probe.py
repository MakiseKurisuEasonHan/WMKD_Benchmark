import json, requests
from pathlib import Path
root=Path('/root/autodl-tmp/WMKD_Benchmark_data/scale_7b/probes')
urls={
 'canonical_chat': 'https://huggingface.co/api/models/meta-llama/Llama-2-7b-chat-hf/revision/f5db02db724555f92da89c216ac04704f23d4590?blobs=true',
 'modelscope_chat': 'https://modelscope.cn/api/v1/models/shakechen/Llama-2-7b-chat-hf/repo/files?Revision=299e68d813ff6f146741f8e8477ed0a57ded4765&Recursive=true',
}
for label,url in urls.items():
    try:
        r=requests.get(url,timeout=30);r.raise_for_status(); d=r.json()
        (root/(label+'_identity.json')).write_text(json.dumps(d,indent=2))
        print(label,json.dumps(d)[:14000],flush=True)
    except Exception as e: print(label,repr(e),flush=True)
