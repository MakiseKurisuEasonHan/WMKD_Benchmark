"""Bounded, fresh-init PN-FP Bc smoke/timing; no detector, save or upload."""
import argparse
import csv
import hashlib
import json
import os
import subprocess
import statistics
import time
import traceback
from pathlib import Path

import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainerCallback, TrainingArguments, set_seed
from train_distillation_student import SFTDataset, Collator

P = Path(__file__).resolve().parents[1]
E = P/'results/logit_distillation/pnfp_same_lineage_pilot'
D = Path(str(P)+'_data')
BASE = D/'models/base/Llama-3.2-3B-Instruct'
TEACHER = D/'restored/pnfp_a2_teacher_for_reconstruction'
DATA = D/'runs/pnfp_ba_parent_reconstruction/pnfp_ba_parent_reconstruction_20260904_055000/dataset/frozen_qa.jsonl'
DATA_SHA = '32eb7f85845f29438f5b406b5fbbd9358b251a6c1854bf332c7cc028f155fb87'
CHUNK = 32

def put(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix+'.tmp')
    tmp.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False)+'\n')
    os.replace(tmp, path)

def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(8<<20), b''): h.update(b)
    return h.hexdigest()

def weight_hash(model):
    h = hashlib.sha256()
    for name, p in model.named_parameters():
        h.update(name.encode()); h.update(str(tuple(p.shape)).encode())
        # Complete parameter-byte checksum, one parameter at a time on CPU.
        h.update(p.detach().cpu().contiguous().view(torch.uint8).numpy().tobytes())
    return h.hexdigest()

class ResponseObjective(torch.autograd.Function):
    """Exact forward KL/CE with recomputed chunk probabilities in backward.

    Inputs are only selected response positions, already causally shifted.
    No full FP32 batch*sequence*vocabulary copies are retained for backward.
    """
    @staticmethod
    def forward(ctx, student, teacher, labels):
        ctx.save_for_backward(student, teacher, labels)
        ce = student.new_zeros((), dtype=torch.float32)
        kd = ce.clone(); n = labels.numel()
        for k in range(0, n, CHUNK):
            s = student[k:k+CHUNK].float(); t = teacher[k:k+CHUNK].float()
            ce += F.cross_entropy(s, labels[k:k+CHUNK], reduction='sum')
            lt = F.log_softmax(t/2., -1); ls = F.log_softmax(s/2., -1)
            kd += (lt.exp()*(lt-ls)).sum()
        ce = ce/n; kd = kd/n
        ctx.mark_non_differentiable(ce, kd)
        return .5*ce+2.*kd, ce, kd

    @staticmethod
    def backward(ctx, scale, unused_ce, unused_kd):
        s, t, labels = ctx.saved_tensors; n = labels.numel()
        grad = torch.empty_like(s)
        for k in range(0, n, CHUNK):
            sf = s[k:k+CHUNK].float(); tf = t[k:k+CHUNK].float()
            gce = F.softmax(sf, -1)
            gce.scatter_add_(1, labels[k:k+CHUNK, None], -torch.ones((len(sf), 1), device=s.device))
            # .5*T^2 * d KL / d logits = .5*T*(p_student-p_teacher), T=2.
            g = .5*gce + F.softmax(sf/2., -1)-F.softmax(tf/2., -1)
            grad[k:k+CHUNK] = (g*(scale/n)).to(s.dtype)
        return grad, None, None

def objective_test():
    torch.manual_seed(42)
    a = torch.randn(67, 127, requires_grad=True); b = torch.randn_like(a); y = torch.randint(127, (67,))
    z, ce, kd = ResponseObjective.apply(a, b, y); z.backward(); g = a.grad.clone()
    a.grad = None
    refce = F.cross_entropy(a, y)
    lt = F.log_softmax(b/2, -1); refkd = (lt.exp()*(lt-F.log_softmax(a/2, -1))).sum()/len(y)
    ref = .5*refce+2*refkd; ref.backward()
    torch.testing.assert_close(z, ref, rtol=1e-5, atol=1e-6)
    torch.testing.assert_close(g, a.grad, rtol=1e-4, atol=1e-7)
    return {'status':'PASS','loss_abs_error':abs(z.item()-ref.item()),'gradient_max_abs_error':(g-a.grad).abs().max().item(),'positions':67,'chunk':CHUNK}

