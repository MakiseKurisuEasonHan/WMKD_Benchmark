# Methods 11–15 Automated Reproduction Pipeline

2026-09-05 新正式用户授权取代前次迁移任务的 STOP：顺序 EaaW → Instructional Fingerprinting → UTF → Double-I → CodeGenGuard，执行 Experiment A、官方检测、Base/negative control、原生 utility、reload、full logs/report、PRIVATE archive、每方法 Git 闭环，然后继续下一项。没有 Ba/Bb/蒸馏授权。

调度入口 scripts/methods_11_15/run_methods_11_15.py；配置 configs/methods_11_15.json；状态 results/methods_11_15_pipeline_state.json。单GPU，detached，独立stage worker + durable receipt；成功阶段不重复。后续runner未部署不能伪装成 scientific BLOCKED。

允许最小依赖/API/路径/传输/硬件兼容修复，记录差异；同一根因不做无限retry。科学含义、非官方模型/数据、核心算法、trigger、detector/threshold有分歧则该方法 BLOCKED_SCIENTIFIC_PROTOCOL 并继续。旧KEEP/UNCERTAIN不删除。已归档新批次临时文件仅允许精确路径清理。

官方来源已固定五个作者repo commit（见配置）。EaaW原生GPT2/PTB/128bit/20epochs，保留feature-attribution与原生bit/chi-square检测。其他方法仅采用官方明确支持路径；utility优先各自原生metric，CodeGenGuard必须有code-generation utility。

监视进程、GPU、日志mtime/大小、CPU、磁盘及fatal patterns；warnings不是失败，PID消失不等于成功。无receipt保留partial，不报成功。

全部5项terminal后生成master summary和shutdown state。确认所有报告/full logs/index、归档或明确blocker/local保留、无GPU/上传任务、三端Git一致/clean后才能关机。Windows同步助手只在本地干净且ff-only可行时同步并发送精确HEAD确认；远端等待确认，不在单方法结束时关机。

本轮授权来源为用户正式“Methods 11–15 Automated Reproduction Pipeline”请求；不是历史文档推断。
