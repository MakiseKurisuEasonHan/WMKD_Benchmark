"""Read-only ModelScope metadata probe; persist evidence on the compute host."""
import inspect
import json
from pathlib import Path
from modelscope.hub.api import HubApi

root = Path('/root/autodl-tmp/WMKD_Benchmark_data/scale_7b/probes')
root.mkdir(parents=True, exist_ok=True)
api = HubApi()
print('SDK', inspect.signature(api.get_model_files), flush=True)
for repo in ['xinyuzhang/Llama-2-7b-hf', 'f541119578/Llama-2-7b-hf']:
    evidence = {'repo': repo}
    for key, call in [('metadata', lambda: api.get_model(repo)),
                      ('files', lambda: api.get_model_files(repo, revision='master', recursive=True))]:
        try:
            evidence[key] = call()
        except Exception as exc:
            evidence[key + '_error'] = str(exc)
    (root / (repo.replace('/', '__') + '.json')).write_text(json.dumps(evidence, indent=2, default=str))
    print(json.dumps(evidence, default=str), flush=True)
