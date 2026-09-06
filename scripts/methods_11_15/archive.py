"""PRIVATE archive + independent file/hash verification; never delete source."""
import os, shutil, sys, stat
from common import *

def archive_model(c,model,extras=()):
    rr=Path(c['run_root']); request=rr/'archive_request.json'
    write(request,{'context':c,'model':str(model),'extras':[str(x) for x in extras]})
    cli=DATA/'artifacts/modelscope_cli_env/bin/python'
    errors=[]
    for workers in (4,1):
        try:
            env=os.environ.copy(); env.pop('PYTHONPATH',None)
            cmd([cli,Path(__file__),request,str(workers)],timeout=10800,env=env)
            return read(rr/'archive.json')
        except Exception as e: errors.append({'workers':workers,'error':str(e)})
    raise Blocked('BLOCKED_ARCHIVE','PRIVATE archive failed; canonical local model retained: '+str(errors))

def main():
    from modelscope_hub.api import HubApi
    req=read(sys.argv[1]); c=req['context']; rr=Path(c['run_root']); workers=int(sys.argv[2])
    secret=DATA/'secrets/modelscope.env'
    assert stat.S_IMODE(secret.stat().st_mode)==0o600
    v=dict(line.split('=',1) for line in secret.read_text().splitlines() if line and not line.startswith('#') and '=' in line)
    assert v['MODELSCOPE_NAMESPACE']=='MakiseKurisuEasonHan'
    api=HubApi(token=v['MODELSCOPE_API_TOKEN'])
    repo='MakiseKurisuEasonHan/WMKD-'+c['method'].replace('_','-')+'-A-'+c['run_id'].split('_a_')[-1]
    package=rr/'archive_package'; package.mkdir(exist_ok=True)
    model=Path(req['model'])
    for p in model.rglob('*'):
        if p.is_file() and '.git' not in p.parts and not any(x.startswith('checkpoint-') for x in p.relative_to(model).parts):
            dst=package/p.relative_to(model); dst.parent.mkdir(parents=True,exist_ok=True)
            if not dst.exists(): os.link(p,dst)
    for p in map(Path,req['extras']):
        dst=package/'WMKD_PROVENANCE'/p.name; dst.parent.mkdir(exist_ok=True)
        if p.is_file(): shutil.copyfile(p,dst)
        elif p.is_dir(): shutil.copytree(p,dst,dirs_exist_ok=True)
    # Freeze all available stage evidence, including failed attempts, with this archive.
    evidence=package/'WMKD_PROVENANCE/RUN_EVIDENCE'; evidence.mkdir(parents=True,exist_ok=True)
    for p in rr.iterdir():
        if p.is_file() and p.suffix in ('.json','.jsonl','.log','.patch') and not p.name.startswith('ARCHIVED'):
            shutil.copyfile(p,evidence/p.name)
    shutil.copytree(rr/'receipts',evidence/'receipts',dirs_exist_ok=True)
    manifest={'method':c['method'],'run_id':c['run_id'],'source':c['spec'],'files':{k:v for k,v in tree_manifest(package).items() if k!='WMKD_ARCHIVE_MANIFEST.json' and not k.startswith('.ms_upload_cache')}}
    write(package/'WMKD_ARCHIVE_MANIFEST.json',manifest)
    expected={**manifest['files'],'WMKD_ARCHIVE_MANIFEST.json':{'size':(package/'WMKD_ARCHIVE_MANIFEST.json').stat().st_size,'sha256':sha(package/'WMKD_ARCHIVE_MANIFEST.json')}}
    def private(r):
        vis=getattr(getattr(r,'visibility',None),'value',getattr(r,'visibility',None))
        return getattr(r,'private',None) is True or vis in (1,'private','PRIVATE')
    if not api.repo_exists(repo,'model'): api.create_repo(repo,'model',visibility=1,description='PRIVATE WMKD official Experiment A reproduction with detector provenance')
    assert private(api.get_repo(repo,'model')),'PRIVATE required before transfer'
    api.upload_folder(repo,'model',package,path_in_repo='',commit_message='Archive canonical Experiment A',disable_tqdm=True,sync_remote_repo=False)
    assert private(api.get_repo(repo,'model'))
    verify=rr/f'archive_verification_workers{workers}'
    got=Path(api.download_repo(repo,'model',local_dir=verify,local_files_only=False,max_workers=workers))
    # Verify the frozen scientific payload; SDK upload-cache bookkeeping is transport-only.
    for name,info in expected.items():
        p=got/name
        assert p.is_file() and p.stat().st_size==info['size'] and sha(p)==info['sha256'],name
    write(rr/'archive.json',{'status':'VERIFIED_ARCHIVED','repository':repo,'visibility':'PRIVATE','canonical_local_retained':str(model),'independent_redownload':True,'verified_files':len(expected),'files':expected,'recovery_directory':str(got),'verified_at':now()})

if __name__=='__main__': main()
