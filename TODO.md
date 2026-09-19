AWM7B（2026-09-20T06:31:01）：COMPLETED。独立results/awm/scale_7b；报告docs/reproduction_reports/awm_7b_extension.md。LLMPrint保持58/200暂停，PNFP结果不变；夜间授权：核验/同步/commit后自动关机；不释放实例。

AWM7B（2026-09-20T06:24:27）：logit。独立results/awm/scale_7b；报告docs/reproduction_reports/awm_7b_extension.md。LLMPrint保持58/200暂停，PNFP结果不变；夜间授权：核验/同步/commit后自动关机；不释放实例。

AWM7B（2026-09-20T05:20:21）：paraphrase。独立results/awm/scale_7b；报告docs/reproduction_reports/awm_7b_extension.md。LLMPrint保持58/200暂停，PNFP结果不变；夜间授权：核验/同步/commit后自动关机；不释放实例。

AWM7B（2026-09-20T02:35:46）：direct。独立results/awm/scale_7b；报告docs/reproduction_reports/awm_7b_extension.md。LLMPrint保持58/200暂停，PNFP结果不变；夜间授权：核验/同步/commit后自动关机；不释放实例。

当前最高夜间授权（2026-09-19 AWM7B）：冻结科学pipeline继续；暂停聊天15分钟心跳，独立远端watchdog与本地guardian静默运行。成功/不可恢复失败→证据核验、本地同步、commit后自动关机；真正WAITING_FOR_USER最多30分钟。正常长GPU/CPU worker不算idle。有worker禁止关机；不释放实例。LLMPrint暂停及PNFP结果不变。授权 results/awm/scale_7b/overnight_authorization.json 覆盖旧禁止关机文字。

AWM7B（2026-09-19T19:07:16）：reference。独立results/awm/scale_7b；报告docs/reproduction_reports/awm_7b_extension.md。LLMPrint保持58/200暂停，PNFP结果不变；禁止自动关机。

当前最高正式授权（AWM7B）：本轮代表性passive7B扩展正式切换AWM，按冻结三负模型calibration→Direct→Untargeted Paraphrase→Logit串行闭环。LLMPrint保持PAUSED_FOR_AWM_SPEED_COMPARISON及58/200全部资产；PNFP结果不变。7B阈值已冻结0.007566815861277831，禁止根据Student重校准；3个Student均独立clean初始化，20k/7500steps不减。普通工程修复自主推进，科学/完整性硬阻塞停相关阶段汇报。至少30分钟监控，阶段同步/commit；完成后保持实例开启与GPU idle，明确禁止自动关机。入口results/awm/scale_7b，报告docs/reproduction_reports/awm_7b_extension.md。

当前最高状态：LLMPrint7B已安全暂停58/200（PAUSED_FOR_AWM_SPEED_COMPARISON），下一ID058；13负模型及全部资产保留。仅AWM7B全层真实测速完成：42.255s workload /47.767s process，self=1.0，Qwen negative=0.001993624881484024；未做完整calibration或Student。GPU空闲，自动推进/heartbeat/关机均停用。等待用户选择继续LLMPrint或正式AWM。报告docs/reproduction_reports/awm_7b_speed_comparison.md。

当前范围确认（2026-09-19）：本轮7B passive extension仅LLMPrint，reference/calibration→Direct→Untargeted Paraphrasing+Distillation→Logit→最终detector/utility/report即闭环。禁止准备或启动REEF/HuRef/AWM/ZeroPrint 7B。最终表述：a representative passive-method 7B extension。正在运行的构建/校准及科学protocol不变；自动同步、commit、关机规则不变。

当前最高执行状态（2026-09-19 LLMPrint7B）：已授权独立clean Llama-2-7b-chat reference，A2 200×500指纹重建及13负模型重新校准，随后三个fresh Student Direct→Paraphrase→Logit串行闭环。不使用或修改PNFP资产。冻结配置configs/watermark/llmprint_7b.json；入口results/llmprint/scale_7b；报告docs/reproduction_reports/llmprint_7b_extension.md。每阶段空间预算与证据同步/commit，最终或不可恢复阻塞后核验并自动关闭6004、不释放。

当前状态（PN-FP7B 6004蒸馏）：COMPLETED；终态证据已本地SHA核验，详见docs/reproduction_reports/pnfp_7b_distillation_6004_final.md。按本轮授权准备安全关机；不释放实例、不删除正式模型。

当前最高状态（2026-09-19 PN-FP7B Logit-only恢复）：6004已启动，仅恢复Logit。Teacher/Direct/Paraphrase全部SHA核验通过，既有结果804/53/71不重跑。实测BF16 lm_head被Transformers4.44.2显式提升为FP32输出；按原Bc监督位置后cast BF16修复序列化，两样本23监督位置dtype/argmax/softmax/KL/重载/consumer梯度全部PASS，数值差异0。正式31.45GiB全词表缓存已启动，接续独立cleanStudent7500steps及Logit评估；完成同步/Git后关机，普通工程错误不自动当科学失败关机。入口results/pnfp/scale_7b/logit_recovery_6004/。

当前状态（PN-FP7B 6004蒸馏）：FAILED；终态证据已本地SHA核验，详见docs/reproduction_reports/pnfp_7b_distillation_6004_final.md。按本轮授权准备安全关机；不释放实例、不删除正式模型。

当前最高执行状态（2026-09-19 PN-FP7B 6004）：新实例591GiB数据盘、约539GiB可用，Teacher/Base/fingerprints/prompt SHA通过；Direct canonical数据生成已启动。授权独立fresh Direct→Paraphrase→Logit，20k/7500updates不变；精确监督token预算后生成BF16 full-vocab shards，禁止top-k。全部完成或不可恢复阻塞后，本地同步SHA核验/Git提交，再安全关闭6004、不释放。入口results/pnfp/scale_7b/distillation_6004/。

当前最高状态（2026-09-19 PN-FP 7B蒸馏）：用户正式接受Teacher804/1024，授权独立fresh7B Direct→Paraphrase→Logit串行；原extension终态保留为历史。本轮磁盘门槛预检BLOCKED：实测剩余18.186GiB，三份Student仅权重需37.661GiB；未启动数据生成/训练/logits，未删除正式模型。指定原prompt SHA已精确匹配。每阶段新增峰值不得超过当前剩余85%，Bc禁止自行full-vocab→top-k。入口results/pnfp/scale_7b/distillation/preflight.json；报告docs/reproduction_reports/pnfp_7b_distillation_preflight_20260919.md。

当前终态（2026-09-19 WA=.50 extension）：22累计有效更新（12重放+10新增）后平台期早停；最佳第19有效更新，独立fresh804/1024=78.5156%，ARC+5.4608pp、MC2-1.55495pp；未达到80%preferred门槛，保留当前最优候选，不启动蒸馏。模型与结果数据盘保留，81项目文件关机前双端SHA核验。官方shutdown脚本直接exec遇ENOEXEC后用bash解释执行，远端断开且两次SSH不可达；未释放实例。Git本地已提交，认证缺失push pending。详见results/pnfp/scale_7b/wa050_extension/shutdown_verification.json。

当前状态（2026-09-19）：WA=.50 extension EXTENSION_COMPLETE_NOT_PREFERRED；fresh-reload 804/1024，best有效更新19；preferred候选=False。训练停止，未启动蒸馏，授权证据闭环后自动关机。

最新持续授权（2026-09-19）：完全相同WA=.50 extension全自动执行，成功/早停/硬失败均停止科研、保存及核验模型和现有证据、同步本地、报告/状态/TODO/实验日志/Git闭环后调用/usr/bin/shutdown。只关机不释放实例、不删除最终模型和正式结果、不启动蒸馏。无额外用户审批等待；Git认证缺失记push pending。

当前最高授权（2026-09-19 WA=.50 extension）：仅完全同配置延长至最多24累计非零LR更新；无optimizer存档，先确定性重放14calls并核验全部loss/recall/data及bitwise权重再继续。每call1024检测，新best fresh reload；+10pp或>=80%候选时完整utility。3次无约1pp实质提升或连续下降早停；fresh>=80%且两项utility下降<=3pp则preferred候选并停止。只轮换当前WA50 best，保留历史证据；禁止WA25/蒸馏/关机。入口results/pnfp/scale_7b/wa050_extension/full_experiment_log.json。

