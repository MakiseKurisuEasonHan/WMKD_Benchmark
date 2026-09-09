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

# Project Status

当前授权更新（2026-09-05）：用户已正式批准五方法串行 Experiment A 自动复现、最小工程修复、逐方法归档/Git闭环及全部terminal后的自动关机。前次等待prompt/STOP仅属于已结束的迁移任务。详见 [docs/METHODS_11_15_AUTOMATION.md](docs/METHODS_11_15_AUTOMATION.md) 与 results/methods_11_15_pipeline_state.json；旧科学设计禁改及KEEP/UNCERTAIN保留规则继续有效。


## 当前阶段 — 2026-09-05 方法 11–15 前规则与状态迁移

以 [docs/CURRENT_STATE.md](docs/CURRENT_STATE.md) 为当前状态入口。第一批十方法 CLOSED：30 comparison slots；32 canonical full-log objects。项目归档已闭环（24 verified / 8 strong-remote / 0 missing / 7 N/A / 2 permanent historical losses）。CTCC 比较使用 Bb2，原 Bb BLOCKED 历史不变。

新增顺序：11 EaaW → 12 Instructional Fingerprinting → 13 UTF → 14 Double-I Watermark → 15 CodeGenGuard。下一目标 METHOD_11_EAAW_EXPERIMENT_A，NOT_STARTED；须等待独立正式 prompt。本次只做状态/规则、精确归档权重清理与 Git 闭环。

清理记录：results/pre_methods_11_15_cleanup.json；验证：results/pre_methods_11_15_validation.json。以下旧快照/待办按历史保留，不应恢复执行。
维护执行完成：26 个已验证归档权重文件删除，释放约 60.6 GiB，剩余约 167.3 GiB；30 个 UNCERTAIN 权重文件保留。修复 Git 换行造成的远端 16 个 full-log SHA 不符，原索引和科学内容未变。完整报告：docs/reproduction_reports/pre_methods_11_15_durable_state_report.md。EaaW NOT_STARTED，STOP 等待独立正式 prompt。



## Current phase — 2026-09-05 proactive Bb final closure

The proactive Bb batch is terminal. PN-FP Bb, EverTracer Bb, iSeal Bb, and SCW Bb are `COMPLETE`; original CTCC Bb is permanently `BLOCKED_AT_PREPROCESSING_ACCEPTANCE_GATE` because identity fallback `202 > 200`, with Student/detector/utility `NOT_RUN`; the distinct CTCC Bb2 scientific variant is `COMPLETE`. No proactive Bb stage is pending or runnable. The strict global full-log audit covers 32 canonical objects; the final closure integrity report is `docs/reproduction_reports/proactive_bb_final_closure_integrity.md`.

The historical snapshots below are retained as time-stamped provenance. Their `NOT_STARTED`, `PENDING`, and earlier HEAD statements describe prior states and are not current instructions or current status.

## Historical phase — 2026-09-03 durable audit before proactive Bb

WMKD_Benchmark has ten ownership-verification methods. Proactive/embedded: PN-FP, EverTracer, CTCC, iSeal, SCW. Passive/intrinsic: LLMPrint, REEF, HuRef, AWM, ZeroPrint. All ten have completed their preferred A/A2 (iSeal ultimately A6) reproduction and Ba evaluation.

Passive Shared Ba is `COMPLETE` with 5/5 detectors positive. Original Passive Bb and Bb2 are both `BLOCKED_AT_PILOT`; their instruction-echo/meta-commentary failure histories remain immutable. Passive Bb3 is `COMPLETE` under run `passive5_shared_bb3_20260903_164929`: 20,000 final records, 4,635 atomic identities (23.175%), 15,365 Qwen submissions, 13,061 paraphrases, 2,256 natural identities, 48 fallbacks, 279 rejected attempts, and zero final leakage/control-token leakage/truncation. Dataset/frozen-file SHA256 are `549d38ca634c2c69a646e23d1bfc65ec019887e43070deec031f97459cc7be99` / `60bd4539b5d332b076a92072b86b51f8ddad3749a0a166f594233f5c1730dd88`. The fresh Student completed 7,500/7,500 steps, final loss `0.962497413953`, and fresh reload passed.

All five Bb3 detectors remained positive: LLMPrint `0.785` (tau `0.7150049776`), REEF `0.967286` (tau `0.4546738923`), HuRef `99.998734` (tau `4.1198940277`), AWM `0.999996` (tau `0.00179533649`), ZeroPrint rescaled `0.917022` (tau `0.6793505996`). Utility was ARC `0.4906143345`, TruthfulQA `0.4544162042`; English/French sanity passed. Under the tested same-backbone standardized behavioral-distillation setting, Bb3 preprocessing did not reduce any passive fingerprint below its frozen threshold. This does not establish fingerprint transfer or universal immunity, and the 23.175% atomic-identity component must always be disclosed.

