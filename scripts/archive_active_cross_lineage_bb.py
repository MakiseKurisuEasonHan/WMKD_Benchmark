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
E = P/'results/active_cross_lineage_bb'
O = E/'archive'
sys.path.insert(0,str(P/'scripts'))
import modelscope_passive5_ba_student_archive as helper

ORDER = ['pnfp','evertracer','ctcc','iseal','scw']
LABEL = dict(pnfp='PNFP',ctcc='CTCC',evertracer='EverTracer',iseal='iSeal',scw='SCW')
GIT = '2e236d133590a789a54e15d9f43f348d15082f59'
REV = '8f4992eda43eea7c770690ddc0de8f732da246f5'
CARDS = {m: 'Active Cross-Lineage Bb preferred final Qwen Student for reproducibility. Scientific results and limitations are recorded in manifest.json.' for m in ORDER}

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
  log=O/'worker.log'
  if not log.exists():log=O/'worker.log'
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




def prepare_one(m, api):
 q=E/m;full=get(q/'full_experiment_log.json');prov=get(q/'model_provenance.json');transfer=get(q/'archive_transfer_receipt.json')
 assert full['scientific_closure']=='COMPLETE' and full['preferred_final_model'] is True
 protocol=full['protocol'];launch=full['launch']
 assert protocol['revision']==REV and protocol['dataset']['target_field']=='paraphrased_answer'
 assert full['training_summary']['steps']==7500 and transfer['status']=='PASS'
 assert prov['status']=='FRESH_RELOAD_VERIFIED' and transfer['source_model']==prov['model_path']
 assert launch['source_git_commit']==GIT
 source=pathlib.Path(transfer['destination'])
 assert source.resolve()==D/'tmp'/('xbb_'+m+'_preferred_transfer_20260909')
 expected={x['name']:x for x in prov['files']}
 for n,x in expected.items():
  f=source/n;assert f.is_file() and not f.is_symlink() and f.stat().st_size==x['bytes'] and sha(f)==x['sha256'],n
 shards=sorted(set(get(source/'model.safetensors.index.json')['weight_map'].values()))
 assert set(shards)<=set(expected) and len(shards)==2
 repo=helper.NAMESPACE+'/Qwen2.5-3B-WMKD-Active-'+LABEL[m]+'-Cross-Lineage-'+('Bb2' if m=='ctcc' else 'Bb')+'-Student'
 # Inventory every owned model repository, using remote identities only.
 repos=[];page=1
 while True:
  result=api.list_repos('model',owner=helper.NAMESPACE,page_size=50,page_number=page);repos+=result.items
  if not result.has_next:break
  page+=1
 assert len(repos)==result.total_count and len({r.id for r in repos})==len(repos)
 inventory=[];matches=[]
 for i,r in enumerate(repos):
  state(m,'REMOTE_UNIQUENESS_INVENTORY',checked=i,total=len(repos))
  fs=files(api,r.id);identities={digest(f) for f in fs}
  hits=[n for n in shards if expected[n]['sha256'] in identities]
  if hits:matches.append(dict(repo=r.id,matching_shards=hits))
  inventory.append(dict(repo=r.id,private=helper.is_private(r),files=fs))
 put(O/(m+'_uniqueness.json'),dict(inventory=inventory,matches=matches,checked_at=now()))
 assert not matches,'EXISTING_MATCHING_WEIGHTS_REUSE_REQUIRED'
 assert not api.repo_exists(repo,'model'),'EXISTING_TARGET_REQUIRES_INSPECTION_NO_OVERWRITE'
 dest=D/'tmp'/('active_cross_lineage_bb_'+m+'_preferred_archive_20260909')
 assert not dest.exists(),'EXISTING_PACKAGE_REQUIRES_RECEIPT_REVIEW'
 dest.mkdir()
 allowed={n for n in expected if n.endswith('.safetensors') or n in ['config.json','generation_config.json','model.safetensors.index.json','tokenizer.json','tokenizer_config.json','special_tokens_map.json','vocab.json','merges.txt','chat_template.jinja','added_tokens.json']}
 assert set(shards)<=allowed
 for n in sorted(allowed):os.link(source/n,dest/n)
 (dest/'LICENSE').write_bytes((D/'models/paraphrasers/Qwen2.5-3B-Instruct/LICENSE').read_bytes())
 utility=full['utility_results']
 meta=dict(project='WMKD_Benchmark',campaign='ACTIVE_CROSS_LINEAGE_BB',method=LABEL[m],experiment=full['experiment'],run_id=full['run_id'],canonical_backbone='Qwen/Qwen2.5-3B-Instruct',model_revision=REV,preferred=True,preferred_final_model=True,scientific_status=full['final_scientific_status'],source_git_commit=GIT,source_tree_has_uncommitted_runner=True,runner_sha256=launch['runner_sha256'],model_source=prov['model_path'],transfer_receipt=str(q/'archive_transfer_receipt.json'),fresh_clean_qwen_initialization=True,continuation_from_other_student=False,training=protocol['training'],dataset=protocol['dataset'],detector_applicability_level=protocol['detector_applicability'],comparison=full.get('comparison'),utility={k:utility[k] for k in ['arc_challenge_acc_norm','truthfulqa_mc2_acc']},retention_basis='User-approved reproducibility retention, not a claim of successful watermark transfer or utility superiority.',artifact_files={n:dict(bytes=(dest/n).stat().st_size,sha256=sha(dest/n)) for n in sorted(allowed|{'LICENSE'})})
 put(dest/'manifest.json',meta)
 (dest/'README.md').write_text('# '+LABEL[m]+' Active Cross-Lineage Bb Qwen Student\n\nPRIVATE preferred reproducibility artifact. Frozen paraphrased Teacher QA, fresh clean Qwen initialization. See manifest.json for measured results and limitations. Training source includes an uncommitted runner whose exact SHA is recorded. This archive does not assert complete watermark transfer. Qwen RESEARCH LICENSE AGREEMENT is included.\n')
 (dest/'SHA256SUMS').write_text(''.join(sha(f)+'  '+f.name+'\n' for f in sorted(dest.iterdir())))
 packfiles={f.name:dict(bytes=f.stat().st_size,sha256=sha(f)) for f in dest.iterdir()}
 for n in packfiles:
  if not n.endswith('.safetensors'):assert not re.search(rb'(?:hf_[A-Za-z0-9]{25,}|gh[pousr]_[A-Za-z0-9]{25,}|-----BEGIN (?:RSA |OPENSSH )?PRIVATE KEY-----)',(dest/n).read_bytes()),n
 pre=dict(status='PASS',repo=repo,package=str(dest),files=packfiles,archive_sha256=sha(dest/'SHA256SUMS'),archive_sha256_definition='SHA256 of SHA256SUMS; binds package files',run_id=full['run_id'],source_preserved=True)
 put(O/(m+'_preflight.json'),pre)
 return pre


