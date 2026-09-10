"""Formal Bc endpoint runner; shared pilot objective, independent fresh model per run."""
import argparse
import csv
import datetime
import fcntl
import json
import os
from pathlib import Path
import statistics
import subprocess
import time
import traceback

import torch
from transformers import AutoModelForCausalLM, TrainingArguments, set_seed
import pnfp_bc_pilot as pilot

P = Path(__file__).resolve().parents[1]
E = P/'results/logit_distillation/same_lineage_bc'
D = Path(str(P)+'_data')

class FormalTrainer(pilot.KDTrainer):
    def compute_loss(self, model, inputs, return_outputs=False, num_items_in_batch=None):
        labels=inputs['labels']; mask=labels[:,1:]!=-100
        self.memory('before_forward')
        with torch.inference_mode():
            teacher_logits=self.teacher(input_ids=inputs['input_ids'],attention_mask=inputs['attention_mask'],use_cache=False).logits
        # The selected tensor is created OUTSIDE inference mode, so backward may
        # retain it as a constant. This is not a clone of batch*seq*vocab logits.
        with torch.no_grad():
            t=teacher_logits[:,:-1][mask].to(torch.bfloat16)
        assert not torch.is_inference(t)
        del teacher_logits
        self.memory('after_teacher_forward')
        outputs=model(input_ids=inputs['input_ids'],attention_mask=inputs['attention_mask'],use_cache=False)
        self.memory('after_student_forward')
        s=outputs.logits[:,:-1][mask]; assert s.shape==t.shape
        loss,ce,kd=pilot.ResponseObjective.apply(s,t,labels[:,1:][mask])
        self.memory('after_KL');assert torch.isfinite(loss).item()
        self.last={'ce_loss':ce.item(),'kd_loss':kd.item(),'scaled_kd_loss':4*kd.item(),'total_loss':loss.item(),'input_tokens':inputs['attention_mask'].sum().item(),'response_tokens':mask.sum().item(),'samples':len(labels),'nan_inf':False}
        return (loss,outputs) if return_outputs else loss

def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()

