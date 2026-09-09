"""User-approved five-model private archival, serial, CPU only, no deletion.

Preflight inventories the account and hashes sources before any upload.
Verification runs in a separate process and hashes actual uncached network bytes
at the upload's immutable commit, without writing redundant model copies.
"""
import datetime
import hashlib
import json
import os
import pathlib
import re
import subprocess
import sys
import time

P = pathlib.Path('/root/autodl-tmp/WMKD_Benchmark')
D = pathlib.Path(str(P)+'_data')
E = P/'results/active_cross_lineage_ba'
O = E/'archive'
sys.path.insert(0,str(P/'scripts'))
import modelscope_passive5_ba_student_archive as helper

ORDER = ['pnfp','ctcc','evertracer','iseal','scw']
LABEL = dict(pnfp='PNFP',ctcc='CTCC',evertracer='EverTracer',iseal='iSeal',scw='SCW')
GIT = 'd8a445735c1625ada4440eb7b2e8ae7b43eac703'
REV = '8f4992eda43eea7c770690ddc0de8f732da246f5'
CARDS = {
 'pnfp':'Cross-lineage Ba Student reproducing partial PN-FP detector acquisition relative to clean Qwen baseline.',
 'ctcc':'Cross-lineage Ba Student with no observed CTCC IAMALIVE trigger acquisition under the frozen detector.',
 'evertracer':'Cross-lineage Ba Student for which the canonical EverTracer detector is not cross-tokenizer comparable; exploratory diagnostic is reported separately.',
 'iseal':'Cross-lineage Ba Student with iSeal detector not applicable under the frozen cross-architecture implementation.',
 'scw':'Cross-lineage Ba Student remaining non-detected under the frozen SCW statistical test.'}

def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def get(p): return json.loads(p.read_text())
def put(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 t=p.with_suffix(p.suffix+'.tmp');t.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n');os.replace(t,p)
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8<<20),b''):h.update(b)
 return h.hexdigest()
def state(m,stage,**kw):
 put(O/'runtime.json',dict(method=m,stage=stage,pid=os.getpid(),updated_at=now(),**kw))
 print(m,stage,flush=True)
def files(api,repo,revision=None):
 return [dict(path=f.path,size=f.size,sha256=f.sha256,lfs=f.lfs) for f in api.list_repo_files(repo,'model',revision=revision,recursive=True) if not f.is_dir]
def digest(f): return (f.get('lfs') or {}).get('sha256') or str((f.get('lfs') or {}).get('oid','')).removeprefix('sha256:') or f.get('sha256')

def preflight():
 assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=P).decode().strip()==GIT
 gates={}
 for m in ORDER:
  state(m,'LOCAL_IDENTITY_CHECK')
  q=E/m;prov=get(q/'model_provenance.json');full=get(q/'full_experiment_log.json');protocol=get(q/'protocol.json');train=get(q/'training_summary.json');data=get(q/'qwen_dataset_preflight.json')
  assert full['status']=='COMPLETE' and train['steps']==7500 and prov['status']=='FRESH_RELOAD_VERIFIED'
  assert protocol['revision']==REV and protocol['initialization']=='fresh_clean_Qwen_not_other_student'
  assert protocol['model_path']==str(D/'models/paraphrasers/Qwen2.5-3B-Instruct')
  assert data['actual_sha256']==data['expected_sha256']==sha(pathlib.Path(data['source_path']))
  model=pathlib.Path(prov['model_path']);assert model.resolve().is_relative_to(D/'runs/active_cross_lineage_ba')
  checks={}
  for x in prov['files']:
   f=model/x['name'];assert f.is_file() and not f.is_symlink();assert f.stat().st_size==x['bytes'] and sha(f)==x['sha256'];checks[x['name']]=dict(bytes=x['bytes'],sha256=x['sha256'])
  shards=sorted(set(get(model/'model.safetensors.index.json')['weight_map'].values()));assert len(shards)==2
  gates[m]=dict(model=str(model),run_id=full['run_id'],repo=helper.NAMESPACE+'/Qwen2.5-3B-WMKD-Active-'+LABEL[m]+'-Cross-Lineage-Ba-Student',files=checks,shards=shards,dataset=data,training=protocol['training'])
 api=helper.api_client();repos=[];page=1
 while True:
  result=api.list_repos('model',owner=helper.NAMESPACE,page_size=50,page_number=page);repos+=result.items
  if not result.has_next:break
  page+=1
 assert len(repos)==result.total_count and len({r.id for r in repos})==len(repos)
 inventory=[];matches=[]
 for i,r in enumerate(repos):
  state('ALL','REMOTE_UNIQUENESS_INVENTORY',checked=i,total=len(repos))
  fs=files(api,r.id);hashes={digest(f) for f in fs}
  for m,g in gates.items():
   hits=[n for n in g['shards'] if g['files'][n]['sha256'] in hashes]
   if hits:matches.append(dict(method=m,repo=r.id,matching_shards=hits,identical_weights=len(hits)==len(g['shards'])))
  inventory.append(dict(repo=r.id,private=helper.is_private(r),files=fs))
 put(O/'uniqueness_inventory.json',dict(checked_at=now(),repositories=len(repos),inventory=inventory,matches=matches))
 # Existing matching weights must be reused after identifying their immutable
 # revision, never uploaded to a duplicate repo automatically.
 assert not matches,'EXISTING_IDENTICAL_OR_OVERLAPPING_WEIGHTS_REQUIRES_REUSE_REVIEW'
 for m,g in gates.items():assert not api.repo_exists(g['repo'],'model'),'EXISTING_TARGET_REPO_REQUIRES_INSPECTION'
 put(O/'preflight.json',dict(status='PASS',gates=gates,source_git_commit=GIT,checked_at=now(),uniqueness='PASS_NO_MATCHING_WEIGHT_SHARDS'))
 state('ALL','PREFLIGHT_COMPLETE')

