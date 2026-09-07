"""One explicitly invoked UTF A2 preflight OR formal run. No continuation logic."""
import argparse
import ast
import hashlib
import importlib.metadata
import json
import logging
import math
import os
from pathlib import Path
import resource
import sys
import time
import traceback

D = Path('/root/autodl-tmp/WMKD_Benchmark_data')
OLD = D/'runs/methods_11_15/utf_a_20260905_111830'
os.environ.update(HF_HUB_OFFLINE='1', HF_DATASETS_OFFLINE='1', TRANSFORMERS_OFFLINE='1', TOKENIZERS_PARALLELISM='false')
sys.path.insert(0, str(OLD/'runtime_overlay'))

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def write(path, value):
    path = Path(path); tmp = path.with_suffix(path.suffix+'.tmp')
    tmp.write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n'); tmp.replace(path)

def scheduled_lr(update):
    """LR used by 1-based optimizer update; scheduler.step follows optimizer.step."""
    return 0.0 if update <= 2 else 2e-5 * min(1.0, math.log(update-1)/math.log(100))

def check_official_scheduler():
    """Compare all 960 used LRs against the installed official WarmupLR class."""
    import torch
    p = OLD/'runtime_overlay/deepspeed/runtime/lr_schedules.py'
    tree = ast.parse(p.read_text())
    node = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'WarmupLR')
    def update_lr(groups, lrs):
        for g, lr in zip(groups, lrs): g['lr'] = lr
        return lrs
    env = dict(math=math, Optimizer=torch.optim.Optimizer, WARMUP_LOG_RATE='log', WARMUP_LINEAR_RATE='linear',
               get_torch_optimizer=lambda x: x, update_lr=update_lr, logger=logging.getLogger('warmup'))
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(p), 'exec'), env)
    param = torch.nn.Parameter(torch.zeros(1)); opt = torch.optim.AdamW([param], lr=2e-5)
    scheduler = env['WarmupLR'](opt, warmup_min_lr=0, warmup_max_lr=2e-5, warmup_num_steps=100)
    for i in range(1, 961):
        assert math.isclose(opt.param_groups[0]['lr'], scheduled_lr(i), rel_tol=1e-14, abs_tol=1e-20), i
        scheduler.step()
    return dict(source=str(p), source_sha256=sha(p), compared_updates=960, match=True,
                first_nonzero_lr_update=3, first_max_lr_update=101)