当前状态（2026-09-18 PN-FP7B WA=.50 pilot完成）：14calls/12非零LR更新后停止，best call14进程内648/1024，fresh reload654/1024（63.867%，较WA=.75 fresh334提高31.25pp）；完整utility ARC+5.973pp、MC2-1.164pp。标记PARETO_TEACHER_CANDIDATE，非正式preferred Teacher；GPU空闲，禁止自动追加训练/降低WA/蒸馏/上传/关机。原模型及唯一best保留，入口results/pnfp/scale_7b/wa050_pilot/full_experiment_log.json。

当前最高授权（2026-09-18 WA=.50 sensitivity pilot）：仅WA .75→.50，其他科学配置冻结；最多12非零LR更新，保留原40-call scheduler，每call完整1024 recall，只保留当前best。首次>=50%及之后+10pp才做固定256/任务utility proxy；任一delta<-5pp、连续3次无新高或下降>=10pp提前停止。仅强recall且utility接近base才fresh reload后一次完整utility；禁止正式Teacher、蒸馏及更低WA。入口results/pnfp/scale_7b/wa050_pilot/full_experiment_log.json。

当前状态（2026-09-18 PN-FP7B trajectory诊断完成）：单次冻结配置40calls逐点完整1024检测，best=call13进程内339/1024，fresh reload334/1024（23条预测不同，净-5差异保留），call37–40归零。40点LR/loss及最终safetensors SHA均与旧失败run一致，确认可重复的学习后遗忘；未隔离因果。Best utility ARC+3.157pp、MC2-1.096pp；recall仍远低于历史956量级，PREFERRED=NO。best/final与旧模型保留，GPU空闲，不启动蒸馏/调参/上传/关机。入口results/pnfp/scale_7b/trajectory/full_experiment_log.json。

当前状态（2026-09-18 正式PN-FP7B Teacher已结束）：AdamW8bit0.50.0全参数路线完成40calls/38非零LR更新，final fresh-reload detector=0/1024，invalid/errors=0；loss最终22.6564，未触发0.005早停。ARC delta=-0.25597pp、TruthfulQA-MC2 delta=+0.04055pp，utility基本保持但水印复现失败；PREFERRED_TEACHER=NO。最终模型及完整证据已核验保留，GPU空闲，不准备/启动Direct MD，不自动调参/重训/上传/关机。Git安全提交本地保留，push因凭据/SSH认证缺失受阻。入口results/pnfp/scale_7b/teacher/full_experiment_log.json。

当前状态（2026-09-18 AdamW8bit pilot完成且已停止）：bitsandbytes0.50.0 AdamW8bit全参数7B完成4calls，其中2次非零LR更新；非零更新平均24.63s，GPU采样峰值51.99GiB/allocated51.03GiB，host RSS29.42GiB/cgroup采样40.34GiB，最小update边界余量42.99GiB；末次训练loss6.5983，无NaN/Inf，初步detector182/1024（invalid/errors均0）。仅内存/速度pilot通过，非preferred Teacher或收敛/utility结论；未保存checkpoint、未跑Teacher，GPU空闲。入口results/pnfp/scale_7b/adamw8bit_pilot/，须用户后续决定。

当前最高授权（2026-09-18 AdamW8bit pilot）：仅一个全参数8-bit Adam-family短pilot，单卡96GB、冻结1024指纹及原PNFP科学配置不变。使用隔离bitsandbytes0.50.0；首步成功且余量>=10GiB才继续最多4次call（前2次原schedule的LR0）；optimizer失败立即停止。禁止继续CPU/BF16-state调参、LoRA、Adafactor、自动Teacher。入口results/pnfp/scale_7b/adamw8bit_pilot/。

当前状态（2026-09-18 GPU BF16 pilot已停止）：隔离DeepSpeed0.19.6支持BF16 master/grad/Adam states；新单卡无offload全参数pilot在第一个optimizer step分配第二moment时OOM，零完成update。GPU采样峰值89.43GiB、host cgroup采样峰值42.10GiB；sec/update及update loss不可用。按用户要求OOM后不重试、不切LoRA、不启动Teacher；当前GPU无worker。报告docs/reproduction_reports/pnfp_7b_gpu_bf16_pilot_20260918.md，证据results/pnfp/scale_7b/gpu_bf16_pilot/。须用户决定后续。

当前最高授权（2026-09-18 GPU BF16 pilot）：仅运行独立单卡96GB、无offload、全参数BF16 master/grad/Adam states短pilot；使用隔离DeepSpeed0.19.6、固定1024指纹、原WA/DM/seed/数据及目标。最多3次optimizer call（包含旧有效warmup后的非零LR更新）后停止，成功也须用户查看peak memory/speed后再决定Teacher。禁止CPU offload重试、LoRA、8-bit optimizer和自动Teacher。旧CPU失败证据保留。恢复入口gpu_bf16_pilot_v1，协议configs/watermark/pnfp_7b_gpu_bf16_pilot.json。

当前最高授权与状态（2026-09-18 PN-FP 7B）：仅PN-FP独立7B scale-extension，当前选择canonical Llama-2-7b-chat-hf@f5db02db724555f92da89c216ac04704f23d4590；ModelScope shakechen固定revision下载及逐文件SHA完成。新实例6003，SSH config C:/Users/Eason/.ssh/config，70GiB数据盘/96GB GPU。最新科学协议为1024 fingerprints、key16/response1、t0.8/k3、WA0.75/DM0.25、seed42、全参数BF16；max40 epochs、训练损失<0.005早停。只做一个最多5-update canonical pilot及廉价utility，健康后fresh正式Teacher；禁止机械沿用旧30epoch、参数网格搜索或自动切LoRA。仅明显utility退化时最多两个指定fallback。当前BLOCKED_HOST_RAM_CANONICAL_CPU_OFFLOAD：两次SIGKILL，零完成update；110GiB主机内存不足以承载当前DeepSpeed CPU offload约113GiB持久张量下限。GPU无worker；保留模型/指纹/日志，未切LoRA、未启动Teacher；速度/loss/recall暂无有效值。恢复入口results/pnfp/scale_7b/pipeline_state.json，冻结协议configs/watermark/pnfp_7b_scale_extension.json。旧实验/旧关机授权仅为历史，不适用于此新实例。

当前 Bc 状态（2026-09-10）：六个独立7500-step run 的训练、原生detector、utility、科学报告及ONE preferred PRIVATE归档均已完成；PNFP110/1024、EverTracer AUC0.59、CTCC0/95、iSeal0/200、SCW p0.8819239735603333，Passive Shared五项过冻结阈值。科学与归档提交ebe7095已push；最终证据、Git三端同步及无worker/GPU空闲gate已核验；仅待关机收据同步后安全关闭新GPU，不得重跑。恢复入口 results/logit_distillation/same_lineage_bc/pipeline_state.json；总报告 docs/reproduction_reports/same_lineage_bc_master_report.md。未满足全部gate前不关机。

当前最高授权（2026-09-10 完整Bc）：PNFP→EverTracer→CTCC→iSeal→SCW→Passive5Shared六个独立fresh Llama3.2-3B onlineKD正式run，7500steps，T2/CE0.5/KD0.5冻结；逐项原Ba frozen20k与schedule核验。PNFP使用已批准reconstructed parent，对照99/1024非原历史98。每run训练→原生detector→utility→科学闭环→ONE preferred PRIVATE archive→manifest+segment验证后推进；pilot不重跑。terminal blocker可继续独立方法；全部6terminal且证据/归档/Git/sync/无worker后授权自动安全关新GPU实例。临时跟进获批，真正新增高风险审批且无可推进工作才30分钟timeout。禁止科学调参、新数据/Teacher替代。完整授权 results/logit_distillation/same_lineage_bc/user_authorization_20260910.txt；恢复入口pipeline_state.json。本段覆盖下方pilot停止限制。

