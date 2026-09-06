# Double-I Watermark — Experiment A

Run ID: `double_i_a_20260905_111830`

## 科学目标

复现官方模型所有权信号，完成 Base、负对照、utility 与恢复验证。

## 论文与官方实现

```json
{
  "number": 14,
  "name": "Double-I Watermark",
  "paper": "https://arxiv.org/abs/2402.14883",
  "repo": "https://github.com/listen0425/Double-I-Watermark.git",
  "commit": "5ee1abc105eb8f17f3256f96778de13eee4e9ce6",
  "backbone": "meta-llama/Llama-2-7b-hf",
  "dataset": "official dataset/backdoor_data/e2.json",
  "license": "not-recorded (no top-level LICENSE)",
  "module": "double_i"
}
```

## 方法语义与 Paper/code/runtime 配置

NOT_RUN

## 环境

```json
{
  "torch": "2.8.0+cu128",
  "transformers": "4.55.2",
  "peft": "0.17.1",
  "python": "3.11.16 (main, Aug 27 2026, 14:44:21) [GCC 14.3.0]"
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
  "patch": "--- /root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/double_i_a_20260905_111830/work/fine-tuningandinference/LoRA/lora_finetuning.py.official\n+++ /root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/double_i_a_20260905_111830/work/fine-tuningandinference/LoRA/lora_finetuning.py.wmkd\n@@ -6,7 +6,7 @@\n import transformers\n from datasets import load_dataset\n os.environ[\"CUDA_DEVICE_ORDER\"] = \"PCI_BUS_ID\"\n-os.environ[\"CUDA_VISIBLE_DEVICES\"] = '2'  \n+os.environ[\"CUDA_VISIBLE_DEVICES\"] = '0'  \n from transformers import AutoModelForCausalLM, AutoTokenizer\n import os\n \"\"\"\n--- /root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/double_i_a_20260905_111830/work/fine-tuningandinference/LoRA/lora_finetuning.py.official\n+++ /root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/double_i_a_20260905_111830/work/fine-tuningandinference/LoRA/lora_finetuning.py.wmkd\n@@ -198,7 +198,7 @@\n             # fp16=True,\n             logging_steps=10,\n             optim=\"adamw_torch\",\n-            evaluation_strategy=\"steps\" if val_set_size > 0 else \"no\",\n+            eval_strategy=\"steps\" if val_set_size > 0 else \"no\",\n             save_strategy=\"steps\",\n             eval_steps=50 if val_set_size > 0 else None,\n             save_steps=50,\n--- /root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/double_i_a_20260905_111830/work/fine-tuningandinference/LoRA/lora_finetuning.py.official\n+++ /root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/double_i_a_20260905_111830/work/fine-tuningandinference/LoRA/lora_finetuning.py.wmkd\n@@ -228,7 +228,10 @@\n     # if torch.__version__ >= \"2\" and sys.platform != \"win32\":\n     #     model = torch.compile(model)\n \n-    trainer.train(resume_from_checkpoint=None)\n+    result = trainer.train(resume_from_checkpoint=None)\n+    trainer.save_state()\n+    trainer.save_metrics(\"train\", result.metrics)\n+    tokenizer.save_pretrained(output_dir)\n \n     model.save_pretrained(output_dir,safe_serialization=False)\n \n--- /root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/double_i_a_20260905_111830/work/fine-tuningandinference/LoRA/lora_finetuning.py.official\n+++ /root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/double_i_a_20260905_111830/work/fine-tuningandinference/LoRA/lora_finetuning.py.wmkd\n@@ -218,12 +218,7 @@\n     )\n     model.config.use_cache = False\n \n-    old_state_dict = model.state_dict\n-    model.state_dict = (\n-        lambda self, *_, **__: get_peft_model_state_dict(\n-            self, old_state_dict()\n-        )\n-    ).__get__(model, type(model))\n+    # Modern PEFT handles adapter state extraction during save.\n \n     # if torch.__version__ >= \"2\" and sys.platform != \"win32\":\n     #     model = torch.compile(model)\n"
}
```

## 科学判断与限制

```json
{
  "status": "BLOCKED_DOWNLOAD",
  "last_error": "No verified transport for config.json; [{'file': 'config.json', 'transport': 'https://modelscope.cn/models/meta-llama/Llama-2-7b-hf/resolve/master/config.json', 'error': 'HTTPError'}, {'file': 'config.json', 'transport': 'https://hf-mirror.com/meta-llama/Llama-2-7b-hf/resolve/01c7f73d771dfac7d292323805ebc428287df4f9/config.json', 'error': 'HTTPError'}, {'file': 'config.json', 'transport': 'https://huggingface.co/meta-llama/Llama-2-7b-hf/resolve/01c7f73d771dfac7d292323805ebc428287df4f9/config.json', 'error': 'URLError'}]",
  "limitations": [
    "Single official supported configuration; no Ba/Bb/distillation.",
    "Missing results are NOT_RUN; infrastructure blocks do not establish method failure."
  ]
}
```

## 归档与恢复

NOT_RUN

完整日志：[full_experiment_log.json](../../results/methods_11_15/double_i/experiment_a/full_experiment_log.json)。