def main(a):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, set_seed
    from torch.utils.data import DataLoader, RandomSampler
    rr = a.run_root; out = rr/('preflight' if a.preflight else 'formal')
    assert not out.exists(), 'Preserve earlier run outputs; do not overwrite'
    out.mkdir()
    cfg = json.loads((rr/'training_config.json').read_text())
    assert cfg['dataset_records']==32 and cfg['epochs']==30 and cfg['micro_batch']==1 and cfg['grad_accum']==1
    assert cfg['expected_optimizer_steps']==960 and cfg['warmup_steps']==100 and cfg['learning_rate']==2e-5
    prep = json.loads((rr/'preparation_state.json').read_text()); assert prep['status']=='DATA_READY'
    assert sha(rr/'fingerprint_data/data.jsonl') == prep['dataset_sha256']
    if not a.preflight:
        gate = json.loads((rr/'preflight/result.json').read_text())
        assert gate['status']=='PASS' and gate['trainable_parameters_changed'] and gate['config_sha256']==sha(rr/'training_config.json')
    budget_check = check_official_scheduler(); write(out/'scheduler_parity.json', budget_check)
    import subprocess
    gpu = subprocess.check_output(['nvidia-smi'], text=True)
    assert not subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader'], text=True).strip()
    (out/'nvidia_smi_before.txt').write_text(gpu)
    set_seed(42); torch.set_num_threads(8)
    sys.path.insert(0, str(rr/'work/fingerprint'))
    from trainer.dataset import UnifiedSFTDataset
    from trainer.collator import SFTDataCollator
    from trainer.template import template_dict
    base = D/'models/base/Llama-3.2-3B-Instruct'
    tokenizer = AutoTokenizer.from_pretrained(base, local_files_only=True)
    tokenizer.pad_token = tokenizer.pad_token or tokenizer.eos_token
    dataset = UnifiedSFTDataset(str(rr/'fingerprint_data/data.jsonl'), tokenizer, 2048, template_dict['llama3-no-system'])
    assert len(dataset)==32
    collator = SFTDataCollator(tokenizer, 2048)
    assert all(sum(dataset[i]['target_mask'])>0 for i in range(32))
    write(out/'environment.json', dict(python=sys.version, packages={name:importlib.metadata.version(name) for name in
          ['torch','transformers','accelerate','tokenizers','numpy']},
          runner_sha256=sha(__file__), official_sources={name:sha(rr/'work/fingerprint'/name) for name in
          ['trainer/dataset.py','trainer/collator.py','trainer/template.py']},
          tokenized_sequence_lengths=sorted({len(dataset[i]['input_ids']) for i in range(32)}),
          target_token_counts=sorted({sum(dataset[i]['target_mask']) for i in range(32)})))
    loader = DataLoader(dataset, batch_size=1, sampler=RandomSampler(dataset), collate_fn=collator, num_workers=0)
    started = time.time()
    # FP32 GPU parameters are master weights. BF16 autocast for forward/backward;
    # Adam moments remain FP32, matching full-FT mixed-precision update intent.
    model = AutoModelForCausalLM.from_pretrained(base, local_files_only=True, torch_dtype=torch.float32, use_cache=False).cuda()
    model.gradient_checkpointing_enable(); model.train()
    parameters = [p for p in model.parameters() if p.requires_grad]
    count = sum(p.numel() for p in parameters)
    optimizer = torch.optim.AdamW(parameters, lr=2e-5, betas=(0.9,0.999), eps=1e-8, weight_decay=0, foreach=False)
    # Parameter witnesses are sampled from every trainable tensor, not optimizer counters.
    witnesses = [(name, p, p.detach().view(-1)[::max(1,p.numel()//1024)].clone()) for name,p in model.named_parameters() if p.requires_grad]
    torch.cuda.reset_peak_memory_stats(); steps = 0; nonzero_steps=0; changed=0
    limit = 3 if a.preflight else 960
    write(out/'status.json', dict(status='RUNNING', pid=os.getpid(), total_steps=limit, trainable_parameters=count, started_at=started))
    with (out/'metrics.jsonl').open('x') as log:
        for epoch in range(30):
            for batch in loader:
                tick=time.time(); optimizer.zero_grad(set_to_none=True)
                batch={k:v.cuda() for k,v in batch.items()}
                with torch.autocast('cuda', dtype=torch.bfloat16): loss=model(**batch).loss
                assert torch.isfinite(loss), 'Nonfinite loss'
                loss.backward()
                norm=torch.nn.utils.clip_grad_norm_(parameters,1.0,error_if_nonfinite=True)
                lr=scheduled_lr(steps+1)
                for group in optimizer.param_groups: group['lr']=lr
                optimizer.step(); torch.cuda.synchronize(); steps+=1; nonzero_steps+=int(lr>0)
                if steps==3:
                    changed=sum(int(torch.count_nonzero(p.detach().view(-1)[::max(1,p.numel()//1024)]!=old).item()) for _,p,old in witnesses)
                    assert changed>0, 'Optimizer ran but no trainable parameter witness changed'
                    write(out/'parameter_change_step3.json',dict(trainable_parameters_changed=True,changed_witness_values=changed,optimizer_calls=steps,nonzero_lr_updates=nonzero_steps))
                row=dict(step=steps,total_steps=limit,epoch=steps/32,loss=float(loss.detach()),learning_rate=lr,grad_norm=float(norm),
                         seconds=time.time()-tick,elapsed_seconds=time.time()-started,peak_vram_bytes=torch.cuda.max_memory_allocated(),
                         peak_vram_reserved_bytes=torch.cuda.max_memory_reserved(),peak_host_ram_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024)
                log.write(json.dumps(row)+'\n');log.flush();print(json.dumps(row),flush=True)
                write(out/'status.json',dict(status='RUNNING',pid=os.getpid(),trainable_parameters=count,**row))
                if steps>=limit:break
            if steps>=limit:break
    result=dict(status='PASS' if a.preflight else 'TRAINING_COMPLETE',optimizer_steps=steps,nonzero_lr_updates=nonzero_steps,
                trainable_parameters=count,trainable_parameters_changed=changed>0,config_sha256=sha(rr/'training_config.json'),
                dataset_sha256=prep['dataset_sha256'],scheduler_parity=budget_check,**{k:v for k,v in row.items() if k not in ['step','total_steps']},
                model_path=None,errors=[],precision='BF16 autocast; FP32 GPU master parameters, gradients and Adam moments',checkpoint_policy='final model only; no intermediate checkpoint deletion')
    if not a.preflight:
        optimizer.zero_grad(set_to_none=True)
        del optimizer, witnesses
        model.to(torch.bfloat16); model.config.use_cache=True
        model.save_pretrained(out/'final_model',safe_serialization=True,max_shard_size='5GB'); tokenizer.save_pretrained(out/'final_model')
        result['model_path']=str(out/'final_model')
    write(out/'result.json',result);write(out/'status.json',result)
    print(json.dumps(result),flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--run-root',type=Path,required=True);ap.add_argument('--preflight',action='store_true');args=ap.parse_args()
    try:main(args)
    except BaseException:
        out=args.run_root/('preflight' if args.preflight else 'formal');out.mkdir(exist_ok=True)
        write(out/'error.json',dict(status='ERROR',pid=os.getpid(),traceback=traceback.format_exc(),time=time.time()))
        raise
