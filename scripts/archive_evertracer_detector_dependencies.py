#!/usr/bin/env python3
"""Archive exact EverTracer detector reference and neighborhoods to PRIVATE ModelScope."""
from __future__ import annotations
import hashlib,json,os,shutil,stat
from datetime import datetime,timezone
from pathlib import Path
from modelscope_hub.api import HubApi

D=Path('/root/autodl-tmp/WMKD_Benchmark_data'); NS='MakiseKurisuEasonHan'; REPO=f'{NS}/WMKD_Benchmark_evertracer_detector_dependencies'; SECRET=D/'secrets/modelscope.env'
RUN=D/'runs/evertracer/evertracer_a_20260828_223155'; REF=RUN/'checkpoints/reference_merged'; RM=RUN/'artifacts/reference_merge_manifest.json'; NB=D/'runs/evertracer/evertracer_a_20260828_223155_cont1/artifacts/frozen_neighborhoods.jsonl'; NB_SHA='7834e3d77704951ea06501c2166e960fef2b147ced3d751a8e55f07ec7b3672b'
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(8<<20),b''):h.update(b)
 return h.hexdigest()
def creds():
 if stat.S_IMODE(SECRET.stat().st_mode)!=0o600:raise RuntimeError('CREDENTIAL_MODE_NOT_600')
 v={}
 for x in SECRET.read_text().splitlines():
  if x and not x.startswith('#') and '=' in x:k,z=x.split('=',1);v[k]=z
 if v.get('MODELSCOPE_NAMESPACE')!=NS or not v.get('MODELSCOPE_API_TOKEN'):raise RuntimeError('CREDENTIAL_UNAVAILABLE')
 return v
def private(r):
 v=getattr(getattr(r,'visibility',None),'value',getattr(r,'visibility',None));return getattr(r,'private',None) is True or v in (1,'private','PRIVATE')