The canonical ModelScope inventory records 4/4 verified PRIVATE Passive-5 artifacts. The global full-log index contains 26/26 unique objects with no broken paths. For proactive Ba, only Teacher-before versus final-Student-after is available; exact watermark disappearance step/epoch is `NOT ESTABLISHED`.

Historical snapshot: proactive-Bb execution was method-scoped. `PROACTIVE_BB_PROTOCOL_FROZEN = YES`: exact validated Passive Bb3 scientific preprocessing, method-specific canonical Ba frozen20k, independent processed20k, independent fresh-canonical Student, Ba-identical training, exact frozen detector reuse, and Ba-matched utility. At that time EverTracer Bb was `DETECTOR_COMPLETE_UTILITY_PENDING`; CTCC Bb, iSeal Bb, and PN-FP/SCW had not started. This paragraph is superseded by the current closure state above.

Latest confirmed pre-audit closure: local HEAD = `origin/main` = `a633b232e1c09523e54b8a9537d84347d5e94d14`, ahead/behind `0/0`, clean. Post-commit state must be revalidated in the final handoff.

### Proactive Bb readiness continuation — 2026-09-03

Direct SSH endpoint `connect.westd.seetacloud.com:48835` restored access; alias `6000` is invalid because it resolves to `0.0.23.112:22`. Remote Git is safely on clean `main` at canonical `539b5a57`, with the former detached SCW checkout preserved as `historical/scw-deployment-45d6f77`. EverTracer, CTCC, and iSeal canonical Ba frozen20k survive with 20,000 records and distinct verified content hashes; PN-FP and SCW parents are absent. The three surviving parents require archive before Bb. Exact Passive Bb3 Qwen model/tokenizer and manifest are absent. All five methods remain NOT_READY; no formal work started.

## Historical pre-Bb preparation snapshot — 2026-09-03

The benchmark has ten current ownership-verification methods. Proactive/embedded: PN-FP, EverTracer, CTCC, iSeal, SCW. Passive/intrinsic: LLMPrint, REEF, HuRef, AWM, ZeroPrint. All ten have completed preferred A/A2/A6 reproduction objects and Ba evaluation; passive Ba correctly used one shared Teacher/dataset/Student because the five passive References are the same canonical model.

Experiment Bb is now frozen by explicit user decision as answer-only Untargeted Paraphrasing followed by Distillation (UP + Distillation). The first Bb cohort is passive methods 6–10: LLMPrint, REEF, HuRef, AWM, and ZeroPrint. Current state is `PASSIVE_6_TO_10_BB_PROTOCOL_PREPARATION`; no Bb run, AutoDL action, GPU task, download, or cleanup is authorized by this audit.

Local Passive-5 Shared Bb development is `PREPARED_NOT_STARTED`: config, versioned prompt, canonical Ba frozen20k gates, paired schema, resumable retry journal, exactly-20k freeze, quality/human audit, Student adapter, Ba/Bb parity validation, detector/utility orchestration, full-log/index support, tests, and a guarded future launcher are present. `Qwen/Qwen2.5-3B-Instruct` is frozen as the paraphraser identity, but its revision is intentionally unresolved and blocks any formal launch.

The canonical Passive-5 Shared Ba frozen20k now has a verified private transport backup at ModelScope dataset `MakiseKurisuEasonHan/WMKD_Benchmark_passive5_shared_ba_frozen20k`. Independent download reproduced 20,000 records and all three canonical identities, including byte-identical JSONL SHA256 `408053fef5fa42b3a203e70ac049f43b73f9b0fccb06189363d0643c3633cbed`. ModelScope revision is unavailable because the SDK dataset-revisions endpoint returned 404; download used the exposed `master` revision. This copy is transport/storage only and does not create or modify a scientific dataset.

The global full-log index currently contains 21 objects. Passive Shared Ba retained detectability for 5/5 frozen detectors in the tested same-backbone setting, which does not establish general KD immunity or newly transferred fingerprints. For proactive Ba, Teacher-before versus final-Student-after is supported, but exact checkpoint-level disappearance remains unestablished for 0/5 complete trajectories.

Latest pre-audit closure: local HEAD = `origin/main` = `21b4e093e557f7f2c80133b88a0fd51ef579a4e5`, ahead/behind `0/0`, clean. This must be revalidated after the audit commit/push.

