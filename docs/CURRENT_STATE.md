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

# WMKD_Benchmark 当前状态：方法 11–15 之前

当前授权更新（2026-09-05）：用户已正式批准五方法串行 Experiment A 自动复现、最小工程修复、逐方法归档/Git闭环及全部terminal后的自动关机。前次等待prompt/STOP仅属于已结束的迁移任务。详见 [METHODS_11_15_AUTOMATION.md](METHODS_11_15_AUTOMATION.md) 与 results/methods_11_15_pipeline_state.json；旧科学设计禁改及KEEP/UNCERTAIN保留规则继续有效。


本文件与 `EXPERIMENT_PROTOCOL.md` 定义当前状态和规则；带日期的旧日志仅为历史证据，不构成新执行指令。项目目标是研究 LLM ownership-verification watermarking/fingerprinting 在知识蒸馏和相关模型提取攻击下的稳健性与稳定性，面向 benchmark / analysis 论文，目标 ICLR / 顶级会议。

## 已完成的第一批

方法 1–10：PN-FP、EverTracer、CTCC、iSeal、SCW、LLMPrint、REEF、HuRef、AWM、ZeroPrint。
正式比较矩阵已 CLOSED：10 reproduction + 10 Ba + 10 Bb comparison = 30 个比较实验槽位；共享被动攻击不是五次独立训练。
PN-FP、EverTracer、iSeal、SCW Bb COMPLETE；CTCC 使用独立 Bb2 COMPLETE 填入比较槽位。
原 CTCC Bb 永久保留为 `BLOCKED_AT_PREPROCESSING_ACCEPTANCE_GATE`：fallback 202 > gate 200，后续 Student/detector/utility `NOT_RUN`。

| 方法 / 原生指标 | Teacher | Base | Ba | Bb comparison |
|---|---|---|---|---|
| PN-FP / matches | 956/1024 | 1/1024 | 98/1024 | 72/1024 |
| EverTracer / AUC, TPR | 1, 1 | .4417, .05 | .4987, .06 | .4757, .08 |
| CTCC / trigger | 95/95 | 0/95 | 0/95 | Bb2: 0/95; negatives 0/205 |
| iSeal / registered; BLEU | 179/200; 69.171651 | 0/200; 2.332514 | 0/200; 2.589326 | 0/200; 2.3018129521270327 |
| SCW / p-value | 0 | .9199569225 | .8440861702 | .9529914855957031 |

以上指标不可统一为伪造的 retention %。仅支持已测设置下的结论，不能推导普遍移除、普遍免疫或精确消失步骤。
来源：`reproduction_reports/proactive_bb_final_closure_integrity.md`、各方法 canonical summary/full log。

Passive Shared Ba COMPLETE；原 Bb 与 Bb2 均 `BLOCKED_AT_PILOT`；Bb3 COMPLETE，5/5 frozen detectors positive。
Bb3 含 4,635/20,000 = 23.175% atomic identity，必须披露；同骨干结果不证明指纹转移或普遍 KD 免疫。

## 冻结的历史 UP 参考

`VALIDATED_UP_REFERENCE = PASSIVE_SHARED_BB3`。
若 Qwen non-special-token count <= 1，保留 source answer；否则使用冻结的 Qwen2.5-3B-Instruct semantic-preserving paraphrase。
Prompt SHA256 `7f4284788b5147bca7f444db989eab6f2f9f3a10eb06fddb309fc06748414495`；do_sample=true、temperature=.7、top_p=.9、seed=42。
这不是方法 11–15 已获授权的新攻击配置，不得回写历史协议。

## 证据、归档与恢复

Canonical index：`../results/experiment_full_logs_index.json`：32 objects / 32 unique composite IDs，严格路径及 SHA 检查见 `../results/pre_methods_11_15_validation.json`。
30 比较槽位与 32 canonical scientific objects 不是同一计数口径。此次维护不新增 scientific object。

Canonical archive：`../results/project_archive_inventory.json`，41 artifacts：24 VERIFIED_ARCHIVED、8 ARCHIVED_STRONGLY_VERIFIED、0 MISSING_ARCHIVE、7 NOT_APPLICABLE、2 PERMANENTLY_UNAVAILABLE。
早期模型 full independent redownload 样本为 2；另外 8 个 strong-remote 不得称为 full-redownload。
报告：`reproduction_reports/project_modelscope_archive_final_report.md`。

