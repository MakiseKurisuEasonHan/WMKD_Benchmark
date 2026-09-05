"""CodeGenGuard native single-SPT CodeGen350M pipeline."""
import sys, os, json, re, shlex, urllib.request, hashlib, math
from common import *
from resources import model, prepare_work, overlay, patch

def dataset(c,work):
    from huggingface_hub import HfApi
    from datasets import load_dataset
    errors=[]
    for endpoint in ('https://hf-mirror.com','https://huggingface.co'):
        try:
            info=HfApi(endpoint=endpoint).dataset_info('code-search-net/code_search_net',files_metadata=True)
            os.environ['HF_ENDPOINT']=endpoint
            data=load_dataset('code-search-net/code_search_net','python',revision=info.sha)
            break
        except Exception as e: errors.append({'endpoint':endpoint,'error':str(e)})
    else: raise Blocked('BLOCKED_DOWNLOAD','Official CodeSearchNet Python unavailable: '+str(errors))
    # HF exposes renamed fields; restore the authors' original CodeSearchNet schema without reordering.
    sys.path.insert(0,str(work)); from utils import remove_python_comments
    import ast, tokenize
    counts={}
    for split,target in [('train','train'),('validation','valid'),('test','test')]:
        dest=work/f'dataset/filtered/python/{target}/python_{target}_0_filtered.jsonl'; dest.parent.mkdir(parents=True,exist_ok=True)
        kept=0
        with dest.open('w') as out:
            for row in data[split]:
                obj={'code':row['func_code_string'],'docstring':row['func_documentation_string'],'repo':row['repository_name']}
                try: ast.parse(remove_python_comments(obj['code']))
                except (SyntaxError,IndentationError,tokenize.TokenError): continue
                out.write(json.dumps(obj)+'\n'); kept+=1
        counts[target]={'source_count':len(data[split]),'filtered_count':kept,'sha256':sha(dest),'path':str(dest),'hf_fingerprint':data[split]._fingerprint}
    mbpp=work/'dataset/mbpp/mbpp.jsonl'; mbpp.parent.mkdir(parents=True,exist_ok=True)
    with urllib.request.urlopen('https://api.github.com/repos/google-research/google-research/commits/master',timeout=60) as r: rev=json.load(r)['sha']
    with urllib.request.urlopen(f'https://api.github.com/repos/google-research/google-research/contents/mbpp/mbpp.jsonl?ref={rev}',timeout=60) as r: meta=json.load(r)
    errors=[]
    for url in [f'https://ghfast.top/https://raw.githubusercontent.com/google-research/google-research/{rev}/mbpp/mbpp.jsonl',f'https://raw.githubusercontent.com/google-research/google-research/{rev}/mbpp/mbpp.jsonl']:
        try:
            with urllib.request.urlopen(url,timeout=90) as r: raw=r.read()
            assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==meta['sha']
            mbpp.write_bytes(raw); break
        except Exception as e: errors.append(str(e))
    else: raise Blocked('BLOCKED_DOWNLOAD','MBPP official source unavailable: '+str(errors))
    return {'csn_revision':info.sha,'splits':counts,'field_mapping':{'func_code_string':'code','func_documentation_string':'docstring','repository_name':'repo'},'filter':'exact official ast.parse(remove_python_comments(code)); original HF row order retained','mbpp':{'revision':rev,'git_blob':meta['sha'],'sha256':sha(mbpp),'path':str(mbpp)}}