当前状态（2026-09-10 PN-FP Bc pilot）：用户已批准 frozen reconstructed parent20k，非原历史Ba exact replay；2-step smoke与独立fresh-init100-step onlineKD均PASS且已停止。T2、CE/KD各0.5、BF16fullFT、batch8、LR1e-5、seed42、7500horizon/225warmup；中位0.31160248s/step、peak allocated35.95GiB；Teacher全参数hash不变、Student已更新。禁止自动full7500/detector/utility/模型上传/新方法/关机。主对照重建Ba trajectory99/1024；原历史Ba98/1024独立保留。等待用户full-run科学决定。入口 results/logit_distillation/pnfp_same_lineage_pilot/pilot_summary.json；报告 docs/reproduction_reports/pnfp_same_lineage_logit_kd_pilot.md。

当前夜间持续授权（2026-09-10 Sydney）：Active Cross-Lineage Bb 五方法按既定冻结协议串行；每方法科学闭环→preferred PRIVATE归档→manifest+segment验证→下一方法。健康任务持续执行；仅全部科研/归档/证据同步/Git push闭环且无worker后 CAMPAIGN_COMPLETE，或确无其他授权动作且等待真正新用户批准30分钟后 USER_APPROVAL_TIMEOUT，允许安全关机。关机前保存状态/receipt并sync、停止临时跟进。不得把旧即时阶段描述当作重跑命令。原文 results/active_cross_lineage_bb/overnight_authorization_20260910.txt。

当前最高持续授权（2026-09-09）：当前 Active Cross-Lineage Bb 范围内，普通 SSH trust/authorized_keys、同步、轻量 Git commit/push、preferred PRIVATE archive、分段验证、可核验冗余临时文件清理及正常串行推进均已持续授权，无需逐步询问。科学配置不变、唯一科研资产保留、新实例不传 ModelScope token。原 SSH 审批等待解除；PNFP archive 后 EverTracer→CTCC→iSeal→SCW。完整原文 results/active_cross_lineage_bb/continuous_authorization_20260909.txt。仅真正需要新高风险批准且无其他授权工作时适用30分钟等待关机规则。

当前状态（2026-09-09 Active Cross-Lineage Ba 最终闭环）：五个fresh Qwen Student全部7500steps、final save/fresh reload与utility完成。PNFP84/1024（Base43）；CTCC trigger0/95；SCW p0.9158855080604553未检出；EverTracer canonical N/A、exploratory AUC0.523；iSeal Level3 N/A。CPU证据/报告/索引闭环，等待用户独立preferred模型归档选择；禁止新实验、自动上传/删除或关机。shutdown_provenance=UNVERIFIED。入口 results/active_cross_lineage_ba/pipeline_state.json；总报告 docs/reproduction_reports/active_cross_lineage_ba_final_20260909.md。

当前最高授权（2026-09-08 ACTIVE CROSS-LINEAGE Ba）：仅PN-FP→EverTracer→CTCC→iSeal→SCW，五个独立fresh Qwen2.5-3B-Instruct Student；先五detector跨架构适用性审计和supported clean-Qwen baseline，再冻结各自现有Ba20k的endpoint训练/检测/utility。禁止active Bb/passive/Methods11–15/trajectory。单方法终端blocker可跳过，有限工程重试；禁止科学语义变更和未授权清理。仅五方法全部terminal、完整证据本地同步/Git push/无worker/安全关机收据满足后用户授权正常关机，当前未armed。完整授权 results/active_cross_lineage_ba/user_authorization_20260908.txt；恢复入口同目录pipeline_state.json。

当前最高授权（2026-09-08）：暂停全部 active Bb/Bb2 checkpoint trajectories；保留正在运行的 SCW Ba 及其证据，完成后不进入 active Bb。新优先任务仅 Passive-5 Cross-Lineage Ba/Bb：两个 fresh Qwen2.5-3B-Instruct Student，共享冻结 Shared Ba20k/Bb3paired20k，先 clean Qwen passive-5 baseline，跨架构适用性审计后冻结 detector 语义；严禁强改公式/阈值。新授权覆盖旧 passive 禁止及 active Bb 自动推进，禁自动关机。完整请求 results/passive_cross_lineage/user_authorization_20260908.txt，恢复入口 results/passive_cross_lineage/pipeline_state.json。

当前最高授权（2026-09-07 overnight campaign）：五主动方法Ba后Bb/Bb2严格串行；PNFP Ba已完成不重跑。顺序EverTracer Ba→CTCC Ba→iSeal Ba→SCW Ba→PNFP Bb→EverTracer Bb→CTCC Bb2→iSeal Bb→SCW Bb。每条科学证据闭环后推进；GREEN可最小修复可靠续行，RED记录BLOCKED后可继续独立可运行方法。全部可运行任务结束后必要final preferred模型/新必需dataset PRIVATE归档验证、Git闭环、无任务及最终审计通过后方可关机。禁止Methods11–15/passive/C/200k/科学调参。完整授权 results/active_watermarks_trajectory_followup/overnight_authorization_20260907.txt；恢复入口 overnight_campaign_state.json。本段覆盖下方旧限制，历史证据保留。

当前最高授权（2026-09-07 四方法Ba串行）：PN-FP Ba已CLOSED不重跑；仅EverTracer Ba → CTCC Ba → iSeal Ba → SCW Ba，每条11点0/25/50/100/250/500/1000/2000/4000/6000/7500，按各自历史配置、fresh Base、一条连续训练。每条完整证据/Git闭环后推进下一条，无需逐条GREEN批准；失败/缺失点/SHA或连续性异常立即STOP汇报，不自动修复重训。只在原dataset永久丢失且历史protocol可唯一恢复时允许重建并显式标记。禁止Bb/Bb2、模型上传、关机。永久入口 results/active_watermarks_trajectory_followup/four_ba_serial_state.json。此段覆盖下方旧执行授权。

当前状态（2026-09-07 PN-FP Ba follow-up CLOSED）：11点全部完成，matches=1/1/3/58/79/86/85/94/99/99/99（各/1024）；final fresh reload逐条一致，完整性PASS。reconstructed parent非历史Ba exact replay。仅当前Ba已完成，等待用户下一步；禁止自动Bb/其他方法/上传模型/关机。永久证据 results/pnfp/experiment_ba_trajectory_followup/；报告 docs/reproduction_reports/pnfp_ba_trajectory_followup_20260907.md。

当前唯一执行授权（2026-09-07）：PN-FP Ba reconstructed-parent checkpoint trajectory follow-up，11点 0/25/50/100/250/500/1000/2000/4000/6000/7500；fresh canonical 3B Base、历史冻结配置、一条连续训练。GPU smoke PASS且idle已恢复，正式启动前再次核验。所有trajectory证据永久保留，最新可恢复checkpoint及最终7500模型保留；检测失败即停，不自动重跑，不继续Bb或其他方法，不关机。闭环后才更新global index并Git提交推送。本条覆盖下方旧执行授权；非历史Ba exact replay。入口 results/pnfp/experiment_ba_trajectory_followup/。

最新科学决定：用户已批准 PN-FP 使用现有 protocol-faithful reconstructed parent，作为独立 direct/paraphrased 配对 follow-up，非历史 Ba exact replay。历史98/1024和72/1024仅作reference，不再作为继续门槛。数据缺失阻塞已对PN-FP解除，GPU真实空闲门槛仍未通过；未训练。两个独立protocol/full log已创建，见 results/active_watermarks_trajectory_followup/pnfp_*。SCW原始数据替代尚未批准。