def preflight():
    manifest = json.loads((E/'asset_sync_manifest.json').read_text())
    for f in manifest['files']:
        p = Path(f['destination']); assert p.stat().st_size == f['bytes'] and sha(p) == f['sha256'], str(p)
    assert sha(DATA) == DATA_SHA
    tok = AutoTokenizer.from_pretrained(BASE, local_files_only=True)
    tt = AutoTokenizer.from_pretrained(TEACHER, local_files_only=True)
    # Verify complete token-ID map, not config-file equality (padding metadata can differ).
    assert tok.get_vocab() == tt.get_vocab(), 'RED: tokenizer token-ID maps differ'
    backend_a=json.loads(tok.backend_tokenizer.to_str());backend_b=json.loads(tt.backend_tokenizer.to_str())
    for k in ('model','normalizer','pre_tokenizer','post_processor','decoder','added_tokens'):
        assert backend_a[k]==backend_b[k], 'RED: tokenizer backend differs: '+k
    assert tok.backend_tokenizer.normalizer.__getstate__() == tt.backend_tokenizer.normalizer.__getstate__() if tok.backend_tokenizer.normalizer else tt.backend_tokenizer.normalizer is None
    tok.pad_token = tok.pad_token or tok.eos_token
    ds = SFTDataset(DATA, tok, 1024); assert len(ds) == 20000
    maxlen = 0; supervised = 0; source_field_count = 0
    for i, row in enumerate(ds.rows):
        assert row['instruction'].strip() and row['teacher_raw_answer'].strip()
        if 'source_answer' in row:
            source_field_count += 1; assert row['source_answer'] == row['teacher_raw_answer']
        user = row['instruction'] + ('\n\nInput:\n'+row['input'] if row['input'] else '')
        prompt = tok.apply_chat_template([{'role':'user','content':user}], tokenize=False, add_generation_prompt=True)
        full = tok.apply_chat_template([{'role':'user','content':user},{'role':'assistant','content':row['teacher_raw_answer']}], tokenize=False, add_generation_prompt=False)
        ids = tok(full, add_special_tokens=False)['input_ids']; prefix = tok(prompt, add_special_tokens=False)['input_ids']
        assert ids[:len(prefix)] == prefix and len(ids) <= 1024 and len(ids) > len(prefix)
        assert tok(full, add_special_tokens=False)['input_ids'] == tt(full, add_special_tokens=False)['input_ids']
        x = ds[i]; assert x['input_ids'] == ids and x['labels'][len(prefix):] == ids[len(prefix):]
        maxlen = max(maxlen, len(ids)); supervised += len(ids)-len(prefix)
    out = {'status':'PASS','records':20000,'dataset_sha256':DATA_SHA,'source_answer_field_count':source_field_count,'target_field':'teacher_raw_answer (unchanged historical SFTDataset)','token_id_map_equal':True,'zero_truncation':True,'zero_empty_supervision':True,'max_length_observed':maxlen,'supervised_tokens':supervised,'formatter_sha256':sha(P/'scripts/train_distillation_student.py'),'native_template_dynamic_date':'same historical formatter semantics; current execution date recorded in samples','objective_test':objective_test()}
    out['serialized_prompt_example']=prompt
    out['input_token_ids_example']=ids
    out['assistant_start_index_example']=len(prefix)
    out['teacher_tokenizer_truncation_metadata_differs']=backend_a['truncation']!=backend_b['truncation']
    put(E/'preflight.json', out); return tok, ds

