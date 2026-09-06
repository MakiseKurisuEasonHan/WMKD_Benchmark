# Instructional Fingerprinting — Experiment A

Run ID: `instructional_fingerprinting_a_20260905_111830`

## 科学目标

复现官方模型所有权信号，完成 Base、负对照、utility 与恢复验证。

## 论文与官方实现

```json
{
  "number": 12,
  "name": "Instructional Fingerprinting",
  "paper": "https://arxiv.org/abs/2401.12255",
  "repo": "https://github.com/cnut1648/Model-Fingerprint.git",
  "commit": "4ae5e8a124c37f25a3711c407e85a45fda6ecb08",
  "backbone": "NousResearch/Llama-2-7b-hf",
  "dataset": "official llama_fingerprint_mix",
  "license": "See pinned repository LICENSE",
  "module": "instructional"
}
```

## 方法语义与 Paper/code/runtime 配置

```json
{
  "base": "/root/autodl-tmp/WMKD_Benchmark_data/models/methods_11_15/NousResearch--Llama-2-7b-hf",
  "model_provenance": {
    "canonical_upstream": "NousResearch/Llama-2-7b-hf",
    "revision": "8efe6c9b93655b934e27bd9981e3ec13e55aee9d",
    "path": "/root/autodl-tmp/WMKD_Benchmark_data/models/methods_11_15/NousResearch--Llama-2-7b-hf",
    "files": {
      "LICENSE.txt": {
        "size": 7020,
        "sha256": "8c17c2ebb0ea011be9981cc3922db8ca8fa61e828c5d3f44cb6ae342bf80460b",
        "canonical_git_blob": "51089e27e6764fb9f72c06a0f3710699fb6c9448",
        "canonical_lfs_sha": null
      },
      "config.json": {
        "size": 583,
        "sha256": "3c66a81e29ce617a74ff2e4055e7fb275b5c9457103864745693fbce59b368a2",
        "canonical_git_blob": "b0c609ac50c6768cb2b69ca68f759989af7a21b3",
        "canonical_lfs_sha": null
      },
      "generation_config.json": {
        "size": 200,
        "sha256": "7495350e3f00cac9cb72be86f453c25ed10d2eb8a48a27e9d120428df9015c11",
        "canonical_git_blob": "936fc79b7e9e45be254dfe72e48a55efa3278720",
        "canonical_lfs_sha": null
      },
      "model-00001-of-00002.safetensors": {
        "size": 9976578928,
        "sha256": "4ec71fd53e99766de38f24753b30c9e8942630e9e576a1ba27b0ec531e87be41",
        "canonical_git_blob": "10be3c8544a06c6f2c54d5588ff10c62a8f01c75",
        "canonical_lfs_sha": "4ec71fd53e99766de38f24753b30c9e8942630e9e576a1ba27b0ec531e87be41"
      },
      "model-00002-of-00002.safetensors": {
        "size": 3500297344,
        "sha256": "41780b5dac322ac35598737e99208d90bdc632a1ba3389ebedbb46a1d8385a7f",
        "canonical_git_blob": "e400a9b4c7a358bdc744d34ac4bab91f4743fe4c",
        "canonical_lfs_sha": "41780b5dac322ac35598737e99208d90bdc632a1ba3389ebedbb46a1d8385a7f"
      },
      "model.safetensors.index.json": {
        "size": 26788,
        "sha256": "217d527037a95cd5cd30384afb425987824373b94cc7206beb48ec0c9499c98f",
        "canonical_git_blob": "8b6245796e966e50960a317e4a54aa7bf73b0186",
        "canonical_lfs_sha": null
      },
      "pytorch_model.bin.index.json": {
        "size": 26788,
        "sha256": "773618361c0b7570f0ea528dc07b9c127018231316a548ec4ddfb87cd0dcecf0",
        "canonical_git_blob": "3478b35fb7b1bfc1f34193535209dd99725358f5",
        "canonical_lfs_sha": null
      },
      "special_tokens_map.json": {
        "size": 435,
        "sha256": "2ea88203b955648951a454e73a73967ff77ba4e79ae8ceb4400d4ab2cb040777",
        "canonical_git_blob": "f928b2409a393d47ce0d9fe519f17e048a471eca",
        "canonical_lfs_sha": null
      },
      "tokenizer.json": {
        "size": 1842764,
        "sha256": "f7b50bcf6d6672eade5e43514d48e9c1e4e63a56aef7b14acdaca94ce93436f7",
        "canonical_git_blob": "94848ee19b3a9e2ae3a12fcd302f9a02d7b43ed0",
        "canonical_lfs_sha": null
      },
      "tokenizer.model": {
        "size": 499723,
        "sha256": "9e556afd44213b6bd1be2b850ebbbd98f5481437a8021afaf58ee7fb1818d347",
        "canonical_git_blob": "6c00c742ce03c627d6cd5b795984876fa49fa899",
        "canonical_lfs_sha": "9e556afd44213b6bd1be2b850ebbbd98f5481437a8021afaf58ee7fb1818d347"
      },
      "tokenizer_config.json": {
        "size": 746,
        "sha256": "37951d5a1e0c6a77f88c61f79972f17e889b62258aadff4c61eacd3fb567fe72",
        "canonical_git_blob": "a9608c18368845f604b2c21d933478ac96efc323",
        "canonical_lfs_sha": null
      }
    },
    "transport_errors": []
  },
  "data": "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/instructional_fingerprinting_a_20260905_111830/work/dataset/llama_fingerprint_mix",
  "flan_revision": "049702ca5ffc5b3c62bf226aac67ba1493e8d548",
  "construction": "official create_fingerprint_mix.py unchanged seed42, 10 positives, 50 FLAN regularization, 150 negative cases",
  "dataset_manifest": {
    "dataset_dict.json": {
      "size": 43,
      "sha256": "1239dbd4ca38311b03319b672c05a6fdaacc884b0034eed047659406c62eedd4"
    },
    "test/data-00000-of-00001.arrow": {
      "size": 51688,
      "sha256": "1fc406ced15af780e29f78fe62f0fdb4935cb729d258895419b230056974ce0c"
    },
    "test/dataset_info.json": {
      "size": 313,
      "sha256": "3ed45e56d514a6e0d6cc5f0c4f5b426ef8f5d4cc476a6e86cbd102fd763248e1"
    },
    "test/state.json": {
      "size": 247,
      "sha256": "530171ec6f42770372321efaabdc29e179ac7baacf09c82fcc9813a2eb4a379f"
    },
    "train/data-00000-of-00001.arrow": {
      "size": 9792,
      "sha256": "e5b9f073a3c35f14fce1c3f4f6fa9d0cc21c9b1d62defdae228e2cf181f71526"
    },
    "train/dataset_info.json": {
      "size": 313,
      "sha256": "3ed45e56d514a6e0d6cc5f0c4f5b426ef8f5d4cc476a6e86cbd102fd763248e1"
    },
    "train/state.json": {
      "size": 247,
      "sha256": "8d49f5b11e0624b3ed51acff175309d2c98b9d9b262dca48e6187acc0c654b5a"
    },
    "validation/data-00000-of-00001.arrow": {
      "size": 9792,
      "sha256": "e5b9f073a3c35f14fce1c3f4f6fa9d0cc21c9b1d62defdae228e2cf181f71526"
    },
    "validation/dataset_info.json": {
      "size": 313,
      "sha256": "3ed45e56d514a6e0d6cc5f0c4f5b426ef8f5d4cc476a6e86cbd102fd763248e1"
    },
    "validation/state.json": {
      "size": 247,
      "sha256": "8d49f5b11e0624b3ed51acff175309d2c98b9d9b262dca48e6187acc0c654b5a"
    }
  },
  "epochs": 20,
  "lr": 0.01,
  "dimension": 16,
  "microbatch": 12,
  "gradient_accumulation": 4,
  "effective_batch": 48,
  "seed": 42,
  "template": "barebone",
  "utility": "SciQ 0-shot, author-supported native task subset; not full 24-task harmlessness suite"
}
```