## 2026-09-01 four-method pre-formal smoke complete (historical)

LLMPrint A2 remains safely paused at 97/200 with IDs 000-096 immutable and future lineage restricted to `A2_cont1_missing_ids_only`. REEF, AWM, HuRef and ZeroPrint compatibility smokes all completed and persisted independently; none is a formal scientific result. AutoDL ended idle at 0 MiB GPU use with 377 GiB free disk and no shutdown. Integrated formal readiness is **NO**: REEF/AWM are conditionally ready after panel/threshold freezes, ZeroPrint additionally needs an official-budget speed gate, and HuRef remains `TIME_BUDGET_RISK` pending sorted-token and 4096-token scaling evidence. No formal A or Ba started.

## Historical phase snapshot

Current closure is **5/10**: PN-FP, EverTracer, CTCC, iSeal, and SCW are FULLY CLOSED. Remaining methods are LLMPrint, REEF, AWM, HuRef and ZeroPrint. LLMPrint A2 `llmprint_a2_20260901_064855` is safely `PAUSED_BY_USER_FOR_PRE_FORMAL_MULTI_METHOD_SMOKE` at 97/200; IDs 000–096 are immutable and only 097–199 may be handled by a future A2 cont1. REEF/AWM/HuRef/ZeroPrint are in official-audit and bounded-smoke preparation only. No formal run for those four, no Ba, and no automatic shutdown is authorized.

SCW strict A remains a preserved pre-formal infrastructure/data-access attempt: Formal training never started, and its PyArrow/GIL finalization plus overseas official-data access failures are not a scientific failure. The explicitly authorized A2 domestic-data adaptation completed, produced the preferred Teacher, and Ba completed with a fresh canonical Student. The detailed immutable history below is retained rather than rewritten.

iSeal is FULLY CLOSED through A and Ba plus private ModelScope archival. Experiment A remains blocked before formal launch by the pinned public-code exact-zero gate; authorized A2-A6 culminated in preferred Teacher A6 (179/200 registered). Ba Student `iseal_ba_20260830_165442` completed 7,500 steps from the fresh canonical base. Registered success fell 179/200 → 0/200, equal to Base 0/200 (89.5-point drop; 0% thresholded retention); ARC/TruthfulQA were 0.481229/0.449818, ordinary generation 10/10, and fresh reload passed. Teacher/Student private archives passed remote metadata verification and await independent destination SHA256. Bb/A7 were not created.

CTCC is FULLY CLOSED through Experiments A and Ba plus private ModelScope archival. Experiment A run `ctcc_a_20260829_190251` established the preferred Teacher from all pinned public-artifact records (Trigger 461, Suppression 428, Normal 1000; total 1889) without augmentation. Official source is pinned to `Xuzhenhua55/CTCC@8db93218260bed31b8f18acc9c6ac3e1955d3a42`; the paper's 500/500/1000 total 2000 remains a paper-vs-public-artifact discrepancy.

The full released test contains 95 Trigger, 100 Suppression, and 105 Normal records. Teacher/Base trigger activation was 95/95 versus 0/95; Teacher combined-negative false activation was 0/205. CTCC Ba preserved the failed 40,007-raw parent, completed through infrastructure-only generation continuation `ctcc_ba_generation_20260829_195943_cont1`, froze exactly 20,000 QA (SHA256 `621c9aedcf3a4a1db86a4848bbf93fa893d18022f15b913e8aeeb28739412484`), and trained fresh-canonical Student `ctcc_ba_20260830_025244` for 7,500/7,500 steps. Fresh-reload evaluation continuation `ctcc_ba_eval_20260830_033556_cont1` produced Student Trigger 0/95, negatives 0/205, ARC 0.483788, TruthfulQA MC2 0.450614, and a passing ordinary-generation sanity check. The bounded result is that CTCC trigger retention fell to the Base level under this tested standardized direct-distillation setting while tested utility remained functional.

The CTCC preferred Teacher LoRA adapter and Ba inference-ready Student final model are uploaded to private ModelScope repositories `MakiseKurisuEasonHan/WMKD-CTCC-A-Teacher` and `MakiseKurisuEasonHan/WMKD-CTCC-Ba-Student`. Both are `uploaded_to_modelscope_awaiting_destination_hash_verification`: source manifests and remote filename/count/size/blob-metadata checks passed, but a future independent destination download is required for full SHA256 verification.

