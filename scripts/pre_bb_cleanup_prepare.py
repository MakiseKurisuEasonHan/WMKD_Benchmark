"""Build an exact-path deletion proposal and verify protected inputs; no deletion."""
import pathlib,json,hashlib,os,stat,datetime
P=pathlib.Path('/root/autodl-tmp/WMKD_Benchmark');D=pathlib.Path(str(P)+'_data');O=P/'results/pre_bb_cleanup_20260909'
def get(p):return json.loads(p.read_text())
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8<<20),b''):h.update(b)
 return h.hexdigest()
def put(n,d):(O/n).write_text(json.dumps(d,indent=2)+'\n')
protected=[];candidates=[]
def protect(f,expected,role):
 f=pathlib.Path(f);assert f.is_file(),str(f)
 h=sha(f);assert h==expected,(str(f),'SHA mismatch')
 protected.append(dict(path=str(f),sha256=h,bytes=f.stat().st_size,role=role))
base=D/'models/paraphrasers/Qwen2.5-3B-Instruct'
for x in get(P/'results/active_cross_lineage_ba/canonical_model_and_runner_preflight.json')['files']:protect(base/x['path'],x['sha256'],'CANONICAL_QWEN_BASE')
print('BASE PASS',flush=True)
for m,a in [('pnfp','experiment_bb'),('evertracer','experiment_bb'),('ctcc','experiment_bb2'),('iseal','experiment_bb'),('scw','experiment_bb')]:
 full=get(P/'results'/m/a/'full_experiment_log.json')
 if m=='evertracer':root=D/'runs/evertracer_bb/evertracer_bb_20260903_130000';expected=full['preprocessing']['processed20k']['frozen_jsonl_sha256']
 else:root=pathlib.Path(full['artifacts']['runtime_root']);expected=full['preprocessing']['physical_sha256']
 f=root/'dataset/frozen_paired_qa.jsonl';protect(f,expected,m.upper()+'_'+('BB2' if m=='ctcc' else 'BB')+'_FROZEN')
 assert sum(1 for line in f.open() if json.loads(line))==20000
 # All currently frozen detector manifest paths remain explicitly protected.
 def walk(v):
  if isinstance(v,dict):
   if isinstance(v.get('path'),str) and v['path'].startswith('/root/'):
    q=pathlib.Path(v['path']);h=v.get('sha256')
    if q.is_file() and isinstance(h,str) and len(h)==64:protect(q,h,m.upper()+'_DETECTOR_ASSET')
   for t in v.values():walk(t)
  elif isinstance(v,list):
   for t in v:walk(t)
 walk(get(P/'results'/m/'experiment_ba_trajectory_followup/detector_assets_manifest.json'))
 print(m,'BB/DTECTOR PASS',flush=True)
put('protected_inputs_before.json',protected)
large=get(O/'large_file_inventory.json');byinode={}
for x in large:byinode.setdefault((x['device'],x['inode']),[]).append(x)
for group,methods in [('active_cross_lineage_ba',['pnfp','ctcc','evertracer','iseal','scw']),('passive_cross_lineage',['ba','bb'])]:
 for m in methods:
  q=P/'results'/group/m;r=get(q/'modelscope_archive.json');assert r['status']=='COMPLETE' and r['visibility']=='PRIVATE' and len(r['revision'])==40
  if group=='active_cross_lineage_ba':
   assert r['verification_status']=='PASS';model=pathlib.Path(get(q/'model_provenance.json')['model_path'])
  else:
   assert r['all_sha_match'] and r['independent_download'];model=pathlib.Path(get(q/'final_model_manifest.json')['files'][0]['path']).parent
  for n,v in r['files'].items():
   if not n.endswith('.safetensors'):continue
   f=model/n;assert f.is_file();s=f.stat();assert s.st_size==v['bytes'] and sha(f)==v['sha256']
   links=byinode.get((s.st_dev,s.st_ino),[]);assert len(links)==s.st_nlink,'UNACCOUNTED_HARDLINK'
   for x in links:
    target=pathlib.Path(x['path']);assert target.resolve()==target and target.is_relative_to(D) and not target.is_symlink()
    assert target.parent==model or target.is_relative_to(D/'tmp'),str(target)
    candidates.append(dict(path=str(target),classification='ARCHIVED_REMOTE_COPY' if target.parent==model else 'REDUNDANT_ARCHIVE_STAGING_WEIGHT',reason='Verified preferred Student archived at immutable revision; XBb must start from clean Qwen, not this Student',logical_size=x['bytes'],estimated_blocks=x['blocks'],hardlink_count=x['nlink'],inode=x['inode'],device=x['device'],sha256=v['sha256'],recoverability_source=r['repo'],remote_revision=r['revision'],verification_mode=r.get('verification_mode','FULL_INDEPENDENT_DOWNLOAD'),scientific_dependency_check='Not a Teacher/Base/dataset/detector asset; configs and scientific evidence retained',deleted=False))
  print(group,m,'ARCHIVED WEIGHTS PASS',flush=True)
# Only pip HTTP download cache; installed environments and other caches are KEEP.
cache=D/'cache/pip_py311/http-v2'
for root,dirs,names in os.walk(cache,followlinks=False):
 for n in names:
  f=pathlib.Path(root)/n;s=f.lstat();assert stat.S_ISREG(s.st_mode) and s.st_nlink==1
  candidates.append(dict(path=str(f),classification='CACHE',reason='pip HTTP download cache, not installed packages or scientific data',logical_size=s.st_size,estimated_blocks=s.st_blocks*512,hardlink_count=s.st_nlink,inode=s.st_ino,device=s.st_dev,recoverability_source='Python package index / retained installed environments',remote_revision=None,scientific_dependency_check='Download cache only; environments retained',deleted=False))
unique={}
for x in candidates:unique[(x['device'],x['inode'])]=x['estimated_blocks']
put('exact_cleanup_proposal.json',dict(status='VERIFIED_PENDING_EVIDENCE_GIT_GATE',objects=candidates,logical_bytes=sum(x['logical_size'] for x in candidates),estimated_blocks_freed=sum(unique.values()),protected_inputs=len(protected),created_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),scope='Only exact listed regular files; no directory recursion at deletion; all other paths KEEP'))
print('PROPOSAL',len(candidates),'UNIQUE_PHYSICAL_GIB',sum(unique.values())/1024**3,flush=True)