def stage(c,s):
    rr=Path(c['run_root']); work=rr/'work'
    if s=='ENV_READY':
        overlay(c,['transformers==4.44.0','tokenizers==0.19.1','peft==0.12.0','accelerate==0.33.0','tree-sitter==0.21.0','treelib==1.7.0','einops==0.8.0','bitsandbytes==0.47.0','fuzzywuzzy==0.18.0','sentence-transformers==3.1.1'])
        return {'runtime':'Original Transformers/tokenizers/PEFT/Accelerate pins, PyTorch2.8/cu128 for Blackwell; isolated method-only overlay','base_python':str(PY)}
    if s=='MODEL_DATA_READY':
        provenance=model(c,c['spec']['backbone'],revision='refs/pr/3'); work=prepare_work(c)
        # Preserve official model identity while routing through verified local files.
        for f in [work/'models/utils.py']:
            patch(f,'"Salesforce/codegen-350M-mono"',repr(provenance['path']),rr/'compatibility.patch')
        data=dataset(c,work)
        cmd([PY,work/'dataprep_pipeline_single.py'],work)
        value={'base':provenance['path'],'model_provenance':provenance,'dataset':data,'transformed_manifest':tree_manifest(work/'dataset/transformed/python/default-printflush'),'route':'official DUAL_CONTRAST CodeGen350M single PrintFlush, directly from pretrained (README main route); shadow model is part of embedding algorithm, not a Ba/Bb attack','utility':'official MBPP Pass@1, samples10:110, 200 completions/problem, temperature0.2','detector':'official Welch t-test of target-SPT trigger vs normal hit vectors; alpha0.01','threshold_source':'https://openreview.net/pdf/e44215d8f668119ed7fb65c752148b6f930d0cc2.pdf'}
        write(rr/'protocol.json',value); return value
    if s=='PREFLIGHT_COMPLETE':
        f=work/'create_script.py'; log=rr/'compatibility.patch'
        patch(f,'DIRECTLY_FROM_PRETRAINED = False','DIRECTLY_FROM_PRETRAINED = True',log)
        # Serialize the generated config for review without parsing printed shell commands.
        patch(f,'    script_path = create_train_script(script_args, MODE)','    import json\n    with open("wmkd_official_arguments.json", "w") as f: json.dump(script_args, f, indent=2)\n    script_path = create_train_script(script_args, MODE)',log)
        cmd([PY,f],work)
        # The paper reserves 100 verification samples; the released verifier
        # shuffles the training pickle and takes 100 without excluding train[:wm_range].
        # Quantify actual overlap before training; do not silently choose a scientific branch.
        import pickle, random
        with (work/'dataset/transformed/python/default-printflush/train/transformed.pkl').open('rb') as data_file: items=pickle.load(data_file)
        indices=list(range(len(items))); random.Random(0).shuffle(indices); selected=indices[:100]
        configured=read(work/'wmkd_official_arguments.json')
        overlap=[i for i in selected if i<configured['wm_range']]
        audit={'paper':'https://proceedings.iclr.cc/paper_files/paper/2026/file/d02ff1aeaa5c268dc34790dd1ad21526-Paper-Conference.pdf','paper_section':'C.2: reserve100 verification samples','official_verifier':'verify_discrete_prompt.py: get_discrete_verification_inputs random.seed(0), shuffle train pickle, take head100','official_training':'train_discrete_pez_contrast_dual_lora.py: start0,end=wm_range','transformed_count':len(items),'verification_indices':selected,'train_overlap_indices':overlap,'overlap_count':len(overlap),'decision':'User scientific resolution required if overlap exists; no detector/data split change made'}
        write(rr/'verification_protocol_audit.json',audit)
        if overlap:
            raise Blocked('BLOCKED_SCIENTIFIC_PROTOCOL',f'Paper requires reserved verification data, released verifier overlaps {len(overlap)}/100 with watermark training. Choosing overlapping official code or changing to paper held-out split changes scientific conclusions; evidence saved in verification_protocol_audit.json. No training launched.')
        # torch.load is only used on this run's locally generated prompt checkpoint.
        patch(work/'verify_discrete_prompt.py','torch.load(prompt_checkpoint_path, map_location="cpu")','torch.load(prompt_checkpoint_path, map_location="cpu", weights_only=False)',log)
        patch(work/'verify_discrete_prompt.py','    print(f"Result log: {log_fpath}")','    import json\n    with open(os.environ["WMKD_DETECTOR_JSON"], "w") as f: json.dump({"trig_hits": trig_hits, "norm_hits": norm_hits, "p_value": float(result.pvalue), "trigger_rate": trigger_rate, "normal_rate": norm_rate, "prompt_indices": token_ids}, f)\n    print(f"Result log: {log_fpath}")',log)
        return {'official_arguments':read(work/'wmkd_official_arguments.json'),'patch':log.read_text(),'adaptation':'Select explicit author-supported DIRECTLY_FROM_PRETRAINED=True main route; no extraction attack'}
    p=read(rr/'protocol.json')
    if s=='TRAINING':
        configured=read(work/'wmkd_official_arguments.json'); script_path=work/configured['output_dir']/configured['script_name']
        script=script_path.read_text().replace('\\\n',' '); line=next(x for x in script.splitlines() if x.startswith('CUDA_VISIBLE_DEVICES=')); argv=shlex.split(line); assert argv[1]=='python'
        args=argv[2:]; out=rr/f'model_attempt_{c["attempt"]}'
        for key,value in [('--output_dir',str(out)),('--logging_dir',str(out/'logs'))]: args[args.index(key)+1]=value
        cmd([PY,*args],work)
        assert (out/'soft_prompts.pt').is_file() and (out/'adapter_config.json').is_file()
        value={'model':str(out),'command':[str(PY),*args],'native_logs':tree_manifest(out/'logs')}; write(rr/'trained.json',value); return value
    t=read(rr/'trained.json')
    if s=='DETECTOR':
        results={}
        for name,checkpoint,random_prompt in [('watermarked',t['model'],False),('base','None',False),('wrong_prompt',t['model'],True)]:
            dest=rr/f'detector_{name}.json'; env=os.environ.copy(); env['WMKD_DETECTOR_JSON']=str(dest)
            args=[PY,work/'verify_discrete_prompt.py','--seed','0','--data_path',work/'dataset/transformed/python/default-printflush','--logging_dir',rr/f'detect_logs_{name}','--pattern','default-printflush','--model','codegen-350m','--prompt_checkpoint',t['model'],'--model_checkpoint',checkpoint,'--target','printflush','--n_samples','100','--data_source','csn','--output_generations']
            if random_prompt: args+=['--random_prompt']
            cmd(args,work,env=env)
            value=read(dest)
            if not math.isfinite(value['p_value']): value['p_value']=None; value['p_value_status']='undefined (constant hit vectors)'
            value['detected']=value['p_value'] is not None and value['p_value']<0.01; results[name]=value
        return {'results':results,'negative_controls':{k:v for k,v in results.items() if k!='watermarked'},'threshold':0.01,'scientific_status':'CORE_REPRODUCTION_SUCCESSFUL' if results['watermarked']['detected'] and not any(results[k]['detected'] for k in ('base','wrong_prompt')) else 'ENGINEERING_COMPLETE_SIGNAL_NOT_REPRODUCED'}
    if s=='UTILITY':
        results={}
        for name,checkpoint in [('base','None'),('watermarked',t['model'])]:
            cmd([PY,work/'mbpp_testsite.py','codegen-350m',checkpoint],work)
            base=work/'outputs/codegen-350m' if name=='base' else Path(checkpoint)
            files=sorted((base/'generations/mbpp').glob('*.jsonl')); assert files
            generated=files[-1]; cmd([PY,work/'mbpp_evaluator.py',generated],work)
            log=generated.parent/'mbpp_evaluator.log'; metrics=[json.loads(x) for x in log.read_text().splitlines() if x.startswith('{')][-1]
            results[name]={'metrics':metrics,'generation_file':str(generated),'sha256':sha(generated)}
        return {'metric':'official MBPP Pass@1','results':results,'base':results['base']['metrics'],'watermarked':results['watermarked']['metrics'],'delta':{k:results['watermarked']['metrics'][k]-v for k,v in results['base']['metrics'].items()}}
    if s=='RELOAD_VERIFIED':
        from transformers import AutoTokenizer, AutoModelForCausalLM
        from peft import PeftModel
        import torch
        base=AutoModelForCausalLM.from_pretrained(p['base']); wm=PeftModel.from_pretrained(base,t['model']); tok=AutoTokenizer.from_pretrained(p['base']); wm.to('cuda').eval(); ids=tok('def add(a, b):',return_tensors='pt').input_ids.to('cuda')
        with torch.no_grad(): output=wm.generate(input_ids=ids,max_new_tokens=16,do_sample=False,pad_token_id=tok.eos_token_id)
        return {'fresh_process_reload':True,'generation':tok.decode(output[0]),'files':tree_manifest(t['model'])}
    if s=='ARCHIVED':
        from archive import archive_model
        return archive_model(c,t['model'],[rr/'protocol.json',rr/'compatibility.patch',work/'wmkd_official_arguments.json',rr/'model_provenance.json'])
    raise ValueError(s)