def main(method):
    q=E/method;cfg=json.loads((q/'protocol.json').read_text())
    lock=(E/'gpu_serial.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    assert not (q/'training_summary.json').exists(),'Existing final run must not rerun'
    assert cfg['epochs']==3 and cfg['optimizer_steps']==7500 and cfg['batch_size']==8 and cfg['gradient_accumulation_steps']==1
    assert cfg['lr']==1e-5 and cfg['temperature']==2 and cfg['ce_weight']==cfg['kd_weight']==.5
    pilot.E=q;pilot.DATA=Path(cfg['dataset_path']);pilot.DATA_SHA=cfg['dataset_sha256'];pilot.TEACHER=Path(cfg['teacher_path'])
    tok,ds=pilot.preflight()
    gpu=subprocess.check_output(['nvidia-smi','--query-gpu=name,memory.total,memory.used,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip()
    assert int(gpu.split(',')[-2])<100 and int(gpu.split(',')[-1])<=5,'GPU_IDLE_GATE'
    output=D/'runs/same_lineage_bc'/cfg['run_id'];assert not output.exists(),'No implicit rerun or resume'
    set_seed(42);torch.cuda.reset_peak_memory_stats();started=now()
    if cfg.get('teacher_loader') == 'canonical_base_plus_original_frozen_peft_adapter':
        assert method == 'ctcc'
        from peft import PeftModel
        teacher_base=AutoModelForCausalLM.from_pretrained(pilot.BASE,local_files_only=True,torch_dtype=torch.bfloat16)
        # Preserve the historical Teacher's unmerged PEFT forward computation.
        teacher=PeftModel.from_pretrained(teacher_base,pilot.TEACHER,local_files_only=True)
    else:
        teacher=AutoModelForCausalLM.from_pretrained(pilot.TEACHER,local_files_only=True,torch_dtype=torch.bfloat16)
    teacher=teacher.cuda().eval();teacher.requires_grad_(False);teacher.config.use_cache=False
    student=AutoModelForCausalLM.from_pretrained(pilot.BASE,local_files_only=True,torch_dtype=torch.bfloat16).cuda();student.config.use_cache=False;student.gradient_checkpointing_enable()
    if cfg.get('teacher_loader') == 'canonical_base_plus_original_frozen_peft_adapter':
        for key in ('model_type','vocab_size','hidden_size','num_hidden_layers','num_attention_heads'):
            assert getattr(teacher.config,key)==getattr(student.config,key),key
        assert teacher.get_output_embeddings().weight.shape==student.get_output_embeddings().weight.shape
        assert not hasattr(student,'peft_config')
    else:
        # state_dict includes both embedding/head names even when Student ties them.
        # Keep the original Teacher tying unchanged (iSeal's native Teacher is untied).
        assert {n:tuple(p.shape) for n,p in teacher.state_dict().items()}=={n:tuple(p.shape) for n,p in student.state_dict().items()}
    tb=pilot.weight_hash(teacher);sb=pilot.weight_hash(student)
    pilot.put(q/'initial_parameter_checksums.json',{'teacher':tb,'student':sb,'timestamp':now(),'fresh_base_revision':cfg['base_revision']})
    args=TrainingArguments(output_dir=str(output),num_train_epochs=3,learning_rate=1e-5,per_device_train_batch_size=8,gradient_accumulation_steps=1,bf16=True,fp16=False,save_strategy='epoch',save_total_limit=1,logging_steps=1,logging_nan_inf_filter=False,report_to=[],seed=42,data_seed=42,remove_unused_columns=False,gradient_checkpointing=True,optim=cfg['optimizer'],lr_scheduler_type=cfg['scheduler'],warmup_ratio=cfg['warmup_ratio'],weight_decay=cfg['weight_decay'],max_steps=-1)
    ref={};cb=pilot.Telemetry(7500,ref,'training')
    trainer=FormalTrainer(model=student,teacher=teacher,stage='training',args=args,train_dataset=ds,data_collator=pilot.Collator(tok),processing_class=tok,callbacks=[cb]);ref['trainer']=trainer
    pilot.put(q/'effective_runtime_config.json',{'training_arguments':args.to_dict(),'gpu_before':gpu,'runner_sha256':pilot.sha(__file__),'pilot_objective_source_sha256':pilot.sha(P/'scripts/pnfp_bc_pilot.py'),'checkpoint_policy':'epoch resumable latest only, no detector trajectory','sampler_class':type(trainer._get_train_sampler()).__name__})
    wall=time.perf_counter();trainer.train();torch.cuda.synchronize();elapsed=time.perf_counter()-wall
    assert trainer.state.global_step==7500 and len(cb.rows)==7500
    ta=pilot.weight_hash(teacher);sa=pilot.weight_hash(student);assert tb==ta and sb!=sa
    assert not teacher.training and all(p.grad is None for p in teacher.parameters())
    final=output/'final_model';save_start=time.perf_counter();trainer.save_model(final);tok.save_pretrained(final);save_seconds=time.perf_counter()-save_start
    rows=cb.rows;post=[x for x in rows if x['step']>args.get_warmup_steps(7500)];times=[x['seconds'] for x in post]
    summary={'status':'COMPLETE','run_id':cfg['run_id'],'steps':7500,'epochs':3,'teacher_frozen':True,'student_updated':True,'teacher_checksum_before':tb,'teacher_checksum_after':ta,'student_checksum_before':sb,'student_checksum_after':sa,'started_at':started,'completed_at':now(),'train_wall_seconds':elapsed,'save_seconds':save_seconds,'warmup_wall_seconds':sum(x['seconds'] for x in rows[:args.get_warmup_steps(7500)]),'post_warmup_mean_sec_per_step':statistics.mean(times),'post_warmup_median_sec_per_step':statistics.median(times),'all_step_mean_seconds':statistics.mean(x['seconds'] for x in rows),'all_step_median_seconds':statistics.median(x['seconds'] for x in rows),'tokens_per_second':sum(x['input_tokens'] for x in post)/sum(times),'samples_per_second':sum(x['samples'] for x in post)/sum(times),'peak_allocated':torch.cuda.max_memory_allocated(),'peak_reserved':torch.cuda.max_memory_reserved(),'nan_inf_count':0,'oom_count':0,'final_model':str(final),'final_files':[{'name':p.name,'bytes':p.stat().st_size,'sha256':pilot.sha(p)} for p in sorted(final.iterdir()) if p.is_file()]}
    for filename,data in [('loss_trace.csv',rows),('memory_trace.csv',trainer.mem)]:
        with (q/filename).open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=sorted(set().union(*(x.keys() for x in data))));w.writeheader();w.writerows(data)
    pilot.put(q/'training_summary.json',summary);pilot.put(q/'training_exit.json',{'returncode':0,'completed_at':now()})
    print('FORMAL_TRAINING_COMPLETE',method,flush=True)

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('method',choices=['pnfp','evertracer','ctcc','iseal','scw','passive_shared']);m=a.parse_args().method
    try:main(m)
    except BaseException:
        pilot.put(E/m/'training_exit.json',{'returncode':1,'completed_at':now(),'error':traceback.format_exc(),'restart_policy':'inspect latest checkpoint before any continuation; no implicit retrain'});raise
