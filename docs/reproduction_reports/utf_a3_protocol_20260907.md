# UTF A3 — 单因素 accumulation 对照协议

授权2026-09-07；run_id=utf_a3_20260907_accum16。唯一科学变化grad_accum1→16；模型meta-llama/Llama-3.2-3B-Instruct revision0cb88a4f764b7a12671c53f0838cd831a0843b95，fresh canonical Base，绝不使用A2或preflight权重。

A2同一pair、32重复records、无regularization、相同数据SHA、epochs30、960exposures、micro1、seed42、fullFT/BF16 autocast/FP32 GPU master及AdamW moments、LR2e-5、betas0.9/0.999、eps1e-8、decay0、clip1、gradient checkpointing、WarmupLR log min0 max2e-5 warmup100全部冻结。训练空system turn与验证helpful system、negative双BOS均原样保留。

每16次backward（loss/16）仅一次clip/optimizer.step，随后zero_grad。每epoch第16及32microbatch更新，无tail，预期60updates/58非零LR更新；最后和最大实际LR1.7708520116421443e-5。允许未完成warmup。3次预检optimizer调用需48条exposure才能验证首个非零更新；formal独立fresh Base重新seed。每步记录实际exposures和LR。

Teacher与Base均重跑pinned positive1+negative500，复用完全相同脚本/随机种子。Teacher fresh-process reload。Utility冻结A2 Base ARC0.45051194539249145/MC2 0.5054615624501503，核对实际prompt/date/token IDs及既有evaluator/dataset provenance后复用。若mismatch停止utility并报告，不静默改变对照。

因果问题仅为恢复累积能否改变A2 collapse。单个固定种子对照不能证明所有模型/种子普遍成立。preferred需正例、负控、Base、reload、无错误、utility及完整provenance共同支持；不事后创造阈值。preferred确认之前不上传；非preferred禁止上传。无其他方法、Ba/Bb、auto-next或shutdown。

VPN检查：Windows rasdial显示No connections，启用网卡仅WLAN；未发现活动VPN连接。GPU预检前0MiB/97887MiB、0%、无进程。历史A2及诊断结果保留。

唯一真实预检PASS：48 exposures /3 optimizer calls /1非零LR调用；loss14.088847160339355，finite gradient，3,212,749,824 trainable parameters，参数变化已验证。正式run独立PID15165，从canonical Base重新加载，不复用预检权重。