PN-FP reproduction and direct-distillation evaluation are CLOSED. A2 is the preferred utility-preserving teacher; Ba is complete with strong watermark degradation and partial retention. Bb was not run and remains deferred. No PN-FP GPU or transfer process is active.

EverTracer is FULLY CLOSED after protected cleanup. Experiments A and Ba are scientifically and operationally complete. A's preferred teacher achieved member-oriented AUC/TPR@FPR<=5% of 1.0/1.0. Ba run `evertracer_ba_20260829_124055` completed with student AUC/TPR 0.4987/0.06, indicating that direct distillation reduced the detector signal to near chance while reload and generation sanity passed. There is no EverTracer blocker; Bb remains NOT RUN/deferred.

The EverTracer A preferred teacher and Ba student were uploaded to their fixed private ModelScope repositories. Both archives are `uploaded_to_modelscope_awaiting_destination_hash_verification`; full destination SHA256 remains deferred to a future download on another machine.

The canonical cross-session rules are consolidated in `docs/EXPERIMENT_PROTOCOL.md`. The selected benchmark methods are PN-FP, CTCC, SCW, EverTracer, iSeal, LLMPrint, and REEF. Current default lifecycle is A → Ba; A2/A3 are reserved for scientific-configuration corrections, while unchanged-science engineering recovery uses immutable continuation lineage. Bb remains NOT RUN/deferred while all seven methods' A and Ba are prioritized first; a future explicitly approved UP implementation is not inherently limited to Dipper.

The durable benchmark default is a same-family, same-size, same-revision A/Ba/Bb design using canonical `meta-llama/Llama-3.2-3B-Instruct@0cb88a4f764b7a12671c53f0838cd831a0843b95`. Every method's Ba must use that method's own preferred teacher to generate its own answers; another watermark's teacher, QA, frozen 20k, or student must never be reused. Students always start from fresh canonical unwatermarked weights. Any method-specific backbone or Ba deviation requires a recorded blocker and explicit user approval.

Completed methods: **5/7** (PN-FP, EverTracer, CTCC, iSeal, and SCW). Remaining: **LLMPrint, REEF**. LLMPrint is at the authorized preparation/audit stage only. The canonical Llama remains preserved. The last verified AutoDL operational baseline is Ubuntu 22.04, Python 3.12, PyTorch 2.8.0, CUDA 12.8, RTX PRO 6000 96 GB ×1, Intel Xeon Platinum 8470Q with 22 vCPUs, 110 GB RAM, 30 GB system disk, and approximately 500 GB data capacity (50 GB free + 450 GB paid); it must be revalidated after reconnecting. Older 208-vCPU/approximately-1-TiB records are historical only.

## Completed

- Established the independent WMKD_Benchmark repository structure.
- Added baseline documentation, project logs, and safeguards against committing large artifacts or secrets.
- Defined the confirmed high-level research question and intended workflow without claiming experimental results.
- Created the private GitHub repository and synchronized the initialization commit on `main`.
- Initialized the La Trobe lightweight project mirror and dedicated large-artifact warehouse.
- Initialized the AutoDL compute checkout, isolated compute-data root, and project-specific cache paths.
- Fixed and downloaded the shared Llama-3.2-3B-Instruct backbone revision on Windows with a complete SHA256 manifest.
- Archived the same fixed Llama-3.2-3B-Instruct revision in the La Trobe warehouse as exactly 12 verified files (6,434,748,511 bytes), with a server-side machine-readable manifest and full SHA256 equality.
- Fixed the PNFP official source commit and created a compatible isolated AutoDL environment.
- Evaluated ModelScope candidate `LLM-Research/Llama-3.2-3B-Instruct`, rejected it as a standalone provenance source, and later used its 11 matching files only as transport payloads under an explicitly approved repair protocol.
- Established the complete canonical Llama-3.2-3B-Instruct snapshot on AutoDL as exactly 12 files and 6,434,748,511 bytes, with full SHA256 equality to the frozen Hugging Face manifest and no `original/` directory.
- Passed offline tokenizer, chat-template, BF16 single-GPU model-load, and short-generation smoke checks in the existing PNFP environment.
- Added a reusable best-effort Gmail SMTP notification subsystem for future formal runners, with external mode-600 secret storage, duplicate protection, non-secret tests, and an optional read-only terminal-state watcher. Credentials are not yet configured and no watcher is attached to the active PN-FP run.
- Deployed the three notification utilities as standalone files under the AutoDL data root without changing the active AutoDL Git checkout or PN-FP process; credential configuration and watcher launch were intentionally deferred until an independent test could succeed.
- Configured the external mode-600 Gmail secret, successfully sent independent test `email_test_20260827_233957`, and started read-only detached watcher PID 89850 for the active PN-FP run. No retrospective STARTED event was sent; the training PIDs and AutoDL checkout remained unchanged.

