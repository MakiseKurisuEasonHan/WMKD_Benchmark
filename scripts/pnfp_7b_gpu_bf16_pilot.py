"""Independent GPU-resident BF16 Adam-state pilot; never launch Teacher."""
import hashlib, json, os, resource, statistics, sys, time, traceback
from pathlib import Path
ROOT=Path('/root/autodl-tmp/WMKD_Benchmark_data/scale_7b')
P=Path('/root/autodl-tmp/WMKD_Benchmark')
OUT=ROOT/os.environ.get('PNFP_GPU_BF16_RUN','gpu_bf16_pilot_v1')

class PilotFinished(Exception): pass

def main():
    import torch, deepspeed
    from transformers import TrainerCallback, set_seed
    from deepspeed.runtime.config import DeepSpeedConfig
    assert deepspeed.__version__=='0.19.6',deepspeed.__version__
    cfg=json.loads((P/'configs/watermark/pnfp_7b_gpu_bf16_pilot.json').read_text())
    source=ROOT/'pnfp_source';os.chdir(source);sys.path.insert(0,str(source))
    import finetune_multigpu as official
    fp=json.loads((ROOT/'fingerprint_manifest.json').read_text())
    assert hashlib.sha256(Path(fp['official_output']).read_bytes()).hexdigest()==cfg['fingerprint_sha256']
    assert hashlib.sha256((source/'generated_data/benign.json').read_bytes()).hexdigest()=='bd18da3b5a56002822a9789d83667452597ccc16979df3277fe2d04ff10a0201'
    set_seed(42);torch.backends.cudnn.deterministic=True
    rows=[];wa=[];holder={};start=time.perf_counter()
    original_args=official.TrainingArguments
    def adapted_args(*args,**kw):
        ds=kw['deepspeed'];ds.pop('bfloat16',None)
        ds.update(cfg['deepspeed'])
        assert not any(k.startswith('offload') for k in ds['zero_optimization'])
        probe=dict(ds,train_micro_batch_size_per_gpu=6,train_batch_size=1026,gradient_accumulation_steps=171)
        parsed=DeepSpeedConfig(probe)
        assert parsed.bfloat16_config.bf16_master_weights_and_grads and parsed.bfloat16_config.bf16_optimizer_states
        # DeepSpeed0.16.9 silently clamps warmup0 to2;0.19.6 rejects0.
        # Preserve the effective legacy schedule, verified over all40 steps.
        kw.update(warmup_steps=2,gradient_checkpointing=True,gradient_checkpointing_kwargs={'use_reentrant':False},report_to=[])
        result=original_args(*args,**kw)
        (OUT/'resolved_training_args.json').write_text(json.dumps(result.to_dict(),indent=2,default=str))
        return result
    official.TrainingArguments=adapted_args
    class NoEvalStop(TrainerCallback):
        def __init__(self,*args,**kw):pass
    official.EarlyStoppingByLoss=NoEvalStop
    base_wa=official.ModelAverageCallback
    class GPUWA(base_wa):
        def __init__(self,*args,**kw):
            super().__init__(*args,**kw);self.orig_model=self.orig_model.cuda()
        def on_epoch_end(self,*args,**kw):
            torch.cuda.synchronize();t=time.perf_counter();r=super().on_epoch_end(*args,**kw)
            torch.cuda.synchronize();wa.append(time.perf_counter()-t);return r
    official.ModelAverageCallback=GPUWA
    class Telemetry(TrainerCallback):
        def on_train_begin(self,args,state,control,**kw):
            assert state.max_steps==40
            engine=holder['trainer'].model_wrapped;z=engine.optimizer
            assert not z.cpu_offload and z.bf16_master_weights_and_gradients and z.bf16_optimizer_states
            assert z.gradient_accumulation_dtype==torch.bfloat16
            assert all(p.device.type=='cuda' and p.dtype==torch.bfloat16 for p in z.single_partition_of_fp32_groups)
            (OUT/'optimizer_identity.json').write_text(json.dumps({'deepspeed':deepspeed.__version__,'module':deepspeed.__file__,'wrapper':type(z).__name__,'optimizer':type(z.optimizer).__name__,'defaults':z.optimizer.defaults,'full_parameter':True,'parameters':sum(p.numel() for p in engine.module.parameters()),'bf16_flags_verified':True,'cpu_offload':z.cpu_offload,'grad_accum_dtype':str(z.gradient_accumulation_dtype)},indent=2,default=str))
        def on_step_begin(self,args,state,control,**kw):
            torch.cuda.synchronize();self.t=time.perf_counter()
            z=holder['trainer'].model_wrapped.optimizer
            self.before=z.single_partition_of_fp32_groups[0].detach().view(-1)[:65536].clone()
            self.lr=[g['lr'] for g in z.optimizer.param_groups]
        def on_step_end(self,args,state,control,**kw):
            torch.cuda.synchronize();tr=holder['trainer'];z=tr.model_wrapped.optimizer
            loss=float(tr.accum_loss);tr.accum_loss=None;assert torch.isfinite(torch.tensor(loss))
            moment_tensors=[v for s in z.optimizer.state.values() for k,v in s.items() if k in ('exp_avg','exp_avg_sq')]
            assert moment_tensors and all(v.dtype==torch.bfloat16 and v.device.type=='cuda' for v in moment_tensors)
            steps=[float(s['step']) for s in z.optimizer.state.values() if 'step' in s]
            assert steps and min(steps)>=state.global_step
            row={'update':state.global_step,'sec_per_update':time.perf_counter()-self.t,'training_loss':loss,'lr_used':self.lr,'adam_step_min':min(steps),'moment_dtypes':sorted(set(str(v.dtype) for v in moment_tensors)),'moment_devices':sorted(set(str(v.device) for v in moment_tensors)),'sample_changed_elements':int((self.before!=z.single_partition_of_fp32_groups[0].detach().view(-1)[:65536]).sum()),'peak_gpu_allocated_bytes':torch.cuda.max_memory_allocated(),'peak_gpu_reserved_bytes':torch.cuda.max_memory_reserved(),'peak_host_process_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024}
            rows.append(row)
            with (OUT/'steps.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
            print('PILOT_UPDATE '+json.dumps(row),flush=True)
            if state.global_step>=cfg['pilot_updates'] or loss<.005:control.should_training_stop=True
        def on_train_end(self,*args,**kw):raise PilotFinished()
    parent=official.CustomTrainer
    class PilotTrainer(parent):
        def __init__(self,*args,**kw):
            kw['model'].config.use_cache=False
            super().__init__(*args,**kw);a=self.args
            assert len(self.train_dataset)==1024 and a.per_device_train_batch_size==6 and a.gradient_accumulation_steps==171
            assert self.data_collator.num_to_add==2 and len(self.train_dataset[0]['input_ids'])==64
            assert all(p.requires_grad for p in self.model.parameters())
            self.accum_loss=None;holder['trainer']=self;self.add_callback(Telemetry())
        def training_step(self,*args,**kw):
            loss=super().training_step(*args,**kw)
            self.accum_loss=loss.detach().float() if self.accum_loss is None else self.accum_loss+loss.detach().float()
            return loss
    official.CustomTrainer=PilotTrainer
    torch.cuda.reset_peak_memory_stats()
    try:
        official.finetune(model_path=str(ROOT/'models/Llama-2-7b-chat-hf'),model_size='7B-chat',model_family='llama',num_fingerprints=1024,max_key_length=16,max_response_length=1,num_train_epochs=40,learning_rate=5e-5,batch_size=8,fingerprint_generation_strategy='perinucleus',fingerprints_file_path=fp['official_output'],forgetting_regularizer_strength=.75,weight_decay=1e-4,deepspeed_stage=2,use_lora=False,benign_proportion=.25,benign_data_file_path=str(source/'generated_data/benign.json'),use_chat_template=True,num_responses_per_fingerprint=1,result_path=str(OUT/'official')+'/',seed=42)
    except PilotFinished:pass
    assert rows and (len(rows)==cfg['pilot_updates'] or rows[-1]['training_loss']<.005)
    result={'status':'PILOT_PASS_STOPPED_FOR_USER_REVIEW','optimizer_updates':len(rows),'wall_seconds':time.perf_counter()-start,'steps':rows,'wa_seconds':wa,'peak_gpu_allocated_bytes':torch.cuda.max_memory_allocated(),'peak_gpu_reserved_bytes':torch.cuda.max_memory_reserved(),'peak_host_process_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,'teacher_started':False,'checkpoint_saved':False,'numerically_identical_to_FP32_Adam':False}
    (OUT/'result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)

if __name__=='__main__':
    try:main()
    except BaseException:
        (OUT/'failure.json').write_text(json.dumps({'status':'FAILED_STOPPED','traceback':traceback.format_exc(),'teacher_started':False},indent=2));raise