def main():
 source=json.loads(RM.read_text()); expected={x['path']:{'size':x['bytes'],'sha256':x['sha256']} for x in source['files']}
 for n,x in expected.items():
  p=REF/n
  if not p.is_file() or p.stat().st_size!=x['size'] or sha(p)!=x['sha256']:raise RuntimeError('REFERENCE_SOURCE_IDENTITY_FAIL:'+n)
 if sha(NB)!=NB_SHA or sum(1 for _ in open(NB,'rb'))!=200:raise RuntimeError('NEIGHBORHOODS_SOURCE_IDENTITY_FAIL')
 stamp=datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S');stage=D/'tmp'/f'modelscope_upload_evertracer_detector_dependencies_{stamp}';(stage/'reference_merged').mkdir(parents=True)
 for n in expected:os.link(REF/n,stage/'reference_merged'/n)
 shutil.copyfile(NB,stage/'frozen_neighborhoods.jsonl');shutil.copyfile(RM,stage/'reference_merge_manifest.json')
 manifest={'schema_version':'wmkd.evertracer-detector-dependencies-archive.v1','repository':REPO,'visibility':'PRIVATE','canonical_run':'evertracer_a_20260828_223155','reference_source':str(REF),'reference_source_manifest':str(RM),'reference_source_manifest_sha256':sha(RM),'reference_files':expected,'reference_total_bytes':sum(x['size'] for x in expected.values()),'frozen_neighborhoods_source':str(NB),'frozen_neighborhoods_size':NB.stat().st_size,'frozen_neighborhoods_sha256':NB_SHA,'frozen_neighborhoods_count':200,'lineage':['EverTracer A canonical detector','EverTracer Ba canonical detector','EverTracer Bb frozen detector'],'scientific_artifact_unchanged':True,'created_at':datetime.now(timezone.utc).isoformat()}
 (stage/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');(stage/'README.md').write_text('# WMKD EverTracer detector dependencies\n\nPRIVATE transport archive of the exact canonical reference_merged model and frozen 200-record neighborhoods. No training, merging, regeneration, or scientific change was performed.\n')
 files=[p for p in stage.rglob('*') if p.is_file() and p.name!='SHA256SUMS'];(stage/'SHA256SUMS').write_text(''.join(f'{sha(p)}  {p.relative_to(stage).as_posix()}\n' for p in sorted(files)))
 api=HubApi(token=creds()['MODELSCOPE_API_TOKEN'])
 if api.repo_exists(REPO,'model'):
  r=api.get_repo(REPO,'model')
  if not private(r):raise RuntimeError('EXISTING_REPO_NOT_PRIVATE')
  fs=[x.path for x in api.list_repo_files(REPO,'model',recursive=True) if not x.is_dir]
  if fs:raise RuntimeError('EXISTING_REPO_CONTENT_REQUIRES_REVIEW')
 else:api.create_repo(REPO,'model',visibility=1,description='Private exact EverTracer detector dependencies')
 if not private(api.get_repo(REPO,'model')):raise RuntimeError('PRIVATE_NOT_CONFIRMED_BEFORE_UPLOAD')
 api.upload_folder(REPO,'model',stage,path_in_repo='',commit_message='Archive exact EverTracer detector dependencies',disable_tqdm=True,sync_remote_repo=False)
 if not private(api.get_repo(REPO,'model')):raise RuntimeError('PRIVATE_NOT_CONFIRMED_AFTER_UPLOAD')
 remote={x.path:{'size':int(x.size),'sha256':x.sha256,'blob_id':x.blob_id} for x in api.list_repo_files(REPO,'model',recursive=True) if not x.is_dir}
 checks={};bad=[]
 for n,x in expected.items():
  key='reference_merged/'+n;o=remote.get(key);ok=bool(o and o['size']==x['size'] and o['sha256']==x['sha256'] and o['blob_id']==x['sha256']);checks[key]={'expected':x,'remote':o,'match':ok}
  if not ok:bad.append(key)
 if bad:raise RuntimeError('REFERENCE_STRONG_REMOTE_FAIL:'+str(bad))
 verify=D/'tmp'/f'modelscope_verify_evertracer_neighborhoods_{stamp}';got=Path(api.download_repo(REPO,'model',local_dir=verify,allow_patterns=['frozen_neighborhoods.jsonl','manifest.json','SHA256SUMS','README.md'],local_files_only=False,max_workers=4))
 rp=got/'frozen_neighborhoods.jsonl'
 if sha(rp)!=NB_SHA or rp.stat().st_size!=NB.stat().st_size or sum(1 for _ in open(rp,'rb'))!=200:raise RuntimeError('NEIGHBORHOODS_INDEPENDENT_VERIFY_FAIL')
 evidence={'status':'PASS','classification':'VERIFIED_ARCHIVED','repository':REPO,'visibility':'PRIVATE','reference_model_verification_tier':'ARCHIVED_STRONGLY_VERIFIED','reference_source_manifest_sha256':sha(RM),'reference_checks':checks,'frozen_neighborhoods_verification_tier':'VERIFIED_ARCHIVED','frozen_neighborhoods_sha256':NB_SHA,'frozen_neighborhoods_count':200,'frozen_neighborhoods_independent_redownload':True,'verification_directory':str(got),'scientific_configuration_changed':False,'verified_at':datetime.now(timezone.utc).isoformat(),'temporary_verification_copy_deleted':False}
 out=D/'archive_remediation/evidence'/f'evertracer_detector_dependencies_{stamp}.json';out.write_text(json.dumps(evidence,indent=2)+'\n');shutil.rmtree(got);evidence['temporary_verification_copy_deleted']=True;evidence['deleted_at']=datetime.now(timezone.utc).isoformat();out.write_text(json.dumps(evidence,indent=2)+'\n');print(json.dumps({'status':'PASS','repository':REPO,'reference':'ARCHIVED_STRONGLY_VERIFIED','neighborhoods':'VERIFIED_ARCHIVED','evidence':str(out)}))
if __name__=='__main__':main()
