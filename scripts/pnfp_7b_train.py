"""A2 official training with runtime evidence and a horizon-preserving speed stop."""
import argparse, hashlib, json, os, resource, shutil, statistics, sys, time
from pathlib import Path

ROOT=Path('/root/autodl-tmp/WMKD_Benchmark_data/scale_7b')
SOURCE=ROOT/'pnfp_source';MODEL=ROOT/'models/Llama-2-7b-chat-hf'

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--stage',choices=['speed','teacher'],required=True)
    parser.add_argument('--local_rank',type=int,default=0);a=parser.parse_args()
    out=ROOT/'runs'/a.stage;out.mkdir(parents=True,exist_ok=False)
    os.chdir(SOURCE);sys.path.insert(0,str(SOURCE))
    import torch
    from transformers import TrainerCallback, set_seed
    import finetune_multigpu as official
    set_seed(42);torch.backends.cudnn.deterministic=True
    fp=json.loads((ROOT/'fingerprint_manifest.json').read_text())
    assert hashlib.sha256(Path(fp['official_output']).read_bytes()).hexdigest()==fp['sha256']
    benign=SOURCE/'generated_data/benign.json'
    assert hashlib.sha256(benign.read_bytes()).hexdigest()=='bd18da3b5a56002822a9789d83667452597ccc16979df3277fe2d04ff10a0201'
    assert shutil.disk_usage(ROOT).free>20*1024**3
    rows=[];wa=[];runtime={};peak_used=0;loss_rows=[];trainer_ref={}
    class TrainingLossStop(TrainerCallback):
        def __init__(self,loss_threshold):self.threshold=loss_threshold
        def on_log(self,args,state,control,logs=None,**kwargs):
            # Trainer's display loss is rounded. Telemetry below records and
            # thresholds the unrounded full-update loss instead.
            return control
    # Paper Appendix D/user instruction stops on TRAIN loss. Released callback
    # instead watches eval_loss; preserve this explicit, authorized difference.
    official.EarlyStoppingByLoss=TrainingLossStop
    class Telemetry(TrainerCallback):
        def on_train_begin(self,args,state,control,**kwargs):
            assert state.max_steps==40,state.max_steps
            runtime['trainer_max_steps']=state.max_steps
            runtime['optimizer_class']=type(kwargs['optimizer']).__name__
            (out/'runtime.json').write_text(json.dumps(runtime,indent=2,default=str))
        def on_step_begin(self,args,state,control,**kwargs):
            torch.cuda.synchronize();self.begin=time.perf_counter()
        def on_step_end(self,args,state,control,**kwargs):
            nonlocal peak_used
            torch.cuda.synchronize()
            trainer=trainer_ref['trainer']
            value=float(trainer.update_loss);assert torch.isfinite(torch.tensor(value))
            trainer.update_loss=None
            loss_rows.append({'step':state.global_step,'training_loss':value})
            with (out/'train_loss.jsonl').open('a') as f:f.write(json.dumps(loss_rows[-1])+'\n')
            if value<.005:control.should_training_stop=True
            row={'step':state.global_step,'seconds':time.perf_counter()-self.begin,
                 'elapsed_since_launch':time.perf_counter()-start,
                 'peak_allocated':torch.cuda.max_memory_allocated(),'peak_reserved':torch.cuda.max_memory_reserved(),
                 'host_peak_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
                 'disk_used_bytes':shutil.disk_usage(ROOT).used}
            peak_used=max(peak_used,row['disk_used_bytes']);rows.append(row)
            with (out/'steps.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
            if a.stage=='speed' and state.global_step>=5:control.should_training_stop=True
        def on_log(self,args,state,control,logs=None,**kwargs):
            if logs and 'loss' in logs:assert torch.isfinite(torch.tensor(logs['loss'])),'nonfinite loss'
    parent_wa=official.ModelAverageCallback
    class TimedWA(parent_wa):
        def __init__(self,*args,**kwargs):
            super().__init__(*args,**kwargs)
            # Same immutable BF16 reference and same averaging formula; use
            # spare VRAM instead of competing with CPU optimizer state.
            self.orig_model=self.orig_model.cuda()
        def on_epoch_end(self,*args,**kwargs):
            torch.cuda.synchronize();start=time.perf_counter();result=super().on_epoch_end(*args,**kwargs)
            torch.cuda.synchronize();wa.append(time.perf_counter()-start);return result
    official.ModelAverageCallback=TimedWA
    parent=official.CustomTrainer
    class RecordedTrainer(parent):
        def __init__(self,*args,**kwargs):
            super().__init__(*args,**kwargs)
            tr=self.args
            assert tr.per_device_train_batch_size==6 and tr.gradient_accumulation_steps==171
            assert tr.bf16 and tr.num_train_epochs==40 and tr.learning_rate==5e-5 and tr.weight_decay==1e-4
            assert len(self.train_dataset)==1024
            assert all(p.requires_grad for p in self.model.parameters())
            assert self.model.config.hidden_size==4096 and self.model.config.num_hidden_layers==32
            assert tr.seed==42
            assert self.data_collator.num_to_add==2
            sample=self.train_dataset[0]
            assert len(sample['input_ids'])==64
            assert sum(x!=-100 for x in sample['labels'])>0
            runtime.update({'training_arguments':tr.to_dict(),'model_config':self.model.config.to_dict(),
                            'trainable_parameters':sum(p.numel() for p in self.model.parameters()),
                            'dataset_count':len(self.train_dataset),'sequence_length':64,
                            'fingerprint_microbatch':6,'benign_per_microbatch':2,
                            'gradient_accumulation_steps':171,'wa':.75,'benign_proportion':.25,
                            'first_tokenized_example':sample,'stage':a.stage,'full_horizon':40,
                            'early_stop_metric':'epoch mixed-data training cross entropy < 0.005',
                            'speed_stop_steps':5 if a.stage=='speed' else None})
            self.add_callback(Telemetry())
            self.update_loss=None;trainer_ref['trainer']=self
        def training_step(self,*args,**kwargs):
            loss=super().training_step(*args,**kwargs)
            # Transformers4.44.2 returns detached loss / accumulation_steps;
            # summing over the official full-batch update matches logged loss.
            self.update_loss=loss.detach().float() if self.update_loss is None else self.update_loss+loss.detach().float()
            return loss
    official.CustomTrainer=RecordedTrainer
    torch.cuda.reset_peak_memory_stats();start=time.perf_counter()
    h=official.finetune(model_path=str(MODEL),model_size='7B-chat',model_family='llama',
        num_fingerprints=1024,max_key_length=16,max_response_length=1,num_train_epochs=40,
        learning_rate=5e-5,batch_size=8,fingerprint_generation_strategy='perinucleus',
        fingerprints_file_path=fp['official_output'],forgetting_regularizer_strength=.75,
        weight_decay=1e-4,deepspeed_stage=2,use_lora=False,benign_proportion=.25,
        benign_data_file_path=str(benign),use_chat_template=True,num_responses_per_fingerprint=1,
        result_path=str(out/'official')+'/',seed=42)
    elapsed=time.perf_counter()-start
    expected=5 if a.stage=='speed' else 40
    early=bool(loss_rows) and loss_rows[-1]['training_loss']<.005
    assert len(rows)==expected or early,('Unexpected early stop',len(rows),expected)
    final=out/'official/saved_models'/h/'final_model';assert final.exists()
    times=[x['seconds'] for x in rows];steady=times[1:] or times
    cadence=[rows[i]['elapsed_since_launch']-rows[i-1]['elapsed_since_launch'] for i in range(1,len(rows))]
    summary={'status':'PASS','stage':a.stage,'optimizer_steps':len(rows),'wall_seconds':elapsed,
             'median_steady_seconds_per_optimizer_step':statistics.median(steady),
             'wa_seconds':wa,'projected_40_update_compute_plus_WA_seconds':40*(statistics.median(steady)+statistics.mean(wa)),
             'median_epoch_cadence_seconds_including_eval_and_WA':statistics.median(cadence) if cadence else None,
             'projected_max40_seconds_including_epoch_evaluation':40*statistics.median(cadence) if cadence else None,
             'loss_trajectory':loss_rows,'early_stopped_on_training_loss':early,
             'time_to_convergence':'Not inferable from a short pilot; report observed curve and 40-update upper-horizon estimate',
             'projection_excludes_eval_load_and_save':True,'peak_allocated_bytes':torch.cuda.max_memory_allocated(),
             'peak_reserved_bytes':torch.cuda.max_memory_reserved(),'peak_disk_used_observed_bytes':max(peak_used,shutil.disk_usage(ROOT).used),
             'final_model':str(final),'final_model_bytes':sum(p.stat().st_size for p in final.iterdir() if p.is_file()),
             'science_result':a.stage=='teacher'}
    (out/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary),flush=True)
if __name__=='__main__':main()
