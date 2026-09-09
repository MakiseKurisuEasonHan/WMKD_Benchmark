"""Windows SFTP relay with resume, exact package SHA, and safe target install."""
import base64
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHA = '3599a2988301c34a8a86af32b2aa685d807909dab8b51352605c854c3d0aba18'
SIZE = 28082896
LOCAL = ROOT / 'artifacts/xbb_minimal_assets_20260909.tar.gz'
SOURCE = '/root/autodl-tmp/WMKD_Benchmark_data/tmp/xbb_minimal_asset_transfer_20260909/assets.tar.gz'
TARGET = '/root/autodl-tmp/xbb_deployment/assets.tar.gz.partial'


def sftp(host, command):
    print(json.dumps({'host': host, 'stage': command.split()[0]}), flush=True)
    subprocess.run(['sftp', '-oBatchMode=yes', '-oConnectTimeout=15', '-b', '-', host], input=command + '\n', text=True, check=True)


def main():
    if not (LOCAL.exists() and LOCAL.stat().st_size == SIZE and hashlib.sha256(LOCAL.read_bytes()).hexdigest() == SHA):
        sftp('6002', f'reget "{SOURCE}" "{LOCAL.as_posix()}"')
    assert LOCAL.stat().st_size == SIZE
    assert hashlib.sha256(LOCAL.read_bytes()).hexdigest() == SHA
    print('LOCAL_PACKAGE_SHA_PASS', flush=True)
    exists = subprocess.run(['ssh', '-T', '-oBatchMode=yes', '-oConnectTimeout=15', '6000bb', 'test -f ' + TARGET]).returncode
    assert exists in (0, 1), 'Target connectivity failed'
    verb = 'reput' if exists == 0 else 'put'
    sftp('6000bb', f'{verb} "{LOCAL.as_posix()}" "{TARGET}"')
    remote = r'''
import pathlib,hashlib,json,tarfile,datetime,shutil
root=pathlib.Path('/root/autodl-tmp')
package=root/'xbb_deployment/assets.tar.gz.partial'
assert package.stat().st_size==28082896
assert hashlib.sha256(package.read_bytes()).hexdigest()=='3599a2988301c34a8a86af32b2aa685d807909dab8b51352605c854c3d0aba18'
with tarfile.open(package) as tar:
 manifest=json.load(tar.extractfile('xbb_transfer_manifest.json'))
 expected={f['relative']:f for f in manifest['files']}
 assert len(expected)==70
 assert {m.name for m in tar.getmembers()}==set(expected)|{'xbb_transfer_manifest.json'}
 for name,item in expected.items():
  member=tar.getmember(name);assert member.isfile() and member.size==item['bytes']
  target=root/name;assert target.resolve().is_relative_to(root)
  data=tar.extractfile(member).read();assert hashlib.sha256(data).hexdigest()==item['sha256']
  if target.exists():
   assert target.is_file() and hashlib.sha256(target.read_bytes()).hexdigest()==item['sha256'],'Existing destination differs: '+name
  else:
   target.parent.mkdir(parents=True,exist_ok=True)
   with target.open('xb') as f:f.write(data)
  assert target.stat().st_size==item['bytes']
  assert hashlib.sha256(target.read_bytes()).hexdigest()==item['sha256']
  item['destination_sha_verified']=True
  if item['role'].startswith('dataset_') and item.get('records'):
   with target.open() as f:rows=[json.loads(line) for line in f if line.strip()]
   assert len(rows)==20000 and all(isinstance(r.get('paraphrased_answer'),str) and r['paraphrased_answer'].strip() for r in rows)
   item['destination_records']=len(rows)
p=root/'WMKD_Benchmark/results/active_cross_lineage_bb'
receipt={'status':'PASS','verified_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':'ssh6002','target':'ssh6000bb','package_sha256':'3599a2988301c34a8a86af32b2aa685d807909dab8b51352605c854c3d0aba18','package_bytes':28082896,'files':manifest['files'],'file_count':70,'source_uncompressed_bytes':sum(f['bytes'] for f in manifest['files']),'token_transferred':False,'weights_transferred':False}
(p/'asset_transfer_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
state=json.loads((p/'pipeline_state.json').read_text());state.update(datasets='5/5 SHA_RECORD_TARGET_PASS',asset_restore_blocker=None,asset_transfer='70/70 SHA_PASS',current_stage='WAITING_EXISTING_BASE_DOWNLOAD_AND_ENV_INSTALL');(p/'pipeline_state.json').write_text(json.dumps(state,indent=2)+'\n')
print(json.dumps(receipt))
'''
    result = subprocess.run(['ssh', '-T', '-oBatchMode=yes', '-oConnectTimeout=15', '6000bb', "/root/miniconda3/bin/python -B -c 'import sys,base64;exec(base64.b64decode(sys.stdin.read()))'"], input=base64.b64encode(remote.encode()), capture_output=True, check=True)
    receipt = json.loads(result.stdout)
    receipt['local_package_sha_verified'] = True
    receipt['network_payload_bytes_two_legs'] = SIZE * 2
    (ROOT / 'results/active_cross_lineage_bb/asset_transfer_receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({k: v for k, v in receipt.items() if k != 'files'}), flush=True)


if __name__ == '__main__':
    main()
