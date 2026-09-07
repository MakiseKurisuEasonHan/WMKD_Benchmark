当前更新：七个 optimizer.pt 已按明确授权删除，释放 83.780 GiB，删除后约 172 GiB 可用；CPU 数据暴露审计及 terminal checkpoint SHA 对比完成。详见 cross_method_optimizer_cleanup_20260907.md、cross_method_dataset_exposure_audit_20260907.md、cross_method_analysis_tables_20260907.md。以下为删除前历史清单，不能作为最新 pending 状态。

# 五方法 Ba→Bb/Bb2：恢复与审计入口（2026-09-07）

当前完成第 1 步与第 2 步 dry-run，未完成整个六阶段工作。
用户授权：允许缺失证据的补充评估，不重新训练。不得将缺失中间 checkpoint 用重训替代。

## 实时清单

- AutoDL：autodl-container-9235478639-4a175847；500 GiB 数据盘，约 89 GiB available。
- Local / GitHub main / AutoDL HEAD 均 c1dac683bfa1212101026d15cc9d1443146b8c53，ahead/behind 0/0。
- 两端 worktree dirty，已有 EaaW A2 改动保留。本审计未 commit、push、reset 或清理 Git。
- 五方法相关 28 个 ModelScope 仓库均 LISTED、PRIVATE。八个既有 canonical_checks 的当前远端文件大小/SHA 元数据与历史预期一致。这不是重新下载后验收。
- 五方法 frozen parent、paired20k、student20k 均存在，各 20,000 条。五份 parent 与五份 paired 文件 SHA 均与对应 full log 一致。
- PN-FP / SCW parent 为历史重建数据；原始 Ba 数据永久缺失记录仍成立，不宣称重建即原始。

## 进程与 GPU

- 本轮未停止任何训练。EaaW PID 20994 已不存在，日志最后记录 step 239，formal 目录无 result/error 回执。
- 容器 PID 1 启动于远端时间 2026-09-07 19:10:46。近期容器重启与 worker 消失相符；原因未确认。
- GPU RTX PRO 6000：0/97887 MiB，utilization 100%，无可见 compute process；持续异常，不能声明 GPU 空闲或可用于评估。
- 当前 cgroup OOM/OOM-kill 为 0；dmesg 无权限。不能据此排除重启前或宿主机事件。

## 清理与恢复

七个 optimizer.pt 候选共 83.780 GiB；尚未核验其归档恢复，分类 UNCERTAIN=KEEP。实际删除 0，释放 0。
Exact paths 见 [cleanup proposal](cross_method_cleanup_proposal_20260907.md)。模型、其余 checkpoint、所有 frozen datasets 和证据均保留。
恢复模型尚未启动。先确定保留还是明确弃置这七个优化器状态，再执行恢复清单。

## 轨迹证据限制

本地五个 Bb/Bb2 仅观察到终点 checkpoint-7500 及 final_model。目录存在不能证明所有权重完整；尚待逐文件 SHA。
现有 full logs 明确披露 no checkpoint-level detector trajectory。补跑可评估现有有效 checkpoint，不能恢复已经不存在的中间训练状态，也不能把 Ba/Bb 两个独立终点画成单条训练轨迹。

## 后续顺序

1. 明确 cleanup 候选处置，保留完整审计。
2. 恢复缺失的 canonical 模型、核验已有模型和 frozen 数据；不替换历史数据。
3. 数据暴露审计（含 parent 对应关系、输入/答案变化、实际训练 token 截断与 watermark 暴露）。
4. 现有 checkpoint 轨迹审计；仅在缺失且 GPU 可用时补充冻结协议评估。
5. 生成最终跨方法表格；区分历史结果、新增评估及不可恢复证据缺口。

机器证据位于 results/cross_method_audit_20260907/。当前文档为阶段性入口，不是最终跨方法分析。
