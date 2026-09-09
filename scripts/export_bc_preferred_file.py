"""Proposed forced-command read-only SSH export; no shell or token access.

Not activated by this file alone. Requires separately approved authorized_keys entry.
The requesting old host supplies: METHOD FILENAME OFFSET.
"""
import json
import os
from pathlib import Path
import sys

P = Path('/root/autodl-tmp/WMKD_Benchmark')
D = Path(str(P) + '_data')


def main():
    if os.environ.get('SSH_ORIGINAL_COMMAND', '').startswith('bc-receive '):
        from bc_frozen_asset_transfer import receive
        return receive()
    args = os.environ.get('SSH_ORIGINAL_COMMAND', '').split()
    assert len(args) == 3
    method, name, offset_text = args
    assert method in ('pnfp', 'evertracer', 'ctcc', 'iseal', 'scw', 'passive_shared')
    assert Path(name).name == name and offset_text.isdecimal()
    q = P/'results/logit_distillation/same_lineage_bc'/method
    full = json.loads((q/'full_experiment_log.json').read_text())
    assert full.get('scientific_closure') == 'COMPLETE'
    assert full.get('preferred_final_model') is True
    provenance = json.loads((q/'model_provenance.json').read_text())
    assert provenance['status'] == 'FRESH_RELOAD_VERIFIED'
    model = Path(provenance['model_path'])
    assert model.resolve().is_relative_to(D/'runs/same_lineage_bc')
    approved = {f['name']: f for f in provenance['files']}
    assert name in approved
    path = model/name
    assert path.is_file() and not path.is_symlink()
    assert path.resolve().parent == model.resolve()
    assert path.stat().st_size == approved[name]['bytes']
    offset = int(offset_text)
    assert 0 <= offset <= path.stat().st_size
    with path.open('rb') as source:
        source.seek(offset)
        while block := source.read(2 << 20):
            sys.stdout.buffer.write(block)


if __name__ == '__main__':
    main()
