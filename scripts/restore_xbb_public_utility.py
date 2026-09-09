"""Restore only pinned public utility data; never evaluate a model."""
import os
from pathlib import Path
import json
import hashlib
import datetime

D = Path('/root/autodl-tmp/WMKD_Benchmark_data')
P = Path('/root/autodl-tmp/WMKD_Benchmark')
os.environ.update(HF_ENDPOINT='https://hf-mirror.com', HF_HOME=str(D/'cache/huggingface'), HF_HUB_CACHE=str(D/'cache/huggingface/hub'), HF_DATASETS_CACHE=str(D/'cache/huggingface/datasets'), HF_HUB_DISABLE_IMPLICIT_TOKEN='1', HF_HUB_DOWNLOAD_TIMEOUT='45')
for key in ['HF_HUB_OFFLINE', 'HF_DATASETS_OFFLINE', 'TRANSFORMERS_OFFLINE']:
    os.environ.pop(key, None)

from huggingface_hub import snapshot_download
from datasets import load_dataset

SPECS = [
    ('allenai/ai2_arc', 'ARC-Challenge', '210d026faf9955653af8916fad021475a3f00453', {
        'README.md': (9001, '4a293e352253d771604725c978adcea71ee6504e89ed40e1cb0024ecafa9b37e'),
        'ARC-Challenge/test-00000-of-00001.parquet': (203808, '62f03257e737aed263f55c6abf87c7bb0028a44a6bdd2a26eb1279eb42c1d1e9'),
        'ARC-Challenge/train-00000-of-00001.parquet': (189909, 'e488c1587ffdcfc8443f916c53488a95cd471c5790e0746c6bfe4cecf20962cb'),
        'ARC-Challenge/validation-00000-of-00001.parquet': (55743, '395a5c88d1580d69855fbaee9450270578df1ad5af6259771cd0a42c20e99f05'),
    }),
    ('truthful_qa', 'multiple_choice', '741b8276f2d1982aa3d5b832d3ee81ed3b896490', {
        'README.md': (9588, '9e06075e7a580802a227e31cc456b37bdf5a174637f22e142b7609d709dd5f95'),
        'multiple_choice/validation-00000-of-00001.parquet': (271033, '23f08e230ca4ed66babf3a72419af7cbde1f3d734dd396ac4cf6d088bd162afd'),
    }),
]


def main():
    results = []
    out = P/'results/active_cross_lineage_bb/public_utility_restore.json'
    for repo, config, revision, expected in SPECS:
        print(json.dumps({'stage': 'RESTORE_PUBLIC_FROZEN_DATA', 'repo': repo}), flush=True)
        snapshot = Path(snapshot_download(repo_id=repo, repo_type='dataset', revision=revision, allow_patterns=list(expected), max_workers=1, token=False))
        checks = []
        for name, (size, digest) in expected.items():
            f = snapshot/name
            assert f.stat().st_size == size and hashlib.sha256(f.read_bytes()).hexdigest() == digest, name
            checks.append(dict(path=name, bytes=size, sha256=digest, match=True))
        dataset = load_dataset(repo, config, revision=revision, cache_dir=str(D/'cache/huggingface/datasets'), token=False)
        counts = {k: len(v) for k,v in dataset.items()}
        assert counts == ({'train': 1119, 'test': 1172, 'validation': 299} if config == 'ARC-Challenge' else {'validation': 817}), counts
        results.append(dict(repo=repo, config=config, revision=revision, snapshot=str(snapshot), files=checks, splits=counts))
        out.write_text(json.dumps({'status': 'PASS' if len(results)==2 else 'IN_PROGRESS', 'checked_at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'source': 'public fixed-revision download; SHA compared against historical canonical snapshot', 'old_cache_copied': False, 'model_evaluation_performed': False, 'datasets': results}, indent=2)+'\n')
    print('PUBLIC_UTILITY_RESTORE_PASS', flush=True)


if __name__ == '__main__':
    main()
