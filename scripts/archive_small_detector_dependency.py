#!/usr/bin/env python3
"""Archive one exact small detector dependency to a PRIVATE ModelScope dataset."""
from __future__ import annotations
import argparse, hashlib, json, shutil, stat
from datetime import datetime, timezone
from pathlib import Path
from modelscope_hub.api import HubApi

DATA=Path('/root/autodl-tmp/WMKD_Benchmark_data'); SECRET=DATA/'secrets/modelscope.env'; NS='MakiseKurisuEasonHan'
CASES={
 'pnfp': {'repo':f'{NS}/WMKD_Benchmark_pnfp_canonical_detector_keys','file':DATA/'runs/pnfp_bb/pnfp_bb_20260904_055000/evaluation/detector_input/fingerprint_keys-perinucleus--root-autodl-tmp-WMKD_Benchmark_data-models-base-Llama-3.2-3B-Instruct-nucleus_threshold-0.8-response_length-16-use_chat_template-True.json','name':'fingerprint_keys.json','sha':'922d3aec3b6bbac62dcdcf617b41e08a1384e7875db77aa6c4f9a278e03a8612','used_count':1024,'role':'PN-FP canonical detector fingerprint-key package'},
 'scw': {'repo':f'{NS}/WMKD_Benchmark_scw_recovered_exact_detector_input','file':DATA/'evaluation/scw/a2_french_eval/scw_a2_french_eval_1000.jsonl','name':'scw_a2_french_eval_1000.jsonl','sha':'c60cd7d03acbd3535c5564eafe521f88179833761924953fa599237c5082a69d','used_count':1000,'role':'SCW recovered-exact canonical 1000-sample detector input'},
}
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(8<<20),b''):h.update(b)
 return h.hexdigest()
def creds():
 if stat.S_IMODE(SECRET.stat().st_mode)!=0o600: raise RuntimeError('CREDENTIAL_MODE_NOT_600')
 v={}
 for x in SECRET.read_text().splitlines():
  if x and not x.startswith('#') and '=' in x:k,z=x.split('=',1);v[k]=z
 if v.get('MODELSCOPE_NAMESPACE')!=NS or not v.get('MODELSCOPE_API_TOKEN'):raise RuntimeError('CREDENTIAL_UNAVAILABLE')
 return v
def private(r):
 v=getattr(getattr(r,'visibility',None),'value',getattr(r,'visibility',None));return getattr(r,'private',None) is True or v in (1,'private','PRIVATE')
def main():
 a=argparse.ArgumentParser();a.add_argument('case',choices=CASES);x=a.parse_args();c=CASES[x.case];src=c['file']
 if not src.is_file() or sha(src)!=c['sha']:raise RuntimeError('CANONICAL_SOURCE_IDENTITY_MISMATCH')
 stamp=datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S'); stage=DATA/'tmp'/f'modelscope_upload_{x.case}_detector_dependency_{stamp}';stage.mkdir(parents=True)
 shutil.copyfile(src,stage/c['name'])
 manifest={'schema_version':'wmkd.detector-dependency-archive.v1','method':x.case.upper(),'artifact_role':c['role'],'source_path':str(src),'canonical_filename':c['name'],'physical_sha256':c['sha'],'physical_size':src.stat().st_size,'detector_count_used':c['used_count'],'scientific_artifact_unchanged':True,'repository':c['repo'],'visibility':'PRIVATE','secret_policy_review':'PRIVATE scientific detector dependency explicitly authorized for archival; contains no service credential, API token, password, SSH key, or environment secret','created_at':datetime.now(timezone.utc).isoformat()}
 (stage/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');(stage/'README.md').write_text(f"# {c['role']}\n\nPrivate transport archive of the exact existing WMKD_Benchmark detector dependency. No regeneration or scientific change. Verify against manifest and SHA256SUMS.\n")
 (stage/'SHA256SUMS').write_text(''.join(f'{sha(p)}  {p.name}\n' for p in sorted(stage.iterdir()) if p.name!='SHA256SUMS'))
 api=HubApi(token=creds()['MODELSCOPE_API_TOKEN'])
 if api.repo_exists(c['repo'],'dataset'):
  r=api.get_repo(c['repo'],'dataset')
  if not private(r):raise RuntimeError('EXISTING_REPO_NOT_PRIVATE')
  files=[z.path for z in api.list_repo_files(c['repo'],'dataset',recursive=True) if not z.is_dir]
  if files:raise RuntimeError('EXISTING_REPO_CONTENT_REQUIRES_REVIEW')
 else: api.create_repo(c['repo'],'dataset',visibility=1,description=c['role'])
 if not private(api.get_repo(c['repo'],'dataset')):raise RuntimeError('PRIVATE_NOT_CONFIRMED_BEFORE_UPLOAD')
 api.upload_folder(c['repo'],'dataset',stage,path_in_repo='',commit_message=f'Archive {c["role"]}',disable_tqdm=True,sync_remote_repo=False)
 if not private(api.get_repo(c['repo'],'dataset')):raise RuntimeError('PRIVATE_NOT_CONFIRMED_AFTER_UPLOAD')
 verify=DATA/'tmp'/f'modelscope_verify_{x.case}_detector_dependency_{stamp}';got=Path(api.download_repo(c['repo'],'dataset',local_dir=verify,local_files_only=False,max_workers=4))
 infrastructure={'.gitattributes','.mdlignore','.ms_upload_cache'}
 expected={p.name:(p.stat().st_size,sha(p)) for p in stage.iterdir() if p.is_file() and p.name not in infrastructure};observed={p.name:(p.stat().st_size,sha(p)) for p in got.iterdir() if p.is_file() and p.name not in infrastructure}
 if expected!=observed or observed[c['name']][1]!=c['sha']:raise RuntimeError('INDEPENDENT_REDOWNLOAD_VERIFICATION_FAILED')
 evidence={'status':'PASS','classification':'VERIFIED_ARCHIVED','repository':c['repo'],'visibility':'PRIVATE','source':manifest,'package_files':{k:{'size':v[0],'sha256':v[1]} for k,v in expected.items()},'independent_redownload':True,'verification_directory':str(got),'scientific_configuration_changed':False,'verified_at':datetime.now(timezone.utc).isoformat(),'temporary_verification_copy_deleted':False}
 out=DATA/'archive_remediation/evidence'/f'{x.case}_detector_dependency_{stamp}.json';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(evidence,indent=2)+'\n')
 shutil.rmtree(got);shutil.rmtree(stage);evidence['temporary_verification_copy_deleted']=True;evidence['upload_staging_deleted']=True;out.write_text(json.dumps(evidence,indent=2)+'\n')
 print(json.dumps({'status':'PASS','classification':'VERIFIED_ARCHIVED','repository':c['repo'],'evidence':str(out)}))
if __name__=='__main__':main()
