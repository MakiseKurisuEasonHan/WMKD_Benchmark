当前最高状态（2026-09-20 7B最终收口）：仅无卡核验/总结/文档/Git；不启动训练、检测、utility、生成、下载或关机。PN-FP Teacher804/1024；Direct53、Paraphrase71、Logit144（均/1024）已完成。AWM Reference1.0；Direct0.9999952428042889、Paraphrase0.9999933559447527、Logit0.9999957373365760；冻结tau0.007566815861277831，均检出。LLMPrint保持PAUSED_FOR_AWM_SPEED_COMPARISON58/200，cross-lineage暂停未运行。权威汇总 docs/reproduction_reports/7b_scale_extension_final_summary.md；核验/发布状态 results/scale_7b_final_audit/。以下旧授权与阶段状态为历史记录，不是新执行指令。

当前最高授权（2026-09-10 完整Bc）：PNFP→EverTracer→CTCC→iSeal→SCW→Passive5Shared六个独立fresh Llama3.2-3B onlineKD正式run，7500steps，T2/CE0.5/KD0.5冻结；逐项原Ba frozen20k与schedule核验。PNFP使用已批准reconstructed parent，对照99/1024非原历史98。每run训练→原生detector→utility→科学闭环→ONE preferred PRIVATE archive→manifest+segment验证后推进；pilot不重跑。terminal blocker可继续独立方法；全部6terminal且证据/归档/Git/sync/无worker后授权自动安全关新GPU实例。临时跟进获批，真正新增高风险审批且无可推进工作才30分钟timeout。禁止科学调参、新数据/Teacher替代。完整授权 results/logit_distillation/same_lineage_bc/user_authorization_20260910.txt；恢复入口pipeline_state.json。本段覆盖下方pilot停止限制。

当前状态（2026-09-10 PN-FP Bc pilot）：用户已批准 frozen reconstructed parent20k，非原历史Ba exact replay；2-step smoke与独立fresh-init100-step onlineKD均PASS且已停止。T2、CE/KD各0.5、BF16fullFT、batch8、LR1e-5、seed42、7500horizon/225warmup；中位0.31160248s/step、peak allocated35.95GiB；Teacher全参数hash不变、Student已更新。禁止自动full7500/detector/utility/模型上传/新方法/关机。主对照重建Ba trajectory99/1024；原历史Ba98/1024独立保留。等待用户full-run科学决定。入口 results/logit_distillation/pnfp_same_lineage_pilot/pilot_summary.json；报告 docs/reproduction_reports/pnfp_same_lineage_logit_kd_pilot.md。

当前夜间持续授权（2026-09-10 Sydney）：Active Cross-Lineage Bb 五方法按既定冻结协议串行；每方法科学闭环→preferred PRIVATE归档→manifest+segment验证→下一方法。健康任务持续执行；仅全部科研/归档/证据同步/Git push闭环且无worker后 CAMPAIGN_COMPLETE，或确无其他授权动作且等待真正新用户批准30分钟后 USER_APPROVAL_TIMEOUT，允许安全关机。关机前保存状态/receipt并sync、停止临时跟进。不得把旧即时阶段描述当作重跑命令。原文 results/active_cross_lineage_bb/overnight_authorization_20260910.txt。

当前最高持续授权（2026-09-09）：当前 Active Cross-Lineage Bb 范围内，普通 SSH trust/authorized_keys、同步、轻量 Git commit/push、preferred PRIVATE archive、分段验证、可核验冗余临时文件清理及正常串行推进均已持续授权，无需逐步询问。科学配置不变、唯一科研资产保留、新实例不传 ModelScope token。原 SSH 审批等待解除；PNFP archive 后 EverTracer→CTCC→iSeal→SCW。完整原文 results/active_cross_lineage_bb/continuous_authorization_20260909.txt。仅真正需要新高风险批准且无其他授权工作时适用30分钟等待关机规则。

