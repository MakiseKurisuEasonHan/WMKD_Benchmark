# EaaW — Experiment A

Run ID: `eaaw_a_20260905_111830_cont2`

## 科学目标

复现官方模型所有权信号，完成 Base、负对照、utility 与恢复验证。

## 论文与官方实现

```json
{
  "number": 11,
  "name": "EaaW",
  "paper": "https://arxiv.org/abs/2405.04825",
  "repo": "https://github.com/shaoshuo-ss/EaaW.git",
  "commit": "845432e24db227561e188af70e762d3c44d07475",
  "backbone": "openai-community/gpt2",
  "dataset": "ptb_text_only",
  "license": "MIT",
  "module": "eaaw"
}
```

## 方法语义与 Paper/code/runtime 配置

```json
{
  "model": "/root/autodl-tmp/WMKD_Benchmark_data/models/llmprint_validation/models/openai-community--gpt2/snapshots/master",
  "canonical_model": "openai-community/gpt2",
  "model_manifest": {
    ".gitattributes": {
      "size": 998,
      "sha256": "910c41f30c4c80595edecc4f433a28e29b0dcbdb492b4d48a9a0591b5ebe4396"
    },
    "64-8bits.tflite": {
      "size": 125162496,
      "sha256": "c966da3b74697803352ca7c6f2f220e7090a557b619de9da0c6b34d89f7825c1"
    },
    "64-fp16.tflite": {
      "size": 248269688,
      "sha256": "1ceafd82e733dd4b21570b2a86cf27556a983041806c033a55d086e0ed782cd3"
    },
    "64.tflite": {
      "size": 495791932,
      "sha256": "cfcd510b239d90b71ee87d4e57a5a8c2d55b2a941e5d9fe5852298268ddbe61b"
    },
    "README.md": {
      "size": 8092,
      "sha256": "0fcd631078093c2aa1d93438b898320b8a1167784e2a1ab37b8016e9de8b3c2e"
    },
    "config.json": {
      "size": 665,
      "sha256": "0daed7749b4f02b8f76240d5444551d7b08712dab4d0adb8239c56ba823bb7b4"
    },
    "configuration.json": {
      "size": 73,
      "sha256": "f888421726665e8a84b738eed42a64875aed79de8be7daade851ac8bf4c0cef9"
    },
    "flax_model.msgpack": {
      "size": 497764120,
      "sha256": "192e8257ae9e8f796f764630f4a488a6a16d1461762d62b49ef7405df951a283"
    },
    "generation_config.json": {
      "size": 124,
      "sha256": "ed0b32ac72c0f5f44a719abb2d7786ea5146c871f83717b7f2018065954de02b"
    },
    "merges.txt": {
      "size": 456318,
      "sha256": "1ce1664773c50f3e0cc8842619a93edc4624525b728b188a9e0be33b7726adc5"
    },
    "model.safetensors": {
      "size": 548105171,
      "sha256": "248dfc3911869ec493c76e65bf2fcf7f615828b0254c12b473182f0f81d3a707"
    },
    "pytorch_model.bin": {
      "size": 548118077,
      "sha256": "7c5d3f4b8b76583b422fcb9189ad6c89d5d97a094541ce8932dce3ecabde1421"
    },
    "rust_model.ot": {
      "size": 702517648,
      "sha256": "adf0adedbf4016b249550f866c66a3b3a3d09c8b3b3a1f6e5e9a265d94e0270e"
    },
    "tf_model.h5": {
      "size": 497933648,
      "sha256": "d08c1307f7dfae6f878e0a2ca5715d587d2640530db8ef96fc0c1fc474dd9fee"
    },
    "tokenizer.json": {
      "size": 1355256,
      "sha256": "8414cab924d8b9b33013f0d221c5862f365ee9be39c5c2bfae8a5a9e970478a6"
    },
    "tokenizer_config.json": {
      "size": 26,
      "sha256": "5e04eb606e3a1583530a42e36c2a6b6615c86f34fe77e44d9ddeb43ff940931f"
    },
    "vocab.json": {
      "size": 1042301,
      "sha256": "196139668be63f3b5d6574427317ae82f612a97c5d1cdaf36ed2256dbf636783"
    }
  },
  "dataset_files": {
    "train": {
      "path": "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/eaaw_a_20260905_111830_cont2/ptb/ptb_train.txt",
      "raw_path": "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/eaaw_a_20260905_111830_cont2/ptb/ptb_train.raw.txt",
      "raw_sha256": "fcea919f6cf83f35d4d00c6cbf08040d13d4155226340912e2fef9c9c4102cbf",
      "upstream": "https://raw.githubusercontent.com/wojzaremba/lstm/76870253cfca069477f06b7056af87f98490b6eb/data/ptb.train.txt",
      "transport": "https://ghfast.top/https://raw.githubusercontent.com/wojzaremba/lstm/76870253cfca069477f06b7056af87f98490b6eb/data/ptb.train.txt",
      "revision": "76870253cfca069477f06b7056af87f98490b6eb",
      "sha256": "5145926136ee9aef6f359b267ac09cc8a920879cd71725de17c490dd111d2998",
      "size": 5017482,
      "preprocessing": "Official ptb_text_only _generate_examples: line.strip()",
      "builder_source": "https://raw.githubusercontent.com/huggingface/datasets/1.18.4/datasets/ptb_text_only/ptb_text_only.py"
    },
    "valid": {
      "path": "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/eaaw_a_20260905_111830_cont2/ptb/ptb_valid.txt",
      "raw_path": "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/eaaw_a_20260905_111830_cont2/ptb/ptb_valid.raw.txt",
      "raw_sha256": "c9fe6985fe0d4ccb578183407d7668fc6066c20700cb4cf87d8ff1cc34df1bf2",
      "upstream": "https://raw.githubusercontent.com/wojzaremba/lstm/76870253cfca069477f06b7056af87f98490b6eb/data/ptb.valid.txt",
      "transport": "https://ghfast.top/https://raw.githubusercontent.com/wojzaremba/lstm/76870253cfca069477f06b7056af87f98490b6eb/data/ptb.valid.txt",
      "revision": "76870253cfca069477f06b7056af87f98490b6eb",
      "sha256": "fadf6277290823f881b7bf39b84e88536c87a859cd629dcfd1d2dfdef06097cf",
      "size": 393042,
      "preprocessing": "Official ptb_text_only _generate_examples: line.strip()",
      "builder_source": "https://raw.githubusercontent.com/huggingface/datasets/1.18.4/datasets/ptb_text_only/ptb_text_only.py"
    },
    "test": {
      "path": "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/eaaw_a_20260905_111830_cont2/ptb/ptb_test.txt",
      "raw_path": "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/eaaw_a_20260905_111830_cont2/ptb/ptb_test.raw.txt",
      "raw_sha256": "dd65dff31e70846b2a6030a87482edcd5d199130cdcfa1f3dccbb033728deee0",
      "upstream": "https://raw.githubusercontent.com/wojzaremba/lstm/76870253cfca069477f06b7056af87f98490b6eb/data/ptb.test.txt",
      "transport": "https://ghfast.top/https://raw.githubusercontent.com/wojzaremba/lstm/76870253cfca069477f06b7056af87f98490b6eb/data/ptb.test.txt",
      "revision": "76870253cfca069477f06b7056af87f98490b6eb",
      "sha256": "c2f8c16a611595d31da5acdb7a61d50e7d5e95f6b9c05fceda5f5ddc4383e791",
      "size": 442423,
      "preprocessing": "Official ptb_text_only _generate_examples: line.strip()",
      "builder_source": "https://raw.githubusercontent.com/huggingface/datasets/1.18.4/datasets/ptb_text_only/ptb_text_only.py"
    }
  },
  "ptb_upstream_revision": "76870253cfca069477f06b7056af87f98490b6eb",
  "official_script": "text-generation/scripts/gpt2.sh",
  "epochs": 20,
  "train_num_samples": 1000,
  "batch_size": 2,
  "effective_batch_size": 2,
  "learning_rate": 0.0003,
  "warmup_steps": 50,
  "alpha1": 1.0,
  "alpha2": 1.0,
  "wm_length": 128,
  "trigger_size": 1,
  "max_mask_token_size": 8,
  "seed": 42,
  "mixed_precision": "bf16",
  "gradient_checkpointing": true,
  "download_attempts": [],
  "model_prior_provenance": "results/llmprint/validation_negative_panel_manifest.json"
}
```