def package(m,g):
 q=E/m;model=pathlib.Path(g['model']);dest=D/'tmp'/('active_cross_lineage_'+m+'_preferred_archive_20260909')
 assert not dest.exists(),'PACKAGE_EXISTS_REQUIRES_REVIEW'
 dest.mkdir()
 allowed={n for n in g['files'] if n.endswith('.safetensors') or n in ['config.json','generation_config.json','model.safetensors.index.json','tokenizer.json','tokenizer_config.json','special_tokens_map.json','vocab.json','merges.txt','chat_template.jinja','added_tokens.json']}
 assert set(g['shards'])<=allowed
 for n in sorted(allowed):os.link(model/n,dest/n)
 (dest/'LICENSE').write_bytes((D/'models/paraphrasers/Qwen2.5-3B-Instruct/LICENSE').read_bytes())
 full=get(q/'full_experiment_log.json');utility=get(q/'utility_results.json')
 meta=dict(project='WMKD_Benchmark',campaign='ACTIVE_CROSS_LINEAGE_BA',method=LABEL[m],experiment='XBa',run_id=g['run_id'],canonical_backbone='Qwen/Qwen2.5-3B-Instruct',model_revision=REV,
  preferred=True,preferred_final_model=True,scientific_status=full['scientific_status'],source_git_commit=GIT,model_source=str(model),fresh_clean_qwen_initialization=True,continuation_from_other_student=False,
  training=g['training'],dataset=g['dataset'],detector_applicability_level=full['detector_applicability_level'],canonical_detector_result=full['canonical_detector_result'],exploratory_detector_result=full.get('exploratory_detector_result'),
  utility={k:utility[k] for k in ['arc_challenge_acc_norm','truthfulqa_mc2_acc']},retention_basis='Explicit user preferred-retention decision for reproducibility; not proof of successful watermark transfer or superiority on all utility metrics.',
  artifact_files={n:dict(bytes=(dest/n).stat().st_size,sha256=sha(dest/n)) for n in sorted(allowed|{'LICENSE'})})
 # Keep only result summaries, not SCW arrays or other detector raw material.
 meta['canonical_detector_result']=full.get('scientific_interpretation',full['scientific_status']) if isinstance(meta['canonical_detector_result'],dict) else meta['canonical_detector_result']
 if isinstance(meta['exploratory_detector_result'],dict):meta['exploratory_detector_result']={k:v for k,v in meta['exploratory_detector_result'].items() if not isinstance(v,(dict,list))}
 put(dest/'manifest.json',meta)
 (dest/'README.md').write_text('# '+LABEL[m]+' Active Cross-Lineage Ba Qwen Student\n\n'+CARDS[m]+'\n\nPRIVATE preferred reproducibility artifact, explicitly selected by the user.\n\nQwen2.5-3B-Instruct derivative under the included Qwen RESEARCH LICENSE AGREEMENT. See manifest.json for dataset provenance, training configuration, utility and scientific limitations. No optimizer/intermediate checkpoints/raw evaluation arrays are included.\n')
 (dest/'SHA256SUMS').write_text(''.join(sha(f)+'  '+f.name+'\n' for f in sorted(dest.iterdir())))
 expected={f.name:dict(bytes=f.stat().st_size,sha256=sha(f)) for f in dest.iterdir()}
 for n in expected:
  if not n.endswith('.safetensors'):assert not re.search(rb'(?:hf_[A-Za-z0-9]{25,}|gh[pousr]_[A-Za-z0-9]{25,}|-----BEGIN (?:RSA |OPENSSH )?PRIVATE KEY-----)',(dest/n).read_bytes()),n
 pre=dict(status='PASS',repo=g['repo'],package=str(dest),files=expected,archive_sha256=sha(dest/'SHA256SUMS'),archive_sha256_definition='SHA256 of SHA256SUMS; this binds the complete preferred package',run_id=g['run_id'],source_preserved=True)
 put(O/(m+'_preflight.json'),pre);return pre

