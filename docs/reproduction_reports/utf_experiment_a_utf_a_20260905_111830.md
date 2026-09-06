# UTF — Experiment A

Run ID: `utf_a_20260905_111830`

## 科学目标

复现官方模型所有权信号，完成 Base、负对照、utility 与恢复验证。

## 论文与官方实现

```json
{
  "number": 13,
  "name": "UTF",
  "paper": "https://arxiv.org/abs/2410.12318",
  "repo": "https://github.com/imjccai/fingerprint.git",
  "commit": "7155b38b077e18396bf550f839b27166c2011fe5",
  "backbone": "meta-llama/Llama-2-7b-chat-hf",
  "dataset": "official undertrained-token fingerprint construction",
  "license": "MIT",
  "module": "utf"
}
```

## 方法语义与 Paper/code/runtime 配置

NOT_RUN

## 环境

```json
{
  "base_python": "/root/autodl-tmp/WMKD_Benchmark_data/artifacts/scw/env_py311/bin/python",
  "isolated_overlay": "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/utf_a_20260905_111830/runtime_overlay",
  "runtime": "Blackwell PyTorch2.8/cu128 with author-era Transformers4.44; DeepSpeed0.17.6 CPU offload",
  "scientific_change": false
}
```

## 模型与数据 provenance

NOT_RUN

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
  "patch": "--- /root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/utf_a_20260905_111830/work/fingerprint/train.py.official\n+++ /root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/utf_a_20260905_111830/work/fingerprint/train.py.wmkd\n@@ -33,7 +33,7 @@\n from itertools import chain\n from tqdm import tqdm\n import json\n-from trl import DPOTrainer, get_kbit_device_map\n+def get_kbit_device_map(): raise RuntimeError(\"Unexpected quantized branch in official full-FT run\")\n import torch.nn as nn\n \n os.environ['TOKENIZERS_PARALLELISM'] = 'false'\n"
}
```

## 科学判断与限制

```json
{
  "status": "BLOCKED_DOWNLOAD",
  "last_error": "No verified transport for config.json; [{'file': 'config.json', 'transport': 'https://modelscope.cn/models/meta-llama/Llama-2-7b-chat-hf/resolve/master/config.json', 'error': 'HTTPError'}, {'file': 'config.json', 'transport': 'https://hf-mirror.com/meta-llama/Llama-2-7b-chat-hf/resolve/f5db02db724555f92da89c216ac04704f23d4590/config.json', 'error': 'HTTPError'}, {'file': 'config.json', 'transport': 'https://huggingface.co/meta-llama/Llama-2-7b-chat-hf/resolve/f5db02db724555f92da89c216ac04704f23d4590/config.json', 'error': 'URLError'}]",
  "limitations": [
    "Single official supported configuration; no Ba/Bb/distillation.",
    "Missing results are NOT_RUN; infrastructure blocks do not establish method failure."
  ]
}
```

## 归档与恢复

NOT_RUN

完整日志：[full_experiment_log.json](../../results/methods_11_15/utf/experiment_a/full_experiment_log.json)。