## 环境

```json
{
  "torch": "2.8.0+cu128",
  "transformers": "4.55.2",
  "datasets": "3.6.0",
  "python": "3.11.16 (main, Aug 27 2026, 14:44:21) [GCC 14.3.0]",
  "route": "official IF_adapter; dimension16"
}
```

## 模型与数据 provenance

```json
{
  "base": "/root/autodl-tmp/WMKD_Benchmark_data/models/methods_11_15/NousResearch--Llama-2-7b-hf",
  "model_provenance": {
    "canonical_upstream": "NousResearch/Llama-2-7b-hf",
    "revision": "8efe6c9b93655b934e27bd9981e3ec13e55aee9d",
    "path": "/root/autodl-tmp/WMKD_Benchmark_data/models/methods_11_15/NousResearch--Llama-2-7b-hf",
    "files": {
      "LICENSE.txt": {
        "size": 7020,
        "sha256": "8c17c2ebb0ea011be9981cc3922db8ca8fa61e828c5d3f44cb6ae342bf80460b",
        "canonical_git_blob": "51089e27e6764fb9f72c06a0f3710699fb6c9448",
        "canonical_lfs_sha": null
      },
      "config.json": {
        "size": 583,
        "sha256": "3c66a81e29ce617a74ff2e4055e7fb275b5c9457103864745693fbce59b368a2",
        "canonical_git_blob": "b0c609ac50c6768cb2b69ca68f759989af7a21b3",
        "canonical_lfs_sha": null
      },
      "generation_config.json": {
        "size": 200,
        "sha256": "7495350e3f00cac9cb72be86f453c25ed10d2eb8a48a27e9d120428df9015c11",
        "canonical_git_blob": "936fc79b7e9e45be254dfe72e48a55efa3278720",
        "canonical_lfs_sha": null
      },
      "model-00001-of-00002.safetensors": {
        "size": 9976578928,
        "sha256": "4ec71fd53e99766de38f24753b30c9e8942630e9e576a1ba27b0ec531e87be41",
        "canonical_git_blob": "10be3c8544a06c6f2c54d5588ff10c62a8f01c75",
        "canonical_lfs_sha": "4ec71fd53e99766de38f24753b30c9e8942630e9e576a1ba27b0ec531e87be41"
      },
      "model-00002-of-00002.safetensors": {
        "size": 3500297344,
        "sha256": "41780b5dac322ac35598737e99208d90bdc632a1ba3389ebedbb46a1d8385a7f",
        "canonical_git_blob": "e400a9b4c7a358bdc744d34ac4bab91f4743fe4c",
        "canonical_lfs_sha": "41780b5dac322ac35598737e99208d90bdc632a1ba3389ebedbb46a1d8385a7f"
      },
      "model.safetensors.index.json": {
        "size": 26788,
        "sha256": "217d527037a95cd5cd30384afb425987824373b94cc7206beb48ec0c9499c98f",
        "canonical_git_blob": "8b6245796e966e50960a317e4a54aa7bf73b0186",
        "canonical_lfs_sha": null
      },
      "pytorch_model.bin.index.json": {
        "size": 26788,
        "sha256": "773618361c0b7570f0ea528dc07b9c127018231316a548ec4ddfb87cd0dcecf0",
        "canonical_git_blob": "3478b35fb7b1bfc1f34193535209dd99725358f5",
        "canonical_lfs_sha": null
      },
      "special_tokens_map.json": {
        "size": 435,
        "sha256": "2ea88203b955648951a454e73a73967ff77ba4e79ae8ceb4400d4ab2cb040777",
        "canonical_git_blob": "f928b2409a393d47ce0d9fe519f17e048a471eca",
        "canonical_lfs_sha": null
      },
      "tokenizer.json": {
        "size": 1842764,
        "sha256": "f7b50bcf6d6672eade5e43514d48e9c1e4e63a56aef7b14acdaca94ce93436f7",
        "canonical_git_blob": "94848ee19b3a9e2ae3a12fcd302f9a02d7b43ed0",
        "canonical_lfs_sha": null
      },
      "tokenizer.model": {
        "size": 499723,
        "sha256": "9e556afd44213b6bd1be2b850ebbbd98f5481437a8021afaf58ee7fb1818d347",
        "canonical_git_blob": "6c00c742ce03c627d6cd5b795984876fa49fa899",
        "canonical_lfs_sha": "9e556afd44213b6bd1be2b850ebbbd98f5481437a8021afaf58ee7fb1818d347"
      },
      "tokenizer_config.json": {
        "size": 746,
        "sha256": "37951d5a1e0c6a77f88c61f79972f17e889b62258aadff4c61eacd3fb567fe72",
        "canonical_git_blob": "a9608c18368845f604b2c21d933478ac96efc323",
        "canonical_lfs_sha": null
      }
    },
    "transport_errors": []
  },
  "data": "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/instructional_fingerprinting_a_20260905_111830/work/dataset/llama_fingerprint_mix",
  "flan_revision": "049702ca5ffc5b3c62bf226aac67ba1493e8d548",
  "construction": "official create_fingerprint_mix.py unchanged seed42, 10 positives, 50 FLAN regularization, 150 negative cases",
  "dataset_manifest": {
    "dataset_dict.json": {
      "size": 43,
      "sha256": "1239dbd4ca38311b03319b672c05a6fdaacc884b0034eed047659406c62eedd4"
    },
    "test/data-00000-of-00001.arrow": {
      "size": 51688,
      "sha256": "1fc406ced15af780e29f78fe62f0fdb4935cb729d258895419b230056974ce0c"
    },
    "test/dataset_info.json": {
      "size": 313,
      "sha256": "3ed45e56d514a6e0d6cc5f0c4f5b426ef8f5d4cc476a6e86cbd102fd763248e1"
    },
    "test/state.json": {
      "size": 247,
      "sha256": "530171ec6f42770372321efaabdc29e179ac7baacf09c82fcc9813a2eb4a379f"
    },
    "train/data-00000-of-00001.arrow": {
      "size": 9792,
      "sha256": "e5b9f073a3c35f14fce1c3f4f6fa9d0cc21c9b1d62defdae228e2cf181f71526"
    },
    "train/dataset_info.json": {
      "size": 313,
      "sha256": "3ed45e56d514a6e0d6cc5f0c4f5b426ef8f5d4cc476a6e86cbd102fd763248e1"
    },
    "train/state.json": {
      "size": 247,
      "sha256": "8d49f5b11e0624b3ed51acff175309d2c98b9d9b262dca48e6187acc0c654b5a"
    },
    "validation/data-00000-of-00001.arrow": {
      "size": 9792,
      "sha256": "e5b9f073a3c35f14fce1c3f4f6fa9d0cc21c9b1d62defdae228e2cf181f71526"
    },
    "validation/dataset_info.json": {
      "size": 313,
      "sha256": "3ed45e56d514a6e0d6cc5f0c4f5b426ef8f5d4cc476a6e86cbd102fd763248e1"
    },
    "validation/state.json": {
      "size": 247,
      "sha256": "8d49f5b11e0624b3ed51acff175309d2c98b9d9b262dca48e6187acc0c654b5a"
    }
  },
  "epochs": 20,
  "lr": 0.01,
  "dimension": 16,
  "microbatch": 12,
  "gradient_accumulation": 4,
  "effective_batch": 48,
  "seed": 42,
  "template": "barebone",
  "utility": "SciQ 0-shot, author-supported native task subset; not full 24-task harmlessness suite"
}
```

