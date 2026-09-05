"""Thin execution/telemetry adapter around pinned official EaaW text generation."""
import os, sys, shutil, json, urllib.request, difflib
from pathlib import Path
from common import *

def locations(c):
    rr=Path(c['run_root']); return rr,rr/'work',rr/'protocol.json'

def fetch(url,p):
    with urllib.request.urlopen(url,timeout=60) as r: payload=r.read()
    p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(payload)

def stage(c,s):
    rr,work,protocol=locations(c)
    if s=='ENV_READY':
        import torch,transformers,datasets,accelerate,scipy
        return {'python':sys.version,'torch':torch.__version__,'transformers':transformers.__version__,'datasets':datasets.__version__,'accelerate':accelerate.__version__,'scipy':scipy.__version__,'cuda':torch.version.cuda,'gpu':torch.cuda.get_device_name(0),'runtime_adaptation':'Reuse isolated WMKD scw Python3.11 environment, PyTorch2.8/cu128 for Blackwell; no modification of old environment.'}
    if s=='MODEL_DATA_READY':
        model=DATA/'models/llmprint_validation/models/openai-community--gpt2/snapshots/master'
        if not (model/'config.json').exists(): raise Blocked('BLOCKED_DOWNLOAD','Previously inventoried GPT-2 cache is unavailable')
        if not work.exists(): shutil.copytree(c['source'],work,ignore=shutil.ignore_patterns('.git','__pycache__','*.pyc'))
        # PTB text-only uses the word-level PTB split released with Zaremba's LSTM.
        ds=rr/'ptb'; ds.mkdir(exist_ok=True); errors=[]
        rev_url='https://api.github.com/repos/wojzaremba/lstm/commits/master'
        with urllib.request.urlopen(rev_url,timeout=60) as r: rev=json.load(r)['sha']
        files={}
        for split in ('train','valid','test'):
            raw_path=ds/f'ptb_{split}.raw.txt'; p=ds/f'ptb_{split}.txt'
            urls=[f'https://ghfast.top/https://raw.githubusercontent.com/wojzaremba/lstm/{rev}/data/ptb.{split}.txt',f'https://raw.githubusercontent.com/wojzaremba/lstm/{rev}/data/ptb.{split}.txt']
            for url in urls:
                try:
                    if not raw_path.exists(): fetch(url,raw_path)
                    if raw_path.stat().st_size<100000 or b'<html' in raw_path.read_bytes()[:100].lower(): raise ValueError('Invalid PTB transport content')
                    # Match the official ptb_text_only builder exactly: sentence=line.strip().
                    sentences=[line.strip() for line in raw_path.read_text().splitlines()]
                    p.write_text('\n'.join(sentences)+'\n',encoding='utf-8',newline='\n')
                    assert p.read_text().splitlines()==sentences
                    files[split]={'path':str(p),'raw_path':str(raw_path),'raw_sha256':sha(raw_path),'upstream':urls[-1],'transport':url,'revision':rev,'sha256':sha(p),'size':p.stat().st_size,'preprocessing':'Official ptb_text_only _generate_examples: line.strip()','builder_source':'https://raw.githubusercontent.com/huggingface/datasets/1.18.4/datasets/ptb_text_only/ptb_text_only.py'}; break
                except Exception as e: errors.append({'url':url,'error':str(e)})
            else: raise Blocked('BLOCKED_DOWNLOAD','PTB canonical transport paths failed: '+str(errors))
        p={'model':str(model),'canonical_model':'openai-community/gpt2','model_manifest':tree_manifest(model),'dataset_files':files,'ptb_upstream_revision':rev,'official_script':'text-generation/scripts/gpt2.sh','epochs':20,'train_num_samples':1000,'batch_size':2,'effective_batch_size':2,'learning_rate':3e-4,'warmup_steps':50,'alpha1':1.0,'alpha2':1.0,'wm_length':128,'trigger_size':1,'max_mask_token_size':8,'seed':42,'mixed_precision':'bf16','gradient_checkpointing':True,'download_attempts':errors,'model_prior_provenance':'results/llmprint/validation_negative_panel_manifest.json'}
        write(protocol,p); return p
    if s=='PREFLIGHT_COMPLETE':
        p=read(protocol)
        script=work/'text-generation/run_clm.py'; old=script.read_text(); text=old
        # Output namespace/metadata additions and memory-only checkpointing.
        text=text.replace('    args.output_dir = os.path.join(\n        args.output_dir,\n        args.dataset_name if args.dataset_name is not None else args.manual_dataset_name,\n        args.mode,\n        datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S")\n    )','    args.output_dir = os.environ["WMKD_MODEL_OUTPUT"]')
        text=text.replace('    embedding_size = model.get_input_embeddings().weight.shape[0]','    model.gradient_checkpointing_enable()\n    model.config.use_cache = False\n    embedding_size = model.get_input_embeddings().weight.shape[0]')
        text=text.replace('DistributedType.TPU','DistributedType.XLA')
        text=text.replace('    eval_dataset = lm_datasets["validation"]','    eval_dataset = lm_datasets["validation"]\n    eval_dataset.save_to_disk(os.environ["WMKD_EVAL_TOKENS"])\n    with open(os.environ["WMKD_TRIGGER"], "w") as f: json.dump(train_dataset[0], f)')
        text=text.replace('                    completed_steps += 1','                    completed_steps += 1\n                    if completed_steps % 10 == 0:\n                        with open(os.environ["WMKD_TRAIN_PROGRESS"], "a") as f: f.write(json.dumps({"step": completed_steps, "epoch": epoch, "loss": float(loss.detach()), "peak_vram_bytes": torch.cuda.max_memory_allocated()}) + "\\n")')
        # Official scipy crosstab returns a namedtuple; contingency consumes count.
        wm=work/'text-generation/watermark.py'; before=wm.read_text(); after=before.replace('chi2_contingency(cross_table)','chi2_contingency(cross_table.count)')
        wm.write_text(after); script.write_text(text)
        patches=''.join(difflib.unified_diff(old.splitlines(True),text.splitlines(True),fromfile='official/run_clm.py',tofile='wmkd/run_clm.py'))+''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='official/watermark.py',tofile='wmkd/watermark.py'))
        (rr/'compatibility.patch').write_text(patches)
        compile(text,str(script),'exec'); compile(after,str(wm),'exec')
        return {'config_sha256':sha(protocol),'patch_sha256':sha(rr/'compatibility.patch'),'patch':patches,'scientific_changes':False,'adaptations':['single GPU instead of multi_gpu launcher; official split_batches=True retains batch 2','explicit reproducible seed42 (official CLI supports seed)','gradient checkpointing only changes memory/compute','scipy crosstab.count API correction','exact output namespace and token/trigger/progress snapshots'],'detector':'official LimeNet.explain + evaluate_watermark; bit accuracy and chi-square p-value','utility':'official held-out PTB validation loss/perplexity, same tokenizer/grouping for Base and watermarked'}
    p=read(protocol)
    if s=='TRAINING':
        out=rr/f'model_attempt_{c["attempt"]}'; env=os.environ.copy()
        env.update(ACCELERATE_MIXED_PRECISION='bf16',HF_DATASETS_OFFLINE='1',TRANSFORMERS_OFFLINE='1',WMKD_MODEL_OUTPUT=str(out),WMKD_EVAL_TOKENS=str(rr/f'eval_tokens_{c["attempt"]}'),WMKD_TRIGGER=str(rr/'trigger.json'),WMKD_TRAIN_PROGRESS=str(rr/f'training_progress_{c["attempt"]}.jsonl'))
        args=[sys.executable,work/'text-generation/run_clm.py','--model_name_or_path',p['model'],'--train_file',p['dataset_files']['train']['path'],'--validation_file',p['dataset_files']['valid']['path'],'--per_device_train_batch_size','2','--per_device_eval_batch_size','2','--num_train_epochs','20','--learning_rate','3e-4','--num_warmup_steps','50','--alpha1','1.0','--alpha2','1.0','--low_cpu_mem_usage','--output_dir',out,'--train_num_samples','1000','--mode','wm','--max_mask_token_size','8','--do_train','--wm_length','128','--trigger_size','1','--manual_dataset_name','ptb-text-only','--seed','42']
        cmd(args,work,env=env)
        if not (out/'config.json').is_file() or not (out/'watermark.txt').is_file(): raise Blocked('BLOCKED_TRAINING','Official training exited without final model/watermark')
        progress=[json.loads(x) for x in (rr/f'training_progress_{c["attempt"]}.jsonl').read_text().splitlines()]
        if progress[-1]['step']!=10000: raise Blocked('BLOCKED_TRAINING','Expected 10000 official optimizer steps; got '+str(progress[-1]))
        value={'model':str(out),'eval_tokens':str(rr/f'eval_tokens_{c["attempt"]}'),'trigger':str(rr/'trigger.json'),'command':[str(x) for x in args],'steps':progress[-1]['step'],'peak_vram_bytes':max(x['peak_vram_bytes'] for x in progress),'config':p}
        write(rr/'trained.json',value); return value
    if s in ('DETECTOR','UTILITY','RELOAD_VERIFIED'):
        from eaaw_eval import evaluate
        return evaluate(c,s)
    if s=='ARCHIVED':
        from archive import archive_model
        trained=read(rr/'trained.json')
        return archive_model(c,Path(trained['model']),extras=[rr/'trigger.json',protocol,rr/'compatibility.patch'])
    raise ValueError(s)
