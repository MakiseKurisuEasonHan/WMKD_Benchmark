"""Restricted SSH receiver: accepts only frozen manifest files; never a shell."""
import hashlib
import json
import os
import sys
from pathlib import Path

ROOT = Path('/root/autodl-tmp/WMKD_Benchmark')
E = ROOT / 'results/logit_distillation/pnfp_same_lineage_pilot'

def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(8 << 20), b''): h.update(b)
    return h.hexdigest()

def main():
    role, name = os.environ['SSH_ORIGINAL_COMMAND'].split()
    rows = json.loads((E/'asset_sync_manifest.json').read_text())['files']
    match = [f for f in rows if f['role'] == role and f['name'] == name]
    assert len(match) == 1
    item = match[0]; p = Path(item['destination'])
    assert p.resolve().is_relative_to(Path(str(ROOT)+'_data')) and not p.is_symlink()
    if p.exists():
        assert p.stat().st_size == item['bytes'] and sha(p) == item['sha256']
        # Drain sender to avoid broken pipe when an identical asset already exists.
        while sys.stdin.buffer.read(8 << 20): pass
        print('EXISTING_SHA_PASS'); return
    p.parent.mkdir(parents=True, exist_ok=True)
    part = p.with_name(p.name+'.bc-transfer-partial')
    assert not part.exists(), 'Partial exists; inspect before retry'
    h = hashlib.sha256(); count = 0
    with part.open('xb') as f:
        while block := sys.stdin.buffer.read(8 << 20):
            count += len(block); assert count <= item['bytes']
            h.update(block); f.write(block)
        f.flush(); os.fsync(f.fileno())
    assert count == item['bytes'] and h.hexdigest() == item['sha256']
    os.rename(part, p)
    print('DESTINATION_SHA_PASS')

if __name__ == '__main__': main()
