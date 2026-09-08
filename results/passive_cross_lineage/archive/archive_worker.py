import pathlib,json,hashlib,subprocess,sys,os,datetime,re,traceback
P=pathlib.Path('/root/autodl-tmp/WMKD_Benchmark');D=pathlib.Path(str(P)+'_data');E=P/'results/passive_cross_lineage';O=E/'archive';sys.path.insert(0,str(P/'scripts'))
import modelscope_passive5_ba_student_archive as helper
REV='8f4992eda43eea7c770690ddc0de8f732da246f5'
def put(p,d):
 t=p.with_suffix(p.suffix+'.tmp');t.write_text(json.dumps(d,indent=2,default=str)+'\n');os.replace(t,p)
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8<<20),b''):h.update(b)
 return h.hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def main():
 api=helper.api_client();repos=[];page=1
 while True:
  r=api.list_repos('model',owner=helper.NAMESPACE,page_size=50,page_number=page);repos+=r.items
  if not r.has_next:break
  page+=1
 assert len(repos)==r.total_count and len({x.id for x in repos})==len(repos)
 gates={}
 for role in ['ba','bb']:
  F=E/role;full=json.loads((F/'full_experiment_log.json').read_text());assert full['status']=='COMPLETE'
  assert json.loads((F/'utility/exit_record.json').read_text())['returncode']==0
  M=D/f'runs/passive_cross_lineage_{role}/passive_cross_lineage_{role}_20260908/training/final_model';manifest=json.loads((F/'final_model_manifest.json').read_text());expected={pathlib.Path(x['path']).name:x['sha256'] for x in manifest['files']}
  hashes={p.name:sha(p) for p in M.iterdir() if p.is_file()};assert hashes==expected
  shards=set(json.loads((M/'model.safetensors.index.json').read_text())['weight_map'].values());assert len(shards)==2
  repo=helper.NAMESPACE+'/Qwen2.5-3B-WMKD-Passive5-Cross-Lineage-'+role.capitalize()+'-Student'
  assert not api.repo_exists(repo,'model'), 'EXISTING_PROPOSED_REPO_REQUIRES_INSPECTION'
  gates[role]=dict(model=str(M),hashes=hashes,shards=sorted(shards),repo=repo)
 inventory=[];duplicates=[]
 for r in repos:
  files=api.list_repo_files(r.id,'model',recursive=True);digests={f.sha256 for f in files if f.sha256}
  for f in files:
   if f.lfs:digests.add(f.lfs.get('sha256') or str(f.lfs.get('oid','')).replace('sha256:',''))
  matches=[role for role,g in gates.items() if any(g['hashes'][n] in digests for n in g['shards'])]
  if matches:duplicates.append(dict(repo=r.id,roles=matches))
  inventory.append(dict(repo=r.id,private=helper.is_private(r),files=[dict(path=f.path,size=f.size,sha256=f.sha256,lfs=f.lfs) for f in files if not f.is_dir]))
 put(O/'uniqueness_inventory.json',dict(status='PASS' if not duplicates else 'BLOCKED',repositories=len(repos),total_count=r.total_count if hasattr(r,'total_count') else len(repos),duplicates=duplicates,inventory=inventory,proposed={k:v['repo'] for k,v in gates.items()},checked_at=now()))
 assert not duplicates,duplicates
 head=subprocess.check_output(['git','-C',str(P),'rev-parse','HEAD']).decode().strip()
 for role,g in gates.items():
  F=E/role;M=pathlib.Path(g['model']);package=D/'tmp'/('passive_cross_lineage_'+role+'_preferred_archive_20260908');assert not package.exists();package.mkdir()
  allowed={n for n in g['hashes'] if n.endswith('.safetensors') or n in ['config.json','generation_config.json','model.safetensors.index.json','tokenizer.json','tokenizer_config.json','special_tokens_map.json','vocab.json','merges.txt','chat_template.jinja','added_tokens.json']}
  assert set(g['shards'])<=allowed and 'training_args.bin' not in allowed
  for name in sorted(allowed):os.link(M/name,package/name)
  (package/'LICENSE').write_bytes((D/'models/paraphrasers/Qwen2.5-3B-Instruct/LICENSE').read_bytes())
  clean=json.loads((E/'clean_qwen_baseline/utility/utility_results.json').read_text());utility=json.loads((F/'utility/utility_results.json').read_text());delta={k:utility[k]-clean[k] for k in ['arc_challenge_acc_norm','truthfulqa_mc2_acc']}
  metadata=dict(project='WMKD_Benchmark',method='Passive-5 Cross-Lineage',experiment=role.capitalize(),run_id=f'passive_cross_lineage_{role}_20260908',canonical_backbone='Qwen/Qwen2.5-3B-Instruct',model_revision=REV,preferred=True,preferred_final_model=True,scientific_status='COMPLETE',source_git_commit=head,source=str(M),fresh_clean_initialization=True,resume_from_ba=False,utility_delta=delta,retention_basis='Explicit user scientific retention decision; reproducibility and analysis, not superiority on all utility or proof of watermark transfer',calibration_limitation='Qwen participated in historical detector threshold calibration; clean-Qwen is not an independent held-out negative; threshold crossing does not prove successful watermark transfer',artifact_files={n:dict(bytes=(package/n).stat().st_size,sha256=sha(package/n)) for n in sorted(allowed|{'LICENSE'})})
  put(package/'manifest.json',metadata)
  (package/'README.md').write_text('# Qwen WMKD Passive Cross-Lineage '+role.capitalize()+' Student\n\nPRIVATE research reproducibility archive. Preferred retained artifact by explicit user decision.\n\n'+metadata['calibration_limitation']+'\n\nQwen2.5-3B-Instruct derivative, governed by included Qwen RESEARCH LICENSE AGREEMENT. No optimizer or intermediate checkpoints. See manifest.json and SHA256SUMS.\n')
  names=sorted(p.name for p in package.iterdir());(package/'SHA256SUMS').write_text(''.join(sha(package/n)+'  '+n+'\n' for n in names));names.append('SHA256SUMS');expected={n:dict(bytes=(package/n).stat().st_size,sha256=sha(package/n)) for n in names}
  for n in names:
   if not n.endswith('.safetensors'):
    assert not re.search(rb'(?:hf_[A-Za-z0-9]{25,}|gh[pousr]_[A-Za-z0-9]{25,}|-----BEGIN (?:RSA |OPENSSH )?PRIVATE KEY-----)',(package/n).read_bytes()),n
  put(F/'archive_preflight.json',dict(status='PASS',repo=g['repo'],package=str(package),files=expected,archive_sha256=sha(package/'SHA256SUMS'),archive_sha256_definition='SHA256 of SHA256SUMS; manifest binds every artifact file',preferred_final_model=True,utility_delta=delta,source_preserved=True))
  put(O/'runtime.json',dict(role=role,stage='UPLOAD',started_at=now()))
  assert not api.repo_exists(g['repo'],'model')
  api.create_repo(g['repo'],'model',visibility=1,description='PRIVATE WMKD research retained final '+role+' Qwen Student; no causal watermark transfer claim')
  assert helper.is_private(api.get_repo(g['repo'],'model'))
  result=api.upload_folder(g['repo'],'model',package,path_in_repo='',commit_message='Archive ONE preferred final '+role+' Student',allow_patterns=names,ignore_patterns=['.ms_upload_cache'],use_cache=False,disable_tqdm=True,sync_remote_repo=False)
  put(F/'archive_upload_receipt.json',dict(repo=g['repo'],upload_result=result,revisions=api.list_repo_revisions(g['repo'],'model'),files=expected,archive_sha256=sha(package/'SHA256SUMS')))
  put(O/'runtime.json',dict(role=role,stage='FRESH_REMOTE_VERIFY',started_at=now()))
  # Independent process and empty cache ensure content is retrieved, not reused from source/upload cache.
  verify=D/'tmp'/('passive_cross_lineage_'+role+'_remote_verify_20260908');assert not verify.exists()
  subprocess.run([sys.executable,'-B',__file__,'verify',role],check=True)
 put(O/'exit_record.json',dict(status='BOTH_PRIVATE_ARCHIVES_VERIFIED',completed_at=now()))