当前最高授权（2026-09-07，主动水印 trajectory follow-up）：Methods 11–15 永久退出当前项目范围，不再继续 EaaW/UTF/Double-I/CodeGenGuard 等探索。仅新目录中的 PN-FP、EverTracer、CTCC、iSeal、SCW Ba/Bb（CTCC Bb2）十条 checkpoint follow-up 获准重新训练，严格按用户给定顺序、历史配置和 fresh canonical Base。旧 no-retraining 限制仅对本次明确批准的 follow-up 解除，历史科学对象不覆盖。step0=Base，Teacher 单独参考；checkpoints=0/100/250/500/1000/2000/4000/7500。当前 PN-FP Ba 因原始 frozen dataset 不可恢复及 GPU 0MiB/100%异常阻塞，禁止用重建数据代替 same dataset，禁止跳过首条门槛、GPU reset/kill unrelated process 或自动关机。EaaW 当前无存活进程，记录为 ALREADY_EXITED_CONFIRMED，不虚构 SIGTERM/退出时间。恢复入口：results/active_watermarks_trajectory_followup/pipeline_state.json。此条覆盖下方全部旧执行授权。

最新授权（2026-09-07 EaaW A2恢复）：用户正式批准GPT2_UNK_EOT_50256→LLAMA32_END_OF_TEXT_128001；SCIENTIFIC_ADAPTATION=APPROVED_WITH_UNPROVEN_EQUIVALENCE。仅此mask映射，其他released/native科学配置保持：SGD、batch2、accum1、20epochs、LR3e-4、128bits。仅原A2：一次真实预检后formal、fresh reload、Teacher及controls，通过后utility；失败立即停止、不调参。native严格等价性UNPROVEN永久保留。禁止其他方法、orchestrator、auto-next/shutdown。此条覆盖下方旧mask阻塞。

当前最高状态（2026-09-07 EaaW canonical 3B A2）：用户已批准仅EaaW A2；本轮CPU科学审计后发现RED，BLOCKED_SCIENTIFIC_MASK_TOKEN_MAPPING。canonical八文件SHA验证PASS；Llama-3.2 unk_token_id=None，尚未批准替代mask。预检/训练/detector/utility/上传均NOT_RUN，未创建模型。等待用户决定exact masking baseline；不得自动继续。旧EaaW native A仍成功、作为NATIVE_REPRODUCTION_EVIDENCE，CANONICAL_BENCHMARK_ELIGIBLE=NO；UTF A4保留闭环状态。报告 docs/reproduction_reports/eaaw_a2_final_report_20260907.md。禁止其他方法、Ba/Bb、orchestrator/guardian、auto-next/shutdown。下方旧执行授权仅供历史参考。

当前状态（2026-09-07 UTF A4 已结束）：STOPPED_AFTER_A4；仅epochs30→3，正式96 exposures / 6 optimizer calls / 4 nonzero-LR updates。Teacher正例0/1，Case C INSUFFICIENT_FINGERPRINT_LEARNING；COMPLETED_NOT_PREFERRED，preferred=NO，benchmark eligible=NO。负例、Base detector、utility均NOT_RUN，global collapse未评估。模型本地保留、不上传不删除。禁止任何继续执行、A5、其他方法、auto-next及auto-shutdown；等待用户新的科学决定。完整报告：docs/reproduction_reports/utf_a4_final_report_20260907.md。下方旧授权仅为历史记录。

最新授权（2026-09-07 UTF A4）：仅epochs30→3，其余A3冻结；fresh Base、单次预检、6次正式更新。Teacher先跑；positive丢失或collapse则立即停止Base/utility并轻量闭环。禁止A5/其他方法、orchestrator、auto-next/shutdown。preferred前不上传，不删除模型。此条覆盖下方旧STOP。

最新停止授权（2026-09-07）：UTF A3因Teacher negative500/500停止；COMPLETED_NOT_PREFERRED，preferred=NO，benchmark eligible=NO。禁止任何后续science、upload/recovery或删除模型，仅允许短只读root-cause audit。不得A4。此前A3执行授权由本条覆盖。

当前最高授权（2026-09-07 UTF A3）：仅A3单因素grad_accum1→16，其他A2科学条件冻结；fresh canonical Base，单次预检后正式30epochs/60updates，Teacher+Base detector及Teacher utility。preferred确认前不上传；结束STOP，不启动其他方法/Ba/Bb/自动关机。A2历史状态保持。

最新永久规则（2026-09-07）：每个正式实验最多上传一个最终preferred模型，preferred=false禁止上传；UTF A2 COMPLETED_NOT_PREFERRED，仅证据/Git闭环后STOP。远端已提交对象和本地模型保留待明确删除批准。详见 docs/ARTIFACT_ARCHIVE_POLICY.md；本段覆盖下方历史归档授权。

<!-- UTF_A2_CURRENT_AUTHORITY_20260907 -->
当前最高优先级授权（2026-09-07，UTF A2 新 prompt）：仅执行 Method 13 UTF Experiment A2；STRICT SERIAL INTERACTIVE MODE。Methods 11–15 canonical benchmark 永久统一为 meta-llama/Llama-3.2-3B-Instruct，revision 0cb88a4f764b7a12671c53f0838cd831a0843b95。旧 UTF 7B A 保留 historical / superseded protocol，OLD_UTF_A_CANONICAL_BENCHMARK_ELIGIBLE=NO，不标记 FAILED，不覆盖历史结果。
禁止 orchestrator、guardian/watchdog、自动 continuation、auto-next 和 auto-shutdown。仅允许 UTF 专用实现及单项任务；不得运行 11/12/14/15、Ba/Bb 或其他 watermark。旧远端 supervisor 2051 和本地 sync helper 32236 已停止，模型身份检查时未发现相关旧进程。
当前 UTF A2 已完成科学与轻量证据闭环，模型归档按新规则停止且未验收：30 epochs / 960 updates，PREFERRED_TEACHER=NO；Teacher fingerprint 1/1、非触发负控500/500，Base 0/1、0/500；ARC delta=-0.0708191126，MC2 delta=-0.0014838436。状态 WAITING_FOR_USER_SCIENTIFIC_DECISION；下一科学配置须用户批准。30/3 paper/code discrepancy及选择依据保留。完整结果见 docs/reproduction_reports/utf_a2_final_report_20260907.md。
详见 docs/reproduction_reports/utf_a2_initial_checkpoint_20260907.md 与 results/methods_11_15_pipeline_state.json。以下旧授权与阶段文字仅供历史参考；如冲突，以本段及最新用户决定为准。
<!-- UTF_A2_CURRENT_AUTHORITY_END -->

<!-- WMKD_METHODS_11_15_CURRENT_BEGIN -->
当前授权（2026-09-07）：用户明确解除暂停，仅恢复 Method 13 UTF Experiment A，STRICT SERIAL INTERACTIVE MODE。先修复 DeepSpeed 整数兼容并通过真实单步 preflight，再正式训练、detector、negative control、utility、reload、归档验证及 Git 闭环。不得启动 Method 14/15；auto_advance=false，auto_shutdown=false；UTF 闭环后 STOP。历史暂停证据保留。

EaaW / Instructional Fingerprinting CLOSED；UTF 等待 attempt 4 单步预检；Double-I / CodeGenGuard NOT_STARTED。
<!-- WMKD_METHODS_11_15_CURRENT_END -->

# TODO

当前授权更新（2026-09-05）：用户已正式批准五方法串行 Experiment A 自动复现、最小工程修复、逐方法归档/Git闭环及全部terminal后的自动关机。前次等待prompt/STOP仅属于已结束的迁移任务。详见 [docs/METHODS_11_15_AUTOMATION.md](docs/METHODS_11_15_AUTOMATION.md) 与 results/methods_11_15_pipeline_state.json；旧科学设计禁改及KEEP/UNCERTAIN保留规则继续有效。


## 当前阶段 — 2026-09-05 方法 11–15 前规则与状态迁移

以 [docs/CURRENT_STATE.md](docs/CURRENT_STATE.md) 为当前状态入口。第一批十方法 CLOSED：30 comparison slots；32 canonical full-log objects。项目归档已闭环（24 verified / 8 strong-remote / 0 missing / 7 N/A / 2 permanent historical losses）。CTCC 比较使用 Bb2，原 Bb BLOCKED 历史不变。

新增顺序：11 EaaW → 12 Instructional Fingerprinting → 13 UTF → 14 Double-I Watermark → 15 CodeGenGuard。下一目标 METHOD_11_EAAW_EXPERIMENT_A，NOT_STARTED；须等待独立正式 prompt。本次只做状态/规则、精确归档权重清理与 Git 闭环。