## Current task

- Experiment A completed successfully (`1019/1024`, reload validation passed).
- Experiment A formal report and machine-readable summary record 30/30 epochs, eval_loss 0.0119302, base 1/1024 and paired difference 99.4141 percentage points.
- Experiment A2 completed scientifically through parent training run `pnfp_exp_a2_20260828_025240` plus immutable evaluation continuation `pnfp_exp_a2_eval_20260828_105530`. A2 achieved 956/1024 PN-FP detection, passed watermark and utility gates, and is the preferred Ba teacher.
- Experiment A1 completed with 1019/1024 detection but severe ordinary-generation degradation.
- Experiment A2 completed scientifically through training plus immutable evaluation continuation, achieved 956/1024, passed both gates, and is the preferred utility-preserving teacher.
- Experiment Ba run `pnfp_exp_ba_20260828_111148` completed its engineering pipeline. A2→Ba detection fell from 93.359375% to 9.5703125% (83.7890625-point drop; 10.251046% retention) while the utility gate passed. The bounded scientific result is strong degradation with partial retention under this tested setting.
- The old A1-based failed Ba run `pnfp_exp_ba_20260828_012228` remains immutable. Bb, UP, and Dipper have not started.

## Blockers

- No PN-FP scientific blocker remains. Notification delivery remains best-effort and outside scientific success criteria.
- The artifact protocol now separates immutable source/upload checks from destination-side full SHA256; see `docs/storage/artifact_transfer_protocol.md`.
- PN-FP A2 teacher and Ba student are private at `MakiseKurisuEasonHan/WMKD-PNFP-A2-Teacher` and `MakiseKurisuEasonHan/WMKD-PNFP-Ba-Student`. Both remain `uploaded_to_modelscope_awaiting_destination_hash_verification` under the current protocol; Ba's stronger same-source remote re-read is preserved but is not distinct-destination verification.
- Completed PN-FP large training/readback artifacts were cleaned from AutoDL with approximately 48 GiB reclaimed. The canonical Llama-3.2-3B-Instruct remains preserved as 12 files, 6,434,748,511 bytes, with 12/12 SHA256 passed.
- EverTracer has no blocker. Protected cleanup reclaimed 77.958 GiB while preserving the canonical base, Teacher, Student, Reference, adapters, frozen neighborhoods, final20k, raw32k, shared infrastructure/cache, and credentials.

## Next step

- iSeal A/Ba and private archival are fully closed. Do not create A7, run Bb, or perform destructive cleanup without separate explicit approval.
- SCW is FULLY CLOSED through strict-A infrastructure history, A2 preferred Teacher, standardized Ba, private ModelScope archival, canonical full JSON logs, and bounded cleanup.
- LLMPrint detector/panel freeze is complete and formal 300-fingerprint construction is explicitly authorized only after all 14 readiness gates pass. The next action is remote provenance/hash/GPU verification plus a minimal `CUBLAS_WORKSPACE_CONFIG=:4096:8` sanity, followed by one detached formal launch if and only if every gate passes. Ba, 20k generation, Student training, and automatic scientific reconfiguration remain prohibited.
- After separate explicit user authorization, final AutoDL cleanup deleted only the five audited exact paths: A2-A5 non-preferred Teacher artifacts and Ba `checkpoint-7500`. Logical size removed was 47,429,470,039 bytes; filesystem used space decreased by 47,429,681,152 bytes. Canonical base, A6 Teacher, Ba final Student, frozen20k, ModelScope manifests, shared infrastructure/cache, raw generation, and all other-watermark artifacts remain protected.


## A2 immutable evaluation continuation `pnfp_exp_a2_eval_20260828_105530`

Parent training run `pnfp_exp_a2_20260828_025240` remains operationally FAILED after external dataset acquisition failure. The validated checkpoint and reusable evaluations plus this continuation establish the final result. Watermark gate: **passed**; utility gate: **passed**; judgement: **A2 is the preferred PN-FP teacher for future Ba**.


## A2-teacher formal Ba run `pnfp_exp_ba_20260828_111148`