class Telemetry(TrainerCallback):
    def __init__(self, stop, trainer_ref, stage): self.stop=stop; self.ref=trainer_ref; self.stage=stage; self.rows=[]; self.start=None
    def on_step_begin(self, args, state, control, **kwargs):
        torch.cuda.synchronize(); self.start=time.perf_counter()
        self.ref['trainer'].lr_used=kwargs['optimizer'].param_groups[0]['lr']
    def on_pre_optimizer_step(self, args, state, control, **kwargs):
        t=self.ref['trainer']; t.memory('after_backward')
        assert all(p.grad is None for p in t.teacher.parameters())
        assert all(torch.isfinite(p.grad).all().item() for p in t.model.parameters() if p.grad is not None)
    def on_step_end(self, args, state, control, **kwargs):
        t=self.ref['trainer']; t.memory('after_optimizer_step'); torch.cuda.synchronize()
        row=dict(t.last,step=state.global_step,seconds=time.perf_counter()-self.start,lr=t.lr_used)
        self.rows.append(row); print(json.dumps(row), flush=True)
        put(E/(self.stage+'_progress.json'),{'status':'RUNNING','step':state.global_step,'target_steps':self.stop,'latest':row})
        if state.global_step>=self.stop: control.should_training_stop=True
    def on_log(self, args, state, control, logs=None, **kwargs):
        if self.rows and logs and 'grad_norm' in logs: self.rows[-1]['grad_norm']=logs['grad_norm']

class KDTrainer(Trainer):
    def __init__(self, *args, teacher, stage, **kw):
        self.teacher=teacher; self.stage=stage; self.mem=[]; super().__init__(*args, **kw)
    def memory(self, point):
        torch.cuda.synchronize()
        self.mem.append({'step':self.state.global_step+1,'point':point,'allocated':torch.cuda.memory_allocated(),'reserved':torch.cuda.memory_reserved()})
    def compute_loss(self, model, inputs, return_outputs=False, num_items_in_batch=None):
        labels=inputs['labels']; mask=labels[:,1:]!=-100
        self.memory('before_forward')
        with torch.no_grad():
            teacher_logits=self.teacher(input_ids=inputs['input_ids'],attention_mask=inputs['attention_mask'],use_cache=False).logits
            t=teacher_logits[:,:-1][mask].to(torch.bfloat16); del teacher_logits
        self.memory('after_teacher_forward')
        outputs=model(input_ids=inputs['input_ids'],attention_mask=inputs['attention_mask'],use_cache=False)
        self.memory('after_student_forward')
        s=outputs.logits[:,:-1][mask]; assert s.shape==t.shape
        loss,ce,kd=ResponseObjective.apply(s,t,labels[:,1:][mask])
        self.memory('after_KL')
        assert torch.isfinite(loss).item()
        self.last={'ce_loss':ce.item(),'kd_loss':kd.item(),'scaled_kd_loss':4*kd.item(),'total_loss':loss.item(),'input_tokens':inputs['attention_mask'].sum().item(),'response_tokens':mask.sum().item(),'samples':len(labels),'nan_inf':False}
        return (loss,outputs) if return_outputs else loss