清理记录：results/pre_methods_11_15_cleanup.json；验证：results/pre_methods_11_15_validation.json。以下旧快照/待办按历史保留，不应恢复执行。
维护执行完成：26 个已验证归档权重文件删除，释放约 60.6 GiB，剩余约 167.3 GiB；30 个 UNCERTAIN 权重文件保留。修复 Git 换行造成的远端 16 个 full-log SHA 不符，原索引和科学内容未变。完整报告：docs/reproduction_reports/pre_methods_11_15_durable_state_report.md。EaaW NOT_STARTED，STOP 等待独立正式 prompt。



## Historical priority — proactive Bb discussion only (superseded)

- [x] Close preferred A/A2 (iSeal ultimately A6) and Ba for all ten methods.
- [x] Preserve Passive Shared Ba as COMPLETE, original Bb/Bb2 as `BLOCKED_AT_PILOT`, and Bb3 as COMPLETE.
- [x] Validate Passive Bb3 at 5/5 detectors positive and disclose 4,635/20,000 (23.175%) atomic identities.
- [x] Preserve 4/4 canonical Passive-5 ModelScope artifacts as verified PRIVATE; do not duplicate-upload.
- [x] Validate 26/26 unique full experiment JSON objects with no broken paths.
- [x] Freeze proactive methods 1–5 Experiment Bb to exact validated Passive Bb3 preprocessing plus method-specific Ba lineage and independent fresh Students.
- [ ] Complete SSH 6000 canonical Ba inventory, minimal compatibility preflight, storage/archive audit, and execution-readiness report without starting formal work.
- [x] Recover access through direct endpoint, safely bring remote Git to canonical main, preserve historical SCW checkout, and inventory existing artifacts.
- [x] Add shared infrastructure-only proactive Bb config/namespace parameterization with frozen-science regression tests.
- [ ] Restore, never regenerate, canonical PN-FP and SCW Ba frozen20k; establish their archive provenance.
- [ ] Archive the surviving EverTracer, CTCC, and iSeal canonical Ba frozen20k before formal Bb.
- [ ] Restore the exact recorded Passive Bb3 Qwen snapshot and rerun only the minimal compatibility inference preflight.
- [ ] Complete proactive full-log closure-builder parameterization before formal completion logging.
- [ ] Preserve five separate proactive Teacher-output lineages, processed Bb datasets, and fresh Students; do not share these across methods.
- [ ] Obtain explicit authorization before `ssh 6000`, downloads, paraphrasing, training, detector/utility execution, or GPU use.
- [ ] Perform no destructive cleanup without the permanent archive/dry-run/classification/explicit-authorization sequence.

## Historical Passive-5 Bb preparation priority — 2026-09-03

- [x] Close A/A2/A6 reproduction and Ba evaluation for all 10 ownership-verification methods.
- [x] Freeze Experiment Bb as answer-only UP followed by distillation.
- [x] Select passive methods 6–10 (LLMPrint, REEF, HuRef, AWM, ZeroPrint) as the first Bb cohort.
- [ ] Prepare and review the passive-shared Bb protocol, preserving paired IDs/instructions/inputs and replacing only the frozen Teacher answer with its UP-paraphrased answer.
- [x] Prepare the shared-control lineage, Qwen paraphraser identity with revision gate, failure-closed paraphrase policy, fresh canonical Student, detector/utility wiring, full-JSON schema/index support, and guarded future launcher.
- [ ] Resolve and freeze the exact `Qwen/Qwen2.5-3B-Instruct` revision during a future authorized download-preparation stage; then run and inspect the 100–200 sample pilot before formal 20k generation.
- [x] Archive the canonical Passive-5 Shared Ba frozen20k to a PRIVATE ModelScope dataset and independently download/verify 20,000 records, all three canonical hashes, and byte identity.
- [ ] Obtain a separate explicit execution prompt before any AutoDL connection, download, paraphrasing, Student training, detector evaluation, or GPU use.
- [ ] Keep shared resources; perform no destructive cleanup before scientific closure, Git/archive gates, dry-run classification, and explicit authorization.

The dated checklists below are historical workflow records and do not override this current priority.

## Four-method pre-formal smoke follow-up — 2026-09-01

- [x] Safely pause LLMPrint A2 at 97/200 and preserve fingerprint IDs 000-096 immutably.
- [x] Pin/audit and locally scaffold REEF, AWM, HuRef and ZeroPrint Experiment A protocols and full-log frameworks.
- [x] Complete one serial, bounded GPU compatibility/resource smoke for each of the four ownership methods.
- [ ] Freeze REEF/AWM/ZeroPrint negative panels and controlling threshold/decision calibration before formal authorization.
- [ ] Build/hash HuRef's canonical sorted-token list and obtain bounded 4096-token scaling evidence; current status is `TIME_BUDGET_RISK`.
- [ ] Run a representative official-budget ZeroPrint generation-speed gate before formal authorization.
- [ ] Obtain explicit user approval before any integrated formal pipeline, LLMPrint A2 cont1, four-method formal A, or Ba.

## High priority

- [x] Close PN-FP, EverTracer, CTCC, iSeal, and SCW: **5/7 complete**.
- [x] Preserve 10/10 canonical full experiment JSON logs and the global index.
- [x] Audit the LLMPrint paper and pin official source `hifi-hyp/ACL-LLMPrint@3e577f98b2bb64780ec2995b074c5aeec9b017e1`; prepare local configuration, wrappers, tests, method record, and validation-negative availability matrix.
- [x] Reconnect to AutoDL, validate idle GPU and canonical Base 12/12 SHA256, prepare 300 tokenizer-valid pairs, and complete exactly one isolated 1000-step fingerprint speed test (212.429 s; 1000/1000).
- [x] Freeze dual detector semantics: paper Primary uses inclusive bits, sample standard deviation (`ddof=1`), raw unclipped `mu + 1.64 sigma`; pinned-release gray-box remains supplementary and cannot change the main conclusion.
- [x] Freeze all 13 validation-negative identities as revision-pinned ModelScope transport mirrors, with zero replacements and zero unresolved slots.
- [x] Pass all original-A readiness gates and launch `llmprint_a_20260901_061225`; preserve this immutable history.
- [x] Safely terminate incomplete formal A after 7/300 complete artifacts under the user-approved scientific redesign; prohibit A partial reuse.
- [x] Complete minimal A2 readiness and launch first-200-pairs × 500-step detached construction `llmprint_a2_20260901_064855`; first health snapshot passed.
- [ ] After A2 construction completes, validate exactly 200/200 × 500/500 before any separately instructed detector evaluation; do not start Ba automatically.
- [ ] Run REEF only under a later separately authorized protocol.
- [x] Pause LLMPrint A2 at 97/200 with immutable completed artifacts and missing-ID-only A2 cont1 semantics.
- [ ] Complete bounded official-code compatibility/resource/speed smokes for REEF, AWM, HuRef and ZeroPrint without launching formal A or Ba.

The older SCW checklist entries below are immutable historical workflow records. Their unchecked items do not override the current 5/7 closure or authorize rerunning strict A.

- [x] Pin SCW official `eth-sri/robust-llm-fingerprints@15bc1929569357130f2dbc0b09f91bbf4f4bd947`, inspect French training/evaluation/detector code and Responsible AI Source Code License 1.1, and prepare local-only Experiment A contracts.
- [x] Fix SCW French/KGW scientific configuration, deterministic aggregate detector/curve semantics, canonical model contract, schemas, static tests, and future detached/speed-test runner without starting a formal run.
- [x] Deploy/verify the exact SCW source and environment, pin provenance, and complete the historical runtime preflight/speed-test stage.
- [x] Preserve strict A as pre-formal and complete the explicitly authorized A2/Ba lineage without rewriting strict-A history.