## 环境

```json
{
  "python": "3.11.16 (main, Aug 27 2026, 14:44:21) [GCC 14.3.0]",
  "torch": "2.8.0+cu128",
  "transformers": "4.55.2",
  "datasets": "3.6.0",
  "accelerate": "1.10.0",
  "scipy": "1.16.2",
  "cuda": "12.8",
  "gpu": "NVIDIA RTX PRO 6000 Blackwell Server Edition",
  "runtime_adaptation": "Reuse isolated WMKD scw Python3.11 environment, PyTorch2.8/cu128 for Blackwell; no modification of old environment."
}
```

## 模型与数据 provenance

```json
{
  "model": "/root/autodl-tmp/WMKD_Benchmark_data/models/llmprint_validation/models/openai-community--gpt2/snapshots/master",
  "canonical_model": "openai-community/gpt2",
  "model_manifest": {
    ".gitattributes": {
      "size": 998,
      "sha256": "910c41f30c4c80595edecc4f433a28e29b0dcbdb492b4d48a9a0591b5ebe4396"
    },
    "64-8bits.tflite": {
      "size": 125162496,
      "sha256": "c966da3b74697803352ca7c6f2f220e7090a557b619de9da0c6b34d89f7825c1"
    },
    "64-fp16.tflite": {
      "size": 248269688,
      "sha256": "1ceafd82e733dd4b21570b2a86cf27556a983041806c033a55d086e0ed782cd3"
    },
    "64.tflite": {
      "size": 495791932,
      "sha256": "cfcd510b239d90b71ee87d4e57a5a8c2d55b2a941e5d9fe5852298268ddbe61b"
    },
    "README.md": {
      "size": 8092,
      "sha256": "0fcd631078093c2aa1d93438b898320b8a1167784e2a1ab37b8016e9de8b3c2e"
    },
    "config.json": {
      "size": 665,
      "sha256": "0daed7749b4f02b8f76240d5444551d7b08712dab4d0adb8239c56ba823bb7b4"
    },
    "configuration.json": {
      "size": 73,
      "sha256": "f888421726665e8a84b738eed42a64875aed79de8be7daade851ac8bf4c0cef9"
    },
    "flax_model.msgpack": {
      "size": 497764120,
      "sha256": "192e8257ae9e8f796f764630f4a488a6a16d1461762d62b49ef7405df951a283"
    },
    "generation_config.json": {
      "size": 124,
      "sha256": "ed0b32ac72c0f5f44a719abb2d7786ea5146c871f83717b7f2018065954de02b"
    },
    "merges.txt": {
      "size": 456318,
      "sha256": "1ce1664773c50f3e0cc8842619a93edc4624525b728b188a9e0be33b7726adc5"
    },
    "model.safetensors": {
      "size": 548105171,
      "sha256": "248dfc3911869ec493c76e65bf2fcf7f615828b0254c12b473182f0f81d3a707"
    },
    "pytorch_model.bin": {
      "size": 548118077,
      "sha256": "7c5d3f4b8b76583b422fcb9189ad6c89d5d97a094541ce8932dce3ecabde1421"
    },
    "rust_model.ot": {
      "size": 702517648,
      "sha256": "adf0adedbf4016b249550f866c66a3b3a3d09c8b3b3a1f6e5e9a265d94e0270e"
    },
    "tf_model.h5": {
      "size": 497933648,
      "sha256": "d08c1307f7dfae6f878e0a2ca5715d587d2640530db8ef96fc0c1fc474dd9fee"
    },
    "tokenizer.json": {
      "size": 1355256,
      "sha256": "8414cab924d8b9b33013f0d221c5862f365ee9be39c5c2bfae8a5a9e970478a6"
    },
    "tokenizer_config.json": {
      "size": 26,
      "sha256": "5e04eb606e3a1583530a42e36c2a6b6615c86f34fe77e44d9ddeb43ff940931f"
    },
    "vocab.json": {
      "size": 1042301,
      "sha256": "196139668be63f3b5d6574427317ae82f612a97c5d1cdaf36ed2256dbf636783"
    }
  },
  "dataset_files": {
    "train": {
      "path": "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/eaaw_a_20260905_111830_cont2/ptb/ptb_train.txt",
      "raw_path": "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/eaaw_a_20260905_111830_cont2/ptb/ptb_train.raw.txt",
      "raw_sha256": "fcea919f6cf83f35d4d00c6cbf08040d13d4155226340912e2fef9c9c4102cbf",
      "upstream": "https://raw.githubusercontent.com/wojzaremba/lstm/76870253cfca069477f06b7056af87f98490b6eb/data/ptb.train.txt",
      "transport": "https://ghfast.top/https://raw.githubusercontent.com/wojzaremba/lstm/76870253cfca069477f06b7056af87f98490b6eb/data/ptb.train.txt",
      "revision": "76870253cfca069477f06b7056af87f98490b6eb",
      "sha256": "5145926136ee9aef6f359b267ac09cc8a920879cd71725de17c490dd111d2998",
      "size": 5017482,
      "preprocessing": "Official ptb_text_only _generate_examples: line.strip()",
      "builder_source": "https://raw.githubusercontent.com/huggingface/datasets/1.18.4/datasets/ptb_text_only/ptb_text_only.py"
    },
    "valid": {
      "path": "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/eaaw_a_20260905_111830_cont2/ptb/ptb_valid.txt",
      "raw_path": "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/eaaw_a_20260905_111830_cont2/ptb/ptb_valid.raw.txt",
      "raw_sha256": "c9fe6985fe0d4ccb578183407d7668fc6066c20700cb4cf87d8ff1cc34df1bf2",
      "upstream": "https://raw.githubusercontent.com/wojzaremba/lstm/76870253cfca069477f06b7056af87f98490b6eb/data/ptb.valid.txt",
      "transport": "https://ghfast.top/https://raw.githubusercontent.com/wojzaremba/lstm/76870253cfca069477f06b7056af87f98490b6eb/data/ptb.valid.txt",
      "revision": "76870253cfca069477f06b7056af87f98490b6eb",
      "sha256": "fadf6277290823f881b7bf39b84e88536c87a859cd629dcfd1d2dfdef06097cf",
      "size": 393042,
      "preprocessing": "Official ptb_text_only _generate_examples: line.strip()",
      "builder_source": "https://raw.githubusercontent.com/huggingface/datasets/1.18.4/datasets/ptb_text_only/ptb_text_only.py"
    },
    "test": {
      "path": "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/eaaw_a_20260905_111830_cont2/ptb/ptb_test.txt",
      "raw_path": "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/eaaw_a_20260905_111830_cont2/ptb/ptb_test.raw.txt",
      "raw_sha256": "dd65dff31e70846b2a6030a87482edcd5d199130cdcfa1f3dccbb033728deee0",
      "upstream": "https://raw.githubusercontent.com/wojzaremba/lstm/76870253cfca069477f06b7056af87f98490b6eb/data/ptb.test.txt",
      "transport": "https://ghfast.top/https://raw.githubusercontent.com/wojzaremba/lstm/76870253cfca069477f06b7056af87f98490b6eb/data/ptb.test.txt",
      "revision": "76870253cfca069477f06b7056af87f98490b6eb",
      "sha256": "c2f8c16a611595d31da5acdb7a61d50e7d5e95f6b9c05fceda5f5ddc4383e791",
      "size": 442423,
      "preprocessing": "Official ptb_text_only _generate_examples: line.strip()",
      "builder_source": "https://raw.githubusercontent.com/huggingface/datasets/1.18.4/datasets/ptb_text_only/ptb_text_only.py"
    }
  },
  "ptb_upstream_revision": "76870253cfca069477f06b7056af87f98490b6eb",
  "official_script": "text-generation/scripts/gpt2.sh",
  "epochs": 20,
  "train_num_samples": 1000,
  "batch_size": 2,
  "effective_batch_size": 2,
  "learning_rate": 0.0003,
  "warmup_steps": 50,
  "alpha1": 1.0,
  "alpha2": 1.0,
  "wm_length": 128,
  "trigger_size": 1,
  "max_mask_token_size": 8,
  "seed": 42,
  "mixed_precision": "bf16",
  "gradient_checkpointing": true,
  "download_attempts": [],
  "model_prior_provenance": "results/llmprint/validation_negative_panel_manifest.json"
}
```