当前最高授权（2026-09-09，用户聊天正文确认）：批准 Active Cross-Lineage Bb 预检及原授权串行实验，覆盖下方历史 Bb 禁止条款。仅 PN-FP XBb→EverTracer XBb→CTCC XBb2→iSeal XBb→SCW XBb；新实例 ssh6000bb、旧CPU资产源 ssh6002。fresh Qwen固定revision、冻结paraphrased数据、原科学配置；新实例不配置或传递ModelScope token。完整范围以 results/active_cross_lineage_bb/ 下用户授权和 pipeline_state.json 为准。

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

当前授权（2026-09-07）：用户明确解除暂停，仅恢复 Method 13 UTF Experiment A，STRICT SERIAL INTERACTIVE MODE。先修复 DeepSpeed 整数兼容并通过真实单步 preflight，再正式训练、detector、negative control、utility、reload、归档验证及 Git 闭环。不得启动 Method 14/15；auto_advance=false，auto_shutdown=false；UTF 闭环后 STOP。历史暂停证据保留。

当前唯一执行范围（2026-09-06 用户新 prompt）：Method 13 UTF Experiment A，STRICT SERIAL INTERACTIVE MODE。EaaW 和 Instructional Fingerprinting 已成功闭环，不重跑。禁止启动 Method 14/15、Ba/Bb、KD 或 paraphrasing attack；UTF 闭环后等待用户下一步范围授权。工程错误最小修复、有界重试当前方法，RED 科学歧义报告用户。UTF canonical 为 meta-llama/Llama-2-7b-chat-hf，revision f5db02db724555f92da89c216ac04704f23d4590；公开镜像只改变传输，必须核验全部 canonical 文件身份，不向第三方镜像发送 HF token。详见 docs/METHODS_11_15_AUTOMATION.md 和 pipeline state 的 execution_scope=utf_only。

# WMKD_Benchmark 会话入口

当前授权更新（2026-09-05）：用户已正式批准五方法串行 Experiment A 自动复现、最小工程修复、逐方法归档/Git闭环及全部terminal后的自动关机。前次等待prompt/STOP仅属于已结束的迁移任务。详见 [docs/METHODS_11_15_AUTOMATION.md](docs/METHODS_11_15_AUTOMATION.md) 与 results/methods_11_15_pipeline_state.json；旧科学设计禁改及KEEP/UNCERTAIN保留规则继续有效。


始终用中文与用户交流。先读 `docs/CURRENT_STATE.md`、`docs/EXPERIMENT_PROTOCOL.md`、`PROJECT_STATUS.md`、`TODO.md`，再读相关实验报告及日志。当前 Git 文件是恢复入口，历史日志不是新执行授权。

第一批十方法已 CLOSED：30 comparison slots、32 canonical full-log objects。下一目标 `METHOD_11_EAAW_EXPERIMENT_A = NOT_STARTED`。必须等用户独立正式 Experiment A prompt；状态迁移/清理任务不授权 science、模型/数据下载或新方法 clone。

用户与 ChatGPT 决定科研设计；按正式 prompt 执行，不擅改科学配置。方法 11–15 优先官方原生最小科学有效设置，不自动沿用旧 3B 骨干。A2/A3 表示科学变化，cont 表示运行延续。每个正式科学对象必须有 full_experiment_log.json 并入全局索引；不编造缺失值。

开始任务重验本地与 AutoDL Git。AutoDL 用 `ssh -p 32514 root@connect.westd.seetacloud.com`，不假设 alias 6000；学校 VPN 关闭（La Trobe 开启）。长 GPU 实验 detached，一次一个大型任务；不得干扰他人进程。

下载优先本地/cache/ModelScope/可信国内镜像；保留官方 identity/revision/SHA。清理须按用户授权的 exact-path dry-run，只有全部归档恢复及无使用等门槛通过的 DELETE 可删；UNCERTAIN=KEEP。不得删除代码、日志、报告、索引、归档验证及唯一证据。不得 force/reset/clean/history rewrite；不得提交大模型/数据/cache/secret。

任务结束给出“给 ChatGPT 的总结”，包括实际动作、文件、运行/结果、环境、归档、Git、阻塞、未做事项和下一步授权边界。详细规则以 docs/EXPERIMENT_PROTOCOL.md 为准。