- [x] Pin official iSeal source, implement the minimal canonical adaptation, and complete the mandatory two-step trainability audit.
- [x] Preserve the official iSeal Experiment A trainability blocker and complete explicitly authorized A2-A6 lineage without rewriting that history.
- [x] Select A6 as preferred Teacher and complete iSeal Ba, fresh-reload evaluation, formal reporting, and private archival.
- [x] Audit and consolidate canonical protocol and current-facing project state after CTCC closure without starting or downloading a fourth watermark.

- [x] Resolve CTCC A's paper/public-artifact discrepancy by formally using all pinned 461/428/1000 records without augmentation.
- [x] Deploy CTCC config/scripts, freeze official files, validate real Llama-3 serialization, and pass 11/11 runtime preflight checks.
- [x] Complete detached CTCC A run `ctcc_a_20260829_190251`; establish 95/95 trigger, 0/205 negative activation, functional utility, reload pass, and preferred teacher YES.
- [x] Preserve failed CTCC Ba generation parent and complete infrastructure-only continuation with 46,009 combined raw, 20,160 deterministic unique, and exactly 20,000 frozen QA.
- [x] Complete fresh-canonical CTCC Ba Student training `ctcc_ba_20260830_025244` at 7,500/7,500 steps.
- [x] Complete fresh-reload CTCC detector, ARC, TruthfulQA, and ordinary-generation evaluation through infrastructure-only continuation `ctcc_ba_eval_20260830_033556_cont1`.
- [x] Upload the CTCC preferred Teacher adapter and Ba inference-ready Student to their fixed private ModelScope repositories with source and remote metadata verification.
- [ ] Perform CTCC ModelScope destination-side full SHA256 only during a future real download on another machine.
- [ ] CTCC Bb remains NOT RUN / deferred; do not perform cleanup or start another watermark without explicit approval.

- [x] Audit and consolidate the post-EverTracer fixed project protocol without selecting or starting a third watermark.

- [x] Complete EverTracer Experiment A through immutable continuation 2 and establish the preferred teacher.
- [x] Complete EverTracer Ba run `evertracer_ba_20260829_124055` with exactly 20,000 teacher-specific QA and a fresh canonical student.
- [x] Upload the EverTracer A preferred teacher and Ba student to their fixed private ModelScope repositories with source and remote metadata verification.
- [ ] Perform destination-side full SHA256 only during a future real download on another machine.
- [x] Complete the authorized EverTracer closure and protected cleanup; reclaim 77.958 GiB while preserving every protected artifact.
- [x] EverTracer Bb detector and frozen Ba-matched utility complete; final scientific closure complete.
- [x] Select SCW as the fifth watermark and complete the authorized local-only Experiment A preparation; formal A remains NOT RUN.
- [x] Deploy exact local SCW code to AutoDL, pin official source/model/datasets, pass runtime-effective preflight, and complete the isolated 4-step representative speed test without starting Formal A.
- [x] Research and locally implement the SCW exact finite materialized-stream runtime adaptation with deterministic synthetic audit tests; classify it conditionally as `RUNTIME_DATA_ACCESS_ADAPTATION`, not A2.
- [x] Superseded by the explicitly approved A2 domestic-data adaptation and completed A2/Ba lineage; strict A remains a preserved pre-formal blocker, not a pending rerun.

- [x] Initialize the independent local project structure.
- [x] Add repository documentation and project-management logs.
- [x] Add strict ignore rules for secrets and large artifacts.
- [x] Create and verify the private GitHub repository and synchronized `main` branch.
- [x] Initialize the La Trobe lightweight mirror and dedicated large-artifact warehouse.
- [x] Approve PNFP as the first watermark reproduction target and record Experiment A settings.
- [x] Initialize the AutoDL compute checkout and isolated data/cache structure.
- [x] Create and validate the PNFP-specific AutoDL environment.
- [x] Archive the fixed Llama-3.2-3B-Instruct revision in canonical La Trobe storage and verify all 12 files by size and SHA256.
- [x] Evaluate the ModelScope Llama-3.2-3B-Instruct candidate and reject it after a downloaded canonical-file mismatch confirmed it is not byte-identical.
- [x] Complete the fixed Llama model transfer to AutoDL and verify all SHA256 values.
- [x] Run offline tokenizer/model load and short generation smoke after transfer verification.
- [x] Explicitly authorize formal PNFP Experiment A training in a separate task.
- [x] Define the durable formal experiment protocol and dedicated PN-FP log convention.
- [x] Launch corrected PN-FP Experiment A through the independent runner (`pnfp_exp_a_20260827_232033`).
- [x] Complete PN-FP Experiment A checkpoint reload, watermarked/base evaluation, paired metrics, and summary.
- [x] Prepare paired PN-FP Ba/Bb configs, dataset/UP validation, schemas, logs, report templates, and guarded dry-run runners.
- [x] Pin the official CAN repository at `9a2b01af1fadcece2893d32460ed9449093f8fb9`.
- [x] Cancel and remove the incorrect partial 1B student download before any formal Ba run or notification.
- [x] Launch formal same-size 3B Ba run `pnfp_exp_ba_20260828_012228`; preserve its fail-fast evidence after teacher QA generation yielded 0 valid candidates and 64 parse failures.
- [x] Diagnose the failed teacher generation with bounded ordinary/CAN-style/JSON tests and add tested no-progress guards.
- [x] Establish A2 as the utility-preserving preferred PN-FP teacher after both watermark and utility gates passed.
- [x] Complete and formally close A2-based Ba run `pnfp_exp_ba_20260828_111148`; record strong watermark degradation with partial retention and a passed utility gate.
- [ ] Keep Bb and all Dipper/UP downloads deferred until a separate future approval.
- [x] Implement and test reusable experiment email notification infrastructure without touching the active PN-FP process.
- [x] Deploy standalone notification utilities outside the active AutoDL Git checkout.
- [x] Configure the Gmail App Password interactively on AutoDL and send one successful independent test email.
- [x] Start and verify the read-only detached watcher for the current PN-FP run.
- [x] Finalize Experiment A dedicated log, formal report, and machine-readable summary with mutually consistent authoritative results.
- [x] Harden SMTP with bounded retries, serial STARTTLS fallback, terminal pending queue, and CPU-only retry utility.
- [ ] Retry the legitimate missed Experiment A COMPLETED notification when the AutoDL credential becomes reachable; do not send STARTED.

## Medium priority

- [x] Complete final iSeal sample-scale A6 and select A6 as preferred Teacher (`179/200` full registered; `86/100` historical A5 subset; reload PASS).
- [x] Complete iSeal Ba through frozen20k, Student, fresh-reload evaluation, reporting, and private Teacher/Student ModelScope archival.
- [x] Close iSeal Bb as `COMPLETE` (20k preprocessing, 7,500-step Student, PRIVATE archive verification, detector, utility, and formal closure). A7 remains a separate historical/future concept and was not run as part of Bb.

- [ ] Analyze the PN-FP Ba result further only if an additional scientific question is approved.
- [x] Upload the A2 canonical teacher to private ModelScope with immutable source/upload checks; destination-side verification remains a future transfer-stage gate.
- [x] Complete and close PN-FP Bb under the frozen proactive-Bb protocol; preserve the protocol-faithful parent-reconstruction limitation.
- [ ] Complete SCW formal A only under a future explicit AutoDL execution prompt; current local preparation is not a scientific result.
- [ ] Define dependency-management and environment-reproduction conventions.
- [ ] Define storage and synchronization policies for future large artifacts.
- [ ] Add method-specific reproducibility instructions after research decisions are approved.

## Completed

- Local initialization scaffold created on 2026-08-27.
- Private GitHub repository created and connected on 2026-08-27.
- La Trobe school-server storage endpoint initialized on 2026-08-27.
- AutoDL compute endpoint and isolated data root initialized on 2026-08-27.
- PNFP official source and isolated environment prepared on 2026-08-27; model transfer was still blocked at that preparation stage.
- Fixed Llama-3.2-3B-Instruct canonical school-server archive completed and fully verified on 2026-08-27.
- Fixed Llama-3.2-3B-Instruct AutoDL snapshot completed and fully verified on 2026-08-27; offline tokenizer/model/generation smoke passed without starting training.


