#!/usr/bin/env python3
"""Full-parameter causal-LM SFT for frozen PN-FP Ba QA."""

import argparse
import json
from pathlib import Path

import torch
from torch.utils.data import Dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments, set_seed


class SFTDataset(Dataset):
    def __init__(self, path, tokenizer, max_length):
        self.rows = [json.loads(line) for line in Path(path).open(encoding="utf-8") if line.strip()]
        self.tokenizer, self.max_length = tokenizer, max_length
    def __len__(self): return len(self.rows)
    def __getitem__(self, index):
        row = self.rows[index]
        user = row["instruction"] + (("\n\nInput:\n" + row["input"]) if row["input"] else "")
        prompt = self.tokenizer.apply_chat_template([{"role":"user","content":user}], tokenize=False, add_generation_prompt=True)
        full = self.tokenizer.apply_chat_template([{"role":"user","content":user},{"role":"assistant","content":row["teacher_raw_answer"]}], tokenize=False, add_generation_prompt=False)
        prompt_ids = self.tokenizer(prompt, add_special_tokens=False)["input_ids"]
        encoded = self.tokenizer(full, add_special_tokens=False, truncation=True, max_length=self.max_length)
        labels = encoded["input_ids"].copy()
        labels[:min(len(prompt_ids), len(labels))] = [-100] * min(len(prompt_ids), len(labels))
        return {"input_ids": encoded["input_ids"], "attention_mask": encoded["attention_mask"], "labels": labels}


class Collator:
    def __init__(self, tokenizer): self.tokenizer = tokenizer
    def __call__(self, features):
        width = max(len(x["input_ids"]) for x in features)
        result = {"input_ids": [], "attention_mask": [], "labels": []}
        for item in features:
            pad = width - len(item["input_ids"])
            result["input_ids"].append(item["input_ids"] + [self.tokenizer.pad_token_id] * pad)
            result["attention_mask"].append(item["attention_mask"] + [0] * pad)
            result["labels"].append(item["labels"] + [-100] * pad)
        return {key: torch.tensor(value) for key, value in result.items()}


def main():
    p=argparse.ArgumentParser(); p.add_argument("--model-path",required=True); p.add_argument("--dataset",required=True)
    p.add_argument("--output-dir",required=True); p.add_argument("--batch-size",type=int,default=8)
    p.add_argument("--epochs",type=int,default=3); p.add_argument("--learning-rate",type=float,default=1e-5)
    p.add_argument("--seed",type=int,default=42); p.add_argument("--max-length",type=int,default=1024)
    args=p.parse_args(); set_seed(args.seed)
    tokenizer=AutoTokenizer.from_pretrained(args.model_path,local_files_only=True); tokenizer.pad_token=tokenizer.pad_token or tokenizer.eos_token
    model=AutoModelForCausalLM.from_pretrained(args.model_path,local_files_only=True,torch_dtype=torch.bfloat16)
    model.config.use_cache=False; model.gradient_checkpointing_enable()
    dataset=SFTDataset(args.dataset,tokenizer,args.max_length)
    if len(dataset)!=20000: raise ValueError(f"formal Ba requires 20000 samples, found {len(dataset)}")
    training=TrainingArguments(output_dir=args.output_dir,num_train_epochs=args.epochs,learning_rate=args.learning_rate,
        per_device_train_batch_size=args.batch_size,gradient_accumulation_steps=1,bf16=True,fp16=False,
        save_strategy="epoch",save_total_limit=1,logging_steps=10,report_to=[],seed=args.seed,data_seed=args.seed,
        remove_unused_columns=False,gradient_checkpointing=True,optim="adamw_torch",lr_scheduler_type="cosine",
        warmup_ratio=0.03,weight_decay=0.0)
    trainer=Trainer(model=model,args=training,train_dataset=dataset,data_collator=Collator(tokenizer))
    trainer.train(); final=Path(args.output_dir)/"final_model"; trainer.save_model(final); tokenizer.save_pretrained(final)
    print(json.dumps({"status":"completed","checkpoint":str(final),"train_samples":len(dataset)}))

if __name__=="__main__": main()