def verify(role):
 api=helper.api_client();F=E/role;pre=json.loads((F/'archive_preflight.json').read_text());repo=pre['repo'];dest=D/'tmp'/('passive_cross_lineage_'+role+'_remote_verify_20260908');assert not dest.exists()
 download=api.download_repo(repo,'model',local_dir=dest,cache_dir=dest.parent/(dest.name+'_cache'),ignore_patterns=['.gitattributes','.mdlignore'],max_workers=2,local_files_only=False)
 expected=pre['files'];actual={p.name for p in dest.iterdir() if p.is_file()};assert actual==set(expected),(actual,set(expected))
 for n,v in expected.items():assert (dest/n).stat().st_size==v['bytes'] and sha(dest/n)==v['sha256'],n
 assert helper.is_private(api.get_repo(repo,'model'))
 receipt=dict(status='COMPLETE',repo=repo,visibility='PRIVATE',revision='master',revision_metadata=api.list_repo_revisions(repo,'model'),archive_sha256=pre['archive_sha256'],archive_sha256_definition=pre['archive_sha256_definition'],files=expected,total_bytes=sum(v['bytes'] for v in expected.values()),file_count=len(expected),fresh_verifier_pid=os.getpid(),independent_download=True,verification_directory=str(dest),all_sha_match=True,source_preserved=True,verified_at=now())
 put(F/'modelscope_archive.json',receipt)
if __name__=='__main__':
 try:
  verify(sys.argv[2]) if len(sys.argv)>1 and sys.argv[1]=='verify' else main()
 except BaseException:
  put(O/'error.json',dict(error=traceback.format_exc(),time=now()));raise
