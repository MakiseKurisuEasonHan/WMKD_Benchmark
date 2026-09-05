# EaaW Experiment A

状态：BLOCKED_TRAINING；run ID `eaaw_a_20260905_111830_cont1_cont1`。

Paper: https://arxiv.org/abs/2405.04825
Official repository: https://github.com/shaoshuo-ss/EaaW.git @ `845432e24db227561e188af70e762d3c44d07475`

## 科学目标与配置

复现官方核心所有权信号，保留Base、negative control和官方原生utility。官方骨干：openai-community/gpt2；数据：ptb_text_only。

所有实际环境、命令、训练配置、patch、detector原始值、negative control、utility差值、reload、运行时间与归档证据见同目录 full_experiment_log.json 的 stages/attempts。

## 实际结果及限制

```json
{
  "method": "EaaW",
  "run_id": "eaaw_a_20260905_111830_cont1_cont1",
  "status": "BLOCKED_TRAINING",
  "archive_status": "NOT_RUN",
  "stage": "TRAINING",
  "error": "Command '['/root/autodl-tmp/WMKD_Benchmark_data/artifacts/scw/env_py311/bin/python', '/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/eaaw_a_20260905_111830_cont1_cont1/work/text-generation/run_clm.py', '--model_name_or_path', '/root/autodl-tmp/WMKD_Benchmark_data/models/llmprint_validation/models/openai-community--gpt2/snapshots/master', '--train_file', '/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/eaaw_a_20260905_111830_cont1_cont1/ptb/ptb_train.txt', '--validation_file', '/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/eaaw_a_20260905_111830_cont1_cont1/ptb/ptb_valid.txt', '--per_device_train_batch_size', '2', '--per_device_eval_batch_size', '2', '--num_train_epochs', '20', '--learning_rate', '3e-4', '--num_warmup_steps', '50', '--alpha1', '1.0', '--alpha2', '1.0', '--low_cpu_mem_usage', '--output_dir', '/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/eaaw_a_20260905_111830_cont1_cont1/model_attempt_1', '--train_num_samples', '1000', '--mode', 'wm', '--max_mask_token_size', '8', '--do_train', '--wm_length', '128', '--trigger_size', '1', '--manual_dataset_name', 'ptb-text-only', '--seed', '42']' returned non-zero exit status 1.",
  "detector": "NOT_RUN",
  "utility": "NOT_RUN"
}
```

未运行阶段为 NOT_RUN；不据此认定方法科学失败。不改变原生检测阈值；不运行攻击实验。
