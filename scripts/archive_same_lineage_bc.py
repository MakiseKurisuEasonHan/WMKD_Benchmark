"""Bc-only PRIVATE preferred archival using the proven segment verifier on old CPU."""
import json
import os
from pathlib import Path
import re
import sys
import fcntl
import subprocess
import archive_active_cross_lineage_bb as engine

P=Path(__file__).resolve().parents[1];D=Path(str(P)+'_data');E=P/'results/logit_distillation/same_lineage_bc'
ORDER=['pnfp','evertracer','ctcc','iseal','scw','passive_shared']
LABEL=dict(pnfp='PNFP',evertracer='EverTracer',ctcc='CTCC',iseal='iSeal',scw='SCW',passive_shared='Passive5-Shared')

def prepare(m,api):
    q=E/m;full=engine.get(q/'full_experiment_log.json');cfg=full['protocol'];train=full['training']
    transfer=engine.get(q/'archive_transfer_receipt.json')
    assert full['scientific_closure']=='COMPLETE' and full['preferred_final_model'] is True
    assert full['fresh_process_reload'] is True and train['steps']==7500 and train['teacher_frozen']
    assert cfg['base_revision']=='0cb88a4f764b7a12671c53f0838cd831a0843b95'
    assert transfer['status']=='PASS' and transfer['source_model']==train['final_model']
    staging=Path(os.environ.get('WMKD_BC_ARCHIVE_STAGING_ROOT',str(D/'tmp')))
    assert staging in (D/'tmp',Path('/tmp/WMKD_Bc_archive_stage'))
    source=Path(transfer['destination']);assert source.resolve()==staging/('bc_'+m+'_preferred_transfer_20260910')
    expected={f['name']:f for f in train['final_files']}
    for n,x in expected.items():
        f=source/n;assert f.is_file() and not f.is_symlink() and f.stat().st_size==x['bytes'] and engine.sha(f)==x['sha256']
    shards=set(engine.get(source/'model.safetensors.index.json')['weight_map'].values());assert shards<=set(expected)
    repo=engine.helper.NAMESPACE+'/Llama-3.2-3B-WMKD-'+LABEL[m]+'-Same-Lineage-Bc-Student'
    inventory=[];matches=[];page=1;repos=[]
    while True:
        response=api.list_repos('model',owner=engine.helper.NAMESPACE,page_size=50,page_number=page);repos+=response.items
        if not response.has_next:break
        page+=1
    assert len(repos)==response.total_count and len({r.id for r in repos})==len(repos)
    for r in repos:
        fs=engine.files(api,r.id);ids={engine.digest(f) for f in fs};hits=[n for n in shards if expected[n]['sha256'] in ids]
        if hits:matches.append({'repo':r.id,'matching_shards':hits})
        inventory.append({'repo':r.id,'files':fs})
    engine.put(engine.O/(m+'_uniqueness.json'),{'inventory':inventory,'matches':matches,'checked_at':engine.now()})
    assert not matches,'EXISTING_EQUIVALENT_ARCHIVE_REQUIRES_REUSE_REVIEW'
    assert not api.repo_exists(repo,'model'),'TARGET_EXISTS_REQUIRES_REVIEW'
    dest=staging/('same_lineage_bc_'+m+'_preferred_archive_20260910');assert not dest.exists();dest.mkdir()
    allowed={n for n in expected if n.endswith('.safetensors') or n in ['config.json','generation_config.json','model.safetensors.index.json','tokenizer.json','tokenizer_config.json','special_tokens_map.json','chat_template.jinja','added_tokens.json']}
    for n in sorted(allowed):os.link(source/n,dest/n)
    (dest/'LICENSE.txt').write_bytes((D/'models/base/Llama-3.2-3B-Instruct/LICENSE.txt').read_bytes())
    meta={'project':'WMKD_Benchmark','campaign':'SAME_LINEAGE_ONLINE_LOGIT_DISTILLATION_Bc','method':LABEL[m],'experiment':'Bc','run_id':cfg['run_id'],'canonical_backbone':'meta-llama/Llama-3.2-3B-Instruct','model_revision':cfg['base_revision'],'preferred':True,'preferred_final_model':True,'scientific_status':full['final_scientific_status'],'source_git_commit':engine.GIT,'source_tree_has_uncommitted_runner':full.get('source_tree_has_uncommitted_runner',True),'runner_sha256':full['runner_sha256'],'fresh_clean_initialization':True,'continuation_from_other_student':False,'protocol':cfg,'detector':full['detector'],'utility':full['utility'],'retention_basis':'User-approved reproducibility artifact; not proof of watermark transfer or utility superiority.','artifact_files':{n:{'bytes':(dest/n).stat().st_size,'sha256':engine.sha(dest/n)} for n in sorted(allowed|{'LICENSE.txt'})}}
    engine.put(dest/'manifest.json',meta)
    (dest/'README.md').write_text('# '+LABEL[m]+' Same-Lineage Bc Student\n\nPRIVATE preferred reproducibility artifact. Fresh canonical Llama, frozen ordinary parent data, online CE+KL distillation. See manifest.json for identities, actual results and limitations.\n')
    (dest/'SHA256SUMS').write_text(''.join(engine.sha(f)+'  '+f.name+'\n' for f in sorted(dest.iterdir())))
    files={f.name:{'bytes':f.stat().st_size,'sha256':engine.sha(f)} for f in dest.iterdir()}
    for n in files:
        if not n.endswith('.safetensors'):assert not re.search(rb'hf_[A-Za-z0-9]{25,}|gh[pousr]_[A-Za-z0-9]{25,}|-----BEGIN (?:RSA |OPENSSH )?PRIVATE KEY-----',(dest/n).read_bytes())
    pre={'status':'PASS','repo':repo,'package':str(dest),'files':files,'archive_sha256':engine.sha(dest/'SHA256SUMS'),'archive_sha256_definition':'SHA256 of SHA256SUMS; binds package files','run_id':cfg['run_id'],'source_preserved':True}
    engine.put(engine.O/(m+'_preflight.json'),pre);return pre