def verify(m):
 api=helper.api_client();pre=get(O/(m+'_preflight.json'));upload=get(O/(m+'_upload.json'));repo=pre['repo'];rev=upload['revision'];assert re.fullmatch('[0-9a-f]{40}',rev)
 assert helper.is_private(api.get_repo(repo,'model'))
 remote=files(api,repo,rev);expected=pre['files'];names={f['path'] for f in remote};assert set(expected)<=names
 extras=names-set(expected);assert extras<= {'.gitattributes','.mdlignore'},extras
 checked={}
 for n in sorted(names):
  expected_entry=expected.get(n)
  if expected_entry is None:
   rf=next(f for f in remote if f['path']==n);expected_entry=dict(bytes=rf['size'],sha256=digest(rf))
  h=hashlib.sha256();count=0;last=time.monotonic();content=[]
  response=api.downloader._client.download_stream(repo,'model',n,rev,headers=api.downloader._build_download_headers())
  response.raise_for_status()
  with response:
   for block in response.iter_content(chunk_size=8<<20):
    if not block:continue
    h.update(block);count+=len(block)
    if n=='manifest.json':content.append(block)
    if time.monotonic()-last>30:state(m,'REMOTE_STREAM_VERIFY',file=n,bytes_read=count,total_bytes=expected_entry['bytes']);last=time.monotonic()
  assert count==expected_entry['bytes'] and h.hexdigest()==expected_entry['sha256'],n
  if n=='manifest.json':
   d=json.loads(b''.join(content));assert d['run_id']==pre['run_id'] and d['preferred'] is True and d['source_git_commit']==GIT
  checked[n]=dict(bytes=count,sha256=h.hexdigest(),match=True)
  state(m,'REMOTE_FILE_VERIFIED',file=n)
 assert helper.is_private(api.get_repo(repo,'model'))
 receipt=dict(status='COMPLETE',repo=repo,visibility='PRIVATE',revision=rev,archive_sha256=pre['archive_sha256'],archive_sha256_definition=pre['archive_sha256_definition'],
  file_count=len(expected),total_bytes=sum(v['bytes'] for v in expected.values()),remote_file_count=len(names),managed_extra_files=sorted(extras),files=checked,remote_verification='PASS_ALL_FILES_SIZE_AND_SHA',
  independent_download=True,verification_mode='FRESH_PROCESS_UNCACHED_NETWORK_STREAM_NO_DISK_COPY',verifier_pid=os.getpid(),source_preserved=True,verification_copy_deleted=False,
  uniqueness='PASS_ACCOUNT_INVENTORY_NO_MATCHING_WEIGHTS_BEFORE_UPLOAD',uploaded_at=upload['uploaded_at'],verified_at=now())
 put(E/m/'modelscope_archive.json',receipt)