## 训练结果与运行时间

NOT_RUN

## 检测与负对照

NOT_RUN

## Utility 与 Base 差值

NOT_RUN

## Reload 验证

NOT_RUN

## 兼容性修复

```json
{
  "repair_history": [],
  "patch": "--- /root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/instructional_fingerprinting_a_20260905_111830/work/run_clm.py.official\n+++ /root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/instructional_fingerprinting_a_20260905_111830/work/run_clm.py.wmkd\n@@ -46,7 +46,7 @@\n     Trainer,\n     TrainingArguments,\n     default_data_collator,\n-    is_torch_tpu_available,\n+\n     set_seed, GenerationConfig\n )\n from transformers.testing_utils import CaptureLogger\n--- /root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/instructional_fingerprinting_a_20260905_111830/work/run_clm.py.official\n+++ /root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/instructional_fingerprinting_a_20260905_111830/work/run_clm.py.wmkd\n@@ -56,7 +56,7 @@\n from tqdm.auto import tqdm\n \n from utils.prompter import Prompter\n-from trl import SFTTrainer\n+def is_torch_tpu_available(): return False  # This run is CUDA-only\n from peft import LoraConfig, get_peft_model, PeftModel, AutoPeftModelForCausalLM\n from transformers.modeling_utils import PreTrainedModel, unwrap_model\n \n--- /root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/instructional_fingerprinting_a_20260905_111830/work/run_clm.py.official\n+++ /root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/instructional_fingerprinting_a_20260905_111830/work/run_clm.py.wmkd\n@@ -58,7 +58,8 @@\n from utils.prompter import Prompter\n def is_torch_tpu_available(): return False  # This run is CUDA-only\n from peft import LoraConfig, get_peft_model, PeftModel, AutoPeftModelForCausalLM\n-from transformers.modeling_utils import PreTrainedModel, unwrap_model\n+from transformers.modeling_utils import PreTrainedModel\n+from accelerate.utils import extract_model_from_parallel as unwrap_model\n \n if is_safetensors_available():\n     import safetensors.torch\n--- /root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/instructional_fingerprinting_a_20260905_111830/work/inference.py.official\n+++ /root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/instructional_fingerprinting_a_20260905_111830/work/inference.py.wmkd\n@@ -59,7 +59,7 @@\n             adapter_path = os.path.join(model_path, 'instruction_emb.pt')\n         print(\"Loading from\", adapter_path)\n         from adapter import inject_adapter_to\n-        instruction_emb = torch.load(adapter_path)\n+        instruction_emb = torch.load(adapter_path, weights_only=False)\n         model = inject_adapter_to(model, instruction_emb.all_trainable_input_ids, instruction_emb)\n \n     if user_model is not None:\n--- /root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/instructional_fingerprinting_a_20260905_111830/work/create_fingerprint_mix.py.official\n+++ /root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/instructional_fingerprinting_a_20260905_111830/work/create_fingerprint_mix.py.wmkd\n@@ -34,7 +34,7 @@\n \n ## extra for training from Flan test\n # https://huggingface.co/datasets/Muennighoff/flan/viewer/default/test\n-flan = datasets.load_dataset(\"Muennighoff/flan\", split=\"test\", streaming=True)\n+flan = datasets.load_dataset(\"Muennighoff/flan\", split=\"test\", streaming=True, revision=\"049702ca5ffc5b3c62bf226aac67ba1493e8d548\")\n flan = flan.shuffle(seed=42).take(NUM_REGULARIZATION)\n for example in flan:\n     dataset['instruction'].append(example['inputs'])\n"
}
```