def run(m):
    lock=(engine.O/'execution.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    if (E/m/'modelscope_archive.json').exists():
        assert engine.get(E/m/'modelscope_archive.json')['status']=='COMPLETE';return
    api=engine.helper.api_client();up=engine.O/(m+'_upload.json')
    if not up.exists():
        prepath=engine.O/(m+'_preflight.json')
        if prepath.exists():
            pre=engine.get(prepath)
            for n,v in pre['files'].items():
                f=Path(pre['package'])/n;assert f.stat().st_size==v['bytes'] and engine.sha(f)==v['sha256']
            assert not api.repo_exists(pre['repo'],'model'),'Remote exists without receipt: inspect before retry'
        else:pre=prepare(m,api)
        engine.state(m,'UPLOAD_PRIVATE');api.create_repo(pre['repo'],'model',visibility=1,description=engine.CARDS[m]);assert engine.helper.is_private(api.get_repo(pre['repo'],'model'))
        result=api.upload_folder(pre['repo'],'model',Path(pre['package']),path_in_repo='',allow_patterns=list(pre['files']),ignore_patterns=['.ms_upload_cache'],use_cache=False,disable_tqdm=True,sync_remote_repo=False,commit_message='Archive ONE approved preferred Same-Lineage Bc Student')
        assert re.fullmatch('[0-9a-f]{40}',result['commit_id'])
        engine.put(up,{'repo':pre['repo'],'revision':result['commit_id'],'uploaded_at':engine.now(),'upload_result':result})
    engine.state(m,'INDEPENDENT_VERIFY')
    subprocess.run([sys.executable,'-B',__file__,'verify',m],check=True)
    receipt=engine.get(E/m/'modelscope_archive.json');assert receipt['status']=='COMPLETE'
    full=engine.get(E/m/'full_experiment_log.json');full.update(modelscope_archive=receipt,archive_status='COMPLETE_PRIVATE_REMOTE_VERIFIED');engine.put(E/m/'full_experiment_log.json',full)
    engine.state(m,'COMPLETE')

if __name__=='__main__':
    mode,m=sys.argv[1:3];assert m in ORDER
    engine.E=E;engine.O=E/'archive';engine.O.mkdir(parents=True,exist_ok=True)
    engine.ORDER=ORDER;engine.GIT=engine.get(E/m/'full_experiment_log.json')['source_git_commit']
    engine.REV='0cb88a4f764b7a12671c53f0838cd831a0843b95';engine.__file__=__file__
    engine.UPLOAD_LOG_PATH=E/m/'archive_chain.log'
    engine.CARDS={k:'PRIVATE Same-Lineage Bc preferred Llama Student for reproducibility.' for k in ORDER};engine.prepare_one=prepare
    if mode=='run':run(m)
    elif mode=='verify':engine.verify_segment(m)
    else:raise ValueError(mode)
