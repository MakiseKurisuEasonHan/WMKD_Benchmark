"""CTCC A LoRA SFT with response-only loss and preserved multi-turn roles."""
import argparse, hashlib, json, os, time
from pathlib import Path

import torch, yaml
from peft import LoraConfig, get_peft_model
from torch.utils.data import Dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments

from ctcc_serialization_audit import messages


class CTCCDataset(Dataset):
    def __init__(self, root, tokenizer, cutoff):
        records=[]
        for name in ("trigger_set.json","suppression_set.json","normal_set.json"):
            records += json.loads((Path(root)/name).read_text(encoding="utf-8"))
        self.items=[]; dropped=0
        for record in records:
            conversation=messages(record); full_ids=tokenizer.apply_chat_template(conversation,tokenize=True,add_generation_prompt=False)
            labels=[-100]*len(full_ids)
            for index,item in enumerate(conversation):
                if item["role"]!="assistant": continue
                before=conversation[:index]
                prompt=tokenizer.apply_chat_template(before,tokenize=True,add_generation_prompt=True)
                completed=tokenizer.apply_chat_template(conversation[:index+1],tokenize=True,add_generation_prompt=False)
                if completed[:len(prompt)]!=prompt: raise ValueError("assistant response prefix is not stable")
                labels[len(prompt):len(completed)]=completed[len(prompt):]
            full_ids=full_ids[:cutoff];labels=labels[:cutoff]
            if all(x==-100 for x in labels): dropped+=1;continue
            self.items.append({"input_ids":full_ids,"attention_mask":[1]*len(full_ids),"labels":labels})
        if dropped: raise ValueError(f"{dropped} records lost all assistant labels at cutoff")
        if len(self.items)!=1889: raise ValueError(f"expected 1889 records, got {len(self.items)}")
    def __len__(self): return len(self.items)
    def __getitem__(self,index): return self.items[index]


class Collator:
    def __init__(self,pad): self.pad=pad
    def __call__(self,features):
        width=max(len(x["input_ids"]) for x in features);out={"input_ids":[],"attention_mask":[],"labels":[]}
        for row in features:
            n=width-len(row["input_ids"])
            out["input_ids"].append(row["input_ids"]+[self.pad]*n)
            out["attention_mask"].append(row["attention_mask"]+[0]*n)
            out["labels"].append(row["labels"]+[-100]*n)
        return {k:torch.tensor(v,dtype=torch.long) for k,v in out.items()}


def main():
    p=argparse.ArgumentParser();p.add_argument("--config",required=True);p.add_argument("--run-dir",required=True);a=p.parse_args()
    c=yaml.safe_load(Path(a.config).read_text());t=c["training"];run=Path(a.run_dir);adapter=run/"checkpoints/adapter";adapter.mkdir(parents=True,exist_ok=True)
    os.environ.update({"TOKENIZERS_PARALLELISM":"false","WANDB_DISABLED":"true","TRANSFORMERS_OFFLINE":"1","HF_HUB_OFFLINE":"1"})
    tok=AutoTokenizer.from_pretrained(c["model"]["path"],local_files_only=True);tok.pad_token=tok.eos_token
    data=CTCCDataset(c["dataset"]["frozen_root"],tok,t["cutoff_len"])
    model=AutoModelForCausalLM.from_pretrained(c["model"]["path"],local_files_only=True,torch_dtype=torch.bfloat16,attn_implementation="sdpa")
    model.config.use_cache=False
    model=get_peft_model(model,LoraConfig(r=t["lora_rank"],lora_alpha=t["lora_alpha"],lora_dropout=t["lora_dropout"],target_modules="all-linear",task_type="CAUSAL_LM",bias="none"))
    trainable=sum(x.numel() for x in model.parameters() if x.requires_grad);total=sum(x.numel() for x in model.parameters())
    args=TrainingArguments(output_dir=str(run/"checkpoints/trainer"),num_train_epochs=t["epochs"],learning_rate=t["learning_rate"],lr_scheduler_type=t["lr_scheduler_type"],per_device_train_batch_size=t["per_device_train_batch_size"],gradient_accumulation_steps=t["gradient_accumulation_steps"],bf16=True,optim=t["optimizer"],weight_decay=t["weight_decay"],max_grad_norm=t["max_grad_norm"],warmup_steps=t["warmup_steps"],logging_steps=5,save_steps=t["save_steps"],save_total_limit=2,seed=c["seed"],data_seed=c["seed"],report_to=[],remove_unused_columns=False,dataloader_num_workers=8,dataloader_pin_memory=True)
    started=time.time();trainer=Trainer(model=model,args=args,train_dataset=data,data_collator=Collator(tok.pad_token_id));result=trainer.train();trainer.save_state();model.save_pretrained(adapter);tok.save_pretrained(adapter)
    metrics=dict(result.metrics);metrics.update({"records":len(data),"trainable_parameters":trainable,"total_parameters":total,"elapsed_wall_seconds":time.time()-started,"adapter_path":str(adapter)})
    (run/"metrics/training.json").write_text(json.dumps(metrics,indent=2)+"\n");print(json.dumps(metrics,indent=2))
if __name__=="__main__": main()
