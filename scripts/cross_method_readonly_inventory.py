"""Read-only storage/process or ModelScope inventory; never downloads or mutates artifacts."""
import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

P = Path('/root/autodl-tmp/WMKD_Benchmark')
D = Path('/root/autodl-tmp/WMKD_Benchmark_data')

def command(args):
    r = subprocess.run(args, capture_output=True, text=True, timeout=60)
    return {'returncode': r.returncode, 'stdout': r.stdout, 'stderr': r.stderr}

def main():
    mode = argparse.ArgumentParser()
    mode.add_argument('--mode', choices=['local', 'remote'], required=True)
    args = mode.parse_args()
    out = {'checked_at': datetime.now(timezone.utc).isoformat(), 'mode': args.mode,
           'read_only': True}
    if args.mode == 'local':
        out['hostname'] = command(['hostname'])
        out['processes'] = command(['ps', '-eo', 'pid,ppid,stat,lstart,etime,args'])
        out['gpu'] = command(['nvidia-smi'])
        out['disk'] = command(['df', '-B1', str(D)])
        out['git'] = {name: command(['git', '-C', str(P), *cmd]) for name, cmd in {
            'head': ['rev-parse', 'HEAD'], 'origin_main': ['rev-parse', 'origin/main'],
            'ahead_behind': ['rev-list', '--left-right', '--count', 'HEAD...origin/main'],
            'status': ['status', '--porcelain']}.items()}
        out['large_files'] = []
        out['checkpoint_directories'] = []
        out['dataset_files'] = []
        for root in ['runs', 'models', 'restored', 'datasets', 'cache', 'tmp']:
            for parent, dirs, files in os.walk(D / root, followlinks=False):
                if any(x in parent.split('/') for x in ['secrets', 'credentials']):
                    dirs[:] = []
                    continue
                p = Path(parent)
                if p.name.startswith('checkpoint') or p.name in ['final_model', 'student', 'teacher']:
                    out['checkpoint_directories'].append(str(p))
                for name in files:
                    f = p / name
                    try:
                        s = f.stat()
                    except OSError:
                        continue
                    item = {'path': str(f), 'bytes': s.st_size, 'allocated_bytes': s.st_blocks*512,
                            'inode': s.st_ino, 'device': s.st_dev, 'nlink': s.st_nlink,
                            'symlink': f.is_symlink(), 'resolved': str(f.resolve()), 'mtime': s.st_mtime}
                    if s.st_size >= 100_000_000:
                        out['large_files'].append(item)
                    if name.endswith(('.jsonl', '.arrow', '.parquet')) and root in ['runs','datasets','restored']:
                        out['dataset_files'].append(item)
    else:
        sys.path.insert(0, str(P / 'scripts'))
        from modelscope_evertracer_archive import api_client, remote_sha, is_private
        api = api_client()
        inventory = json.loads((P / 'results/project_archive_inventory.json').read_text())
        out['repositories'] = []
        seen = set()
        for artifact in inventory['artifacts']:
            repo = artifact.get('modelscope_repo')
            kind = artifact.get('repo_type')
            if not repo or artifact['method'] not in ['PN-FP','EverTracer','CTCC','iSeal','SCW'] or (repo,kind) in seen:
                continue
            seen.add((repo,kind))
            row = {'artifact_id': artifact['artifact_id'], 'repo': repo, 'type': kind,
                   'historical_evidence': artifact.get('evidence')}
            try:
                info = api.get_repo(repo, kind)
                row['private'] = is_private(info)
                items = [f for f in api.list_repo_files(repo, kind, recursive=True) if not f.is_dir]
                row['files'] = [{'path': f.path, 'size': getattr(f, 'size', None),
                                 'sha256': remote_sha(f)} for f in items]
                row['status'] = 'LISTED'
            except Exception as e:
                row['status'] = 'READ_ERROR'
                row['error_type'] = type(e).__name__
            out['repositories'].append(row)
    print(json.dumps(out, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