def verify_segment(m):
 """2026-09-09 user policy: small files fully fetched; shards sampled."""
 api=helper.api_client();pre=get(O/(m+'_preflight.json'));upload=get(O/(m+'_upload.json'))
 repo=pre['repo'];rev=upload['revision'];expected=pre['files'];segments=[];checked={};remote=[]
 audit=dict(method=m,revision=rev,chunk_bytes=2<<20,segments=segments,started_at=now())
 try:
  assert re.fullmatch('[0-9a-f]{40}',rev),'IMMUTABLE_REVISION_INVALID'
  assert helper.is_private(api.get_repo(repo,'model')),'REPO_NOT_PRIVATE'
  remote=files(api,repo,rev);byname={f['path']:f for f in remote};extras=set(byname)-set(expected)
  assert len(byname)==len(remote) and set(expected)<=set(byname) and extras<={'.gitattributes','.mdlignore'},'REMOTE_FILE_LIST_MISMATCH'
  # Preserve upload anomaly evidence; do not silently sample a retried upload.
  log=P/'results/active_cross_lineage_ba/archive/archive_worker.log'
  if not log.exists():log=P/'results/active_cross_lineage_ba/archive/worker.log'
  if log.exists():
   body=log.read_text(errors='replace');start=body.rfind(m+' UPLOAD_PRIVATE');end=body.find(m+' INDEPENDENT_VERIFY',start)
   assert start>=0 and end>=start,'UPLOAD_LOG_WINDOW_UNCONFIRMED'
   window=body[start:end];audit['upload_log_window_sha256']=hashlib.sha256(window.encode()).hexdigest()
   assert not re.search(r'(?i)retry|retrying|interrupted|partial failure|traceback|\berror\b',window),'UPLOAD_RETRY_OR_INTERRUPTION'
  else:raise ValueError('UPLOAD_LOG_NOT_FOUND')
  for n in sorted(byname):
   rf=byname[n];v=expected.get(n,dict(bytes=rf['size'],sha256=digest(rf)))
   assert rf['size']==v['bytes'] and digest(rf)==v['sha256'], 'REMOTE_SIZE_OR_IDENTITY_MISMATCH:'+n
   if n.endswith('.safetensors') and v['bytes']>64<<20:
    length=2<<20;size=v['bytes'];offsets=[0,size//4-length//2,size//2-length//2,3*size//4-length//2,size-length]
    for offset in offsets:
     with (pathlib.Path(pre['package'])/n).open('rb') as source:source.seek(offset);local=source.read(length)
     assert len(local)==length,'SOURCE_CHUNK_INCOMPLETE'
     headers=api.downloader._build_download_headers();headers['Range']=f'bytes={offset}-{offset+length-1}'
     response=api.downloader._client.download_stream(repo,'model',n,rev,headers=headers)
     with response:
      assert response.status_code==206 and response.headers.get('Content-Range')==f'bytes {offset}-{offset+length-1}/{size}','RANGE_NOT_SUPPORTED_OR_INCONSISTENT'
      h=hashlib.sha256();count=0
      for block in response.iter_content(chunk_size=1<<20):
       count+=len(block);assert count<=length,'RANGE_OVERREAD';h.update(block)
     item=dict(file=n,offset=offset,length=length,source_chunk_sha256=hashlib.sha256(local).hexdigest(),remote_chunk_sha256=h.hexdigest())
     item['match']=count==length and item['source_chunk_sha256']==item['remote_chunk_sha256'];segments.append(item);put(O/(m+'_segment_verification.json'),audit)
     assert item['match'],'CHUNK_SHA_MISMATCH:'+n
     state(m,'REMOTE_SEGMENT_VERIFIED',file=n,offset=offset,segment_count=len(segments))
    checked[n]=dict(bytes=size,sha256=v['sha256'],sha256_basis='REMOTE_METADATA_MATCHES_SOURCE_FULL_SHA',match=True,full_remote_bytes_verified=False,verification_basis='MANIFEST_AND_FIVE_SEGMENTS')
   else:
    response=api.downloader._client.download_stream(repo,'model',n,rev,headers=api.downloader._build_download_headers());response.raise_for_status()
    h=hashlib.sha256();count=0;content=[]
    with response:
     for block in response.iter_content(chunk_size=1<<20):
      count+=len(block);assert count<=v['bytes'],'SMALL_FILE_OVERREAD';h.update(block)
      if n=='manifest.json':content.append(block)
    assert count==v['bytes'] and h.hexdigest()==v['sha256'],'SMALL_FILE_SHA_MISMATCH:'+n
    if n=='manifest.json':
     manifest=json.loads(b''.join(content));assert manifest['run_id']==pre['run_id'] and manifest['preferred'] is True and manifest['source_git_commit']==GIT
    checked[n]=dict(bytes=count,sha256=h.hexdigest(),match=True,full_remote_bytes_verified=True)
  assert helper.is_private(api.get_repo(repo,'model'))
  assert files(api,repo,rev)==remote,'REMOTE_METADATA_CHANGED'
 except Exception as exc:
  audit.update(status='FULL_DOWNLOAD_TRIGGERED',reason=type(exc).__name__+': '+str(exc),completed_at=now());put(O/(m+'_segment_verification.json'),audit)
  state(m,'FULL_DOWNLOAD_ESCALATION',reason=audit['reason'])
  verify(m)
  r=get(E/m/'modelscope_archive.json');r.update(verification_mode='FULL_INDEPENDENT_DOWNLOAD',verification_status='PASS',full_independent_download_sha_verified='PASS',full_remote_download_performed=True,reason_if_full_download_triggered=audit['reason'],segment_count=len(segments),segment_matches=sum(x['match'] for x in segments));put(E/m/'modelscope_archive.json',r)
  return
 audit.update(status='PASS',completed_at=now());put(O/(m+'_segment_verification.json'),audit)
 receipt=dict(status='COMPLETE',repo=repo,visibility='PRIVATE',revision=rev,archive_sha256=pre['archive_sha256'],archive_sha256_definition=pre['archive_sha256_definition'],file_count=len(expected),total_bytes=sum(v['bytes'] for v in expected.values()),remote_file_count=len(remote),managed_extra_files=sorted(extras),files=checked,
  remote_manifest_verification='PASS',remote_manifest_and_segment_verification='PASS',remote_verification='REMOTE_MANIFEST_AND_SEGMENT_VERIFICATION_PASS',verification_mode='MANIFEST_PLUS_SEGMENT',verification_status='PASS',full_remote_download_performed=False,full_independent_download_sha_verified='NOT_PERFORMED',reason_if_full_download_triggered=None,segment_count=len(segments),segment_matches=sum(x['match'] for x in segments),segments=segments,chunk_bytes=2<<20,independent_download=False,independent_network_segment_reads=True,verifier_pid=os.getpid(),source_preserved=True,uniqueness='PASS_ACCOUNT_INVENTORY_NO_MATCHING_WEIGHTS_BEFORE_UPLOAD',uploaded_at=upload['uploaded_at'],verified_at=now())
 put(E/m/'modelscope_archive.json',receipt)


def run():
 pre=get(O/'preflight.json');assert pre['status']=='PASS'
 api=helper.api_client()
 for m in ORDER:
  if (E/m/'modelscope_archive.json').exists():
   assert get(E/m/'modelscope_archive.json')['status']=='COMPLETE';continue
  g=pre['gates'][m]
  if not (O/(m+'_upload.json')).exists():
   assert not api.repo_exists(g['repo'],'model'),'EXISTING_REMOTE_WITHOUT_RECEIPT_REQUIRES_INSPECTION'
   state(m,'BUILD_PACKAGE')
   if (O/(m+'_preflight.json')).exists():
    pack=get(O/(m+'_preflight.json'))
    for n,v in pack['files'].items():
     f=pathlib.Path(pack['package'])/n
     assert f.stat().st_size==v['bytes'] and sha(f)==v['sha256']
   else:pack=package(m,g)
   state(m,'UPLOAD_PRIVATE')
   api.create_repo(g['repo'],'model',visibility=1,description=CARDS[m])
   assert helper.is_private(api.get_repo(g['repo'],'model'))
   result=api.upload_folder(g['repo'],'model',pathlib.Path(pack['package']),path_in_repo='',allow_patterns=list(pack['files']),ignore_patterns=['.ms_upload_cache'],use_cache=False,disable_tqdm=True,sync_remote_repo=False,commit_message='Archive ONE user-approved preferred final XBa Student')
   assert re.fullmatch('[0-9a-f]{40}',result['commit_id'])
   put(O/(m+'_upload.json'),dict(repo=g['repo'],revision=result['commit_id'],uploaded_at=now(),upload_result=result))
  state(m,'INDEPENDENT_VERIFY')
  subprocess.run([sys.executable,'-B',__file__,'verify',m],check=True)
  receipt=get(E/m/'modelscope_archive.json')
  for name in ['model_provenance.json','full_experiment_log.json','closure_summary.json']:
   f=E/m/name;d=get(f);d.update(preferred_final_model=True,modelscope_archive=receipt,archive_status='COMPLETE_PRIVATE_REMOTE_VERIFIED');put(f,d)
  state(m,'COMPLETE')
 put(E/'model_archive_summary.json',dict(status='COMPLETE',methods={m:get(E/m/'modelscope_archive.json') for m in ORDER},completed_at=now(),git_metadata_closure='PENDING'))
 state('ALL','ARCHIVAL_COMPLETE')

if __name__=='__main__':
 O.mkdir(parents=True,exist_ok=True)
 if sys.argv[1]=='run':
  import fcntl
  execution_lock=(O/'execution.lock').open('a')
  fcntl.flock(execution_lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 try:
  if sys.argv[1]=='preflight':preflight()
  elif sys.argv[1]=='verify':
   (verify_segment if sys.argv[2] in ['evertracer','iseal','scw'] else verify)(sys.argv[2])
  elif sys.argv[1]=='run':run()
  else:raise ValueError('Unknown mode')
 except BaseException as exc:
  put(O/'error.json',dict(time=now(),error_type=type(exc).__name__,message=str(exc)[:1000]));raise
