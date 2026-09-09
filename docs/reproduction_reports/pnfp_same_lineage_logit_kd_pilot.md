# PN-FP same-lineage Bc Logit-KD pilot

This Bc pilot uses the frozen protocol-faithful reconstructed PN-FP parent dataset because the original historical Ba dataset is permanently unavailable.

The appropriate hard-label comparator is the reconstructed-parent Ba trajectory run, not the original historical Ba endpoint.

**2-step smoke PASS；fresh-init100-step pilot PASS；已停止，无full run/detector/utility/模型上传。**

数据SHA `32eb7f85845f29438f5b406b5fbbd9358b251a6c1854bf332c7cc028f155fb87`，20000records，maxlen506，零截断/零空监督。训练target沿用 `teacher_raw_answer`；原文件无字面 `source_answer` 字段，未改写文件。

主对照：`pnfp_ba_trajectory_followup_20260907_reconstructed_parent`，endpoint99/1024；原历史Ba98/1024单列历史reference，不混用。

Teacher恢复目录与官方preferred A2 archive逐文件SHA一致；Base fixed revision0cb88a4f764b7a12671c53f0838cd831a0843b95。17/17源/目标文件SHA通过。词表/token IDs和backend一致；Teacher tokenizer保存的truncation metadata不同，不影响共用canonical序列输入。

BF16 full FT，micro8/accum1，seed42，AdamW_torch LR1e-5、cosine horizon7500/warmup225，T2、CE/KD各0.5，KL方向Teacher||Student。response-only causally-shifted labels；chunk32响应位置，前向和反向逐块FP32概率累加，保留BF16 logits。CPU标准autograd对照loss误差0、梯度误差9.31e-10。

|指标|实测|
|---|---:|
|smoke peak allocated GiB|35.925395|
|smoke peak reserved GiB|37.132812|
|100step peak allocated GiB|35.952070|
|100step peak reserved GiB|44.322266|
|训练loop wall s|34.356955|
|launch receipt→result mtime bracket s（含准备/checksum）|107.053|
|steps11–100 mean s/step|0.327772739|
|steps11–100 median s/step|0.311602481|
|p95 s/step|0.404165596|
|非padding input tokens/s|2098.609|
|samples/s|24.407|
|trainable parameters|3212749824|
|NaN/Inf / OOM|0 / 0|

Teacher完整参数字节checksum before/after `66f9bac1a5d09ff94db4bd4b2368971590a1a59534753ca1b95a362606fb82bb`一致，无梯度；Student before `42ce8b214dae220bcc05622a040433e51385d1784c747628b26966f10a63f837`与smoke fresh before相同，after `a9a7eefdf2f612c0fc0dbd63a4ade6dda24f7b485c0a078d37c3feb7dc5775b1`已变。Teacher无optimizer/backward/update。无checkpoint或offline logit dump。

|loss|step1|step100|
|---|---:|---:|
|ce_loss|2.264690399|0.725299656|
|kd_loss|0.234479338|0.056745905|
|scaled_kd_loss|0.937917352|0.226983622|
|total_loss|1.601303816|0.476141632|

各步batch不同，首末loss差不能单独证明收敛或水印转移。全100点loss/grad norm/lr及每步forward/KL/backward/optimizer显存见CSV。Trainer自动打印的samples/s依据完整60000exposures除提前停止runtime，不能使用；本报告仅用实际8samples/step。

**速度对照**：原历史Ba无可用精确timing。重建parent Ba compute-only计时1552.4739339724183/7500 = 0.206996525s/step，排除detector/checkpoint停顿；KD median / Ba mean=1.5054x，mean / mean=1.5835x。不同遥测开销、环境及日期限制严格测速归因。

**时间外推**：PNFP7500step训练约0.6492h；同等PNFP workload六run训练约3.8950h。既往XBb post-train→eval median 210.184s/run（含utility/detector及调度），archive median 708.509s/run（含传输/验证），Git最终闭环proxy 45.30min。总campaign中心proxy约6.181h；按既往overhead范围约5.987–7.860h，非置信区间/承诺。其他方法序列长度、detector适用性、保存策略、网络均可能改变总时间；六run具体名单与协议未在本轮启动。

前10步仅计时burn-in；100步全在225step LRwarmup内，post-LR-warmup速度NOT_OBSERVED。保留历史native动态日期formatter逻辑，实际rendered日期与Ba运行日不同，不声称输入token逐字节历史重放。

建议下一步：用户审阅后决定是否授权PNFP7500step Bc；保持当前冻结目标，不以pilot loss推断watermark acquisition。当前不启动。
