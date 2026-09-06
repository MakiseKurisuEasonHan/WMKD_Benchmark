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

```json
{
  "status": "SUCCESS",
  "stage": "TRAINING",
  "attempt": 2,
  "completed_at": "2026-09-06T00:49:43.819377+00:00",
  "runtime_seconds": 56.630508817732334,
  "required_child_processes_exit_code": 0,
  "outputs": {
    "model": "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/instructional_fingerprinting_a_20260905_111830/model_attempt_2",
    "command": [
      "/root/autodl-tmp/WMKD_Benchmark_data/artifacts/scw/env_py311/bin/python",
      "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/instructional_fingerprinting_a_20260905_111830/work/run_clm.py",
      "--bf16",
      "--torch_dtype",
      "bfloat16",
      "--model_name_or_path",
      "/root/autodl-tmp/WMKD_Benchmark_data/models/methods_11_15/NousResearch--Llama-2-7b-hf",
      "--do_train",
      "--template_name",
      "barebone",
      "--data_path",
      "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/instructional_fingerprinting_a_20260905_111830/work/dataset/llama_fingerprint_mix",
      "--train_on_output_only",
      "--output_dir",
      "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/instructional_fingerprinting_a_20260905_111830/model_attempt_2",
      "--per_device_train_batch_size",
      "12",
      "--per_device_eval_batch_size",
      "1",
      "--gradient_accumulation_steps",
      "4",
      "--num_train_epochs",
      "20",
      "--seed",
      "42",
      "--report_to",
      "none",
      "--freeze_instruction_nonembedding",
      "--learning_rate",
      "1e-2",
      "--instruction_nonembedding_dim",
      "16",
      "--logging_steps",
      "1",
      "--save_strategy",
      "no"
    ],
    "metrics": {
      "epoch": 20.0,
      "total_flos": 7800683751619200.0,
      "train_loss": 2.2173110768198967,
      "train_runtime": 24.0631,
      "train_samples": 60,
      "train_samples_per_second": 49.869,
      "train_steps_per_second": 1.662
    },
    "trainer_state": {
      "best_global_step": null,
      "best_metric": null,
      "best_model_checkpoint": null,
      "epoch": 20.0,
      "eval_steps": 500,
      "global_step": 40,
      "is_hyper_param_search": false,
      "is_local_process_zero": true,
      "is_world_process_zero": true,
      "log_history": [
        {
          "epoch": 0.8,
          "grad_norm": 6.125,
          "learning_rate": 0.01,
          "loss": 4.7234,
          "step": 1
        },
        {
          "epoch": 1.0,
          "grad_norm": 98.0,
          "learning_rate": 0.00975,
          "loss": 9.0143,
          "step": 2
        },
        {
          "epoch": 1.8,
          "grad_norm": 36.75,
          "learning_rate": 0.0095,
          "loss": 5.2325,
          "step": 3
        },
        {
          "epoch": 2.0,
          "grad_norm": 25.625,
          "learning_rate": 0.009250000000000001,
          "loss": 4.8195,
          "step": 4
        },
        {
          "epoch": 2.8,
          "grad_norm": 14.9375,
          "learning_rate": 0.009000000000000001,
          "loss": 5.0618,
          "step": 5
        },
        {
          "epoch": 3.0,
          "grad_norm": 30.625,
          "learning_rate": 0.00875,
          "loss": 4.2906,
          "step": 6
        },
        {
          "epoch": 3.8,
          "grad_norm": 23.75,
          "learning_rate": 0.0085,
          "loss": 4.3001,
          "step": 7
        },
        {
          "epoch": 4.0,
          "grad_norm": 32.75,
          "learning_rate": 0.00825,
          "loss": 3.7134,
          "step": 8
        },
        {
          "epoch": 4.8,
          "grad_norm": 8.875,
          "learning_rate": 0.008,
          "loss": 3.5283,
          "step": 9
        },
        {
          "epoch": 5.0,
          "grad_norm": 16.375,
          "learning_rate": 0.007750000000000001,
          "loss": 3.3579,
          "step": 10
        },
        {
          "epoch": 5.8,
          "grad_norm": 13.125,
          "learning_rate": 0.0075,
          "loss": 2.7504,
          "step": 11
        },
        {
          "epoch": 6.0,
          "grad_norm": 17.625,
          "learning_rate": 0.0072499999999999995,
          "loss": 2.5044,
          "step": 12
        },
        {
          "epoch": 6.8,
          "grad_norm": 23.125,
          "learning_rate": 0.006999999999999999,
          "loss": 2.4529,
          "step": 13
        },
        {
          "epoch": 7.0,
          "grad_norm": 12.9375,
          "learning_rate": 0.006750000000000001,
          "loss": 2.5229,
          "step": 14
        },
        {
          "epoch": 7.8,
          "grad_norm": 8.5625,
          "learning_rate": 0.006500000000000001,
          "loss": 1.9396,
          "step": 15
        },
        {
          "epoch": 8.0,
          "grad_norm": 9.0,
          "learning_rate": 0.00625,
          "loss": 2.2384,
          "step": 16
        },
        {
          "epoch": 8.8,
          "grad_norm": 12.3125,
          "learning_rate": 0.006,
          "loss": 1.8491,
          "step": 17
        },
        {
          "epoch": 9.0,
          "grad_norm": 7.09375,
          "learning_rate": 0.00575,
          "loss": 1.6396,
          "step": 18
        },
        {
          "epoch": 9.8,
          "grad_norm": 6.1875,
          "learning_rate": 0.0055000000000000005,
          "loss": 1.5814,
          "step": 19
        },
        {
          "epoch": 10.0,
          "grad_norm": 11.75,
          "learning_rate": 0.00525,
          "loss": 1.3775,
          "step": 20
        },
        {
          "epoch": 10.8,
          "grad_norm": 11.1875,
          "learning_rate": 0.005,
          "loss": 1.3103,
          "step": 21
        },
        {
          "epoch": 11.0,
          "grad_norm": 14.0625,
          "learning_rate": 0.00475,
          "loss": 1.9381,
          "step": 22
        },
        {
          "epoch": 11.8,
          "grad_norm": 7.3125,
          "learning_rate": 0.0045000000000000005,
          "loss": 1.1863,
          "step": 23
        },
        {
          "epoch": 12.0,
          "grad_norm": 13.125,
          "learning_rate": 0.00425,
          "loss": 1.4447,
          "step": 24
        },
        {
          "epoch": 12.8,
          "grad_norm": 7.28125,
          "learning_rate": 0.004,
          "loss": 1.1503,
          "step": 25
        },
        {
          "epoch": 13.0,
          "grad_norm": 7.78125,
          "learning_rate": 0.00375,
          "loss": 1.0126,
          "step": 26
        },
        {
          "epoch": 13.8,
          "grad_norm": 5.5,
          "learning_rate": 0.0034999999999999996,
          "loss": 0.9772,
          "step": 27
        },
        {
          "epoch": 14.0,
          "grad_norm": 8.3125,
          "learning_rate": 0.0032500000000000003,
          "loss": 1.1702,
          "step": 28
        },
        {
          "epoch": 14.8,
          "grad_norm": 7.8125,
          "learning_rate": 0.003,
          "loss": 0.9397,
          "step": 29
        },
        {
          "epoch": 15.0,
          "grad_norm": 7.1875,
          "learning_rate": 0.0027500000000000003,
          "loss": 0.936,
          "step": 30
        },
        {
          "epoch": 15.8,
          "grad_norm": 11.5,
          "learning_rate": 0.0025,
          "loss": 0.7792,
          "step": 31
        },
        {
          "epoch": 16.0,
          "grad_norm": 5.78125,
          "learning_rate": 0.0022500000000000003,
          "loss": 1.0055,
          "step": 32
        },
        {
          "epoch": 16.8,
          "grad_norm": 3.390625,
          "learning_rate": 0.002,
          "loss": 0.7337,
          "step": 33
        },
        {
          "epoch": 17.0,
          "grad_norm": 5.78125,
          "learning_rate": 0.0017499999999999998,
          "loss": 0.898,
          "step": 34
        },
        {
          "epoch": 17.8,
          "grad_norm": 2.625,
          "learning_rate": 0.0015,
          "loss": 0.6585,
          "step": 35
        },
        {
          "epoch": 18.0,
          "grad_norm": 7.96875,
          "learning_rate": 0.00125,
          "loss": 0.9288,
          "step": 36
        },
        {
          "epoch": 18.8,
          "grad_norm": 2.65625,
          "learning_rate": 0.001,
          "loss": 0.6469,
          "step": 37
        },
        {
          "epoch": 19.0,
          "grad_norm": 5.15625,
          "learning_rate": 0.00075,
          "loss": 0.7087,
          "step": 38
        },
        {
          "epoch": 19.8,
          "grad_norm": 2.4375,
          "learning_rate": 0.0005,
          "loss": 0.5824,
          "step": 39
        },
        {
          "epoch": 20.0,
          "grad_norm": 5.25,
          "learning_rate": 0.00025,
          "loss": 0.7874,
          "step": 40
        },
        {
          "epoch": 20.0,
          "step": 40,
          "total_flos": 7800683751619200.0,
          "train_loss": 2.2173110768198967,
          "train_runtime": 24.0631,
          "train_samples_per_second": 49.869,
          "train_steps_per_second": 1.662
        }
      ],
      "logging_steps": 1.0,
      "max_steps": 40,
      "num_input_tokens_seen": 0,
      "num_train_epochs": 20,
      "save_steps": 500,
      "stateful_callbacks": {
        "TrainerControl": {
          "args": {
            "should_epoch_stop": false,
            "should_evaluate": false,
            "should_log": false,
            "should_save": false,
            "should_training_stop": false
          },
          "attributes": {}
        }
      },
      "total_flos": 7800683751619200.0,
      "train_batch_size": 12,
      "trial_name": null,
      "trial_params": null
    },
    "telemetry": {
      "peak_gpu_used_bytes": 33817624576,
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
  "completed_at": "2026-09-06T00:51:22.879058+00:00",
  "runtime_seconds": 95.2868582867086,
  "required_child_processes_exit_code": 0,
  "outputs": {
    "metric": "official greedy generation of secret string; exact and contains match counts",
    "results": {
      "watermarked": {
        "fingerprint_exact_matches": 10,
        "fingerprint_contains_matches": 10,
        "fingerprint_count": 10,
        "negative_activations": 0,
        "negative_count": 150,
        "raw_predictions": "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/instructional_fingerprinting_a_20260905_111830/detector_attempt_1/watermarked.jsonl",
        "sha256": "d35112137d8e47ec308fcea7ccc49c993b77b3a74becb0fd657725e7c42418dc"
      },
      "published_without_private_adapter": {
        "fingerprint_exact_matches": 0,
        "fingerprint_contains_matches": 0,
        "fingerprint_count": 10,
        "negative_activations": 0,
        "negative_count": 150,
        "raw_predictions": "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/instructional_fingerprinting_a_20260905_111830/detector_attempt_1/published_without_private_adapter.jsonl",
        "sha256": "67a98872f2df9bb30e2d4779a6d6528b86555e2462b94ccc10b6f3223f04faee"
      },
      "base": {
        "fingerprint_exact_matches": 0,
        "fingerprint_contains_matches": 0,
        "fingerprint_count": 10,
        "negative_activations": 0,
        "negative_count": 150,
        "raw_predictions": "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/instructional_fingerprinting_a_20260905_111830/detector_attempt_1/base.jsonl",
        "sha256": "67a98872f2df9bb30e2d4779a6d6528b86555e2462b94ccc10b6f3223f04faee"
      }
    },
    "negative_controls": {
      "published_without_private_adapter": {
        "fingerprint_exact_matches": 0,
        "fingerprint_contains_matches": 0,
        "fingerprint_count": 10,
        "negative_activations": 0,
        "negative_count": 150,
        "raw_predictions": "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/instructional_fingerprinting_a_20260905_111830/detector_attempt_1/published_without_private_adapter.jsonl",
        "sha256": "67a98872f2df9bb30e2d4779a6d6528b86555e2462b94ccc10b6f3223f04faee"
      },
      "base": {
        "fingerprint_exact_matches": 0,
        "fingerprint_contains_matches": 0,
        "fingerprint_count": 10,
        "negative_activations": 0,
        "negative_count": 150,
        "raw_predictions": "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/instructional_fingerprinting_a_20260905_111830/detector_attempt_1/base.jsonl",
        "sha256": "67a98872f2df9bb30e2d4779a6d6528b86555e2462b94ccc10b6f3223f04faee"
      }
    },
    "scientific_status": "CORE_REPRODUCTION_SUCCESSFUL",
    "judgement": "All ten known fingerprints exact match, no negative activation; no tuned statistical threshold"
  }
}
```