def run_one(m):
 assert m in ORDER
 import fcntl
 lock=(O/'execution.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 if (E/m/'modelscope_archive.json').exists():
  assert get(E/m/'modelscope_archive.json')['status']=='COMPLETE';return
 api=helper.api_client()
 if not (O/(m+'_upload.json')).exists():
  if (O/(m+'_preflight.json')).exists():
   pre=get(O/(m+'_preflight.json'))
   for n,v in pre['files'].items():
    f=pathlib.Path(pre['package'])/n;assert f.stat().st_size==v['bytes'] and sha(f)==v['sha256']
   assert not api.repo_exists(pre['repo'],'model'),'REMOTE_EXISTS_WITHOUT_UPLOAD_RECEIPT_KEEP_AND_INSPECT'
  else:pre=prepare_one(m,api)
  state(m,'UPLOAD_PRIVATE')
  api.create_repo(pre['repo'],'model',visibility=1,description=CARDS[m])
  assert helper.is_private(api.get_repo(pre['repo'],'model'))
  result=api.upload_folder(pre['repo'],'model',pathlib.Path(pre['package']),path_in_repo='',allow_patterns=list(pre['files']),ignore_patterns=['.ms_upload_cache'],use_cache=False,disable_tqdm=True,sync_remote_repo=False,commit_message='Archive ONE approved preferred final XBb Student')
  assert re.fullmatch('[0-9a-f]{40}',result['commit_id'])
  put(O/(m+'_upload.json'),dict(repo=pre['repo'],revision=result['commit_id'],uploaded_at=now(),upload_result=result))
 state(m,'INDEPENDENT_VERIFY')
 subprocess.run([sys.executable,'-B',__file__,'verify',m],check=True)
 r=get(E/m/'modelscope_archive.json');assert r['status']=='COMPLETE'
 full=get(E/m/'full_experiment_log.json');full.update(modelscope_archive=r,archive_status='COMPLETE_PRIVATE_REMOTE_VERIFIED');put(E/m/'full_experiment_log.json',full)
 state(m,'COMPLETE')


if __name__=='__main__':
 O.mkdir(parents=True,exist_ok=True)
 try:
  if sys.argv[1]=='run':run_one(sys.argv[2])
  elif sys.argv[1]=='verify':verify_segment(sys.argv[2])
  else:raise ValueError('Unknown mode')
 except BaseException as exc:
  put(O/'error.json',dict(time=now(),error_type=type(exc).__name__,message=str(exc)[:1000]));raise
