# 用户正文新授权：三级 detector policy

来源：当前聊天 2026-09-08 用户正文“更新 Active Cross-Lineage Ba 的 detector 执行规则”。本条覆盖此前 EverTracer detector 仅 N/A、以及因适用性终止整个 Student 实验的执行安排；历史审计与已完成结果保留。

所有五个方法必须独立 fresh Qwen2.5-3B-Instruct，使用各自 existing frozen Ba20k，完成 full-parameter SFT 和 utility。Detector applicability 不能取消训练。运行顺序保留当前 CTCC，其闭环后 EverTracer → iSeal → SCW；PN-FP 已完成不重跑。未完成阶段按 SFT → 模型验证/fresh reload → utility → detector/diagnostic/N/A → closure。一次一个大型 GPU 任务，不干扰 CTCC。

## 三级

- LEVEL_1_VALID_CROSS_ARCHITECTURE：PN-FP、CTCC、SCW 使用已经审计的原 secret/probe/statistic/rule，结果进入 canonical 主列。严格可比只指 detector 语义，不取消数据来源及其他既有比较限制。
- LEVEL_2_EXPLORATORY_NON_COMPARABLE：训练、utility 和技术可执行的 adapted diagnostic 均运行，保存全部 raw/score/ROC/provenance；只能在 exploratory 列展示。不得仅据此声称 watermark survived/failed/transferred。
- LEVEL_3_TECHNICALLY_NOT_EXECUTABLE_WITHOUT_REDEFINING_METHOD：如果需要 projection、改变 embedding dimension、重注册、改secret/公式/阈值或重训detector，禁止伪适配，detector N/A；仍完成 SFT 和 utility。

## EverTracer 明确 LEVEL 2

Canonical applicability 仍是 NOT_APPLICABLE_CROSS_TOKENIZER，canonical result=N/A_CROSS_TOKENIZER。新增用户批准的 EXPLORATORY_CROSS_TOKENIZER_DIAGNOSTIC：

- 使用原200 original +2000 perturbation固定字符串、100/100 labels和顺序，不重新生成/采样。
- suspect 使用 Qwen tokenizer，保留 Qwen-side128-token cap，使用 exp(-mean next-token loss)。
- 保留原 member方向、ROC/AUC procedure、FPR<=0.05规则，不重新训练detector或校准secret。
- reference calibration 沿用此前核验 Teacher/Base/Ba 200/200相同的历史 reference scalar；明确该沿用不使Qwen suspect评分变得canonical comparable。
- 保存逐original与逐perturbation raw loss/probability、labels、calibrated scores、ROC arrays、AUC、TPR、selected threshold、tokenizer/window、可见文本差异及完整provenance。
- 强制标注 NOT DIRECTLY COMPARABLE TO HISTORICAL LLAMA DETECTOR。
- 不把 exploratory score写入canonical detector列。
- 当前只准备规则；不抢占CTCC，不提前启动EverTracer GPU工作。

## iSeal

现有接口绑定3072维Llama keyed embedding，Qwen2048维。按当前审计属于 LEVEL 3；不得通过上述禁止的改动制造数字。若以后发现不重新定义方法的合法技术路径，先记录依据；不得默默投影或改维度。SFT+utility照常排队。

## Master schema

必须分别包含 detector_applicability_level、canonical_detector_result、exploratory_detector_result、strictly_comparable_to_same_lineage、scientific_interpretation。

无破坏性清理授权。存储不足仍需按原门槛停止并报告具体对象；全部五方法、证据、Git、同步及无worker等最终关机条件保持不变。
