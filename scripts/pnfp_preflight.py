#!/usr/bin/env python3
"""Minimum runtime preflight for PN-FP Experiment A."""

import argparse
import json
import os
from pathlib import Path
import subprocess

import torch
from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer


parser = argparse.ArgumentParser()
parser.add_argument("--runtime-config", required=True)
args = parser.parse_args()
c = json.loads(Path(args.runtime_config).read_text())
model_path = c["paths"]["model"]

assert torch.cuda.is_available() and torch.cuda.is_bf16_supported()
assert torch.cuda.device_count() == 1
free, total = torch.cuda.mem_get_info()
assert free > 80 * 1024**3, f"Insufficient free VRAM: {free}"
disk = os.statvfs(c["paths"]["data_root"])
assert disk.f_bavail * disk.f_frsize > 100 * 1024**3
assert subprocess.check_output(["git", "-C", c["paths"]["official_source"], "rev-parse", "HEAD"], text=True).strip() == c["source_commit"]

cfg = AutoConfig.from_pretrained(model_path, local_files_only=True)
tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
assert cfg.model_type == "llama" and tokenizer.chat_template
model = AutoModelForCausalLM.from_pretrained(model_path, local_files_only=True, torch_dtype=torch.bfloat16)
total_params = sum(p.numel() for p in model.parameters())
trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
assert total_params == trainable_params and total_params > 3_000_000_000
serialized = tokenizer.apply_chat_template([{"role": "user", "content": "PN-FP preflight"}], add_generation_prompt=True, tokenize=False)
assert serialized
print(json.dumps({"bf16": True, "gpu": torch.cuda.get_device_name(0), "free_vram_bytes": free,
                  "model_type": cfg.model_type, "total_parameters": total_params,
                  "trainable_parameters": trainable_params, "all_parameters_trainable": True,
                  "chat_template_active": True, "runtime_config": c["formal_config"]}, indent=2))
