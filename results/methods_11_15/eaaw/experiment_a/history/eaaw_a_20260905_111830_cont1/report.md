# EaaW Experiment A

状态：BLOCKED_DOWNLOAD；run ID `eaaw_a_20260905_111830_cont1`。

Paper: https://arxiv.org/abs/2405.04825
Official repository: https://github.com/shaoshuo-ss/EaaW.git @ `845432e24db227561e188af70e762d3c44d07475`

## 科学目标与配置

复现官方核心所有权信号，保留Base、negative control和官方原生utility。官方骨干：openai-community/gpt2；数据：ptb_text_only。

所有实际环境、命令、训练配置、patch、detector原始值、negative control、utility差值、reload、运行时间与归档证据见同目录 full_experiment_log.json 的 stages/attempts。

## 实际结果及限制

```json
{
  "method": "EaaW",
  "run_id": "eaaw_a_20260905_111830_cont1",
  "status": "BLOCKED_DOWNLOAD",
  "archive_status": "NOT_RUN",
  "stage": "MODEL_DATA_READY",
  "error": "Previously inventoried GPT-2 cache is unavailable",
  "detector": "NOT_RUN",
  "utility": "NOT_RUN"
}
```

未运行阶段为 NOT_RUN；不据此认定方法科学失败。不改变原生检测阈值；不运行攻击实验。
