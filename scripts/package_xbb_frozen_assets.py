"""Exact frozen-asset transfer package; no model weights or credentials."""
import datetime
import hashlib
import json
import socket
import tarfile
from pathlib import Path

P = Path('/root/autodl-tmp/WMKD_Benchmark')
D = Path(str(P) + '_data')
OUT = D / 'tmp/xbb_minimal_asset_transfer_20260909'


def main():
    OUT.mkdir(exist_ok=True)
    assert not (OUT / 'assets.tar.gz').exists(), 'Inspect existing package, do not replace'
    files = {}

    def add(path, role):
        path = Path(path)
        assert path.is_file() and not path.is_symlink(), str(path)
        assert path.is_relative_to(D) or path.is_relative_to(P)
        assert path.suffix not in ('.safetensors', '.bin', '.pt')
        files[str(path)] = dict(role=role, path=str(path), relative=str(path.relative_to(P.parent)), bytes=path.stat().st_size, sha256=hashlib.sha256(path.read_bytes()).hexdigest())

    for method in ['pnfp', 'evertracer', 'ctcc', 'iseal', 'scw']:
        protocol = json.loads((P / 'results/active_cross_lineage_bb' / method / 'protocol.json').read_text())
        path = Path(protocol['dataset']['source_path'])
        add(path, 'dataset_' + method)
        assert files[str(path)]['sha256'] == protocol['dataset']['sha256']
        # JSONL boundaries are literal newlines, not Unicode text separators.
        with path.open() as stream:
            rows = [json.loads(line) for line in stream if line.strip()]
        assert len(rows) == 20000
        assert all(isinstance(r.get('paraphrased_answer'), str) and r['paraphrased_answer'].strip() for r in rows)
        files[str(path)].update(records=20000, target_field='paraphrased_answer')
        for manifest in path.parent.glob('*.manifest.json'):
            add(manifest, 'dataset_manifest_' + method)
        add(P / 'results' / method / ('experiment_bb2' if method == 'ctcc' else 'experiment_bb') / 'full_experiment_log.json', 'dataset_provenance_' + method)
    path = P / 'results/pnfp/experiment_ba_trajectory_followup/detector_assets_manifest.json'
    manifest = json.loads(path.read_text())
    add(path, 'pnfp_manifest')
    add(manifest['path'], 'pnfp_secret')
    assert files[manifest['path']]['sha256'] == manifest['sha256']
    path = D / 'runs/evertracer/evertracer_a_20260828_223155_cont1/artifacts/frozen_neighborhoods.jsonl'
    add(path, 'evertracer_probes')
    assert files[str(path)]['sha256'] == '7834e3d77704951ea06501c2166e960fef2b147ced3d751a8e55f07ec7b3672b'
    path = P / 'results/active_cross_lineage_ba/evertracer/static_probe_tokenizer_audit.json'
    add(path, 'evertracer_audit')
    for item in json.loads(path.read_text())['historical_scalar_artifacts'].values():
        add(item['path'], 'evertracer_scalar_reference')
        assert files[item['path']]['sha256'] == item['sha256']
    add(D / 'datasets/ctcc/experiment_a/test_set_annotated.json', 'ctcc_detector_queries')
    for name in ['scw_a2_french_eval_1000.jsonl', 'manifest.json']:
        add(D / 'evaluation/scw/a2_french_eval' / name, 'scw_detector_queries')
    for name in ['tokenizer.json', 'tokenizer_config.json', 'special_tokens_map.json', 'config.json']:
        add(D / 'models/base/Llama-3.2-3B-Instruct' / name, 'llama_reference_tokenizer_only')
    source = D / 'artifacts/scw/source'
    for path in (source / 'src/robust_fp').rglob('*'):
        if path.is_file() and path.suffix in ('.py', '.yaml', '.json', '.txt'):
            add(path, 'scw_frozen_detector_source')
    for name in ['pyproject.toml', 'setup.py', 'setup.cfg', 'LICENSE']:
        if (source / name).is_file():
            add(source / name, 'scw_source_metadata')
    manifest = dict(created_at=datetime.datetime.now(datetime.timezone.utc).isoformat(), source_hostname=socket.gethostname(), files=list(files.values()), teacher_weights_included=False, model_weights_included=False, credentials_included=False)
    (OUT / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    with tarfile.open(OUT / 'assets.tar.gz', 'w:gz', compresslevel=6) as tar:
        for item in files.values():
            tar.add(item['path'], arcname=item['relative'], recursive=False)
        tar.add(OUT / 'manifest.json', arcname='xbb_transfer_manifest.json')
    path = OUT / 'assets.tar.gz'
    receipt = dict(package=str(path), bytes=path.stat().st_size, sha256=hashlib.sha256(path.read_bytes()).hexdigest(), file_count=len(files), source_bytes=sum(f['bytes'] for f in files.values()), dataset_gate='5/5 SHA and 20000 and nonempty paraphrased_answer PASS')
    (OUT / 'package_receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt))


if __name__ == '__main__':
    main()