## 训练结果与运行时间

```json
{
  "status": "SUCCESS",
  "stage": "TRAINING",
  "attempt": 1,
  "completed_at": "2026-09-06T00:11:38.583184+00:00",
  "runtime_seconds": 22416.989418007433,
  "required_child_processes_exit_code": 0,
  "outputs": {
    "model": "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/eaaw_a_20260905_111830_cont2/model_attempt_1",
    "eval_tokens": "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/eaaw_a_20260905_111830_cont2/eval_tokens_1",
    "trigger": "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/eaaw_a_20260905_111830_cont2/trigger.json",
    "command": [
      "/root/autodl-tmp/WMKD_Benchmark_data/artifacts/scw/env_py311/bin/python",
      "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/eaaw_a_20260905_111830_cont2/work/text-generation/run_clm.py",
      "--model_name_or_path",
      "/root/autodl-tmp/WMKD_Benchmark_data/models/llmprint_validation/models/openai-community--gpt2/snapshots/master",
      "--train_file",
      "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/eaaw_a_20260905_111830_cont2/ptb/ptb_train.txt",
      "--validation_file",
      "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/eaaw_a_20260905_111830_cont2/ptb/ptb_valid.txt",
      "--per_device_train_batch_size",
      "2",
      "--per_device_eval_batch_size",
      "2",
      "--num_train_epochs",
      "20",
      "--learning_rate",
      "3e-4",
      "--num_warmup_steps",
      "50",
      "--alpha1",
      "1.0",
      "--alpha2",
      "1.0",
      "--low_cpu_mem_usage",
      "--output_dir",
      "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/eaaw_a_20260905_111830_cont2/model_attempt_1",
      "--train_num_samples",
      "1000",
      "--mode",
      "wm",
      "--max_mask_token_size",
      "8",
      "--do_train",
      "--wm_length",
      "128",
      "--trigger_size",
      "1",
      "--manual_dataset_name",
      "ptb-text-only",
      "--seed",
      "42"
    ],
    "steps": 10000,
    "peak_vram_bytes": 22203324416,
    "config": {
      "model": "/root/autodl-tmp/WMKD_Benchmark_data/models/llmprint_validation/models/openai-community--gpt2/snapshots/master",
      "canonical_model": "openai-community/gpt2",
      "model_manifest": {
        ".gitattributes": {
          "size": 998,
          "sha256": "910c41f30c4c80595edecc4f433a28e29b0dcbdb492b4d48a9a0591b5ebe4396"
        },
        "64-8bits.tflite": {
          "size": 125162496,
          "sha256": "c966da3b74697803352ca7c6f2f220e7090a557b619de9da0c6b34d89f7825c1"
        },
        "64-fp16.tflite": {
          "size": 248269688,
          "sha256": "1ceafd82e733dd4b21570b2a86cf27556a983041806c033a55d086e0ed782cd3"
        },
        "64.tflite": {
          "size": 495791932,
          "sha256": "cfcd510b239d90b71ee87d4e57a5a8c2d55b2a941e5d9fe5852298268ddbe61b"
        },
        "README.md": {
          "size": 8092,
          "sha256": "0fcd631078093c2aa1d93438b898320b8a1167784e2a1ab37b8016e9de8b3c2e"
        },
        "config.json": {
          "size": 665,
          "sha256": "0daed7749b4f02b8f76240d5444551d7b08712dab4d0adb8239c56ba823bb7b4"
        },
        "configuration.json": {
          "size": 73,
          "sha256": "f888421726665e8a84b738eed42a64875aed79de8be7daade851ac8bf4c0cef9"
        },
        "flax_model.msgpack": {
          "size": 497764120,
          "sha256": "192e8257ae9e8f796f764630f4a488a6a16d1461762d62b49ef7405df951a283"
        },
        "generation_config.json": {
          "size": 124,
          "sha256": "ed0b32ac72c0f5f44a719abb2d7786ea5146c871f83717b7f2018065954de02b"
        },
        "merges.txt": {
          "size": 456318,
          "sha256": "1ce1664773c50f3e0cc8842619a93edc4624525b728b188a9e0be33b7726adc5"
        },
        "model.safetensors": {
          "size": 548105171,
          "sha256": "248dfc3911869ec493c76e65bf2fcf7f615828b0254c12b473182f0f81d3a707"
        },
        "pytorch_model.bin": {
          "size": 548118077,
          "sha256": "7c5d3f4b8b76583b422fcb9189ad6c89d5d97a094541ce8932dce3ecabde1421"
        },
        "rust_model.ot": {
          "size": 702517648,
          "sha256": "adf0adedbf4016b249550f866c66a3b3a3d09c8b3b3a1f6e5e9a265d94e0270e"
        },
        "tf_model.h5": {
          "size": 497933648,
          "sha256": "d08c1307f7dfae6f878e0a2ca5715d587d2640530db8ef96fc0c1fc474dd9fee"
        },
        "tokenizer.json": {
          "size": 1355256,
          "sha256": "8414cab924d8b9b33013f0d221c5862f365ee9be39c5c2bfae8a5a9e970478a6"
        },
        "tokenizer_config.json": {
          "size": 26,
          "sha256": "5e04eb606e3a1583530a42e36c2a6b6615c86f34fe77e44d9ddeb43ff940931f"
        },
        "vocab.json": {
          "size": 1042301,
          "sha256": "196139668be63f3b5d6574427317ae82f612a97c5d1cdaf36ed2256dbf636783"
        }
      },
      "dataset_files": {
        "train": {
          "path": "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/eaaw_a_20260905_111830_cont2/ptb/ptb_train.txt",
          "raw_path": "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/eaaw_a_20260905_111830_cont2/ptb/ptb_train.raw.txt",
          "raw_sha256": "fcea919f6cf83f35d4d00c6cbf08040d13d4155226340912e2fef9c9c4102cbf",
          "upstream": "https://raw.githubusercontent.com/wojzaremba/lstm/76870253cfca069477f06b7056af87f98490b6eb/data/ptb.train.txt",
          "transport": "https://ghfast.top/https://raw.githubusercontent.com/wojzaremba/lstm/76870253cfca069477f06b7056af87f98490b6eb/data/ptb.train.txt",
          "revision": "76870253cfca069477f06b7056af87f98490b6eb",
          "sha256": "5145926136ee9aef6f359b267ac09cc8a920879cd71725de17c490dd111d2998",
          "size": 5017482,
          "preprocessing": "Official ptb_text_only _generate_examples: line.strip()",
          "builder_source": "https://raw.githubusercontent.com/huggingface/datasets/1.18.4/datasets/ptb_text_only/ptb_text_only.py"
        },
        "valid": {
          "path": "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/eaaw_a_20260905_111830_cont2/ptb/ptb_valid.txt",
          "raw_path": "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/eaaw_a_20260905_111830_cont2/ptb/ptb_valid.raw.txt",
          "raw_sha256": "c9fe6985fe0d4ccb578183407d7668fc6066c20700cb4cf87d8ff1cc34df1bf2",
          "upstream": "https://raw.githubusercontent.com/wojzaremba/lstm/76870253cfca069477f06b7056af87f98490b6eb/data/ptb.valid.txt",
          "transport": "https://ghfast.top/https://raw.githubusercontent.com/wojzaremba/lstm/76870253cfca069477f06b7056af87f98490b6eb/data/ptb.valid.txt",
          "revision": "76870253cfca069477f06b7056af87f98490b6eb",
          "sha256": "fadf6277290823f881b7bf39b84e88536c87a859cd629dcfd1d2dfdef06097cf",
          "size": 393042,
          "preprocessing": "Official ptb_text_only _generate_examples: line.strip()",
          "builder_source": "https://raw.githubusercontent.com/huggingface/datasets/1.18.4/datasets/ptb_text_only/ptb_text_only.py"
        },
        "test": {
          "path": "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/eaaw_a_20260905_111830_cont2/ptb/ptb_test.txt",
          "raw_path": "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/eaaw_a_20260905_111830_cont2/ptb/ptb_test.raw.txt",
          "raw_sha256": "dd65dff31e70846b2a6030a87482edcd5d199130cdcfa1f3dccbb033728deee0",
          "upstream": "https://raw.githubusercontent.com/wojzaremba/lstm/76870253cfca069477f06b7056af87f98490b6eb/data/ptb.test.txt",
          "transport": "https://ghfast.top/https://raw.githubusercontent.com/wojzaremba/lstm/76870253cfca069477f06b7056af87f98490b6eb/data/ptb.test.txt",
          "revision": "76870253cfca069477f06b7056af87f98490b6eb",
          "sha256": "c2f8c16a611595d31da5acdb7a61d50e7d5e95f6b9c05fceda5f5ddc4383e791",
          "size": 442423,
          "preprocessing": "Official ptb_text_only _generate_examples: line.strip()",
          "builder_source": "https://raw.githubusercontent.com/huggingface/datasets/1.18.4/datasets/ptb_text_only/ptb_text_only.py"
        }
      },
      "ptb_upstream_revision": "76870253cfca069477f06b7056af87f98490b6eb",
      "official_script": "text-generation/scripts/gpt2.sh",
      "epochs": 20,
      "train_num_samples": 1000,
      "batch_size": 2,
      "effective_batch_size": 2,
      "learning_rate": 0.0003,
      "warmup_steps": 50,
      "alpha1": 1.0,
      "alpha2": 1.0,
      "wm_length": 128,
      "trigger_size": 1,
      "max_mask_token_size": 8,
      "seed": 42,
      "mixed_precision": "bf16",
      "gradient_checkpointing": true,
      "download_attempts": [],
      "model_prior_provenance": "results/llmprint/validation_negative_panel_manifest.json"
    },
    "telemetry": {
      "peak_gpu_used_bytes": 25150095360,
      "source": "nvidia-smi total used memory sampled every10s; serial GPU scope"
    }
  }
}
```

