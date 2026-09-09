"""Execute only audited exact regular-file paths, after the evidence Git gate."""
import pathlib,json,os,stat,datetime,subprocess,hashlib,sys
P=pathlib.Path('/root/autodl-tmp/WMKD_Benchmark');D=pathlib.Path(str(P)+'_data');O=P/'results/pre_bb_cleanup_20260909'
def get(p):return json.loads(p.read_text())
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def put(p,d):
 t=p.with_suffix('.tmp');t.write_text(json.dumps(d,indent=2)+'\n');os.replace(t,p)
def free():s=os.statvfs(D);return s.f_bavail*s.f_frsize
proposal=get(O/'exact_cleanup_proposal.json');items=proposal['objects'];receipt=O/'autodl_large_cleanup_receipt.json'
assert not receipt.exists(),'DO_NOT_REPEAT_CLEANUP'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=P).decode().strip()==sys.argv[1]
assert subprocess.check_output(['git','rev-parse','origin/main'],cwd=P).decode().strip()==sys.argv[1]
assert get(O/'trajectory_package_receipt.json')['status']=='PASS'
assert all(x['exists'] for x in get(O/'detector_asset_path_audit.json'))
assert len(items)==478 and len({x['path'] for x in items})==len(items)
protected={x['path'] for x in get(O/'protected_inputs_before.json')}
for x in items:
 f=pathlib.Path(x['path']);assert f.is_absolute() and f.is_relative_to(D) and f.resolve()==f and str(f) not in protected
 s=f.lstat();assert stat.S_ISREG(s.st_mode) and s.st_size==x['logical_size'] and s.st_ino==x['inode'] and s.st_dev==x['device'] and s.st_nlink==x['hardlink_count'],str(f)
 assert x['classification'] in ['ARCHIVED_REMOTE_COPY','REDUNDANT_ARCHIVE_STAGING_WEIGHT','CACHE']
 if x['classification']=='CACHE':assert f.is_relative_to(D/'cache/pip_py311/http-v2')
 else:assert f.name in ['model-00001-of-00002.safetensors','model-00002-of-00002.safetensors'] and len(x['remote_revision'])==40
# No scientific/transfer worker may still use these files.
for d in pathlib.Path('/proc').iterdir():
 if not d.name.isdigit() or int(d.name)==os.getpid():continue
 try:cmd=(d/'cmdline').read_bytes().replace(b'\0',b' ').decode(errors='replace')
 except OSError:continue
 assert not any(s in cmd for s in ['archive_active_cross_lineage_ba.py run','archive_active_cross_lineage_ba.py verify','active_cross_lineage_train','torchrun','deepspeed.launcher']),cmd[:200]
r=dict(status='IN_PROGRESS',authorization='user_authorization.txt sections M/N/P/Q',evidence_git_commit=sys.argv[1],started_at=now(),space_before=free(),objects=items,estimated_blocks_freed=proposal['estimated_blocks_freed'],policy='Unlink listed regular files only; preserve directories and all nonlisted contents')
put(receipt,r)
for x in items:
 os.unlink(x['path']);x.update(deleted=True,actual_deletion_timestamp=now());put(receipt,r)
os.sync();r.update(space_after=free(),completed_at=now(),status='COMPLETE');r['actual_space_freed']=r['space_after']-r['space_before'];put(receipt,r)
assert all(not pathlib.Path(x['path']).exists() for x in items)
checks=[]
for x in get(O/'protected_inputs_before.json'):
 f=pathlib.Path(x['path']);h=hashlib.sha256()
 with f.open('rb') as fp:
  for block in iter(lambda:fp.read(8<<20),b''):h.update(block)
 checks.append(dict(path=str(f),role=x['role'],sha256=h.hexdigest(),match=h.hexdigest()==x['sha256']))
assert all(x['match'] for x in checks)
put(O/'post_cleanup_integrity.json',dict(status='PASS',protected_files=checks,deleted_paths_absent=True,free_bytes=free(),gpu_required=True,ready_for_gpu_start=True,new_training_started=False))
print(json.dumps({k:v for k,v in r.items() if k!='objects'}),flush=True)