## A2 immutable evaluation continuation `pnfp_exp_a2_eval_20260828_105530`

Parent training run `pnfp_exp_a2_20260828_025240` remains operationally FAILED after external dataset acquisition failure. The validated checkpoint and reusable evaluations plus this continuation establish the final result. Watermark gate: **passed**; utility gate: **passed**; judgement: **A2 is the preferred PN-FP teacher for future Ba**.


## A2-teacher formal Ba run `pnfp_exp_ba_20260828_111148`

Completed: A2 956/1024 (93.359375%) → Ba 98/1024 (9.5703125%), 83.7890625-point drop and 10.251046% retention; utility and reload gates passed. The result is strong degradation with partial retention under the tested setting. Preserve the immutable old A1-based failure; keep Bb, UP, and Dipper deferred.

## PN-FP final closure

- [x] Mark Experiments A, A2 and Ba CLOSED with bounded conclusions.
- [x] Preserve small scientific and transfer records before AutoDL cleanup.
- [x] Remove completed PN-FP large AutoDL run/readback artifacts while preserving the canonical base, environments, credentials and reusable infrastructure.
- [x] Record the future destination-side artifact verification protocol.
- [ ] Bb remains NOT RUN / deferred.
- [ ] Discuss and select the next watermark reproduction; do not start it without explicit approval.
- [ ] With separate authorization, fix and verify LucieFr authoritative Parquet path discovery for the deterministic finite-stream builder; do not start Gate/Formal A until the user requests a new run.
- [ ] Keep `WMKD_AUTO_SHUTDOWN_ENABLED=false` until the user explicitly re-enables automatic shutdown.
- [x] Freeze the SCW A2 domestic dataset protocol and build/audit the exact 80k-unique, two-pass 160k-exposure local stream.
- [ ] Run the single SCW A2 4-step gate; start Formal A2 only on PASS and arm automatic shutdown only after optimizer step 1 proves Formal A2 started.

## SCW A2 next action

- Keep automatic shutdown disabled until explicitly re-authorized.
- In a separately authorized turn, resolve the fixed French evaluation input offline and resume evaluation from Base generation without retraining.

## SCW A2 evaluation cont2 `scw_a2_eval_cont2_20260901_021640`

Training remained immutable and complete. Cont1 failed at Base detector because the runtime tokenizer lacked a pad token. cont2 reused both immutable 1000-record generation files and applied runtime-only EOS-as-PAD with left padding; Base/Teacher p-values `0.9199569225311279` / `0.0`; preferred Teacher `True`. Ba was not started. Auto-shutdown remained disabled.

## SCW A2 final closure — report/summary cont3

<!-- SCW_A2_FINAL_CLOSURE_CONT3_20260901 -->
Strict A remains a pre-formal infrastructure attempt: Formal training never started and no scientific result was established. A2 run `scw_a2_20260831_214339` completed 2500/2500 and produced the immutable Teacher. Cont1 preserved Base/Teacher 1000-record generations but failed at detector padding infrastructure. Cont2 applied runtime-only left EOS-as-PAD and completed evaluation: Base/Teacher primary p-values `0.9199569225311279 / 0.0`, ARC `0.4505119454 / 0.4488054608`, TruthfulQA MC2 `0.5051617516 / 0.5032315125`, ordinary/French sanity PASS/PASS, and preferred Teacher **YES**. The bounded conclusion is successful SCW core method/idea reproduction under the adapted domestic-data, 80k-pool, deterministic two-pass A2 setting—not exact or full-paper reproduction. Ba remains NOT STARTED. Next step: separately archive the final Teacher to ModelScope, verify the archive, then discuss Ba without starting it automatically.

## SCW A2 preferred Teacher ModelScope archive

<!-- SCW_A2_MODELSCOPE_ARCHIVE_20260901 -->
The immutable SCW A2 preferred Teacher was archived to private repo `MakiseKurisuEasonHan/WMKD-SCW-A2-Teacher`. Upload completed with 9 files / 6,442,815,654 bytes and zero retries. Remote filename, size, and metadata identity verification passed for 9/9 files and all bytes. Source archive manifest SHA256: `0e2bd96ef266fc791e182e793507bfc0db7fe994f1d37ce440adaef923b5dbe1`; Teacher manifest SHA256: `27f68ea443ca1dbc9f02036ac560a12db5cb063ceec589a0144be5586da97b7b`. Status: `uploaded_to_modelscope_awaiting_destination_hash_verification` with `destination_verified=false` because a full destination redownload was intentionally not performed. Preferred Teacher remains YES; Ba remains NOT STARTED. Exact next step: design and explicitly authorize SCW Ba; do not start it automatically.

## SCW Ba `scw_ba_full_20260831_193828_cont1`

Completed standardized Direct Distillation with exactly 20,000 frozen Teacher QA, fresh-canonical 3B Student and Base/Teacher/Student SCW evaluation. Dataset SHA `a8c93d4fc55521abe6abab48aa67cc06a6251ce769caa913bd24adfebb87b05c`; primary p-values `0.9199569225311279` / `0.0` / `0.8440861701965332`; bounded result `lost_or_moved_to_base_regime`. Auto-shutdown remained disabled; Student archive not run.

## SCW Ba Student ModelScope archive

<!-- SCW_BA_STUDENT_MODELSCOPE_ARCHIVE_20260901 -->
The immutable SCW Ba Student from `scw_ba_full_20260831_193828_cont1` was archived to private repo `MakiseKurisuEasonHan/WMKD-SCW-Ba-Student`. Upload and remote filename/size/metadata verification passed for 9 files and 6442815786 bytes. Source manifest SHA256 `f8554fc57258f28b945835dcab759ae4891633cc835918cf63156b14a9f41ef1`; status `uploaded_to_modelscope_awaiting_destination_hash_verification`; `destination_verified=false`. The bounded scientific result remains loss of detectable SCW watermark under the tested standardized Ba condition with the Student in a Base-like negative detector regime. Next step: SCW final closure / commit review; no cleanup was performed.

## After 5/7 closure — 2026-09-01

- [x] Close PN-FP, EverTracer, CTCC, iSeal, and SCW, including preferred Teacher and Ba Student canonical full logs.
- [x] Create the 10-object global full-log index and integrity audit.
- [x] Complete the authorized LLMPrint preparation, preflight, one-fingerprint full-parameter speed test, detector freeze, and validation-panel freeze.
- [ ] Run REEF under a separately authorized protocol.
- [ ] If exact watermark-disappearance timing is required, design a separately authorized offline checkpoint-level detector study; do not infer it from training loss.

## Passive-5 final closure — 2026-09-02

<!-- PASSIVE5_FINAL_CLOSURE_TRACKING_20260902 -->

LLMPrint A2, REEF A protocol-compliance final, HuRef A2, AWM A protocol-compliance final, and ZeroPrint A2 are 5/5 scientifically SUCCESSFUL under their bounded frozen WMKD protocols. Shared Ba `passive5_shared_ba_20260902_114500_cont1` with evaluation continuation `passive5_shared_ba_eval_cont2_20260902_164200` retained ownership detectability for 5/5 frozen detectors under the tested same-backbone direct-distillation setting. This does not prove fingerprint transfer or general KD immunity. Teacher total generation tokens across extension rounds remain NOT RECOVERABLE FROM PERSISTED TELEMETRY. MiniLLM, DistiLLM, paraphrase, and REASMARK are NOT_STARTED. AUTO_SHUTDOWN remains FALSE.


## Passive-5 Shared Ba final Student private ModelScope archive — 2026-09-03

<!-- PASSIVE5_SHARED_BA_STUDENT_MODELSCOPE_ARCHIVE_20260903 -->

Canonical Student run `passive5_shared_ba_20260902_114500_cont1` was archived without mutation to private ModelScope model repository `MakiseKurisuEasonHan/Llama-3.2-WMKD-Passive5-Shared-Ba-Student`. The compliant repository name, included Llama 3.2 license/NOTICE, and “Built with Llama” attribution reflect the upstream redistribution terms. Upload committed 15 canonical/archive files (6,442,834,743 bytes); an independent fresh download verified all 15 filenames, sizes, and SHA256 values. Secret scan and large-file allowlist scan passed. The source remained present with all 10 source hashes unchanged. Passive-5 Bb remains `PREPARED_NOT_STARTED`; no GPU run, paraphrasing, or Student training was started.