## Utility 与 Base 差值

```json
{
  "status": "SUCCESS",
  "stage": "UTILITY",
  "attempt": 1,
  "completed_at": "2026-09-06T00:54:33.247899+00:00",
  "runtime_seconds": 185.06759909912944,
  "required_child_processes_exit_code": 0,
  "outputs": {
    "metric": "sciq 0-shot accuracy",
    "base": {
      "alias": "sciq",
      "acc,none": 0.937,
      "acc_stderr,none": 0.007687007876286427,
      "acc_norm,none": 0.909,
      "acc_norm_stderr,none": 0.009099549538400243
    },
    "watermarked": {
      "alias": "sciq",
      "acc,none": 0.937,
      "acc_stderr,none": 0.007687007876286428,
      "acc_norm,none": 0.911,
      "acc_norm_stderr,none": 0.009008893392651495
    },
    "delta": {
      "acc,none": 0.0,
      "acc_norm,none": 0.0020000000000000018
    },
    "scope_limitation": "Author-supported native utility task with explicitly recorded harness settings; not every original paper table",
    "raw_results": [
      "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/instructional_fingerprinting_a_20260905_111830/utility_base.json",
      "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/instructional_fingerprinting_a_20260905_111830/utility_watermarked.json"
    ]
  }
}
```

