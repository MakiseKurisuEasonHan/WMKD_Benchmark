"""Fast-forward an idle Bc checkout while retaining every incoming-path preimage."""
import datetime
import hashlib
import json
import subprocess
import sys
import tarfile
from pathlib import Path

P = Path('/root/autodl-tmp/WMKD_Benchmark')
E = P / 'results/logit_distillation/same_lineage_bc'

def git(*args):
    return subprocess.check_output(['git', '-C', str(P), *args]).decode().strip()

before = git('rev-parse', 'HEAD')
assert not git('diff', '--cached', '--name-only'), 'Remote staged changes require inspection'
if len(sys.argv) == 2:
    git('fetch', sys.argv[1], 'main:refs/remotes/origin/main')
else:
    git('fetch', 'origin', 'main')
target = git('rev-parse', 'origin/main')
subprocess.run(['git', '-C', str(P), 'merge-base', '--is-ancestor', before, target], check=True)
incoming = set(git('diff', '--name-only', before, target).splitlines())
stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
backup = Path('/root/autodl-tmp/WMKD_Benchmark_data/tmp') / ('bc_git_preimages_' + stamp + '.tar.gz')
preimages = []
with tarfile.open(backup, 'w:gz') as out:
    for name in sorted(incoming):
        p = P / name
        if not p.exists():
            continue
        assert p.is_file() and not p.is_symlink(), name
        assert p.stat().st_size < 100 * 1024**2, name
        preimages.append({'path': name, 'bytes': p.stat().st_size,
                          'sha256': hashlib.sha256(p.read_bytes()).hexdigest()})
        out.add(p, arcname=name)
changed = set(git('diff', '--name-only', 'HEAD').splitlines())
untracked = set(git('ls-files', '--others', '--exclude-standard').splitlines())
conflicts = sorted(incoming & (changed | untracked))
stash = None
if conflicts:
    git('stash', 'push', '--include-untracked', '-m', 'Bc preserved runtime before final ff ' + stamp,
        '--', *conflicts)
    stash = git('rev-parse', 'refs/stash')
git('merge', '--ff-only', 'origin/main')
assert git('rev-parse', 'HEAD') == target
receipt = {'at': stamp, 'before': before, 'after': target, 'mode': 'FAST_FORWARD_ONLY',
           'backup': str(backup), 'backup_sha256': hashlib.sha256(backup.read_bytes()).hexdigest(),
           'preimages': preimages, 'preserved_stash': stash, 'stash_not_dropped': bool(stash),
           'unrelated_worktree_changes_preserved': True}
(E/'final_remote_git_sync.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps({k: v for k, v in receipt.items() if k != 'preimages'}))