## Passive-5 Shared Bb formal preflight — 2026-09-03

<!-- PASSIVE5_SHARED_BB_FORMAL_PREFLIGHT_20260903 -->

Formal Bb execution is explicitly authorized. Canonical Ba frozen20k passed count, file, canonical-record, and sample-ID identity checks. Official `Qwen/Qwen2.5-3B-Instruct` was transported from ModelScope; because the platform exposes only `master`, immutable identity is frozen by revision creation timestamp plus the complete 12-content-file size/SHA256 manifest. Offline tokenizer, chat template, and full CPU model load passed. The prompt SHA is unchanged, 35/35 Bb tests passed, and Ba/Bb training parity passed 19/19 fields. GPU work has not started at this preflight record; the next stage is the deterministic 200-sample pilot.


### Bb pilot attempt 0 operational continuation

The first 200-sample pilot attempt stopped fail-closed with 153 successes and 47 retry-exhausted samples. There was no OOM, CUDA error, truncation, empty generation, or broad semantic failure. Inspection showed the implementation incorrectly treated per-record length-ratio and lexical-change diagnostics as hard validity failures, disproportionately rejecting atomic answers such as names and numbers. Preserve this failed attempt. A minimal operational correction keeps empty output, leakage, control-token leakage, and truncation as hard failures while retaining exact-copy/length/lexical flags as dataset-level diagnostics. Prompt, Qwen snapshot, decoding, source selection, and attack semantics remain unchanged; rerun as pilot cont1 before any full20k work.


Pilot cont1 produced 199/200 valid pairs. Its only exhausted record was source answer `null`, for which all three generations wrapped the unchanged value in the prompt's exact `<SOURCE_ANSWER>` boundary tags. A second and final minimal operational correction strips only those two exact wrapper tags after decoding and records every occurrence; all other leakage markers remain hard failures. This is detector-agnostic output sanitation, not a prompt, decoding, model, source, or attack-semantic change. Preserve cont1 and rerun the fixed 200 as pilot cont2.


Pilot cont2 generated 200/200 records in 63.3096 seconds (3.1591 samples/s, 4,181 output tokens, 66.0406 output tokens/s, peak VRAM 7,226,526,720 bytes), with zero automated hard failures, zero truncation, 21 exact copies (10.5%), and mean/median lexical change 0.69365/0.75. However, deterministic human audit found sample `qa_00454047fe5797416cb0` (`tech`) produced paraphrasing-instruction semantics instead of a paraphrase. Because the frozen gate requires zero prompt leakage, the pilot is not PASS. Status is `SCIENTIFIC_DECISION_REQUIRED`; full20k, Student training, detectors, utility, and archives were not started. All pilot attempts remain preserved.


The user authorized `pilot_cont3` with one detector-agnostic instruction-echo rejection/retry rule as an operational robustness fix, explicitly retaining Experiment Bb and all prior pilot history. The fixed rule uses auditable multi-word prompt/meta-response phrases, requires the phrase to be absent from the source answer, and does not reject isolated generic words such as `rewrite`, `paraphrase`, or `response`. Qwen identity/revision, prompt/SHA, source/order, decoding, seed policy, attack semantics, Student protocol, and detectors remain unchanged. CPU/static tests passed 40/40, training parity passed 19/19, and the prompt SHA remained canonical.

Pilot cont3 generated 200/200 final records from 202 attempts in 63.0964 seconds, with two instruction-echo rejections and same-sample retries. Automated final leakage, control-token leakage, truncation, exhaustion, OOM and CUDA failures were zero; exact copies remained diagnostic at 21/200. Targeted 25-pair human audit found both replacement outputs for source `tech` still described rephrasing/preservation instructions rather than the source answer. This is the same leakage type, so the user-mandated stop condition applies. Full20k and all downstream stages remain NOT_STARTED; cont3 is not a scientific Bb result.

Pilot cont4 is preserved and stopped at the authorized gate: 200/200 automated final records, 202 attempts, 21 natural exact copies, zero identity fallbacks, and zero automated final leakage/truncation, but both retry outputs for source `tech` remain paraphrasing-task descriptions under human audit. Do not start full20k or downstream Bb stages without a new scientific decision.

Pilot cont5 is preserved and stopped: attempts 1 and 2 for both `tech` samples were correctly rejected, while attempt 3 (`SOURCE_ANSWER.tech`) was accepted without a validator reason and fails manual leakage review. Do not patch further or start full20k/downstream stages without a new user decision.

Await scientific freeze of the proposed Bb2 short-answer preprocessing threshold. CPU-only distribution audit recommends the smallest sufficient candidate, `<=1` Qwen non-special token (4,635 identity-preserved; 15,365 sent to Qwen). Do not start a Bb2 run until explicitly frozen and authorized.

Bb2 was subsequently frozen without a short-token bypass and its formal pilot is now BLOCKED_AT_PILOT: both `tech` outputs are unresolved meta-commentary under the new semantic-preservation prompt. Do not patch endlessly or start full20k/downstream stages; await a new scientific decision.
## Passive-5 Shared Bb3 closure — 2026-09-03

<!-- PASSIVE5_SHARED_BB3_TODO_20260903 -->

- [x] Preserve Bb and Bb2 as `BLOCKED_AT_PILOT`.
- [x] Complete Bb3 pilot, canonical full20k, private dataset archive, 19/19 parity, fresh Student training/reload, five frozen detectors, utility, and private Student archive.
- [x] Independently redownload and verify both ModelScope archives.
- [x] Generate Bb3 full JSON, provenance/artifact manifests, detector logs, and final report.
- [ ] Shut down the AutoDL instance manually when convenient; no scientific work remains for Bb3.
- [ ] In a separate explicitly authorized task, plan proactive watermark methods 1–5 UP/distillation; do not start it from this closure.
- [x] Restore/hash-verify exact Passive Bb3 Qwen and pass tiny runtime UP plus canonical SFT formatter smoke for the three available proactive parents.
- [x] Complete proactive Bb full-log skeleton and collision-safe index parameterization.
- [x] Archive EverTracer, CTCC, and iSeal canonical Ba frozen20k to their explicitly approved PRIVATE ModelScope repositories and independently redownload-verify every identity gate.
- [ ] Await a separate explicit prompt before starting Wave-1 full20k preprocessing; do not train Students in the preprocessing release turn.
- [x] Complete and independently archive-verify EverTracer Bb processed20k (`evertracer_bb_20260903_130000`).
- [x] Freeze EverTracer paired20k, emit 20k SFT formatter output, and pass 19/19 Ba/Bb parity without starting Student training.
- [x] Complete fresh EverTracer Bb Student training, fresh-process reload, PRIVATE Student archive, independent SHA verification, and offline redownload reload.
- [x] Complete EverTracer Bb frozen detector evaluation with 200/200 finite scores and canonical comparisons.
- [x] Complete EverTracer Bb utility and final scientific closure; do not start CTCC Bb or iSeal Bb automatically.

## CTCC Bb blocked closure — 2026-09-04

<!-- CTCC_BB_BLOCKED -->
Run `ctcc_bb_20260904_055000`: `BLOCKED_AT_PREPROCESSING_ACCEPTANCE_GATE`. Under the frozen standardized Bb preprocessing protocol, CTCC exceeded the predefined identity-fallback acceptance limit (202 > 200), so the experiment was blocked before Student training. Threshold unchanged; no downstream Student/detector/utility was run.

- [x] Complete tiered verification for 10 early proactive Teacher/Ba model archives (2 full-redownload; 8 strong-remote).
- [x] Archive and independently verify PN-FP, EverTracer, and SCW critical detector dependencies.
- [x] Build the 41-artifact canonical archive inventory and pass strict 32/32 full-log index validation.
- [ ] Do not delete AutoDL data without a separate explicit authorization.