## 检测与负对照

```json
{
  "status": "SUCCESS",
  "stage": "DETECTOR",
  "attempt": 1,
  "completed_at": "2026-09-06T00:11:51.577726+00:00",
  "runtime_seconds": 5.193726897239685,
  "required_child_processes_exit_code": 0,
  "outputs": {
    "base": {
      "bit_accuracy": 0.4453125,
      "matched_bits": 57,
      "total_bits": 128,
      "extracted_bits": [
        -1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        -1.0,
        -1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        -1.0,
        -1.0,
        -1.0,
        1.0,
        -1.0,
        1.0,
        1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        1.0,
        1.0,
        1.0,
        1.0
      ],
      "chi2_statistic": 1.0941422496978053,
      "p_value": 0.2955552392642641,
      "chi2_status": "defined"
    },
    "watermarked": {
      "bit_accuracy": 1.0,
      "matched_bits": 128,
      "total_bits": 128,
      "extracted_bits": [
        -1.0,
        1.0,
        -1.0,
        -1.0,
        -1.0,
        1.0,
        -1.0,
        -1.0,
        -1.0,
        1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        1.0,
        -1.0,
        1.0,
        1.0,
        1.0,
        -1.0,
        1.0,
        -1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        -1.0,
        -1.0,
        1.0,
        1.0,
        1.0,
        -1.0,
        1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        -1.0,
        1.0,
        1.0,
        -1.0,
        1.0,
        -1.0,
        1.0,
        -1.0,
        1.0,
        1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        1.0,
        1.0,
        -1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        -1.0,
        1.0,
        -1.0,
        1.0,
        1.0,
        1.0,
        -1.0,
        1.0,
        -1.0,
        1.0,
        -1.0,
        1.0,
        -1.0,
        -1.0,
        1.0,
        -1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        -1.0,
        -1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        -1.0,
        1.0,
        -1.0,
        1.0,
        1.0,
        -1.0,
        1.0,
        -1.0,
        1.0,
        1.0,
        -1.0,
        1.0,
        -1.0,
        1.0,
        -1.0,
        -1.0,
        1.0,
        1.0,
        -1.0
      ],
      "chi2_statistic": 123.93273353433514,
      "p_value": 8.714844596883318e-29,
      "chi2_status": "defined"
    },
    "negative_controls": {
      "type": "independent trigger from held-out validation, same target key; Base also reported",
      "independent_trigger": {
        "bit_accuracy": 0.5859375,
        "matched_bits": 75,
        "total_bits": 128,
        "extracted_bits": [
          1.0,
          -1.0,
          -1.0,
          -1.0,
          -1.0,
          -1.0,
          -1.0,
          -1.0,
          -1.0,
          -1.0,
          -1.0,
          -1.0,
          -1.0,
          -1.0,
          -1.0,
          -1.0,
          -1.0,
          -1.0,
          -1.0,
          -1.0,
          -1.0,
          -1.0,
          -1.0,
          -1.0,
          1.0,
          1.0,
          -1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          -1.0,
          -1.0,
          -1.0,
          1.0,
          1.0,
          -1.0,
          -1.0,
          -1.0,
          -1.0,
          -1.0,
          -1.0,
          -1.0,
          -1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          -1.0,
          1.0,
          -1.0,
          -1.0,
          1.0,
          -1.0,
          -1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          -1.0,
          1.0,
          -1.0,
          -1.0,
          1.0,
          -1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          -1.0,
          -1.0,
          -1.0,
          -1.0,
          -1.0,
          -1.0,
          -1.0,
          -1.0,
          -1.0,
          -1.0,
          -1.0,
          -1.0,
          -1.0,
          -1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          -1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          -1.0,
          1.0,
          1.0,
          1.0,
          -1.0,
          1.0,
          -1.0,
          1.0,
          1.0,
          1.0,
          -1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          1.0
        ],
        "chi2_statistic": 3.1046431046431047,
        "p_value": 0.078069340408631,
        "chi2_status": "defined"
      },
      "supplementary_wrong_key": {
        "seed": 20260905,
        "bit_accuracy": 0.5,
        "matched_bits": 64,
        "total_bits": 128,
        "extracted_bits": [
          -1.0,
          1.0,
          -1.0,
          -1.0,
          -1.0,
          1.0,
          -1.0,
          -1.0,
          -1.0,
          1.0,
          -1.0,
          -1.0,
          -1.0,
          -1.0,
          1.0,
          -1.0,
          1.0,
          1.0,
          1.0,
          -1.0,
          1.0,
          -1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          -1.0,
          -1.0,
          1.0,
          1.0,
          1.0,
          -1.0,
          1.0,
          -1.0,
          -1.0,
          -1.0,
          -1.0,
          -1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          -1.0,
          1.0,
          1.0,
          -1.0,
          1.0,
          -1.0,
          1.0,
          -1.0,
          1.0,
          1.0,
          -1.0,
          -1.0,
          -1.0,
          -1.0,
          -1.0,
          -1.0,
          -1.0,
          -1.0,
          1.0,
          1.0,
          -1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          -1.0,
          1.0,
          -1.0,
          1.0,
          1.0,
          1.0,
          -1.0,
          1.0,
          -1.0,
          1.0,
          -1.0,
          1.0,
          -1.0,
          -1.0,
          1.0,
          -1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          -1.0,
          -1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          1.0,
          -1.0,
          1.0,
          -1.0,
          1.0,
          1.0,
          -1.0,
          1.0,
          -1.0,
          1.0,
          1.0,
          -1.0,
          1.0,
          -1.0,
          1.0,
          -1.0,
          -1.0,
          1.0,
          1.0,
          -1.0
        ],
        "chi2_statistic": 0.0,
        "p_value": 1.0,
        "chi2_status": "defined",
        "wrong_key_sha256": "eed4d59abb838a233ff4b13b03ab7589300cd9da2c0d112cbe7e03a47bb66619"
      }
    },
    "official_alpha": 0.01,
    "metric": "official bit accuracy and chi-square p-value",
    "scientific_status": "CORE_REPRODUCTION_SUCCESSFUL",
    "judgement_scope": "Official paper Section V alpha=0.01, no threshold tuning; report WSR and controls separately, utility separately."
  }
}
```

