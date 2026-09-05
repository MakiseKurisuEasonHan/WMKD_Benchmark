# EaaW — Experiment A

Run ID: `eaaw_a_20260905_111830_cont1_cont1`

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
      "path": "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/eaaw_a_20260905_111830_cont1_cont1/ptb/ptb_train.txt",
      "upstream": "https://raw.githubusercontent.com/wojzaremba/lstm/76870253cfca069477f06b7056af87f98490b6eb/data/ptb.train.txt",
      "transport": "https://ghfast.top/https://raw.githubusercontent.com/wojzaremba/lstm/76870253cfca069477f06b7056af87f98490b6eb/data/ptb.train.txt",
      "revision": "76870253cfca069477f06b7056af87f98490b6eb",
      "sha256": "fcea919f6cf83f35d4d00c6cbf08040d13d4155226340912e2fef9c9c4102cbf",
      "size": 5101618
    },
    "valid": {
      "path": "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/eaaw_a_20260905_111830_cont1_cont1/ptb/ptb_valid.txt",
      "upstream": "https://raw.githubusercontent.com/wojzaremba/lstm/76870253cfca069477f06b7056af87f98490b6eb/data/ptb.valid.txt",
      "transport": "https://ghfast.top/https://raw.githubusercontent.com/wojzaremba/lstm/76870253cfca069477f06b7056af87f98490b6eb/data/ptb.valid.txt",
      "revision": "76870253cfca069477f06b7056af87f98490b6eb",
      "sha256": "c9fe6985fe0d4ccb578183407d7668fc6066c20700cb4cf87d8ff1cc34df1bf2",
      "size": 399782
    },
    "test": {
      "path": "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/eaaw_a_20260905_111830_cont1_cont1/ptb/ptb_test.txt",
      "upstream": "https://raw.githubusercontent.com/wojzaremba/lstm/76870253cfca069477f06b7056af87f98490b6eb/data/ptb.test.txt",
      "transport": "https://ghfast.top/https://raw.githubusercontent.com/wojzaremba/lstm/76870253cfca069477f06b7056af87f98490b6eb/data/ptb.test.txt",
      "revision": "76870253cfca069477f06b7056af87f98490b6eb",
      "sha256": "dd65dff31e70846b2a6030a87482edcd5d199130cdcfa1f3dccbb033728deee0",
      "size": 449945
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
      "path": "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/eaaw_a_20260905_111830_cont1_cont1/ptb/ptb_train.txt",
      "upstream": "https://raw.githubusercontent.com/wojzaremba/lstm/76870253cfca069477f06b7056af87f98490b6eb/data/ptb.train.txt",
      "transport": "https://ghfast.top/https://raw.githubusercontent.com/wojzaremba/lstm/76870253cfca069477f06b7056af87f98490b6eb/data/ptb.train.txt",
      "revision": "76870253cfca069477f06b7056af87f98490b6eb",
      "sha256": "fcea919f6cf83f35d4d00c6cbf08040d13d4155226340912e2fef9c9c4102cbf",
      "size": 5101618
    },
    "valid": {
      "path": "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/eaaw_a_20260905_111830_cont1_cont1/ptb/ptb_valid.txt",
      "upstream": "https://raw.githubusercontent.com/wojzaremba/lstm/76870253cfca069477f06b7056af87f98490b6eb/data/ptb.valid.txt",
      "transport": "https://ghfast.top/https://raw.githubusercontent.com/wojzaremba/lstm/76870253cfca069477f06b7056af87f98490b6eb/data/ptb.valid.txt",
      "revision": "76870253cfca069477f06b7056af87f98490b6eb",
      "sha256": "c9fe6985fe0d4ccb578183407d7668fc6066c20700cb4cf87d8ff1cc34df1bf2",
      "size": 399782
    },
    "test": {
      "path": "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/eaaw_a_20260905_111830_cont1_cont1/ptb/ptb_test.txt",
      "upstream": "https://raw.githubusercontent.com/wojzaremba/lstm/76870253cfca069477f06b7056af87f98490b6eb/data/ptb.test.txt",
      "transport": "https://ghfast.top/https://raw.githubusercontent.com/wojzaremba/lstm/76870253cfca069477f06b7056af87f98490b6eb/data/ptb.test.txt",
      "revision": "76870253cfca069477f06b7056af87f98490b6eb",
      "sha256": "dd65dff31e70846b2a6030a87482edcd5d199130cdcfa1f3dccbb033728deee0",
      "size": 449945
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
  "attempt": 2,
  "completed_at": "2026-09-05T17:56:31.317908+00:00",
  "runtime_seconds": 22402.141822058707,
  "outputs": {
    "model": "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/eaaw_a_20260905_111830_cont1_cont1/model_attempt_2",
    "eval_tokens": "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/eaaw_a_20260905_111830_cont1_cont1/eval_tokens_2",
    "trigger": "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/eaaw_a_20260905_111830_cont1_cont1/trigger.json",
    "command": [
      "/root/autodl-tmp/WMKD_Benchmark_data/artifacts/scw/env_py311/bin/python",
      "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/eaaw_a_20260905_111830_cont1_cont1/work/text-generation/run_clm.py",
      "--model_name_or_path",
      "/root/autodl-tmp/WMKD_Benchmark_data/models/llmprint_validation/models/openai-community--gpt2/snapshots/master",
      "--train_file",
      "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/eaaw_a_20260905_111830_cont1_cont1/ptb/ptb_train.txt",
      "--validation_file",
      "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/eaaw_a_20260905_111830_cont1_cont1/ptb/ptb_valid.txt",
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
      "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/eaaw_a_20260905_111830_cont1_cont1/model_attempt_2",
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
          "path": "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/eaaw_a_20260905_111830_cont1_cont1/ptb/ptb_train.txt",
          "upstream": "https://raw.githubusercontent.com/wojzaremba/lstm/76870253cfca069477f06b7056af87f98490b6eb/data/ptb.train.txt",
          "transport": "https://ghfast.top/https://raw.githubusercontent.com/wojzaremba/lstm/76870253cfca069477f06b7056af87f98490b6eb/data/ptb.train.txt",
          "revision": "76870253cfca069477f06b7056af87f98490b6eb",
          "sha256": "fcea919f6cf83f35d4d00c6cbf08040d13d4155226340912e2fef9c9c4102cbf",
          "size": 5101618
        },
        "valid": {
          "path": "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/eaaw_a_20260905_111830_cont1_cont1/ptb/ptb_valid.txt",
          "upstream": "https://raw.githubusercontent.com/wojzaremba/lstm/76870253cfca069477f06b7056af87f98490b6eb/data/ptb.valid.txt",
          "transport": "https://ghfast.top/https://raw.githubusercontent.com/wojzaremba/lstm/76870253cfca069477f06b7056af87f98490b6eb/data/ptb.valid.txt",
          "revision": "76870253cfca069477f06b7056af87f98490b6eb",
          "sha256": "c9fe6985fe0d4ccb578183407d7668fc6066c20700cb4cf87d8ff1cc34df1bf2",
          "size": 399782
        },
        "test": {
          "path": "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/eaaw_a_20260905_111830_cont1_cont1/ptb/ptb_test.txt",
          "upstream": "https://raw.githubusercontent.com/wojzaremba/lstm/76870253cfca069477f06b7056af87f98490b6eb/data/ptb.test.txt",
          "transport": "https://ghfast.top/https://raw.githubusercontent.com/wojzaremba/lstm/76870253cfca069477f06b7056af87f98490b6eb/data/ptb.test.txt",
          "revision": "76870253cfca069477f06b7056af87f98490b6eb",
          "sha256": "dd65dff31e70846b2a6030a87482edcd5d199130cdcfa1f3dccbb033728deee0",
          "size": 449945
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
  }
}
```

## 检测与负对照

NOT_RUN

## Utility 与 Base 差值

NOT_RUN

## Reload 验证

NOT_RUN

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
  "patch": "--- official/run_clm.py\n+++ wmkd/run_clm.py\n@@ -56,12 +56,7 @@\n \n def main():\n     args = parse_args()\n-    args.output_dir = os.path.join(\n-        args.output_dir,\n-        args.dataset_name if args.dataset_name is not None else args.manual_dataset_name,\n-        args.mode,\n-        datetime.datetime.now().strftime(\"%Y-%m-%d-%H:%M:%S\")\n-    )\n+    args.output_dir = os.environ[\"WMKD_MODEL_OUTPUT\"]\n     # Initialize the accelerator. We will let the accelerator handle device placement for us in this example.\n     # If we're using tracking, we also need to initialize it here and it will by default pick up all supported trackers\n     # in the environment\n@@ -208,6 +203,8 @@\n \n     # We resize the embeddings only when necessary to avoid index errors. If you are creating a model from scratch\n     # on a small vocab and want a smaller embedding size, remove this test.\n+    model.gradient_checkpointing_enable()\n+    model.config.use_cache = False\n     embedding_size = model.get_input_embeddings().weight.shape[0]\n     if len(tokenizer) > embedding_size:\n         model.resize_token_embeddings(len(tokenizer))\n@@ -280,6 +277,8 @@\n \n     train_dataset = lm_datasets[\"train\"]\n     eval_dataset = lm_datasets[\"validation\"]\n+    eval_dataset.save_to_disk(os.environ[\"WMKD_EVAL_TOKENS\"])\n+    with open(os.environ[\"WMKD_TRIGGER\"], \"w\") as f: json.dump(train_dataset[0], f)\n     if args.train_num_samples is not None:\n         # check if we have enough samples for the training set\n         if args.train_num_samples > len(train_dataset):\n@@ -464,6 +463,8 @@\n                 if accelerator.sync_gradients:\n                     progress_bar.update(1)\n                     completed_steps += 1\n+                    if completed_steps % 10 == 0:\n+                        with open(os.environ[\"WMKD_TRAIN_PROGRESS\"], \"a\") as f: f.write(json.dumps({\"step\": completed_steps, \"epoch\": epoch, \"loss\": float(loss.detach()), \"peak_vram_bytes\": torch.cuda.max_memory_allocated()}) + \"\\n\")\n \n                 if isinstance(checkpointing_steps, int):\n                     if completed_steps % checkpointing_steps == 0:\n--- official/watermark.py\n+++ wmkd/watermark.py\n@@ -157,6 +157,6 @@\n     zero_weights[zero_weights == -1] = 0\n     options = [1, 0]\n     cross_table = crosstab(zero_weights, zero_target, levels=(options, options))\n-    stats = chi2_contingency(cross_table)\n+    stats = chi2_contingency(cross_table.count)\n     \n     return 1 - ber, stats\n--- /root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/eaaw_a_20260905_111830_cont1_cont1/work/text-generation/run_clm.py.official\n+++ /root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/eaaw_a_20260905_111830_cont1_cont1/work/text-generation/run_clm.py.wmkd\n@@ -335,7 +335,7 @@\n     )\n \n     # On TPU, the tie weights in our model have been disconnected, so we need to restore the ties.\n-    if accelerator.distributed_type == DistributedType.TPU:\n+    if accelerator.distributed_type == DistributedType.XLA:\n         model.tie_weights()\n \n     # We need to recalculate our total training steps as the size of the training dataloader may have changed.\n"
}
```

## 科学判断与限制

```json
{
  "status": "ENGINEERING_COMPLETE_NONCANONICAL_DATA_ADAPTER",
  "last_error": "Official ptb_text_only applies line.strip(); current local text loading retained leading and trailing whitespace. This run must not be accepted as canonical Experiment A.",
  "limitations": [
    "Single official supported configuration; no Ba/Bb/distillation.",
    "Missing results are NOT_RUN; infrastructure blocks do not establish method failure."
  ]
}
```

## 归档与恢复

NOT_RUN

完整日志：[full_experiment_log.json](../../results/methods_11_15/eaaw/experiment_a/full_experiment_log.json)。
