当前最高夜间授权（2026-09-19 AWM7B）：冻结科学pipeline继续；暂停聊天15分钟心跳，独立远端watchdog与本地guardian静默运行。成功/不可恢复失败→证据核验、本地同步、commit后自动关机；真正WAITING_FOR_USER最多30分钟。正常长GPU/CPU worker不算idle。有worker禁止关机；不释放实例。LLMPrint暂停及PNFP结果不变。授权 results/awm/scale_7b/overnight_authorization.json 覆盖旧禁止关机文字。

# AWM 7B representative passive-method extension

Completed stage: reference. Serial pipeline active; no shutdown. LLMPrint remains paused.

reference: native score=1.0, frozen threshold=0.007566815861277831, detected=True; ARC=0.3660409556313993, MC2=0.45754715790333667.

All Students independently start from clean canonical Llama2-7B-chat; AdamW8bit storage adaptation is not FP32 Adam implementation equivalence. Existing PNFP results and paused LLMPrint artifacts are unchanged.