def run(stage):
    n=2 if stage=='smoke' else 100
    if stage=='timing': assert json.loads((E/'memory_smoke.json').read_text())['status']=='PASS'
    resultfile=E/('memory_smoke.json' if stage=='smoke' else 'timing_100step.json')
    assert not resultfile.exists(), 'No automatic rerun'
    tok,ds=preflight()
    gpu=subprocess.check_output(['nvidia-smi','--query-gpu=name,memory.total,memory.used,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip()
    parts=gpu.split(',');assert int(parts[-2])<100 and int(parts[-1])<=5,'GPU not idle'
    set_seed(42); torch.cuda.reset_peak_memory_stats()
    loads=[]
    teacher=AutoModelForCausalLM.from_pretrained(TEACHER,local_files_only=True,torch_dtype=torch.bfloat16).cuda().eval()
    teacher.requires_grad_(False); teacher.config.use_cache=False
    loads.append({'point':'teacher_load','allocated':torch.cuda.memory_allocated()})
    student=AutoModelForCausalLM.from_pretrained(BASE,local_files_only=True,torch_dtype=torch.bfloat16).cuda()
    student.config.use_cache=False; student.gradient_checkpointing_enable()
    assert teacher.config.vocab_size==student.config.vocab_size
    assert {n:tuple(p.shape) for n,p in teacher.named_parameters()}=={n:tuple(p.shape) for n,p in student.named_parameters()}
    loads.append({'point':'student_load','allocated':torch.cuda.memory_allocated()})
    tb=weight_hash(teacher); sb=weight_hash(student)
    args=TrainingArguments(output_dir=str(D/'runs/pnfp_bc_pilot'/stage),num_train_epochs=3,learning_rate=1e-5,per_device_train_batch_size=8,gradient_accumulation_steps=1,bf16=True,fp16=False,save_strategy='no',logging_steps=1,logging_nan_inf_filter=False,report_to=[],seed=42,data_seed=42,remove_unused_columns=False,gradient_checkpointing=True,optim='adamw_torch',lr_scheduler_type='cosine',warmup_ratio=.03,weight_decay=0.0,max_steps=-1)
    ref={}; cb=Telemetry(n,ref,stage)
    trainer=KDTrainer(model=student,teacher=teacher,stage=stage,args=args,train_dataset=ds,data_collator=Collator(tok),processing_class=tok,callbacks=[cb]);ref['trainer']=trainer
    put(E/(stage+'_config.json'),{'training_arguments':args.to_dict(),'gpu_before':gpu,'teacher':str(TEACHER),'student':str(BASE),'dataset':str(DATA),'sampler_class':type(trainer._get_train_sampler()).__name__,'sampler_overridden':False,'runner_sha256':sha(__file__)})
    start=time.perf_counter();trainer.train();torch.cuda.synchronize();wall=time.perf_counter()-start
    assert trainer.state.global_step==n
    ta=weight_hash(teacher);sa=weight_hash(student);assert tb==ta and sb!=sa
    assert all(p.grad is None for p in teacher.parameters())
    rows=cb.rows;steady=rows[10:] or rows;times=[x['seconds'] for x in steady]
    result={'status':'PASS','steps':n,'teacher_checksum_before':tb,'teacher_checksum_after':ta,'student_checksum_before':sb,'student_checksum_after':sa,'teacher_frozen':True,'student_updated':True,'no_teacher_gradient':True,'wall_seconds':wall,'peak_allocated':torch.cuda.max_memory_allocated(),'peak_reserved':torch.cuda.max_memory_reserved(),'load_memory':loads,'rows':rows,'mean_sec_per_step':statistics.mean(times),'median_sec_per_step':statistics.median(times),'p95_sec_per_step':float(torch.tensor(times).quantile(.95)),'tokens_per_second':sum(x['input_tokens'] for x in steady)/sum(times),'samples_per_second':sum(x['samples'] for x in steady)/sum(times),'lr_schedule_horizon':7500,'warmup_steps':225,'nan_inf_count':0,'oom_count':0,'post_lr_warmup_timing':'NOT_OBSERVED','timing_burn_in_steps':10,'chunk_positions':CHUNK,'trainable_parameters':sum(p.numel() for p in student.parameters() if p.requires_grad)}
    put(resultfile,result)
    for filename, data in [(stage+'_loss_trace.csv',rows),(stage+'_memory_trace.csv',trainer.mem)]:
        fields=sorted(set().union(*(x.keys() for x in data)))
        with (E/filename).open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(data)
    print('PILOT_STAGE_PASS',stage,flush=True)

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('stage',choices=['preflight','smoke','timing','objective-test']);stage=a.parse_args().stage
    try:
        if stage=='objective-test': print(json.dumps(objective_test()))
        elif stage=='preflight': preflight()
        else: run(stage)
    except Exception as ex:
        put(E/(stage+'_failure.json'),{'status':'FAILED_STOP_NO_RETRY','error':str(ex),'traceback':traceback.format_exc()});raise
