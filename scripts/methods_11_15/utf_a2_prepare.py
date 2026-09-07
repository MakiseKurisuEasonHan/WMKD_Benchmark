"""Explicit UTF A2 source/data preparation only; never launches training."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

D = Path('/root/autodl-tmp/WMKD_Benchmark_data')
P = D.with_name('WMKD_Benchmark')
BASE = D / 'models/base/Llama-3.2-3B-Instruct'
MODEL = 'meta-llama/Llama-3.2-3B-Instruct'
OLD = D / 'runs/methods_11_15/utf_a_20260905_111830'
REV = '7155b38b077e18396bf550f839b27166c2011fe5'

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def write(p, obj):
    Path(p).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + '\n')

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--run-root', type=Path, required=True)
    a = ap.parse_args(); rr = a.run_root
    assert not rr.exists(), 'New A2 run directory required'
    source = D / 'sources/methods_11_15/utf'
    assert subprocess.check_output(['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip() == REV
    rr.mkdir(parents=True)
    shutil.copytree(source, rr/'work', ignore=shutil.ignore_patterns('.git', '__pycache__', '*.pyc'))
    # Copy the pinned, verified source rather than old 7B verification outputs.
    mag_source = OLD/'work/magikarp'
    shutil.copytree(mag_source, rr/'magikarp', ignore=shutil.ignore_patterns('.git', '__pycache__', '*.pyc', 'results', 'meta-llama'))
    provenance = json.loads((OLD/'magikarp_provenance.json').read_text())
    for name, entry in provenance['files'].items():
        assert sha(rr/'magikarp'/name) == entry['sha256'], name
    write(rr/'magikarp_source_provenance.json', provenance)
    patches = []
    def patch(path, old, new, reason):
        text = path.read_text(); assert text.count(old) == 1, str(path)
        before = sha(path); path.write_text(text.replace(old, new))
        patches.append(dict(path=str(path), before_sha256=before, after_sha256=sha(path), old=old, new=new, reason=reason))
    patch(rr/'work/fingerprint/utils/special_tokens.py', 'if "Llama-3.1-8B" in model_path:',
          'if "Llama-3.1-8B" in model_path or "Llama-3.2-3B-Instruct" in model_path:',
          'Same Llama-3 reserved-token range 128000:128256; architecture dispatch only')
    patch(rr/'magikarp/magikarp/unused_tokens.py', 'UNUSED_TOKENS = {',
          'UNUSED_TOKENS = {\n    "meta-llama/Llama-3.2-3B-Instruct": TIKTOKEN_UNUSED_TOKENS,',
          'Canonical tokenizer IDs 177:188 are the same invalid UTF-8 leading-byte F5:FF reference as registered Llama-3; use official tied-embedding cosine branch')
    patch(rr/'magikarp/magikarp/model.py',
          'from transformers import AutoModelForCausalLM, AutoConfig, AutoModelForImageTextToText',
          'from transformers import AutoModelForCausalLM, AutoConfig\ntry:\n    from transformers import AutoModelForImageTextToText\nexcept ImportError:\n    AutoModelForImageTextToText = None',
          'Unused optional vision import; canonical text branch unchanged')
    write(rr/'compatibility_patches.json', patches)
    for parent in [rr/'work', rr/'magikarp']:
        alias = parent/MODEL; alias.parent.mkdir(parents=True, exist_ok=True); alias.symlink_to(BASE, target_is_directory=True)
    env = os.environ.copy()
    env.update(HF_HUB_OFFLINE='1', HF_DATASETS_OFFLINE='1', TRANSFORMERS_OFFLINE='1', TOKENIZERS_PARALLELISM='false',
               PYTHONPATH=str(OLD/'runtime_overlay')+os.pathsep+str(rr/'magikarp'), OMP_NUM_THREADS='8', OPENBLAS_NUM_THREADS='8')
    write(rr/'preparation_state.json', dict(status='TOKEN_VERIFICATION', pid=os.getpid(), started_at=time.time()))
    assert not subprocess.check_output(['nvidia-smi', '--query-compute-apps=pid', '--format=csv,noheader'], text=True).strip()
    subprocess.run([sys.executable, '-u', str(rr/'magikarp/magikarp/fishing.py'), '--model_id', MODEL, '--device', 'cuda'], cwd=rr/'magikarp', env=env, check=True)
    tokens = rr/'magikarp/results/verifications/meta_llama_Llama_3_2_3B_Instruct.jsonl'
    assert tokens.is_file()
    subprocess.run([sys.executable, '-u', str(rr/'work/fingerprint/create_dataset.py'), '--method', 'ut', '--model_path', MODEL,
                    '--jsonl_path', str(tokens), '--output_path', str(rr/'fingerprint_data'), '--num_fingerprint', '32', '--num_regularization', '0',
                    '--x_length_min', '11', '--x_length_max', '15', '--y_length', '5'], cwd=rr/'work', env=env, check=True)
    rows = [json.loads(x) for x in (rr/'fingerprint_data/data.jsonl').read_text().splitlines()]
    assert len(rows) == 32 and len({json.dumps(x, sort_keys=True) for x in rows}) == 1
    write(rr/'preparation_state.json', dict(status='DATA_READY', pid=os.getpid(), completed_at=time.time(), records=32, unique_pairs=1,
          dataset_sha256=sha(rr/'fingerprint_data/data.jsonl'), tokens_sha256=sha(tokens), training_started=False))

if __name__ == '__main__':
    main()
