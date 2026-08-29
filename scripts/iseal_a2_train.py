"""Formal iSeal Experiment A2 trainer after the mandatory gate passes."""

import argparse, datetime, json, os, random, traceback
from pathlib import Path

import numpy as np
import torch
import yaml
from datasets import load_dataset
from torch.utils.data import DataLoader
from transformers import AutoModelForCausalLM, AutoTokenizer, get_linear_schedule_with_warmup

from iseal_trainability_audit import KeyedCipher, TextDataset
from iseal_a2_trainability_audit import A2InstructionFingerprint


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def main():
    p=argparse.ArgumentParser(); p.add_argument("--config",required=True); p.add_argument("--run-root",required=True); p.add_argument("--dataset-cache",required=True); a=p.parse_args()
    run=Path(a.run_root); status_path=run/"status/status.json"; config=yaml.safe_load(Path(a.config).read_text(encoding="utf-8"))
    status={"run_id":run.name,"experiment":f"iSeal {config['experiment']}","status":"RUNNING","stage":"initializing","start_time":datetime.datetime.now().astimezone().isoformat(),"pid":os.getpid(),"exit_code":None}
    write_json(status_path,status)
    try:
        secret_hex=os.environ.get("ISEAL_SECRET_KEY_HEX"); assert secret_hex
        import hashlib
        secret=bytes.fromhex(secret_hex); assert hashlib.sha256(secret).hexdigest()==config["training"]["secret_key_sha256"]
        seed=config["seed"]; random.seed(seed); np.random.seed(seed); torch.manual_seed(seed); torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic=True; torch.backends.cudnn.benchmark=False
        model_path=config["model"]["path"]
        tokenizer=AutoTokenizer.from_pretrained(model_path,local_files_only=True,use_fast=False)
        if tokenizer.pad_token_id is None: tokenizer.pad_token=tokenizer.eos_token
        ds=load_dataset(config["dataset"]["id"],split="train",cache_dir=a.dataset_cache).shuffle(seed=config["dataset"]["shuffle_seed"])
        ranges=config["dataset"].get("registered_index_ranges")
        indices=[i for start,end in ranges for i in range(start,end)] if ranges else list(range(config["dataset"]["registered_count"]))
        registered=ds.select(indices); texts=registered["text"]
        text_ds=TextDataset(texts,tokenizer,config["training"]["max_sequence_length"])
        train_ids=sorted({token for row in text_ds for token in row["input_ids"].tolist()})
        model=AutoModelForCausalLM.from_pretrained(model_path,torch_dtype=torch.bfloat16,device_map="auto",low_cpu_mem_usage=True,local_files_only=True)
        original=model.get_input_embeddings(); repair=config["training"]["initialization_repair"]
        adapter=A2InstructionFingerprint(original,train_ids,config["training"]["adapter_inner_dim"],repair["delta"]["std"]); model.set_input_embeddings(adapter)
        for parameter in model.parameters(): parameter.requires_grad=False
        for parameter in adapter.parameters():
            if parameter is not adapter.orig_emb.weight: parameter.requires_grad=True
        freeze_tied=config.get("scientific_modification",{}).get("freeze_tied_input_embedding_lm_head",False)
        model.lm_head.weight.requires_grad=not freeze_tied
        cipher=KeyedCipher(model.config.hidden_size,config["training"]["cipher_layers"],secret,torch.bfloat16)
        loader=DataLoader(text_ds,batch_size=config["training"]["per_device_batch_size"],shuffle=True)
        total_steps=config["training"]["epochs"]*len(loader); warmup=int(config["training"]["warmup_ratio"]*total_steps)
        optimizer=torch.optim.AdamW([x for x in model.parameters() if x.requires_grad],lr=config["training"]["learning_rate"],weight_decay=config["training"]["weight_decay"],eps=config["training"]["adam_epsilon"])
        scheduler=get_linear_schedule_with_warmup(optimizer,warmup,total_steps)
        status.update(stage="training",total_steps=total_steps,warmup_steps=warmup,trainable_token_count=len(train_ids)); write_json(status_path,status)
        history=[]; device=next(model.parameters()).device; global_step=0
        for epoch in range(config["training"]["epochs"]):
            for batch in loader:
                ids=batch["input_ids"].to(device); mask=batch["attention_mask"].to(device); labels=batch["labels"].to(device)
                lr=optimizer.param_groups[0]["lr"]; out=model(inputs_embeds=cipher.to(device)(model.get_input_embeddings()(ids)),attention_mask=mask,labels=labels)
                out.loss.backward(); torch.nn.utils.clip_grad_norm_(model.parameters(),config["training"]["max_grad_norm"])
                optimizer.step(); scheduler.step(); optimizer.zero_grad(); global_step+=1
                row={"step":global_step,"epoch":epoch+1,"loss":out.loss.item(),"effective_learning_rate":lr}; history.append(row)
                print(json.dumps(row),flush=True)
                status.update(stage="training",step=global_step,epoch=epoch+1,last_loss=out.loss.item()); write_json(status_path,status)
        status.update(stage="saving"); write_json(status_path,status)
        frozen_head=model.lm_head.weight.detach().clone() if freeze_tied else None
        adapter.merge(); model.set_input_embeddings(adapter.orig_emb)
        if freeze_tied:
            model.lm_head.weight=torch.nn.Parameter(frozen_head,requires_grad=False)
            model.config.tie_word_embeddings=False
        checkpoint=run/"checkpoints/teacher_merged"; checkpoint.mkdir(parents=True,exist_ok=True)
        model.save_pretrained(checkpoint,safe_serialization=True,max_shard_size="1GB"); tokenizer.save_pretrained(checkpoint)
        torch.save({"delta":adapter.delta.state_dict(),"A":adapter.A.state_dict(),"B":adapter.B.state_dict(),"train_ids":train_ids},run/"checkpoints/adapter_state.pt")
        write_json(run/"results/training.json",{"run_id":run.name,"epochs":config["training"]["epochs"],"total_steps":total_steps,"warmup_steps":warmup,"final_loss":history[-1]["loss"],"history":history,"checkpoint":str(checkpoint),"registered_count":len(texts),"trainable_token_count":len(train_ids)})
        status.update(status="COMPLETED",stage="training_complete",exit_code=0,end_time=datetime.datetime.now().astimezone().isoformat(),checkpoint=str(checkpoint)); write_json(status_path,status)
    except Exception:
        status.update(status="FAILED",stage="training_failed",exit_code=1,end_time=datetime.datetime.now().astimezone().isoformat(),traceback=traceback.format_exc()); write_json(status_path,status); raise


if __name__=="__main__": main()