## Utility 与 Base 差值

```json
{
  "status": "SUCCESS",
  "stage": "UTILITY",
  "attempt": 1,
  "completed_at": "2026-09-06T00:12:14.114682+00:00",
  "runtime_seconds": 7.607161533087492,
  "required_child_processes_exit_code": 0,
  "outputs": {
    "base": {
      "loss": 4.642741359065802,
      "perplexity": 103.82858924546228,
      "blocks": 698,
      "block_size": 128
    },
    "watermarked": {
      "loss": 3.801581281645592,
      "perplexity": 44.77192557192051,
      "blocks": 698,
      "block_size": 128
    },
    "metric": "PTB validation causal-LM loss and perplexity",
    "delta": {
      "loss": -0.8411600774202102,
      "perplexity": -59.05666367354177
    }
  }
}
```

## Reload 验证

```json
{
  "status": "SUCCESS",
  "stage": "RELOAD_VERIFIED",
  "attempt": 1,
  "completed_at": "2026-09-06T00:12:31.499984+00:00",
  "runtime_seconds": 4.8029224164783955,
  "required_child_processes_exit_code": 0,
  "outputs": {
    "status": "PASS",
    "fresh_process": true,
    "all_parameters_finite": true,
    "sample": "The meaning of life is that we are all united in our common purpose of making the world a better place",
    "files": {
      "all_results.json": {
        "size": 44,
        "sha256": "09ea72b93f03345c14db09bbf4ac153463c12a998a1aa1f801b825ba62a000bc"
      },
      "args.json": {
        "size": 1719,
        "sha256": "1610fe1171ad5382ef6fe797771e43f7c0b79452af5f53ee7befe860c26f6516"
      },
      "config.json": {
        "size": 881,
        "sha256": "5350e9655c01c574313d991ba9e67509444ba1d27a15ba12a22e39c543825fb7"
      },
      "generation_config.json": {
        "size": 119,
        "sha256": "7e9551f88df59ec6a88779ae2c001a8798be69a26f189717728d6436808f1d49"
      },
      "log.log": {
        "size": 5069,
        "sha256": "0eef0b9d74625364b1a9907879d37d52fc25abecbdff93829ceba33524f3b3d8"
      },
      "merges.txt": {
        "size": 456318,
        "sha256": "1ce1664773c50f3e0cc8842619a93edc4624525b728b188a9e0be33b7726adc5"
      },
      "model.safetensors": {
        "size": 497774208,
        "sha256": "b1ae4c6064bbd60f95da09002fffa91c64a16d16c27ddcfb84711351182defe3"
      },
      "special_tokens_map.json": {
        "size": 99,
        "sha256": "6f50ab5a5a509a1c309d6171f339b196a900dc9c99ad0408ff23bb615fdae7ad"
      },
      "tokenizer.json": {
        "size": 3557680,
        "sha256": "1fe93b6152957cf9cfd6d89002467f789ce8b3f3e000b3a2edf27c808ddd0b9e"
      },
      "tokenizer_config.json": {
        "size": 475,
        "sha256": "f1cb5e31899749cf30935ccea01180ab3cfd484bd2bcf3bfdc1aeb9fdf935f6f"
      },
      "vocab.json": {
        "size": 798156,
        "sha256": "3ba3c3109ff33976c4bd966589c11ee14fcaa1f4c9e5e154c2ed7f99d80709e7"
      },
      "watermark.txt": {
        "size": 310,
        "sha256": "a60c79a1010fae5694597ad5e2b47dcc5c789d4d31c6c401fbca8713b5d01f43"
      }
    }
  }
}
```