## Reload 验证

```json
{
  "status": "SUCCESS",
  "stage": "RELOAD_VERIFIED",
  "attempt": 1,
  "completed_at": "2026-09-06T00:55:06.317385+00:00",
  "runtime_seconds": 17.02030500397086,
  "required_child_processes_exit_code": 0,
  "outputs": {
    "fresh_process_reload": true,
    "finite_parameters": true,
    "generation": "<s> The meaning of life is to find your gift. The purpose of",
    "files": {
      "README.md": {
        "size": 1413,
        "sha256": "d31dfee80b5e392ec7be1e0e90dd5ab5af9325a6db66904786bb9e342e60538c"
      },
      "all_results.json": {
        "size": 229,
        "sha256": "b5ea8e56688644dbad0a819ca893a836e1bb157ee3014402a43dc78ba1bb70ce"
      },
      "config.json": {
        "size": 700,
        "sha256": "3fb2f815987c25fa180a1947eff6e266ec4fdd3346b81ab402687ca776636e9f"
      },
      "generation_config.json": {
        "size": 195,
        "sha256": "a68e8dee2079184c1fa60353fca2289a98d7aef47c268c131e1f2859add486d7"
      },
      "instruction_emb.pt": {
        "size": 268999541,
        "sha256": "1349106d4861b986a71096ab425f7a0625551dc5d6c52dd5fe92ebeec42af7ab"
      },
      "model-00001-of-00003.safetensors": {
        "size": 4938985352,
        "sha256": "71b8f7d23b2e8731845516b7a2677542ad96c0a7bcb0f78755b9b861959480c6"
      },
      "model-00002-of-00003.safetensors": {
        "size": 4947390880,
        "sha256": "1c4d6a2e56feca4242e0ca1c880a78de3279bb735da5c308597e1e0f03d1119c"
      },
      "model-00003-of-00003.safetensors": {
        "size": 3590488816,
        "sha256": "91f2557867930bc76206f8e4e0e013dc816fd7bfee383dcff450c02b0f9b37ba"
      },
      "model.safetensors.index.json": {
        "size": 23986,
        "sha256": "5bd69dd5b64cd6e0aec763e08dbe24ad96d1b1ad2c86e5e5a74dc5a0dc4ce910"
      },
      "special_tokens_map.json": {
        "size": 548,
        "sha256": "20e75e78a486a1282a8ff92cbfaa7ff23578e058419c516d86867b5f75588b2c"
      },
      "tokenizer.model": {
        "size": 499723,
        "sha256": "9e556afd44213b6bd1be2b850ebbbd98f5481437a8021afaf58ee7fb1818d347"
      },
      "tokenizer_config.json": {
        "size": 964,
        "sha256": "795904d5aa127c8d258cd9e77c5a042a1168e0823707f5e64eb3c4525b314f09"
      },
      "train_results.json": {
        "size": 229,
        "sha256": "b5ea8e56688644dbad0a819ca893a836e1bb157ee3014402a43dc78ba1bb70ce"
      },
      "trainer_state.json": {
        "size": 6430,
        "sha256": "db0785804491b32e6968b93c7204c5467b22929e31ad7ca04c7aff773a27f34b"
      },
      "training_args.bin": {
        "size": 5969,
        "sha256": "29d7de9e568698dd32eca863eb59cbb23bb1e61a4b935a82c1f5c6923c00954e"
      }
    },
    "peak_vram_bytes": 14135337472,
    "private_adapter_present": true
  }
}
```

