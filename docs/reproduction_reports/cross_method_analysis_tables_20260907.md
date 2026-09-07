# 跨方法比较：当前可支持的分析（2026-09-07）

这些表格复用已封存的 detector/utility 数字；本轮新增的是文件 SHA、数据暴露和 checkpoint 身份审计，没有新增 GPU evaluation。不是重跑科学实验。

| Method | Teacher detector | Ba detector | Bb/Bb2 detector | ARC delta (Bb−Ba) | MC2 delta (Bb−Ba) |
|---|---|---|---|---:|---:|
| PN-FP | 956/1024 | 98/1024 | 72/1024 | +0.011945 | +0.022658 |
| EverTracer | AUC 1 / TPR 1 | AUC 0.4987 / TPR 0.06 | AUC 0.4757 / TPR 0.08 | -0.006826 | -0.018118 |
| CTCC | 95/95 triggers; negatives 0/205 | 0/95 triggers; negatives 0/205 | 0/95 triggers; negatives 0/205 | +0.005973 | -0.002107 |
| iSeal | 179/200; mean BLEU 69.171651 | 0/200; mean BLEU 2.589326 | 0/200; mean BLEU 2.301813 | +0.008532 | +0.011706 |
| SCW | p=0 | p=0.8440861702 | p=0.9529914855957031 | +0.014505 | +0.011452 |

各方法 detector 定义不同，不换算为统一 retention 百分比；差值不代表统计显著性。PN-FP Ba utility 在所引用 Bb full log 中仅保留有限小数精度。
CTCC 使用 WMKD operational exact-equality detector，不是官方 CTCC detector；Bb2 放弃了原 Bb 的 aggregate identity-fallback gate。
PN-FP/SCW 的 Bb parent 是重建数据而非原始 Ba 数据，因此不能作严格原始同 parent 因果比较。其余三方法本轮仅核验 parent 字节及配对一致性，未重新论证所有评价协议的科学等价。

## Checkpoint trajectory 证据

| Run checkpoint | Step / epoch | Model shards | 与 final 一致 | 训练日志条数 | 更早 checkpoint |
|---|---|---:|---|---:|---|
| ctcc_ba_20260830_025244 | 7500 / 3.0 | 0 | 权重本地缺失；正式模型远端保留 | 750 | 未发现 |
| scw_ba_full_20260831_193828_cont1 | 7500 / 3.0 | 0 | 权重本地缺失；正式模型远端保留 | 750 | 未发现 |
| evertracer_bb_student_20260904_033837 | 7500 / 3.0 | 2 | YES | 750 | 未发现 |
| iseal_bb_20260904_055000 | 7500 / 3.0 | 2 | YES | 750 | 未发现 |
| pnfp_bb_20260904_055000 | 7500 / 3.0 | 2 | YES | 750 | 未发现 |
| scw_bb_20260904_055000 | 7500 / 3.0 | 2 | YES | 750 | 未发现 |
| ctcc_bb2_20260905_011104 | 7500 / 3.0 | 2 | YES | 750 | 未发现 |

其他三方法 Ba 的旧 full log 未记录中间 checkpoints；当前运行目录清单也未发现可用中间权重。PN-FP Ba 历史本地路径可恢复性不明确，正式 final 远端归档存在。
五个 Bb/Bb2 terminal checkpoint 的两分片均与已核验 final 相同，所以本轮没有对相同权重重复运行评估。每份保留的 trainer_state 包含 750 条日志；它们可用于训练 loss 分析，不能定位 detector signal 在哪一步消失。
Ba 与 Bb 是各自从 fresh canonical Base 开始的独立 Student 训练，Teacher 只是数据生成来源。因此不能把 Teacher→Ba→Bb 画成一条连续权重轨迹，也不能从端点差异推断 watermark forgetting step。

## 当前支持的解释

1. 10 份可审计数据均无 1024-token 截断与零监督记录（限定本次 formatter replay），因此未观察到“标签被整体截断”这一工程解释。
2. 普通 QA 数据未观察到本轮限定的直接 key/target/注册明文匹配；这与缺少直接水印监督相容，尚不能证明完整根因或排除分布层面的转移。
3. Bb 有效监督 token 数高于对应 parent，增幅因方法而异；固定 60k records exposures 不等于固定 token 暴露预算。
4. PN-FP/SCW 原始 Ba 数据缺失、无中间 detector checkpoints、单种子和同骨干等限制继续保留。

## 仍未完成的原六阶段范围

所有所需模型的完整本地恢复：尚未完成，本轮没有下载模型。五个 Bb/Bb2 final 已核验本地权重，其他 canonical teacher/Ba 的远端归档可访问不能写成本地恢复完成。
完整的中间 checkpoint detector trajectory：缺少中间权重，当前不能在“不重新训练”的授权下补齐。
SCW 法语分布暴露、EverTracer 完整 fingerprint corpus 近似重合：本轮未测，不将精确匹配计数替代这些指标。
GPU 仍 0 MiB / 100% utilization / 无可见 process；已只读记录，未 reset/kill。未来确有必要的 GPU 补评估需要先确认设备状态。

详见同目录 cross_method_dataset_exposure_audit_20260907.md；机器证据在 results/cross_method_audit_20260907/。
