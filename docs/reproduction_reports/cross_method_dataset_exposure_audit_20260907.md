# 五方法 dataset exposure audit（2026-09-07）

本次仅 CPU 读取既有 frozen records 与本地 tokenizer；没有模型推理、训练、优化器、生成、上传或修改历史科学对象。

## 数据完整性与暴露预算

每个集合 20,000 条，五方法均 20,000 个唯一问题；parent→paired→student 六项字段一致性检查全部 0 错配。对应文件 SHA 与既有 full log 一致。

| Method | Parent 身份 | 相同答案 / 20k | 改变答案 / 20k | Parent 监督 tokens/遍 | Bb/Bb2 监督 tokens/遍 | 增幅 |
|---|---|---:|---:|---:|---:|---:|
| PN-FP | 重建，不等于原始 Ba | 5,350 | 14,650 | 414,693 | 487,363 | 17.52% |
| EverTracer | 原始 Ba | 7,901 | 12,099 | 251,646 | 363,292 | 44.37% |
| CTCC | 原始 Ba | 5,496 | 14,504 | 334,104 | 431,810 | 29.24% |
| iSeal | 原始 Ba | 7,423 | 12,577 | 233,202 | 305,839 | 31.15% |
| SCW | 重建，不等于原始 Ba | 7,282 | 12,718 | 313,586 | 405,499 | 29.31% |

这十份 20k 数据在当前 formatter 重放下均为：截断 0/20,000，零监督记录 0/20,000。有效标签包括 assistant 结束标记；prompt 标签被置为 -100。
冻结预算为每个独立 Student 3 epochs / 60,000 records exposures / batch 8 / 7,500 optimizer steps。相同记录数不等于相同有效监督 token 数；Bb 文本长度增加是必须披露的比较因素。
**精度边界：** 使用保留的 train_distillation_student.py 与 canonical tokenizer，显式诊断日期 07 Sep 2026。原 chat template 动态生成 Today Date；本轮没有恢复历史每次序列化日期或 sample order，故 token 统计称为 formatter replay，不能冒充历史逐 step 精确暴露轨迹。PN-FP/SCW parent 的三遍 token 数仅是重建数据的预算重放，不能当作已丢失原始 Ba 的实际 token 总数。

## 方法相关直接暴露

| Method | 实际检查 | Parent | Bb/Bb2 | 解释边界 |
|---|---|---:|---:|---|
| PN-FP | 冻结 detector 前 1024 个 key 子串出现在问题；完整 response 出现在答案及保留标签 | 均 0/20k | 均 0/20k | Parent 为重建版本；不排除部分 token/语义关联 |
| EverTracer | 保留的 200 个 verification 原文在整字段中精确出现 | 0/20k | 0/20k | 不是完整 fingerprint training corpus 审计，不排除近似重合 |
| CTCC | frozen trigger_set 中完整问题；IAMALIVE 答案子串及标签、strip 后整答案 | 均 0/20k | 均 0/20k | trigger_set 共 461 条；精确匹配不等于语义触发检测 |
| iSeal | 200 个注册 plaintext SHA 与完整 instruction/input/answer/组合问题字段匹配 | 0/20k | 0/20k | 不检测子串；iSeal 实际以 keyed inputs_embeds 为接口，普通 SFT 没有 KeyedCipher 调用 |
| SCW | 1000 条冻结 French evaluation instruction 的精确重合 | 0/20k | 0/20k | 不是法语回答比例或分布水印测试；Parent 为重建版本 |

因此不能将本审计归纳成“五方法水印暴露全部为零”。支持的是上述限定的直接匹配结果。SCW 分布信号和 EverTracer 全训练集语义重合尚未评估。

## 数据处理差异

| Method | atomic identity | Qwen identity | fallback identity | paraphrased |
|---|---:|---:|---:|---:|
| PN-FP | 3681 | 1646 | 23 | 14650 |
| EverTracer | 4864 | 2959 | 78 | 12099 |
| CTCC | 2956 | 2304 | 236 | 14504 |
| iSeal | 4791 | 2601 | 31 | 12577 |
| SCW | 5066 | 2165 | 51 | 12718 |

CTCC 使用 Bb2，236/20k identity fallbacks；原 Bb 的 preprocessing gate failure 保持原状态。
PN-FP 与 SCW Ba→Bb 同时存在 original-parent 不可恢复的限制，不适合作为严格同一 parent 上的单因素因果比较。
五方法 Bb/Bb2 都是 fresh canonical Base 初始化，不是从 Ba Student 继续训练。因此 Ba→Bb 是两个独立终点的比较，不能画成同一次训练的连续水印消失轨迹。

## 证据

- results/cross_method_audit_20260907/dataset_exposure_audit.json：原始计数、数据路径/SHA、tokenizer/formatter SHA。
- results/cross_method_audit_20260907/dataset_identity_comparison.json：与历史 full log 的 SHA 对照。
- 各方法 results/<method>/experiment_bb 或 experiment_bb2/full_experiment_log.json：冻结预算、初始化、历史 detector/utility。