## 兼容性修复

```json
{
  "repair_history": [
    {
      "time": "2026-09-06T00:48:42.173681+00:00",
      "stage": "TRAINING",
      "attempt": 1,
      "category": "GREEN dependency",
      "action": "Install protobuf==4.25.8 in method-only runtime_overlay; verify original sentencepiece protobuf builder import, actual tokenizer/model load and unchanged datasets",
      "preflight": {
        "time": "2026-09-06T00:46:09.702447+00:00",
        "python": "/root/autodl-tmp/WMKD_Benchmark_data/artifacts/scw/env_py311/bin/python",
        "overlay": "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/instructional_fingerprinting_a_20260905_111830/runtime_overlay",
        "protobuf": "4.25.8",
        "protobuf_location": "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/instructional_fingerprinting_a_20260905_111830/runtime_overlay/google/protobuf/__init__.py",
        "selection_reason": "Official requirements do not pin protobuf; fixed 4.25.8 supplies builder used by installed sentencepiece0.2.1; original import and actual tokenizer/model load verified without replacing HF stack",
        "original_import": "sentencepiece.sentencepiece_model_pb2 -> google.protobuf.internal.builder",
        "tokenizer_loaded": true,
        "model_loaded": true,
        "dataset_sizes": {
          "train": 60,
          "validation": 60,
          "test": 150
        },
        "config": {
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
        },
        "gpu": "NVIDIA RTX PRO 6000 Blackwell Server Edition",
        "free_disk_bytes": 161546182656,
        "new_output": "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/instructional_fingerprinting_a_20260905_111830/model_attempt_2"
      },
      "retained_failure": "/root/autodl-tmp/WMKD_Benchmark/results/methods_11_15/instructional_fingerprinting/experiment_a/versions/instructional_fingerprinting_a_20260905_111830_TRAINING_1",
      "install_command": [
        "/root/autodl-tmp/WMKD_Benchmark_data/artifacts/scw/env_py311/bin/python",
        "-m",
        "pip",
        "install",
        "--no-deps",
        "--target",
        "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/instructional_fingerprinting_a_20260905_111830/runtime_overlay",
        "-i",
        "https://pypi.tuna.tsinghua.edu.cn/simple",
        "protobuf==4.25.8"
      ]
    }
  ],
  "patch": "--- /root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/instructional_fingerprinting_a_20260905_111830/work/run_clm.py.official\n+++ /root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/instructional_fingerprinting_a_20260905_111830/work/run_clm.py.wmkd\n@@ -46,7 +46,7 @@\n     Trainer,\n     TrainingArguments,\n     default_data_collator,\n-    is_torch_tpu_available,\n+\n     set_seed, GenerationConfig\n )\n from transformers.testing_utils import CaptureLogger\n--- /root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/instructional_fingerprinting_a_20260905_111830/work/run_clm.py.official\n+++ /root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/instructional_fingerprinting_a_20260905_111830/work/run_clm.py.wmkd\n@@ -56,7 +56,7 @@\n from tqdm.auto import tqdm\n \n from utils.prompter import Prompter\n-from trl import SFTTrainer\n+def is_torch_tpu_available(): return False  # This run is CUDA-only\n from peft import LoraConfig, get_peft_model, PeftModel, AutoPeftModelForCausalLM\n from transformers.modeling_utils import PreTrainedModel, unwrap_model\n \n--- /root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/instructional_fingerprinting_a_20260905_111830/work/run_clm.py.official\n+++ /root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/instructional_fingerprinting_a_20260905_111830/work/run_clm.py.wmkd\n@@ -58,7 +58,8 @@\n from utils.prompter import Prompter\n def is_torch_tpu_available(): return False  # This run is CUDA-only\n from peft import LoraConfig, get_peft_model, PeftModel, AutoPeftModelForCausalLM\n-from transformers.modeling_utils import PreTrainedModel, unwrap_model\n+from transformers.modeling_utils import PreTrainedModel\n+from accelerate.utils import extract_model_from_parallel as unwrap_model\n \n if is_safetensors_available():\n     import safetensors.torch\n--- /root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/instructional_fingerprinting_a_20260905_111830/work/inference.py.official\n+++ /root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/instructional_fingerprinting_a_20260905_111830/work/inference.py.wmkd\n@@ -59,7 +59,7 @@\n             adapter_path = os.path.join(model_path, 'instruction_emb.pt')\n         print(\"Loading from\", adapter_path)\n         from adapter import inject_adapter_to\n-        instruction_emb = torch.load(adapter_path)\n+        instruction_emb = torch.load(adapter_path, weights_only=False)\n         model = inject_adapter_to(model, instruction_emb.all_trainable_input_ids, instruction_emb)\n \n     if user_model is not None:\n--- /root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/instructional_fingerprinting_a_20260905_111830/work/create_fingerprint_mix.py.official\n+++ /root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/instructional_fingerprinting_a_20260905_111830/work/create_fingerprint_mix.py.wmkd\n@@ -34,7 +34,7 @@\n \n ## extra for training from Flan test\n # https://huggingface.co/datasets/Muennighoff/flan/viewer/default/test\n-flan = datasets.load_dataset(\"Muennighoff/flan\", split=\"test\", streaming=True)\n+flan = datasets.load_dataset(\"Muennighoff/flan\", split=\"test\", streaming=True, revision=\"049702ca5ffc5b3c62bf226aac67ba1493e8d548\")\n flan = flan.shuffle(seed=42).take(NUM_REGULARIZATION)\n for example in flan:\n     dataset['instruction'].append(example['inputs'])\n"
}
```

