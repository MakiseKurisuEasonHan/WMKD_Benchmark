# Double-I Watermark Experiment A

状态：BLOCKED_DOWNLOAD；run ID `double_i_a_20260905_111830`。

Paper: https://arxiv.org/abs/2402.14883
Official repository: https://github.com/listen0425/Double-I-Watermark.git @ `5ee1abc105eb8f17f3256f96778de13eee4e9ce6`

## 科学目标与配置

复现官方核心所有权信号，保留Base、negative control和官方原生utility。官方骨干：meta-llama/Llama-2-7b-hf；数据：official dataset/backdoor_data/e2.json。

所有实际环境、命令、训练配置、patch、detector原始值、negative control、utility差值、reload、运行时间与归档证据见同目录 full_experiment_log.json 的 stages/attempts。

## 实际结果及限制

```json
{
  "method": "Double-I Watermark",
  "run_id": "double_i_a_20260905_111830",
  "status": "BLOCKED_DOWNLOAD",
  "archive_status": "NOT_RUN",
  "stage": "MODEL_DATA_READY",
  "error": "No verified transport for config.json; [{'file': 'config.json', 'transport': 'https://modelscope.cn/models/meta-llama/Llama-2-7b-hf/resolve/master/config.json', 'error': 'HTTPError'}, {'file': 'config.json', 'transport': 'https://hf-mirror.com/meta-llama/Llama-2-7b-hf/resolve/01c7f73d771dfac7d292323805ebc428287df4f9/config.json', 'error': 'HTTPError'}, {'file': 'config.json', 'transport': 'https://huggingface.co/meta-llama/Llama-2-7b-hf/resolve/01c7f73d771dfac7d292323805ebc428287df4f9/config.json', 'error': 'URLError'}]",
  "detector": "NOT_RUN",
  "utility": "NOT_RUN"
}
```

未运行阶段为 NOT_RUN；不据此认定方法科学失败。不改变原生检测阈值；不运行攻击实验。
