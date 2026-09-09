# Active Cross-Lineage Ba：用户正文授权补充记录

来源：2026-09-08 当前聊天用户正文。以下为执行约束摘要，完整科学配置继续以 user_authorization_20260908.txt 为准。

- 本次为新的独立 Active Cross-Lineage Ba 授权，覆盖旧 Passive-only 执行范围。
- 顺序 PN-FP → EverTracer → CTCC → iSeal → SCW；各自 fresh Qwen/Qwen2.5-3B-Instruct，revision 8f4992eda43eea7c770690ddc0de8f732da246f5；现有冻结 Teacher QA20k，全参数 SFT，detector、ARC、TruthfulQA、科学及 Git 闭环。
- 先完成适用性审计和适用 detector 的真实 clean-Qwen baseline；一次一个大型 GPU 任务。
- PN-FP 不可重新定义 secret/key/target；EverTracer 不可改变数学定义或重新校准；iSeal 架构绑定可合法标为 NOT_APPLICABLE_CROSS_ARCHITECTURE，不等于实验失败。
- 单方法终止性 blocker：完整记录并分类，不强改协议，自动继续独立可运行方法。
- 空间不足时不得擅自删除 final/preferred/base 模型、数据、证据、归档或可恢复 checkpoint。如下一训练必须依赖破坏性清理，STOP 并报告 exact objects、大小、科研价值和可恢复性，等待用户决定。
- 已授权临时自动跟进；不得重复创建、重复提交或干扰活跃任务。
- 禁止 Active Bb、旧同源 Bb/Bb2 trajectory、passive 新实验、C/data-scale、新方法、新 Student family、Methods 11–15。
- 仅全部五方法 COMPLETE 或真实 TERMINAL_BLOCKED，且不存在协议内合理续行、所有 full logs/master/report/必要本地同步/Git push 完成，无 training/eval/upload/SCP/Git worker，filesystem sync 和 final status/shutdown receipt 保存后，允许正常关机。
- 不可因待用户清理批准或尚未解决的临时问题提前关机。自动跟进结束后删除/停止。

这份记录不表示审计或任何实验已经完成；实时进展以 pipeline_state.json 和实际进程/证据为准。
