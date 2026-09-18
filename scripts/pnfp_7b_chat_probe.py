import json
from pathlib import Path
from modelscope.hub.api import HubApi
from modelscope.hub.file_download import model_file_download
root=Path('/root/autodl-tmp/WMKD_Benchmark_data/scale_7b/probes')
api=HubApi()
for repo in ['LLM-Research/Llama-2-7b-chat-hf','shakechen/Llama-2-7b-chat-hf','f541119578/Llama-2-7b-chat-hf']:
    out={'repo':repo}
    try:
        out['metadata']=api.get_model(repo)
        out['files']=api.get_model_files(repo,revision='master',recursive=True)
        for name in ['config.json','tokenizer_config.json']:
            p=model_file_download(repo,name,revision='master',cache_dir=str(root/'sdk_cache'))
            out[name]=json.loads(Path(p).read_text())
    except Exception as e:out['error']=str(e)
    (root/(repo.replace('/','__')+'.json')).write_text(json.dumps(out,indent=2,default=str))
    print(json.dumps(out,default=str),flush=True)