Teacher A2 provenance: `pnfp_exp_a2_20260828_025240` + `pnfp_exp_a2_eval_20260828_105530` (956/1024 = 93.359375%). Frozen QA: 20,000 samples, SHA256 `6ad11ff25826c32d71641c7433993070a8865e9e64e99841856e09b61d861a72`. Base/Ba: 1/1024 (0.09765625%) / 98/1024 (9.5703125%); teacher→Ba drop 83.7890625 points; retention 10.251046%. ARC Base/A2/Ba: 0.448805461 / 0.443686007 / 0.478668942. TruthfulQA MC2 Base/A2/Ba: 0.505450760 / 0.467427921 / 0.463479842. Utility and reload gates passed. Judgement: **PN-FP is vulnerable under the tested direct-distillation setting, with strong degradation and partial retention**. The old A1-based run remains immutable FAILED.
# 2026-08-31 SCW status

SCW Experiment A is transitioning from failed exact online-stream materialization infrastructure to the disclosed `DETERMINISTIC_FINITE_STREAM_SAMPLING_ADAPTATION`. Formal A and Ba have not started. The next authorized run builds/audits the 160k frozen local stream, runs one 4-step clean-exit gate, and starts Formal A only on gate PASS.
# 2026-08-31 SCW recovery hold

SCW Formal A never started. Deterministic run `scw_deterministic_full_20260831_214200` failed before LucieFr pool generation because authoritative Parquet path discovery returned no matching objects. Automatic AutoDL shutdown is temporarily disabled while recovery is debugged; no new orchestrator is authorized in this post-mortem turn.
# 2026-08-31 SCW A2 frozen-data status

SCW A is archived without a formal run or scientific result. SCW A2 domestic-data protocol is frozen with ModelScope Aya French / MS Instruct / MS OpenWebText roles. The unique 80k frozen stream and exact 160k two-pass replay audit passed. Formal A2 remains gated by one 4-step clean-exit run; Ba is not started.

## SCW A2 recovery — 2026-09-01

Formal A2 training is complete (2500/2500) and the Teacher artifact exists. Scientific evaluation is incomplete: Base French generation failed before output because its pinned dataset was not available offline. No detector or utility result exists, so `preferred_teacher` remains `NOT_EVALUATED`. Automatic shutdown is temporarily disabled project-wide.

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

## WMKD 5/7 closure integrity — 2026-09-01

<!-- WMKD_5_OF_7_CLOSURE_INTEGRITY_20260901 -->
PN-FP, EverTracer, CTCC, iSeal, and SCW are **FULLY CLOSED** at the project-record level. Ten canonical preferred-Teacher/Ba-Student full JSON logs and `results/experiment_full_logs_index.json` now preserve the available provenance, configuration, telemetry, detector, utility, continuation, artifact, and archive evidence. Missing historical telemetry is explicitly unavailable; no Ba has checkpoint-level detector evidence, so exact watermark-disappearance steps are not localized. Completed methods: **5/7**. Remaining methods: **LLMPrint** and **REEF**. Automatic shutdown remains disabled.

AutoDL high-confidence cleanup completed after synchronization: 51,689,418,752 filesystem bytes reclaimed from two non-scientific speed-test namespaces and two incomplete fragments. Formal artifacts/checkpoints, frozen datasets, shared Base/cache/utility/environment resources and all ambiguous data remain protected. Current instance remains running with manual shutdown required.

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

Pilot cont4 added the authorized retry-exhaustion identity fallback and passed 42/42 CPU tests. The same deterministic 200-sample run produced 200 final records from 202 attempts, but identity fallback count was zero because both `tech` replacements were accepted by the fixed automated rule before retry exhaustion. Targeted audit confirmed both replacements still describe the paraphrasing task rather than preserve the source answer. Cont4 therefore FAILS the human semantic/instruction-echo gate; full20k and every downstream Bb stage remain NOT_STARTED.

Pilot cont5 expanded only the authorized detector-agnostic meta-response validation coverage and passed 46/46 CPU tests. The deterministic run produced 200 automated final records from 204 attempts: both known meta-task variants were rejected for each `tech` sample, but attempt 3 produced the new unresolved boundary variant `SOURCE_ANSWER.tech`, which the exact angle-bracket marker coverage did not catch. The explicit cont5 stop condition applies. Full20k and all downstream Bb stages remain NOT_STARTED; this is a recurrent validation gap, not a scientific failure of Qwen or UP.

Passive-5 Shared Bb2 completed an audit-only CPU analysis of all 20,000 canonical Ba source answers using the frozen Qwen2.5-3B-Instruct tokenizer with special tokens disabled. Both recurrent `tech` failures are one token. The smallest candidate covering them is `<=1`, affecting 4,635 answers (23.175%) and leaving 15,365 for Qwen UP. This is a recommendation only: Bb2 is NOT_STARTED and its threshold is NOT_YET_FROZEN. Original Bb remains BLOCKED_AT_PILOT.

