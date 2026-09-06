"""Pinned UTF construction, full embedding, verifier and native utility."""
import os, sys, re, urllib.request, hashlib, json, shutil
from common import *
from resources import model, prepare_work, overlay, patch
MAGIKARP_REV='764e8cd02e598deb65692184a03f843ce3543ded'
MAGIKARP_PACKAGES=['termcolor==3.1.0','numpy==1.26.4','scipy==1.13.1','scikit-learn==1.4.2','pandas==2.2.3','matplotlib==3.8.4','seaborn==0.13.2','contourpy==1.2.1','cycler==0.12.1','fonttools==4.53.1','kiwisolver==1.4.5','pyparsing==3.1.2','protobuf==5.29.5','pytz==2024.1']

def magikarp(c,work):
    dest=work/'magikarp'; dest.mkdir(exist_ok=True)
    api=f'https://api.github.com/repos/cohere-ai/magikarp/git/trees/{MAGIKARP_REV}?recursive=1'
    with urllib.request.urlopen(api,timeout=60) as response: tree=json.load(response)['tree']
    manifest={}
    for item in tree:
        name=item['path']
        if item['type']!='blob' or not (name.startswith('magikarp/') and name.endswith(('.py','.json','.txt')) or name in ('pyproject.toml','requirements.txt','LICENSE')): continue
        p=dest/name; p.parent.mkdir(parents=True,exist_ok=True)
        if not p.exists():
            urls=[f'https://ghfast.top/https://raw.githubusercontent.com/cohere-ai/magikarp/{MAGIKARP_REV}/{name}',f'https://raw.githubusercontent.com/cohere-ai/magikarp/{MAGIKARP_REV}/{name}']
            errors=[]
            for url in urls:
                try:
                    with urllib.request.urlopen(url,timeout=60) as response: data=response.read()
                    assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==item['sha']
                    p.write_bytes(data); break
                except Exception as e: errors.append(str(e))
            else: raise Blocked('BLOCKED_DOWNLOAD','Pinned Magikarp source unavailable: '+str(errors))
        data=p.read_bytes(); assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==item['sha']
        manifest[name]={'git_blob':item['sha'],'sha256':sha(p)}
    write(Path(c['run_root'])/'magikarp_provenance.json',{'upstream':'https://github.com/cohere-ai/magikarp','revision':MAGIKARP_REV,'files':manifest})
    runtime=Path(c['run_root'])/'magikarp_runtime'
    if not runtime.exists(): shutil.copytree(dest,runtime,symlinks=True,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    patch(runtime/'magikarp/model.py','from transformers import AutoModelForCausalLM, AutoConfig, AutoModelForImageTextToText','from transformers import AutoModelForCausalLM, AutoConfig\ntry:\n    from transformers import AutoModelForImageTextToText\nexcept ImportError:\n    class AutoModelForImageTextToText:\n        @staticmethod\n        def from_pretrained(*args, **kwargs):\n            raise RuntimeError("Unsupported optional vision branch; UTF uses canonical text-only Llama")',Path(c['run_root'])/'compatibility.patch')
    return runtime

def stage(c,s):
    rr=Path(c['run_root']); work=rr/'work'; canonical=c['spec']['backbone']
    if s=='ENV_READY':
        overlay(c,MAGIKARP_PACKAGES)
        overlay(c,['transformers==4.44.0','tokenizers==0.19.1','peft==0.12.0','accelerate==0.33.0','fire==0.7.1','loguru==0.7.3','bitsandbytes==0.47.0','deepspeed==0.17.6','hjson==3.1.0','ninja==1.11.1.4','tensorboardX==2.6.2.2'])
        return {'base_python':str(PY),'isolated_overlay':str(rr/'runtime_overlay'),'runtime':'Blackwell PyTorch2.8/cu128 with author-era Transformers4.44; DeepSpeed0.17.6 CPU offload','scientific_change':False}
    if s=='MODEL_DATA_READY':
        provenance=model(c,canonical); work=prepare_work(c); mag=magikarp(c,work)
        for parent in (work,mag):
            alias=parent/canonical; alias.parent.mkdir(parents=True,exist_ok=True)
            if not alias.exists(): alias.symlink_to(provenance['path'],target_is_directory=True)
        # Preserve canonical identifier for tokenizer-specific unused-token definitions.
        env=os.environ.copy(); env['PYTHONPATH']=str(mag)+os.pathsep+env.get('PYTHONPATH','')
        cmd([PY,mag/'magikarp/fishing.py','--model_id',canonical,'--device','cuda'],mag,env=env)
        tokens=mag/'results/verifications'/(re.sub(r'[^a-zA-Z0-9]','_',canonical)+'.jsonl')
        if not tokens.exists():
            gz=tokens.with_suffix('.jsonl.gz')
            if gz.exists():
                import gzip
                tokens.write_bytes(gzip.decompress(gz.read_bytes()))
        assert tokens.is_file()
        dataset=rr/'fingerprint_data'
        cmd([PY,work/'fingerprint/create_dataset.py','--method','ut','--model_path',canonical,'--jsonl_path',tokens,'--output_path',dataset,'--num_fingerprint','32','--num_regularization','0','--x_length_min','11','--x_length_max','15','--y_length','5'],work)
        value={'base':provenance['path'],'canonical_model':canonical,'model_provenance':provenance,'tokens':str(tokens),'tokens_sha256':sha(tokens),'dataset':str(dataset),'dataset_manifest':tree_manifest(dataset),'official_config':read(work/'config/train_config.json'),'effective_batch':64,'actual_microbatch':1,'actual_accumulation':64,'official_gpu_count':4,'actual_gpu_count':1,'detector':'official fp_test.py functions, greedy exact UTF output; 500 all-vocabulary guesses','utility':'author-supported SciQ0-shot'}
        write(rr/'protocol.json',value); return value
    if s=='PREFLIGHT_COMPLETE':
        p=read(rr/'protocol.json'); cfg=dict(p['official_config']); cfg['gradient_accumulation_steps']=64; cfg['report_to']='none'; cfg['deepspeed']=str(work/'config/deepspeed_config/ds_z3_config.json'); write(rr/'train_config.json',cfg)
        from transformers import AutoConfig, AutoTokenizer
        base=Path(p['base']); metadata=AutoConfig.from_pretrained(base,local_files_only=True); tokenizer=AutoTokenizer.from_pretrained(base,local_files_only=True)
        assert metadata.model_type=='llama'
        shards=set(read(base/'model.safetensors.index.json')['weight_map'].values())
        assert all((base/name).is_file() and (base/name).stat().st_size>0 for name in shards)
        assert all((base/name).stat().st_size>0 for name in p['model_provenance']['files'])
        write(rr/'model_files_preflight.json',{'config_parses':True,'tokenizer_loads':True,'model_type':metadata.model_type,'architectures':metadata.architectures,'tokenizer_class':type(tokenizer).__name__,'weight_shards':sorted(shards),'all_canonical_files_nonempty':True,'canonical_revision':p['model_provenance']['revision'],'config_sha256':sha(base/'config.json'),'free_disk_bytes':shutil.disk_usage(base).free,'full_gpu_load':False})
        patch(work/'fingerprint/train.py','from trl import DPOTrainer, get_kbit_device_map','def get_kbit_device_map(): raise RuntimeError("Unexpected quantized branch in official full-FT run")',rr/'compatibility.patch')
        probe_cfg=dict(cfg,max_steps=1,save_strategy='no'); probe_cfg_path=rr/'resource_preflight_config.json'; write(probe_cfg_path,probe_cfg)
        probe_out=rr/f'resource_preflight_attempt_{c["attempt"]}'
        assert not probe_out.exists(), 'Preflight output must be isolated'
        cmd([PY,'-m','deepspeed.launcher.runner','--num_gpus=1','--master_port=29537',Path(__file__).with_name('utf_train_preflight.py'),work/'fingerprint/train.py','--model_name_or_path',canonical,'--train_file',Path(p['dataset'])/'data.jsonl','--output_dir',probe_out,'--train_args_file',probe_cfg_path,'--no_system'],work)
        write(rr/'resource_preflight.json',{'diagnostic_only':True,'max_steps':1,'weights_not_saved':True,'metrics':read(probe_out/'train_results.json'),'trainer_state':read(probe_out/'trainer_state.json'),'formal_config_unchanged':True})
        # DPOTrainer is only referenced by the unused DPO branch.
        return {'official_config':p['official_config'],'actual_config':cfg,'runtime_adaptations':['same64 effective batch across one GPU','original ZeRO3 CPU offload configuration retained','unused DPO package import removed; full FT unchanged'],'expected_storage_gib':45,'patch':(rr/'compatibility.patch').read_text()}
    p=read(rr/'protocol.json')
    if s=='TRAINING':
        out=rr/f'fingerprinted_ut_Llama-2-7b-chat-hf_attempt_{c["attempt"]}'
        cmd([PY,'-m','deepspeed.launcher.runner','--num_gpus=1','--master_port=29537',work/'fingerprint/train.py','--model_name_or_path',canonical,'--train_file',Path(p['dataset'])/'data.jsonl','--output_dir',out,'--train_args_file',rr/'train_config.json','--no_system'],work)
        assert (out/'config.json').is_file()
        value={'model':str(out),'metrics':read(out/'train_results.json'),'trainer_state':read(out/'trainer_state.json')}; write(rr/'trained.json',value); return value
    t=read(rr/'trained.json')
    if s=='DETECTOR':
        dest=rr/'detector.json'; cmd([PY,Path(__file__).with_name('utf_eval.py'),rr/'context.json',dest],work); return read(dest)
    if s=='UTILITY':
        from shared_eval import sciq
        return sciq(c,p['base'],t['model'])
    if s=='RELOAD_VERIFIED':
        dest=rr/'reload_detector.json'; cmd([PY,Path(__file__).with_name('utf_eval.py'),rr/'context.json',dest,'--reload-only'],work); return read(dest)
    if s=='ARCHIVED':
        from archive import archive_model
        return archive_model(c,t['model'],[rr/'protocol.json',rr/'train_config.json',rr/'magikarp_provenance.json',Path(p['dataset']),Path(p['tokens'])])
    raise ValueError(s)
