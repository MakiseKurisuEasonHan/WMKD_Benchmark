"""Candidate small-file inspection plus bounded real-shard throughput sample."""
import json, time, shutil
from pathlib import Path
import requests
from modelscope.hub.file_download import model_file_download

root = Path('/root/autodl-tmp/WMKD_Benchmark_data/scale_7b/probes')
repo = 'f541119578/Llama-2-7b-hf'
out = {'repo': repo, 'small_files': {}, 'free_before': shutil.disk_usage(root).free}
for name in ['config.json', 'tokenizer_config.json', 'special_tokens_map.json', 'model.safetensors.index.json', 'README.md']:
    try:
        p = model_file_download(repo, name, revision='master', cache_dir=str(root/'sdk_cache'))
        data = Path(p).read_text()
        out['small_files'][name] = {'path': p, 'text': data}
        print(name, data[:4000], flush=True)
    except Exception as exc:
        out['small_files'][name] = {'error': str(exc)}

if 'text' not in out['small_files']['config.json']:
    raise RuntimeError('No readable model config')
cfg = json.loads(out['small_files']['config.json']['text'])
assert cfg['model_type'] == 'llama' and not cfg.get('quantization_config'), cfg
assert cfg['hidden_size'] == 4096 and cfg['num_hidden_layers'] == 32, cfg
name = 'model-00002-of-00002.safetensors'
url = f'https://modelscope.cn/api/v1/models/{repo}/repo'
# Only a 512 MiB transport sample. This Base candidate is not approved as the
# formal backbone; do not automatically acquire all weights before alignment.
start = time.monotonic()
target = root / 'base_candidate_shard_speed_sample.part'
size = 0
with requests.get(url, params={'Revision':'master','FilePath':name},
                  headers={'Range':'bytes=0-536870911'}, stream=True, timeout=(20,60)) as response:
    response.raise_for_status()
    out['http_status'] = response.status_code
    out['content_range'] = response.headers.get('Content-Range')
    with target.open('xb') as dest:
        for chunk in response.iter_content(4*1024*1024):
            if chunk:
                dest.write(chunk); size += len(chunk)
            if size >= 536870912 or time.monotonic()-start >= 60:
                break
elapsed = time.monotonic()-start
out['download_sample'] = {'file':name, 'path':str(target),'bytes':size,'seconds':elapsed,
                          'MB_per_second':size/elapsed/1e6,
                          'estimated_safetensors_download_seconds':13476876272/(size/elapsed),
                          'safetensors_weight_bytes':13476876272,
                          'formal_backbone_selected':False}
out['free_after'] = shutil.disk_usage(root).free
(root/'base_candidate_transport.json').write_text(json.dumps(out, indent=2))
print(json.dumps({k:v for k,v in out.items() if k!='small_files'}), flush=True)