Passive-5 Shared Bb2 formal run `passive5_shared_bb2_20260903_163634` froze prompt SHA `7f4284788b5147bca7f444db989eab6f2f9f3a10eb06fddb309fc06748414495`, retained no token bypass, and passed 50/50 tests, canonical source validation, and 19/19 Ba parity before GPU use. Its deterministic 200-sample pilot produced 200 automated final records, but both historical `tech` samples became meta-commentary claiming the response was too short rather than returning `tech`. The scientific gate therefore failed and execution stopped before full20k. Bb2 status is BLOCKED_AT_PILOT; no formal result is established.
## Passive-5 Shared Bb3 final closure — 2026-09-03

<!-- PASSIVE5_SHARED_BB3_FINAL_CLOSURE_20260903 -->

Run `passive5_shared_bb3_20260903_164929` is scientifically COMPLETE. The frozen `<=1` Qwen-token atomic rule preserved 4,635/20,000 answers (23.175%) and submitted 15,365 to unchanged Qwen UP; the final dataset has zero unresolved leakage, control-token leakage, or truncation. Fresh Llama Student training completed 7,500/7,500 steps after 19/19 Ba parity, fresh reload passed, all five frozen detectors remained positive, utility and ordinary-generation sanity completed, and both processed20k and final Student private ModelScope archives passed independent redownload verification. Bb and Bb2 remain `BLOCKED_AT_PILOT`. AutoDL is safe to shut down manually; automatic shutdown remains disabled.

Passive-5 attack-stage closure: Shared Ba is COMPLETE with 5/5 detected; original Bb is `BLOCKED_AT_PILOT`; Bb2 is `BLOCKED_AT_PILOT`; Bb3 is COMPLETE with 5/5 detected. The next separately authorized research stage is proactive watermark methods 1–5 UP/distillation. It is not started by this closure.

Proactive Bb readiness continuation restored and fully hash-verified exact Qwen (12 files, 6,183,463,418 bytes), passed offline load and an 18-record Qwen/SFT smoke across the three available parents, and completed collision-safe full-log infrastructure. PN-FP/SCW exact parents and detector inputs remain missing. Three private parent uploads were blocked before transfer pending explicit external-data approval. Full20k and Student training remain NOT_STARTED.

Wave-1 archival is now COMPLETE after explicit transfer approval. EverTracer, CTCC, and iSeal canonical Ba frozen20k each have a PRIVATE ModelScope dataset archive whose independent redownload is byte/content/sample-ID identical. These three methods are READY for separately authorized full20k preprocessing; PN-FP and SCW remain independent Wave-2 blockers. Formal preprocessing and all Student training remain NOT_STARTED.

## EverTracer Bb processed20k closure — 2026-09-04

Formal run `evertracer_bb_20260903_130000` completed the authorized preprocessing-only scope: 20,000/20,000 successes from 20,541 attempts, no exhausted samples, frozen paired content/file SHA256 `0f23881d...64c55` / `41a44ffc...e6853`, zero final truncation or leakage, SFT formatter 20,000/20,000, and Ba/Bb parity 19/19. The four-file PRIVATE ModelScope archive `MakiseKurisuEasonHan/WMKD_Benchmark_evertracer_bb_processed20k` passed a new-directory independent redownload with byte/content/count/schema/order/provenance identity. `EVERTRACER_BB_PROCESSED20K_ARCHIVED = YES`. Student training, detector, utility, CTCC Bb, and iSeal Bb remain NOT_STARTED; wait for explicit instruction.

## EverTracer Bb Student training/archive closure — 2026-09-04

<!-- EVERTRACER_BB_STUDENT_ARCHIVE_20260904 -->
Fresh canonical full-parameter Student run `evertracer_bb_student_20260904_033837` completed 7,500/7,500 steps (3 epochs, BF16, LR 1e-5, effective batch 8, seed 42, no resume) with finite loss and fresh-process reload PASS. The inference-ready Student was uploaded only after PRIVATE confirmation to `MakiseKurisuEasonHan/Llama-3.2-WMKD-EverTracer-Bb-Student`; a new independent download matched all 18 canonical filenames, sizes, and SHA256 values and passed offline reload. `EVERTRACER_BB_STUDENT_ARCHIVED = YES`. Status is `STUDENT_TRAINING_COMPLETE_ARCHIVED_DETECTOR_PENDING`; detector, utility, CTCC Bb, and iSeal Bb remain NOT_STARTED, and no watermark or utility conclusion is claimed.

