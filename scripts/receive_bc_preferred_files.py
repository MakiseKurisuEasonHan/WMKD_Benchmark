"""Old-host, bounded restart-safe receipt of approved final files over SSH.

No ModelScope credentials or SSH private keys are transferred.
"""
import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

P = Path('/root/autodl-tmp/WMKD_Benchmark')
D = Path(str(P) + '_data')
E = P / 'results/logit_distillation/same_lineage_bc'


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(8 << 20), b''):
            h.update(b)
    return h.hexdigest()


def main():
    method = sys.argv[1]
    assert method in ('pnfp', 'evertracer', 'ctcc', 'iseal', 'scw', 'passive_shared')
    q = E / method
    prov = json.loads((q / 'model_provenance.json').read_text())
    full = json.loads((q / 'full_experiment_log.json').read_text())
    assert full['scientific_closure'] == 'COMPLETE'
    assert full['preferred_final_model'] is True
    dest = D / 'tmp' / ('bc_' + method + '_preferred_transfer_20260910')
    dest.mkdir(parents=True, exist_ok=True)
    lock = (E / 'archive_transfer.lock').open('a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    receipt = {'method': method, 'pid': os.getpid(), 'destination': str(dest),
               'status': 'RUNNING', 'files': [], 'source_model': prov['model_path']}

    def save(**kw):
        receipt.update(kw, updated_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
        temp = q / 'archive_transfer_receipt.json.tmp'
        temp.write_text(json.dumps(receipt, indent=2) + '\n')
        os.replace(temp, q / 'archive_transfer_receipt.json')

    save()
    try:
        remaining = sum(x['bytes'] for x in prov['files'])
        assert shutil.disk_usage(dest).free > remaining + (2 << 30)
        for x in prov['files']:
            name = x['name']
            assert Path(name).name == name
            target = dest / name
            part = dest / (name + '.partial')
            assert not target.is_symlink() and not part.is_symlink()
            if target.exists():
                assert target.stat().st_size == x['bytes'] and sha(target) == x['sha256']
            else:
                for attempt in range(1, 4):
                    offset = part.stat().st_size if part.exists() else 0
                    assert offset <= x['bytes']
                    save(current_file=name, received_bytes=offset, expected_bytes=x['bytes'], attempt=attempt)
                    if offset == x['bytes']:
                        break
                    cmd = ['ssh', '-T', '-p', '49453', '-i', '/root/.ssh/id_ed25519',
                           '-o', 'IdentitiesOnly=yes', '-o', 'BatchMode=yes',
                           '-o', 'StrictHostKeyChecking=yes', '-o', 'ConnectTimeout=20',
                           '-o', 'ServerAliveInterval=15', '-o', 'ServerAliveCountMax=4',
                           '-o', 'UserKnownHostsFile=/root/.ssh/wmkd_xbb_known_hosts',
                           'root@connect.westd.seetacloud.com', f'{method} {name} {offset}']
                    with part.open('ab') as out, (q / 'archive_transfer_ssh.log').open('ab') as err:
                        child = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=err)
                        last = time.monotonic()
                        while block := child.stdout.read(2 << 20):
                            out.write(block)
                            if time.monotonic() - last > 15:
                                out.flush()
                                save(current_file=name, received_bytes=out.tell())
                                last = time.monotonic()
                        out.flush()
                        os.fsync(out.fileno())
                        code = child.wait()
                    if code == 0:
                        break
                    save(last_error=f'SSH_EXIT_{code}', attempt=attempt)
                    time.sleep(5)
                assert part.stat().st_size == x['bytes'], 'INCOMPLETE_TRANSFER'
                assert sha(part) == x['sha256'], 'SHA_MISMATCH_KEEP_EVIDENCE'
                part.rename(target)
            receipt['files'].append(dict(x, verified=True))
            save()
        save(status='PASS', current_file=None, verified_files=len(receipt['files']))
    except Exception as exc:
        save(status='BLOCKED', last_error=str(exc))
        raise


if __name__ == '__main__':
    main()