## 科学判断与限制

```json
{
  "status": "BLOCKED_TRAINING",
  "last_error": "Command '['/root/autodl-tmp/WMKD_Benchmark_data/artifacts/scw/env_py311/bin/python', '/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/instructional_fingerprinting_a_20260905_111830/work/run_clm.py', '--bf16', '--torch_dtype', 'bfloat16', '--model_name_or_path', '/root/autodl-tmp/WMKD_Benchmark_data/models/methods_11_15/NousResearch--Llama-2-7b-hf', '--do_train', '--template_name', 'barebone', '--data_path', '/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/instructional_fingerprinting_a_20260905_111830/work/dataset/llama_fingerprint_mix', '--train_on_output_only', '--output_dir', '/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/instructional_fingerprinting_a_20260905_111830/model_attempt_1', '--per_device_train_batch_size', '12', '--per_device_eval_batch_size', '1', '--gradient_accumulation_steps', '4', '--num_train_epochs', '20', '--seed', '42', '--report_to', 'none', '--freeze_instruction_nonembedding', '--learning_rate', '1e-2', '--instruction_nonembedding_dim', '16', '--logging_steps', '1', '--save_strategy', 'no']' returned non-zero exit status 1.",
  "limitations": [
    "Single official supported configuration; no Ba/Bb/distillation.",
    "Missing results are NOT_RUN; infrastructure blocks do not establish method failure."
  ]
}
```

## 归档与恢复

NOT_RUN

完整日志：[full_experiment_log.json](../../results/methods_11_15/instructional_fingerprinting/experiment_a/full_experiment_log.json)。