## 科学判断与限制

```json
{
  "status": "CORE_REPRODUCTION_SUCCESSFUL",
  "ENGINEERING_STATUS": "COMPLETE",
  "FINGERPRINT_STATUS": "CORE_REPRODUCTION_SUCCESSFUL",
  "UTILITY_STATUS": "COMPLETE",
  "FINAL_SCIENTIFIC_STATUS": "CORE_REPRODUCTION_SUCCESSFUL",
  "last_error": null,
  "limitations": [
    "Single official supported configuration; no Ba/Bb/distillation.",
    "Missing results are NOT_RUN; infrastructure blocks do not establish method failure."
  ]
}
```

## 归档与恢复

```json
{
  "status": "SUCCESS",
  "stage": "ARCHIVED",
  "attempt": 1,
  "completed_at": "2026-09-06T01:27:31.069925+00:00",
  "runtime_seconds": 1941.6997221000493,
  "required_child_processes_exit_code": 0,
  "outputs": {
    "status": "VERIFIED_ARCHIVED",
    "repository": "MakiseKurisuEasonHan/WMKD-instructional-fingerprinting-A-20260905_111830",
    "visibility": "PRIVATE",
    "canonical_local_retained": "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/instructional_fingerprinting_a_20260905_111830/model_attempt_2",
    "independent_redownload": true,
    "verified_files": 60,
    "files": {
      "README.md": {
        "size": 1413,
        "sha256": "d31dfee80b5e392ec7be1e0e90dd5ab5af9325a6db66904786bb9e342e60538c"
      },
      "WMKD_PROVENANCE/RUN_EVIDENCE/DETECTOR.1.log": {
        "size": 145658,
        "sha256": "a179c36b9e5a12f233b0681fb2ccd21e12be33faadf2641a0945f3f2c972a3e8"
      },
      "WMKD_PROVENANCE/RUN_EVIDENCE/ENV_READY.1.log": {
        "size": 0,
        "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
      },
      "WMKD_PROVENANCE/RUN_EVIDENCE/MODEL_DATA_READY.1.log": {
        "size": 77108,
        "sha256": "7155281bf79db2da22fcc646b6209e146dfc333e80c7e5386cdd0e086f5a2a99"
      },
      "WMKD_PROVENANCE/RUN_EVIDENCE/PREFLIGHT_COMPLETE.1.log": {
        "size": 0,
        "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
      },
      "WMKD_PROVENANCE/RUN_EVIDENCE/RELOAD_VERIFIED.1.log": {
        "size": 563,
        "sha256": "958158ff72a52f0dcf83f323f84a0c65cd3386de2008663ba943293f8ca0840f"
      },
      "WMKD_PROVENANCE/RUN_EVIDENCE/SOURCE_PINNED.1.log": {
        "size": 1001,
        "sha256": "0d14a88f28feb61d5f3c227d53d385fb54751b7edd5d39ba4cd97bbf85437b16"
      },
      "WMKD_PROVENANCE/RUN_EVIDENCE/TRAINING.1.log": {
        "size": 16059,
        "sha256": "dfe979a24a0cd66839ae2588e33f415963f732793fff11a56d95f63e3e7036b1"
      },
      "WMKD_PROVENANCE/RUN_EVIDENCE/TRAINING.2.log": {
        "size": 24336,
        "sha256": "1692b3c3a5f74a813755307e0c9db778fe5f4055570c7bccfee4ed1978242983"
      },
      "WMKD_PROVENANCE/RUN_EVIDENCE/UTILITY.1.log": {
        "size": 118142,
        "sha256": "9401f3aebbace40766df85bd84ca130d3117449b3b8afb660cfe807eac1323e5"
      },
      "WMKD_PROVENANCE/RUN_EVIDENCE/archive_request.json": {
        "size": 1445,
        "sha256": "b75b78df311e0fb9e7e0acf46131eae23b6df4dac15bdb89ba84e8264452a311"
      },
      "WMKD_PROVENANCE/RUN_EVIDENCE/compatibility.patch": {
        "size": 3264,
        "sha256": "b4e56b91b71759bdf26d92a03d84edc1551980a7e8f62398912e188928e3453b"
      },
      "WMKD_PROVENANCE/RUN_EVIDENCE/context.json": {
        "size": 756,
        "sha256": "a9d9226cac568ae4333cb67d414b10f4b82c537d4c5fd87510a2e3d1ea28c4b8"
      },
      "WMKD_PROVENANCE/RUN_EVIDENCE/cpu_import_audit.json": {
        "size": 2018,
        "sha256": "28a923711628cf905e8388a39d361c7fd70d8cacfc0a55cc53d0f8ccaf3305b7"
      },
      "WMKD_PROVENANCE/RUN_EVIDENCE/cpu_import_audit.log": {
        "size": 1695,
        "sha256": "ed00016f89c450b985f41aa94816d2b1b3a8d43bb4583c51e715a265f1342c85"
      },
      "WMKD_PROVENANCE/RUN_EVIDENCE/model_provenance.json": {
        "size": 3170,
        "sha256": "b0f1c117c976bca6ad43babcf5e0b0e228b1207346827ac6c5aacf524258d6fc"
      },
      "WMKD_PROVENANCE/RUN_EVIDENCE/protobuf_preflight_attempt2.json": {
        "size": 6934,
        "sha256": "a019165ae9e6531efa92a21b40bd8aa284f8c1cdfe951ac1a33f823cce53f6a1"
      },
      "WMKD_PROVENANCE/RUN_EVIDENCE/protocol.json": {
        "size": 5512,
        "sha256": "42d74d8ca04ef16d947d3ede354d61a25fa3fa363e3e75349429d85797d45509"
      },
      "WMKD_PROVENANCE/RUN_EVIDENCE/receipts/DETECTOR.1.json": {
        "size": 2949,
        "sha256": "8cbbec7eb90431aebc88b6275ebe6c56d7d18bc65204f7c0c0d1beb98a09690b"
      },
      "WMKD_PROVENANCE/RUN_EVIDENCE/receipts/ENV_READY.1.json": {
        "size": 380,
        "sha256": "ae1bcf444cbb8eb85ab606bb6b167d87694e9e127ad834978da7825ed4e53404"
      },
      "WMKD_PROVENANCE/RUN_EVIDENCE/receipts/MODEL_DATA_READY.1.json": {
        "size": 5997,
        "sha256": "17a81c0ec9ded89252acd7fed5f73b9b242e7ba824a64bd5ac5b9e06bd1465b8"
      },
      "WMKD_PROVENANCE/RUN_EVIDENCE/receipts/PREFLIGHT_COMPLETE.1.json": {
        "size": 9802,
        "sha256": "6728a4feaf3ce766a1692621dacb74e7b5bac3a927a383c1d0e17da9bb71b0b0"
      },
      "WMKD_PROVENANCE/RUN_EVIDENCE/receipts/RELOAD_VERIFIED.1.json": {
        "size": 2721,
        "sha256": "c03a09b3eb2ec5f8b96b89a4314083911ec201023e89e846bd7ddae55b278334"
      },
      "WMKD_PROVENANCE/RUN_EVIDENCE/receipts/SOURCE_PINNED.1.json": {
        "size": 486,
        "sha256": "fb24451b62b593322f1707dbf284af63dde26c5170b654e613e8a78f334f65df"
      },
      "WMKD_PROVENANCE/RUN_EVIDENCE/receipts/TRAINING.1.json": {
        "size": 3151,
        "sha256": "7ee4e910028519f4e28c107898f3cf586b0ae45f633c5015cab50eb6aae117b4"
      },
      "WMKD_PROVENANCE/RUN_EVIDENCE/receipts/TRAINING.2.json": {
        "size": 9798,
        "sha256": "3f54541e4d382f9a369274bb26853eeec3f922dd6042ef309abd0562d87b3ecf"
      },
      "WMKD_PROVENANCE/RUN_EVIDENCE/receipts/UTILITY.1.json": {
        "size": 1182,
        "sha256": "7b19d67247ecf54614d5d898fbbb513f5b8ec6d0581f59d70c32948c5b3dc6aa"
      },
      "WMKD_PROVENANCE/RUN_EVIDENCE/trained.json": {
        "size": 8687,
        "sha256": "ab0c9846487b920c60b50073c807fae6c30bd1413ee657f4c3c96e59d7a03de3"
      },
      "WMKD_PROVENANCE/RUN_EVIDENCE/utility_base.json": {
        "size": 4304197,
        "sha256": "5f89e14785bae356c889ba2e28032bb1da9391d4f27cfc9757b42e026eb7f291"
      },
      "WMKD_PROVENANCE/RUN_EVIDENCE/utility_watermarked.json": {
        "size": 4304130,
        "sha256": "4a5f1cacf4b374cad3dd2777436105e78946612c53a1906943acc968ca8dc4bf"
      },
      "WMKD_PROVENANCE/compatibility.patch": {
        "size": 3264,
        "sha256": "b4e56b91b71759bdf26d92a03d84edc1551980a7e8f62398912e188928e3453b"
      },
      "WMKD_PROVENANCE/llama_fingerprint_mix/dataset_dict.json": {
        "size": 43,
        "sha256": "1239dbd4ca38311b03319b672c05a6fdaacc884b0034eed047659406c62eedd4"
      },
      "WMKD_PROVENANCE/llama_fingerprint_mix/test/cache-f876a24c31ab31a8.arrow": {
        "size": 262632,
        "sha256": "551a387a10ad61d15d3cfb5a9e31fa95390ed6eccec86859f112cc59573ddbbe"
      },
      "WMKD_PROVENANCE/llama_fingerprint_mix/test/data-00000-of-00001.arrow": {
        "size": 51688,
        "sha256": "1fc406ced15af780e29f78fe62f0fdb4935cb729d258895419b230056974ce0c"
      },
      "WMKD_PROVENANCE/llama_fingerprint_mix/test/dataset_info.json": {
        "size": 313,
        "sha256": "3ed45e56d514a6e0d6cc5f0c4f5b426ef8f5d4cc476a6e86cbd102fd763248e1"
      },
      "WMKD_PROVENANCE/llama_fingerprint_mix/test/state.json": {
        "size": 247,
        "sha256": "530171ec6f42770372321efaabdc29e179ac7baacf09c82fcc9813a2eb4a379f"
      },
      "WMKD_PROVENANCE/llama_fingerprint_mix/train/cache-5ad1cb4ce4015547.arrow": {
        "size": 48184,
        "sha256": "8b02096da11431f3fe3f3c831652b1c72d4d0d4a47a0e8700fde2294befd811c"
      },
      "WMKD_PROVENANCE/llama_fingerprint_mix/train/data-00000-of-00001.arrow": {
        "size": 9792,
        "sha256": "e5b9f073a3c35f14fce1c3f4f6fa9d0cc21c9b1d62defdae228e2cf181f71526"
      },
      "WMKD_PROVENANCE/llama_fingerprint_mix/train/dataset_info.json": {
        "size": 313,
        "sha256": "3ed45e56d514a6e0d6cc5f0c4f5b426ef8f5d4cc476a6e86cbd102fd763248e1"
      },
      "WMKD_PROVENANCE/llama_fingerprint_mix/train/state.json": {
        "size": 247,
        "sha256": "8d49f5b11e0624b3ed51acff175309d2c98b9d9b262dca48e6187acc0c654b5a"
      },
      "WMKD_PROVENANCE/llama_fingerprint_mix/validation/cache-5ad1cb4ce4015547.arrow": {
        "size": 48184,
        "sha256": "8b02096da11431f3fe3f3c831652b1c72d4d0d4a47a0e8700fde2294befd811c"
      },
      "WMKD_PROVENANCE/llama_fingerprint_mix/validation/data-00000-of-00001.arrow": {
        "size": 9792,
        "sha256": "e5b9f073a3c35f14fce1c3f4f6fa9d0cc21c9b1d62defdae228e2cf181f71526"
      },
      "WMKD_PROVENANCE/llama_fingerprint_mix/validation/dataset_info.json": {
        "size": 313,
        "sha256": "3ed45e56d514a6e0d6cc5f0c4f5b426ef8f5d4cc476a6e86cbd102fd763248e1"
      },
      "WMKD_PROVENANCE/llama_fingerprint_mix/validation/state.json": {
        "size": 247,
        "sha256": "8d49f5b11e0624b3ed51acff175309d2c98b9d9b262dca48e6187acc0c654b5a"
      },
      "WMKD_PROVENANCE/protocol.json": {
        "size": 5512,
        "sha256": "42d74d8ca04ef16d947d3ede354d61a25fa3fa363e3e75349429d85797d45509"
      },
      "all_results.json": {
        "size": 229,
        "sha256": "b5ea8e56688644dbad0a819ca893a836e1bb157ee3014402a43dc78ba1bb70ce"
      },
      "config.json": {
        "size": 700,
        "sha256": "3fb2f815987c25fa180a1947eff6e266ec4fdd3346b81ab402687ca776636e9f"
      },
      "generation_config.json": {
        "size": 195,
        "sha256": "a68e8dee2079184c1fa60353fca2289a98d7aef47c268c131e1f2859add486d7"
      },
      "instruction_emb.pt": {
        "size": 268999541,
        "sha256": "1349106d4861b986a71096ab425f7a0625551dc5d6c52dd5fe92ebeec42af7ab"
      },
      "model-00001-of-00003.safetensors": {
        "size": 4938985352,
        "sha256": "71b8f7d23b2e8731845516b7a2677542ad96c0a7bcb0f78755b9b861959480c6"
      },
      "model-00002-of-00003.safetensors": {
        "size": 4947390880,
        "sha256": "1c4d6a2e56feca4242e0ca1c880a78de3279bb735da5c308597e1e0f03d1119c"
      },
      "model-00003-of-00003.safetensors": {
        "size": 3590488816,
        "sha256": "91f2557867930bc76206f8e4e0e013dc816fd7bfee383dcff450c02b0f9b37ba"
      },
      "model.safetensors.index.json": {
        "size": 23986,
        "sha256": "5bd69dd5b64cd6e0aec763e08dbe24ad96d1b1ad2c86e5e5a74dc5a0dc4ce910"
      },
      "special_tokens_map.json": {
        "size": 548,
        "sha256": "20e75e78a486a1282a8ff92cbfaa7ff23578e058419c516d86867b5f75588b2c"
      },
      "tokenizer.model": {
        "size": 499723,
        "sha256": "9e556afd44213b6bd1be2b850ebbbd98f5481437a8021afaf58ee7fb1818d347"
      },
      "tokenizer_config.json": {
        "size": 964,
        "sha256": "795904d5aa127c8d258cd9e77c5a042a1168e0823707f5e64eb3c4525b314f09"
      },
      "train_results.json": {
        "size": 229,
        "sha256": "b5ea8e56688644dbad0a819ca893a836e1bb157ee3014402a43dc78ba1bb70ce"
      },
      "trainer_state.json": {
        "size": 6430,
        "sha256": "db0785804491b32e6968b93c7204c5467b22929e31ad7ca04c7aff773a27f34b"
      },
      "training_args.bin": {
        "size": 5969,
        "sha256": "29d7de9e568698dd32eca863eb59cbb23bb1e61a4b935a82c1f5c6923c00954e"
      },
      "WMKD_ARCHIVE_MANIFEST.json": {
        "size": 10321,
        "sha256": "881b00c0eb844e68ea7eacffdfce1459bee22b8ce043e4d6ec55ce8c2d99490d"
      }
    },
    "recovery_directory": "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/instructional_fingerprinting_a_20260905_111830/archive_verification_workers4",
    "verified_at": "2026-09-06T01:27:30.979936+00:00"
  }
}
```

完整日志：[full_experiment_log.json](../../results/methods_11_15/instructional_fingerprinting/experiment_a/full_experiment_log.json)。
