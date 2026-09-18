def main():
    import torch,bitsandbytes as bnb
    from transformers import TrainerCallback,set_seed
    from deepspeed.runtime.lr_schedules import WarmupDecayLR
    cfg=json.loads((P/'configs/watermark/pnfp_7b_wa050_extension.json').read_text())
    assert bnb.__version__==cfg['bitsandbytes_version']
    assert json.loads((ROOT/'bnb_preflight.json').read_text())['status']=='PASS'
    source=ROOT/'pnfp_source';os.chdir(source);sys.path.insert(0,str(source))
    import finetune_multigpu as official
    fp=json.loads((ROOT/'fingerprint_manifest.json').read_text())
    assert hashlib.sha256(Path(fp['official_output']).read_bytes()).hexdigest()==cfg['fingerprint_sha256']
    assert hashlib.sha256((source/'generated_data/benign.json').read_bytes()).hexdigest()=='bd18da3b5a56002822a9789d83667452597ccc16979df3277fe2d04ff10a0201'
    set_seed(42);torch.backends.cudnn.deterministic=True
    rows=[];wa=[];holder={};start=time.perf_counter();reason='MAX_24_NONZERO_LR_UPDATES'
    args_class=official.TrainingArguments
    def training_args(*args,**kw):
        kw['deepspeed']=None
        kw.update(report_to=[],gradient_checkpointing=True,gradient_checkpointing_kwargs={'use_reentrant':False})
        result=args_class(*args,**kw)
        (OUT/'training_args.json').write_text(json.dumps(result.to_dict(),indent=2,default=str));return result
    official.TrainingArguments=training_args
    class NoEvalStop(TrainerCallback):
        def __init__(self,*a,**kw):pass
    official.EarlyStoppingByLoss=NoEvalStop
    original_wa=official.ModelAverageCallback
    class GPUWA(original_wa):
        def __init__(self,*a,**kw):super().__init__(*a,**kw);self.orig_model=self.orig_model.cuda()
        def on_epoch_end(self,*a,**kw):
            torch.cuda.synchronize();t=time.perf_counter();r=super().on_epoch_end(*a,**kw);torch.cuda.synchronize();wa.append(time.perf_counter()-t)
            step=int(a[1].global_step) if len(a)>1 else int(kw['state'].global_step)
            trajectory_probe(kw['model'],step)
            if should_stop(): a[2].should_training_stop=True
            return r
    official.ModelAverageCallback=GPUWA
    class Telemetry(TrainerCallback):
        def on_train_begin(self,args,state,control,**kw):assert state.max_steps==40
        def on_step_begin(self,args,state,control,**kw):
            torch.cuda.synchronize();self.t=time.perf_counter();tr=holder['trainer'];self.lrs=[g['lr'] for g in tr.raw_optimizer.param_groups]
            self.samples=[p.detach().view(-1)[::max(1,p.numel()//128)].clone() for p in tr.model.parameters()]
        def on_step_end(self,args,state,control,**kw):
            nonlocal reason
            torch.cuda.synchronize();seconds=time.perf_counter()-self.t;tr=holder['trainer'];opt=tr.raw_optimizer
            loss=float(tr.update_loss);tr.update_loss=None;assert torch.isfinite(torch.tensor(loss))
            params=list(tr.model.parameters());finite=all(bool(torch.isfinite(p).all()) for p in params)
            assert finite,'Nonfinite model parameter'
            moment_meta={};moment_bytes=0;step_counts=[]
            for st in opt.state.values():
                if 'step' in st:step_counts.append(int(st['step']))
                for key in ('state1','state2'):
                    if key not in st:continue
                    v=st[key];assert v.device.type=='cuda'
                    label=str(v.dtype);moment_meta[label]=moment_meta.get(label,0)+v.numel();moment_bytes+=v.numel()*v.element_size()
                    if v.is_floating_point():assert bool(torch.isfinite(v).all())
            assert moment_meta.get('torch.uint8',0)>0 and step_counts and min(step_counts)>=state.global_step
            changed=sum(int((x!=p.detach().view(-1)[::max(1,p.numel()//128)]).sum()) for x,p in zip(self.samples,params))
            free,total=torch.cuda.mem_get_info();headroom=min(free,total-torch.cuda.max_memory_reserved())
            row={'update':state.global_step,'sec_per_update':seconds,'training_loss':loss,'lr_used':self.lrs,'adam_step_min':min(step_counts),'sample_changed_elements':changed,'moment_elements_by_dtype':moment_meta,'moment_bytes':moment_bytes,'nan_inf_detected':False,'peak_gpu_allocated_bytes':torch.cuda.max_memory_allocated(),'peak_gpu_reserved_bytes':torch.cuda.max_memory_reserved(),'peak_host_process_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,'headroom_conservative_bytes':headroom}
            rows.append(row)
            with (OUT/'steps.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
            print('PILOT_UPDATE '+json.dumps(row),flush=True)
            # Formal run has no pilot headroom stopping rule.
            # Diagnostic: loss threshold is recorded, not a sole stop rule.
            if state.global_step>=cfg['pilot_max_calls']:control.should_training_stop=True
        def on_train_end(self,*a,**kw):raise PilotFinished()
    parent=official.CustomTrainer
    class PilotTrainer(parent):
        def __init__(self,*a,**kw):
            kw['model'].config.use_cache=False;super().__init__(*a,**kw)
            assert not self.is_deepspeed_enabled
            assert len(self.train_dataset)==1024 and self.args.gradient_accumulation_steps==171 and self.args.per_device_train_batch_size==6
            assert self.data_collator.num_to_add==2 and len(self.train_dataset[0]['input_ids'])==64
            assert all(p.requires_grad and p.dtype==torch.bfloat16 for p in self.model.parameters())
            self.update_loss=None;holder['trainer']=self;self.add_callback(Telemetry())
        def create_optimizer(self):
            names=self.get_decay_parameter_names(self.model)
            groups=[{'params':[p for n,p in self.model.named_parameters() if p.requires_grad and n in names],'weight_decay':self.args.weight_decay},{'params':[p for n,p in self.model.named_parameters() if p.requires_grad and n not in names],'weight_decay':0.0}]
            opt=bnb.optim.AdamW8bit(groups,lr=5e-5,betas=(.9,.999),eps=1e-8,min_8bit_size=4096,is_paged=False)
            self.optimizer=self.raw_optimizer=opt
            identity={'class':type(opt).__module__+'.'+type(opt).__name__,'bitsandbytes_version':bnb.__version__,'torch_version':torch.__version__,'torch_cuda':torch.version.cuda,'all_trainable':all(p.requires_grad for p in self.model.parameters()),'parameter_count':sum(p.numel() for p in self.model.parameters()),'parameter_dtypes':sorted(set(str(p.dtype) for p in self.model.parameters())),'groups':[{'weight_decay':g['weight_decay'],'parameter_count':sum(p.numel() for p in g['params'])} for g in opt.param_groups],'no_deepspeed':True,'no_offload':True}
            (OUT/'optimizer_identity.json').write_text(json.dumps(identity,indent=2));return opt
        def create_scheduler(self,num_training_steps,optimizer=None):
            assert num_training_steps==40
            self.lr_scheduler=WarmupDecayLR(optimizer or self.optimizer,total_num_steps=40,warmup_min_lr=0,warmup_max_lr=5e-5,warmup_num_steps=0)
            return self.lr_scheduler
        def training_step(self,*a,**kw):
            record_batch(a[1] if len(a)>1 else kw['inputs'])
            loss=super().training_step(*a,**kw);assert bool(torch.isfinite(loss)),'Nonfinite microbatch loss'
            self.update_loss=loss.detach().float() if self.update_loss is None else self.update_loss+loss.detach().float()
            return loss
    official.CustomTrainer=PilotTrainer
    torch.cuda.reset_peak_memory_stats()
    try:
        official.finetune(model_path=str(ROOT/'models/Llama-2-7b-chat-hf'),model_size='7B-chat',model_family='llama',num_fingerprints=1024,max_key_length=16,max_response_length=1,num_train_epochs=40,learning_rate=5e-5,batch_size=8,fingerprint_generation_strategy='perinucleus',fingerprints_file_path=fp['official_output'],forgetting_regularizer_strength=.50,weight_decay=1e-4,deepspeed_stage=2,use_lora=False,benign_proportion=.25,benign_data_file_path=str(source/'generated_data/benign.json'),use_chat_template=True,num_responses_per_fingerprint=1,result_path=str(OUT/'official')+'/',seed=42)
    except PilotFinished:pass
    assert rows
    result={'status':'TRAINING_COMPLETE','reason':reason,'optimizer_updates':len(rows),'step1_completed':True,'steps':rows,'wa_seconds':wa,'training_wall_seconds':time.perf_counter()-start,'peak_gpu_allocated_bytes':torch.cuda.max_memory_allocated(),'peak_gpu_reserved_bytes':torch.cuda.max_memory_reserved(),'peak_host_process_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,'nan_inf_detected':False,'teacher_started':True,'checkpoint_saved':True}
    (OUT/'result.json').write_text(json.dumps(result,indent=2))
    result.update(status='PILOT_COMPLETE',reason=stop_decision(),teacher_started=False,checkpoint_saved=True,trajectory=pilot_rows(),final_model_saved=False)
    (OUT/'result.json').write_text(json.dumps(result,indent=2))