归档闭环 flags：ALL_RECOVERABLE_CRITICAL_ARTIFACTS_ARCHIVED、ALL_RECOVERABLE_CRITICAL_MODELS_ARCHIVED、ALL_RECOVERABLE_CRITICAL_DATASETS_ARCHIVED、ALL_CRITICAL_DETECTOR_DEPENDENCIES_ARCHIVED、ALL_COMPLETED_BB_ARTIFACTS_VERIFIED_ARCHIVED、EARLY_A_BA_ARCHIVES_STRONGLY_VERIFIED、STRICT_FULL_LOG_INDEX_32_32_PASS 均 YES。
`EARLY_A_BA_FULL_REDOWNLOAD_SAMPLE_COUNT = 2`。
`SERVER_CAN_BE_DELETED_WITHOUT_NEW_RECOVERABLE_SCIENTIFIC_DATA_LOSS = YES` 是恢复能力结论，不是任意删除授权。

永久历史缺失：PN-FP original canonical Ba frozen20k 与 SCW original canonical Ba frozen20k；后来的 reconstructed parents 是不同身份，已归档验证，不代表原件恢复。
清理仅按 `../results/pre_methods_11_15_cleanup.json` 的 exact DELETE paths 执行；保留历史路径，未来使用前按 archive manifest 恢复并校验 SHA，不能把清理后的本地路径误认为仍存在。

## New proactive ownership-verification methods

| 编号 | 方法 | 当前状态 |
|---|---|---|
| 11 | EaaW | NOT_STARTED |
| 12 | Instructional Fingerprinting | NOT_STARTED |
| 13 | UTF | NOT_STARTED |
| 14 | Double-I Watermark | NOT_STARTED |
| 15 | CodeGenGuard | NOT_STARTED |

这是当前计划顺序，不是不可变的科研设计。均按主动嵌入式语言模型所有权验证方法入选；Instructional Fingerprinting / UTF 使用 fingerprint 术语；CodeGenGuard 面向代码语言模型。正式执行前仍须核实官方实现。
选择优先级：官方代码、稳定实现、小下载、轻量模型、快训练、低工程复杂度。
`NEXT_STAGE = METHOD_11_EAAW_EXPERIMENT_A`，`STATUS = NOT_STARTED`。
等待独立正式 Experiment A prompt；本次任务结束后 STOP。不得下载 EaaW 模型/数据、clone 新方法源码、训练、预处理、detector 或 utility science。

## 新会话恢复入口

1. 读取本文件、`EXPERIMENT_PROTOCOL.md`、根目录 README / PROJECT_STATUS / TODO / DECISIONS / EXPERIMENT_LOG / CODEX_LOG。
2. 本地与 AutoDL 分别 git fetch、status、rev-parse HEAD origin/main、rev-list --left-right --count HEAD...origin/main。历史 HEAD 仅为基线；最终提交用 Git 实际值确认，避免自引用提交 SHA。
3. 本地：`C:\Users\Eason\Desktop\WMKD_Benchmark`；GitHub：`MakiseKurisuEasonHan/WMKD_Benchmark`。
4. AutoDL：`ssh -p 32514 root@connect.westd.seetacloud.com`；代码 `/root/autodl-tmp/WMKD_Benchmark`；数据 `/root/autodl-tmp/WMKD_Benchmark_data`。不能假设旧 alias 6000。AutoDL 学校 VPN 关闭；La Trobe 学校 VPN 开启。
5. 本轮硬件：RTX PRO 6000 97887 MiB，driver 580.82.09 / driver-supported CUDA 13.0；cgroup CPU quota 22 核、memory.max 118111600640 bytes (110 GiB)。宿主 free/nproc 展示的 1 TiB / 208 并非容器配额。CUDA toolkit、Python/PyTorch 实验环境须在正式任务重新核实。
6. 清理前后磁盘、删除列表、保留对象见 cleanup JSON；严格验证见 validation JSON。只继续用户明确授权的下一步。

## 本轮实际发现与修复

在归档权重删除前发现：历史索引在 Windows 为 32/32 PASS，但 AutoDL 有 16 个 full logs 因 Git LF/CRLF 转换而字节 SHA 不符。转换回 CRLF 后全部精确匹配原索引哈希，JSON 科学内容未改变。`.gitattributes` 现逐个固定 32 个对象的原有换行格式（16 CRLF、16 LF），保留原索引及历史哈希。`scripts/validate_durable_state.py` 默认只读；显式 `--restore-indexed-eol` 只允许转换后精确等于既有索引 SHA 的修复，不能容忍或掩盖内容差异。今后新增 full log 时必须固定稳定的换行字节并验证 Windows/Linux 两端。

清理范围有意限定为已匹配 strong-remote evidence 的历史 A/Ba 权重；未额外请求 ModelScope 网络重验证，亦未将 strong-remote 升格为 full-redownload。其它已归档 Bb 模型在本轮未建立逐文件清理匹配，按 UNCERTAIN 保留；这不表示其归档缺失。优化器及其它非权重证据也保留。