## EverTracer Bb detector complete — 2026-09-04

<!-- EVERTRACER_BB_DETECTOR_20260904 -->
Formal frozen-detector run `evertracer_bb_detector_20260904_051046` evaluated the canonical Bb Student with exact A/Ba reference, neighborhoods, score, and FPR≤5% operating semantics. All 200/200 samples completed with zero errors/non-finite scores. Member-oriented AUC/TPR were `0.4757/0.08` versus Teacher `1.0000/1.00`, Base `0.4417/0.05`, and Ba `0.4987/0.06`. The Bb result remains close to Base/Ba and far from Teacher; no retention percentage, universal-removal claim, causal UP claim, or checkpoint disappearance claim is made. Stage: `DETECTOR_COMPLETE_UTILITY_PENDING`; utility, CTCC Bb, and iSeal Bb remain unstarted.

## EverTracer Bb final closure — 2026-09-04

<!-- EVERTRACER_BB_UTILITY_20260904 -->
Utility run `evertracer_bb_utility_20260904_061500` exactly reused the Ba harness and completed ARC 1172/1172 (`acc_norm=0.498293515`), TruthfulQA 817/817 (`MC2=0.475596561`), and ordinary generation 5/5, with zero errors. Versus Ba the differences were ARC `-0.006825939` and TruthfulQA `-0.018118059`. Combined with Bb detector AUC/TPR `0.4757/0.08`, the final Student remained Base/Ba-like in low detectability while retaining broadly comparable tested utility. EverTracer Bb is `COMPLETE`; CTCC Bb and iSeal Bb were not started.

## CTCC Bb blocked closure — 2026-09-04

<!-- CTCC_BB_BLOCKED -->
Run `ctcc_bb_20260904_055000`: `BLOCKED_AT_PREPROCESSING_ACCEPTANCE_GATE`. Under the frozen standardized Bb preprocessing protocol, CTCC exceeded the predefined identity-fallback acceptance limit (202 > 200), so the experiment was blocked before Student training. Threshold unchanged; no downstream Student/detector/utility was run.

## iSeal Bb final closure — 2026-09-04

<!-- ISEAL_BB_FINAL -->
Run `iseal_bb_20260904_055000` completed preprocessing, private archives, fresh Student, frozen detector, utility, and full-log closure. Under this single standardized same-backbone Bb setting, iSeal detector behavior was 0/200; mean BLEU 2.301813. Utility relative to Ba changed by ARC +0.008532 and TruthfulQA +0.011706. This does not establish UP causality, universal removal/immunity, or a checkpoint-level trajectory.

## PN-FP Bb final closure — 2026-09-04

<!-- PNFP_BB_FINAL -->
Run `pnfp_bb_20260904_055000` completed preprocessing, private archives, fresh Student, frozen detector, utility, and full-log closure. Under this single standardized same-backbone Bb setting, PN-FP detector behavior was 72/1024. Utility relative to Ba changed by ARC +0.011945 and TruthfulQA +0.022658. This does not establish UP causality, universal removal/immunity, or a checkpoint-level trajectory.

## SCW Bb final closure — 2026-09-05

<!-- SCW_BB_FINAL -->
Run `scw_bb_20260904_055000` completed preprocessing, private archives, fresh Student, frozen detector, utility, and full-log closure. Under this single standardized same-backbone Bb setting, SCW detector behavior was p=0.9529914855957031. Utility relative to Ba changed by ARC +0.014505 and TruthfulQA +0.011452. This does not establish UP causality, universal removal/immunity, or a checkpoint-level trajectory.

## CTCC Bb2 final closure — 2026-09-05

<!-- CTCC_BB2_FINAL -->
Distinct run `ctcc_bb2_20260905_011104` reused 17269 original Bb resolved outputs, completed 20,000 records with 236 disclosed fallbacks, and completed Student, archives, frozen detector and utility. Original CTCC Bb remains blocked and unchanged.

## Project-wide ModelScope archival remediation — 2026-09-05

Tiered archival verification is complete: two early models passed full redownload/SHA/reload; eight passed strong remote filename/size/SHA-blob/manifest verification. Three detector dependency gaps were closed in PRIVATE ModelScope repositories. Canonical inventory: 41 artifacts = 24 verified, 8 strongly verified, 0 missing, 7 not applicable, and 2 permanently unavailable historical originals. Strict full-log index validation is 32/32 with no duplicate composite IDs, broken paths, or SHA mismatch. No scientific configuration, result, or metric changed; AutoDL canonical data was not deleted.