## 兼容性修复

```json
{
  "repair_history": [
    {
      "time": "2026-09-05T11:30:43.997567+00:00",
      "action": "Use fixed official Git bundle after remote HTTPS failure; no training had started.",
      "previous_run_id": "eaaw_a_20260905_111830",
      "preserved_full_log": "/root/autodl-tmp/WMKD_Benchmark/results/methods_11_15/eaaw/experiment_a/history/eaaw_a_20260905_111830/full_experiment_log.json"
    },
    {
      "time": "2026-09-05T11:38:42.689432+00:00",
      "action": "Resolve verified local GPT-2 snapshot directory; retain official source bundle transport; no training had started.",
      "previous_run_id": "eaaw_a_20260905_111830_cont1",
      "preserved_full_log": "/root/autodl-tmp/WMKD_Benchmark/results/methods_11_15/eaaw/experiment_a/history/eaaw_a_20260905_111830_cont1/full_experiment_log.json"
    },
    {
      "action": "Accelerate renamed DistributedType.TPU to XLA; GPU branch unchanged",
      "category": "API compatibility",
      "scientific_change": false,
      "stage": "TRAINING",
      "attempt": 1,
      "time": "2026-09-05T11:43:09.023505+00:00",
      "retained_report": "/root/autodl-tmp/WMKD_Benchmark/results/methods_11_15/eaaw/experiment_a/versions/eaaw_a_20260905_111830_cont1_cont1_TRAINING_1"
    },
    {
      "time": "2026-09-05T17:56:34.697643+00:00",
      "action": "Retain completed diagnostic checkpoint and all evidence; start equivalent official data-adapter continuation",
      "details": {
        "safe_action": "If not explicitly approved to interrupt, retain full current training progress and checkpoint; after natural completion automatically start eaaw_a_20260905_111830_cont2 with official preprocessing.",
        "official_builder": "https://raw.githubusercontent.com/huggingface/datasets/1.18.4/datasets/ptb_text_only/ptb_text_only.py",
        "approval_state": "Interruption rejected by automatic review; explicit user question pending.",
        "reason": "Official ptb_text_only applies line.strip(); current local text loading retained leading and trailing whitespace. This run must not be accepted as canonical Experiment A.",
        "time": "2026-09-05T12:30:55.6061213Z"
      }
    }
  ],
  "patch": "--- official/run_clm.py\n+++ wmkd/run_clm.py\n@@ -56,12 +56,7 @@\n \n def main():\n     args = parse_args()\n-    args.output_dir = os.path.join(\n-        args.output_dir,\n-        args.dataset_name if args.dataset_name is not None else args.manual_dataset_name,\n-        args.mode,\n-        datetime.datetime.now().strftime(\"%Y-%m-%d-%H:%M:%S\")\n-    )\n+    args.output_dir = os.environ[\"WMKD_MODEL_OUTPUT\"]\n     # Initialize the accelerator. We will let the accelerator handle device placement for us in this example.\n     # If we're using tracking, we also need to initialize it here and it will by default pick up all supported trackers\n     # in the environment\n@@ -208,6 +203,8 @@\n \n     # We resize the embeddings only when necessary to avoid index errors. If you are creating a model from scratch\n     # on a small vocab and want a smaller embedding size, remove this test.\n+    model.gradient_checkpointing_enable()\n+    model.config.use_cache = False\n     embedding_size = model.get_input_embeddings().weight.shape[0]\n     if len(tokenizer) > embedding_size:\n         model.resize_token_embeddings(len(tokenizer))\n@@ -280,6 +277,8 @@\n \n     train_dataset = lm_datasets[\"train\"]\n     eval_dataset = lm_datasets[\"validation\"]\n+    eval_dataset.save_to_disk(os.environ[\"WMKD_EVAL_TOKENS\"])\n+    with open(os.environ[\"WMKD_TRIGGER\"], \"w\") as f: json.dump(train_dataset[0], f)\n     if args.train_num_samples is not None:\n         # check if we have enough samples for the training set\n         if args.train_num_samples > len(train_dataset):\n@@ -336,7 +335,7 @@\n     )\n \n     # On TPU, the tie weights in our model have been disconnected, so we need to restore the ties.\n-    if accelerator.distributed_type == DistributedType.TPU:\n+    if accelerator.distributed_type == DistributedType.XLA:\n         model.tie_weights()\n \n     # We need to recalculate our total training steps as the size of the training dataloader may have changed.\n@@ -464,6 +463,8 @@\n                 if accelerator.sync_gradients:\n                     progress_bar.update(1)\n                     completed_steps += 1\n+                    if completed_steps % 10 == 0:\n+                        with open(os.environ[\"WMKD_TRAIN_PROGRESS\"], \"a\") as f: f.write(json.dumps({\"step\": completed_steps, \"epoch\": epoch, \"loss\": float(loss.detach()), \"peak_vram_bytes\": torch.cuda.max_memory_allocated()}) + \"\\n\")\n \n                 if isinstance(checkpointing_steps, int):\n                     if completed_steps % checkpointing_steps == 0:\n--- official/watermark.py\n+++ wmkd/watermark.py\n@@ -157,6 +157,6 @@\n     zero_weights[zero_weights == -1] = 0\n     options = [1, 0]\n     cross_table = crosstab(zero_weights, zero_target, levels=(options, options))\n-    stats = chi2_contingency(cross_table)\n+    stats = chi2_contingency(cross_table.count)\n     \n     return 1 - ber, stats\n"
}
```

## 科学判断与限制

```json
{
  "status": "BLOCKED_ARCHIVE",
  "last_error": "PRIVATE archive failed; canonical local model retained: [{'workers': 4, 'error': \"Command '['/root/autodl-tmp/WMKD_Benchmark_data/artifacts/modelscope_cli_env/bin/python', '/root/autodl-tmp/WMKD_Benchmark/scripts/methods_11_15/archive.py', '/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/eaaw_a_20260905_111830_cont2/archive_request.json', '4']' returned non-zero exit status 1.\"}, {'workers': 1, 'error': \"Command '['/root/autodl-tmp/WMKD_Benchmark_data/artifacts/modelscope_cli_env/bin/python', '/root/autodl-tmp/WMKD_Benchmark/scripts/methods_11_15/archive.py', '/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/eaaw_a_20260905_111830_cont2/archive_request.json', '1']' returned non-zero exit status 1.\"}]",
  "limitations": [
    "Single official supported configuration; no Ba/Bb/distillation.",
    "Missing results are NOT_RUN; infrastructure blocks do not establish method failure."
  ]
}
```

## 归档与恢复

NOT_RUN

完整日志：[full_experiment_log.json](../../results/methods_11_15/eaaw/experiment_a/full_experiment_log.json)。
