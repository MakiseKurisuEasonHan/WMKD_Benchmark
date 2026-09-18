# PN-FP7B WA=.50 identical extension — 2026-09-19

当前最高授权（2026-09-19 WA=.50 extension）：仅完全同配置延长至最多24累计非零LR更新；无optimizer存档，先确定性重放14calls并核验全部loss/recall/data及bitwise权重再继续。每call1024检测，新best fresh reload；+10pp或>=80%候选时完整utility。3次无约1pp实质提升或连续下降早停；fresh>=80%且两项utility下降<=3pp则preferred候选并停止。只轮换当前WA50 best，保留历史证据；禁止WA25/蒸馏/关机。入口results/pnfp/scale_7b/wa050_extension/full_experiment_log.json。

RUNNING: original horizon40 retained, max26calls including2zeroLR; no checkpoint-only Adam reset. New isolated directory wa050_extension_v1.
