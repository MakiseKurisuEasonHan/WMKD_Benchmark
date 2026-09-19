当前最高状态（2026-09-19 PN-FP7B Logit-only恢复）：6004已启动，仅恢复Logit。Teacher/Direct/Paraphrase全部SHA核验通过，既有结果804/53/71不重跑。实测BF16 lm_head被Transformers4.44.2显式提升为FP32输出；按原Bc监督位置后cast BF16修复序列化，两样本23监督位置dtype/argmax/softmax/KL/重载/consumer梯度全部PASS，数值差异0。正式31.45GiB全词表缓存已启动，接续独立cleanStudent7500steps及Logit评估；完成同步/Git后关机，普通工程错误不自动当科学失败关机。入口results/pnfp/scale_7b/logit_recovery_6004/。

当前状态（PN-FP7B 6004蒸馏）：FAILED；终态证据已本地SHA核验，详见docs/reproduction_reports/pnfp_7b_distillation_6004_final.md。按本轮授权准备安全关机；不释放实例、不删除正式模型。

当前最高执行状态（2026-09-19 PN-FP7B 6004）：新实例591GiB数据盘、约539GiB可用，Teacher/Base/fingerprints/prompt SHA通过；Direct canonical数据生成已启动。授权独立fresh Direct→Paraphrase→Logit，20k/7500updates不变；精确监督token预算后生成BF16 full-vocab shards，禁止top-k。全部完成或不可恢复阻塞后，本地同步SHA核验/Git提交，再安全关闭6004、不释放。入口results/pnfp/scale_7b/distillation_6004/。

当前最高状态（2026-09-19 PN-FP 7B蒸馏）：用户正式接受Teacher804/1024，授权独立fresh7B Direct→Paraphrase→Logit串行；原extension终态保留为历史。本轮磁盘门槛预检BLOCKED：实测剩余18.186GiB，三份Student仅权重需37.661GiB；未启动数据生成/训练/logits，未删除正式模型。指定原prompt SHA已精确匹配。每阶段新增峰值不得超过当前剩余85%，Bc禁止自行full-vocab→top-k。入口results/pnfp/scale_7b/distillation/preflight.json；报告docs/reproduction_reports/pnfp_7b_distillation_preflight_20260919.md。

当前终态（2026-09-19 WA=.50 extension）：22累计有效更新（12重放+10新增）后平台期早停；最佳第19有效更新，独立fresh804/1024=78.5156%，ARC+5.4608pp、MC2-1.55495pp；未达到80%preferred门槛，保留当前最优候选，不启动蒸馏。模型与结果数据盘保留，81项目文件关机前双端SHA核验。官方shutdown脚本直接exec遇ENOEXEC后用bash解释执行，远端断开且两次SSH不可达；未释放实例。Git本地已提交，认证缺失push pending。详见results/pnfp/scale_7b/wa050_extension/shutdown_verification.json。

当前状态（2026-09-19）：WA=.50 extension EXTENSION_COMPLETE_NOT_PREFERRED；fresh-reload 804/1024，best有效更新19；preferred候选=False。训练停止，未启动蒸馏，授权证据闭环后自动关机。

当前状态（2026-09-09 Active Cross-Lineage Ba 最终闭环）：五个fresh Qwen Student全部7500steps、final save/fresh reload与utility完成。PNFP84/1024（Base43）；CTCC trigger0/95；SCW p0.9158855080604553未检出；EverTracer canonical N/A、exploratory AUC0.523；iSeal Level3 N/A。CPU证据/报告/索引闭环，等待用户独立preferred模型归档选择；禁止新实验、自动上传/删除或关机。shutdown_provenance=UNVERIFIED。入口 results/active_cross_lineage_ba/pipeline_state.json；总报告 docs/reproduction_reports/active_cross_lineage_ba_final_20260909.md。

当前最高状态（2026-09-07 EaaW canonical 3B A2）：用户已批准仅EaaW A2；本轮CPU科学审计后发现RED，BLOCKED_SCIENTIFIC_MASK_TOKEN_MAPPING。canonical八文件SHA验证PASS；Llama-3.2 unk_token_id=None，尚未批准替代mask。预检/训练/detector/utility/上传均NOT_RUN，未创建模型。等待用户决定exact masking baseline；不得自动继续。旧EaaW native A仍成功、作为NATIVE_REPRODUCTION_EVIDENCE，CANONICAL_BENCHMARK_ELIGIBLE=NO；UTF A4保留闭环状态。报告 docs/reproduction_reports/eaaw_a2_final_report_20260907.md。禁止其他方法、Ba/Bb、orchestrator/guardian、auto-next/shutdown。下方旧执行授权仅供历史参考。

当前状态（2026-09-07 UTF A4 已结束）：STOPPED_AFTER_A4；仅epochs30→3，正式96 exposures / 6 optimizer calls / 4 nonzero-LR updates。Teacher正例0/1，Case C INSUFFICIENT_FINGERPRINT_LEARNING；COMPLETED_NOT_PREFERRED，preferred=NO，benchmark eligible=NO。负例、Base detector、utility均NOT_RUN，global collapse未评估。模型本地保留、不上传不删除。禁止任何继续执行、A5、其他方法、auto-next及auto-shutdown；等待用户新的科学决定。完整报告：docs/reproduction_reports/utf_a4_final_report_20260907.md。下方旧授权仅为历史记录。

最新永久规则（2026-09-07）：每个正式实验最多上传一个最终preferred模型，preferred=false禁止上传；UTF A2 COMPLETED_NOT_PREFERRED，仅证据/Git闭环后STOP。远端已提交对象和本地模型保留待明确删除批准。详见 docs/ARTIFACT_ARCHIVE_POLICY.md；本段覆盖下方历史归档授权。

<!-- UTF_A2_CURRENT_AUTHORITY_20260907 -->
当前最高优先级授权（2026-09-07，UTF A2 新 prompt）：仅执行 Method 13 UTF Experiment A2；STRICT SERIAL INTERACTIVE MODE。Methods 11–15 canonical benchmark 永久统一为 meta-llama/Llama-3.2-3B-Instruct，revision 0cb88a4f764b7a12671c53f0838cd831a0843b95。旧 UTF 7B A 保留 historical / superseded protocol，OLD_UTF_A_CANONICAL_BENCHMARK_ELIGIBLE=NO，不标记 FAILED，不覆盖历史结果。
禁止 orchestrator、guardian/watchdog、自动 continuation、auto-next 和 auto-shutdown。仅允许 UTF 专用实现及单项任务；不得运行 11/12/14/15、Ba/Bb 或其他 watermark。旧远端 supervisor 2051 和本地 sync helper 32236 已停止，模型身份检查时未发现相关旧进程。
当前 UTF A2 已完成科学与轻量证据闭环，模型归档按新规则停止且未验收：30 epochs / 960 updates，PREFERRED_TEACHER=NO；Teacher fingerprint 1/1、非触发负控500/500，Base 0/1、0/500；ARC delta=-0.0708191126，MC2 delta=-0.0014838436。状态 WAITING_FOR_USER_SCIENTIFIC_DECISION；下一科学配置须用户批准。30/3 paper/code discrepancy及选择依据保留。完整结果见 docs/reproduction_reports/utf_a2_final_report_20260907.md。
详见 docs/reproduction_reports/utf_a2_initial_checkpoint_20260907.md 与 results/methods_11_15_pipeline_state.json。以下旧授权与阶段文字仅供历史参考；如冲突，以本段及最新用户决定为准。
<!-- UTF_A2_CURRENT_AUTHORITY_END -->

# Experiment Log

当前授权更新（2026-09-05）：用户已正式批准五方法串行 Experiment A 自动复现、最小工程修复、逐方法归档/Git闭环及全部terminal后的自动关机。前次等待prompt/STOP仅属于已结束的迁移任务。详见 [docs/METHODS_11_15_AUTOMATION.md](docs/METHODS_11_15_AUTOMATION.md) 与 results/methods_11_15_pipeline_state.json；旧科学设计禁改及KEEP/UNCERTAIN保留规则继续有效。


## 当前阶段 — 2026-09-05 方法 11–15 前规则与状态迁移

以 [docs/CURRENT_STATE.md](docs/CURRENT_STATE.md) 为当前状态入口。第一批十方法 CLOSED：30 comparison slots；32 canonical full-log objects。项目归档已闭环（24 verified / 8 strong-remote / 0 missing / 7 N/A / 2 permanent historical losses）。CTCC 比较使用 Bb2，原 Bb BLOCKED 历史不变。

新增顺序：11 EaaW → 12 Instructional Fingerprinting → 13 UTF → 14 Double-I Watermark → 15 CodeGenGuard。下一目标 METHOD_11_EAAW_EXPERIMENT_A，NOT_STARTED；须等待独立正式 prompt。本次只做状态/规则、精确归档权重清理与 Git 闭环。

清理记录：results/pre_methods_11_15_cleanup.json；验证：results/pre_methods_11_15_validation.json。以下旧快照/待办按历史保留，不应恢复执行。
维护执行完成：26 个已验证归档权重文件删除，释放约 60.6 GiB，剩余约 167.3 GiB；30 个 UNCERTAIN 权重文件保留。修复 Git 换行造成的远端 16 个 full-log SHA 不符，原索引和科学内容未变。完整报告：docs/reproduction_reports/pre_methods_11_15_durable_state_report.md。EaaW NOT_STARTED，STOP 等待独立正式 prompt。



## 2026-09-03 — Rule audit before passive Bb

Local-only audit confirmed ten current methods, completed A/A2/A6 and Ba status, and 21 objects in `results/experiment_full_logs_index.json`. The user froze Bb as answer-only UP followed by distillation and selected passive methods 6–10 (LLMPrint, REEF, HuRef, AWM, ZeroPrint) as the first cohort. No Bb run ID exists; no AutoDL, GPU, download, paraphrase, training, evaluation, archive, or cleanup action was performed.

## 2026-09-03 — Passive-5 Shared Bb local preparation

Prepared the local fail-closed pipeline for one Ba frozen20k → one Qwen-paraphrased20k → one fresh canonical Student → five frozen detector evaluations. Qwen revision remains `REQUIRED_TBD`; the planning full log is not added to the global formal-object index. Status is `PREPARED_NOT_STARTED`; GPU and formal Bb were not started.

## 2026-09-03 — Canonical Passive-5 Shared Ba frozen20k private archive

On no-GPU host `autodl-container-9235478639-4a175847`, the original frozen JSONL passed schema, uniqueness, ordering, 20,000-count, privacy and three-identity gates. Four minimal files were uploaded to PRIVATE ModelScope dataset `MakiseKurisuEasonHan/WMKD_Benchmark_passive5_shared_ba_frozen20k`. The first post-upload revision query hit a non-scientific SDK endpoint 404 after 4/4 commits; a no-reupload continuation independently downloaded all files and reproduced every canonical identity plus byte equality. The source was preserved. No Bb/GPU/Qwen/training action occurred.

## Four ownership-method bounded smokes — 2026-09-01

After safely pausing A2 at 97/200, serial foreground smokes completed for REEF (6.30335 s; 6,437,682,176-byte peak VRAM), AWM (5.80222 s; 6,484,990,464 bytes), HuRef (5.51993 s; 6,988,555,264 bytes), and ZeroPrint (6.80394 s; 6,438,586,880 bytes). Every result records `model_modified=false`, canonical revision `0cb88a4f...`, and `smoke_only=true`; all JSON artifacts passed parsing and were copied under method-specific `results/*/smoke/`. Final AutoDL state was GPU idle, 377 GiB disk available, LLMPrint still paused, no formal A/Ba started, and no shutdown. Integrated formal readiness remains false pending the blockers in `results/ownership_methods_smoke_summary.json`.

This is the concise index of formal WMKD_Benchmark experiments. Full scientific history is kept in each dedicated experiment log.

| Experiment | Status | Main run | Concise result | Dedicated log | Report | Blocker |
|---|---|---|---|---|---|---|
| SCW Experiment A | NOT RUN / blocked on runtime gate | None | Python 3.11/3.12 both abort after 4/4 and `train_end`; exact 160,000-record post-interleave materialized-stream adaptation is locally designed/tested but not run on real data. No scientific result or Teacher exists. | `docs/experiment_logs/scw_experiment_a_log.md` | `docs/reproduction_reports/scw_experiment_a_report_template.md` | Future authorized materialization/audit and one local-materialized 4-step clean-exit gate |
| iSeal Experiment A | BLOCKED BEFORE FORMAL RUN — immutable history | Trainability audit `iseal_trainability_20260830_045431` | Official zero-init adapter delta/A/B had zero gradient and zero update across two steps; full tied embedding/lm_head updated by delta norm 6.019554. No formal A training/evaluation occurred. | `docs/experiment_logs/iseal_experiment_a_log.md` | `docs/reproduction_reports/iseal_experiment_a_blocked_report.md` | Historical blocker was resolved only through explicitly authorized scientific modification in A2; iSeal later closed through A6/Ba |
| iSeal Experiment A2 | COMPLETED — not preferred | `iseal_a2_20260830_054641` | Repaired initialization plus official trainable tied head: registered 10/10, held-out 0/100, utility/ordinary degradation; preferred teacher NO. | A lineage log | `docs/reproduction_reports/iseal_experiment_a2_report.md` | None |
| iSeal Experiment A3 | COMPLETED — not preferred | formal A3 run | Frozen tied embedding/head, adapter-only 10 fingerprints: registered mean 13.147504 and 0/10; utility healthy; preferred teacher NO. | A lineage log | `docs/reproduction_reports/iseal_experiment_a3_report.md` | None |
| iSeal Experiment A4 | COMPLETED — not preferred | `iseal_a4_20260830_061934` | Fixed 100 fingerprints, inner_dim 16: registered 15/100, held-out 0/100, utility/reload healthy; preferred teacher NO. | A lineage log | `docs/reproduction_reports/iseal_experiment_a4_report.md` | None |
| iSeal Experiment A5 | COMPLETED — not preferred | `iseal_a5_20260830_063925` | Sole A4 change inner_dim 16→128: registered 66/100 (mean 56.048270), held-out 0/100, ARC 0.401877, TruthfulQA 0.518636, ordinary 10/10, reload PASS. | A lineage log | `docs/reproduction_reports/iseal_experiment_a5_report.md` | Historical Teacher decision was resolved by authorized A6 |
| iSeal Experiment A6 | COMPLETED — PREFERRED TEACHER | `iseal_a6_20260830_132300` | Sole A5 change 100→200 fingerprints: full registered 179/200; historical A5-100 86/100; held-out 0/100; ARC 0.389932; TruthfulQA 0.477828; ordinary 10/10; reload PASS. | A lineage log | `docs/reproduction_reports/iseal_experiment_a6_report.md` | None; Ba subsequently completed |
| iSeal Experiment Ba | FULLY CLOSED | generation `iseal_ba_generation_20260830_134058`; Student `iseal_ba_20260830_165442` | Exactly-20k SHA `d51c22b9...5aacf`; A6 179/200 → Student 0/200; ARC 0.481229; TruthfulQA 0.449818; ordinary 10/10; reload PASS; private archives uploaded. | A/Ba lineage records | `docs/reproduction_reports/iseal_experiment_ba_report.md` | None; Bb deferred, destination SHA pending |
| CTCC Experiment A | CLOSED | `ctcc_a_20260829_190251` | Teacher/Base trigger 95/95 vs 0/95; Teacher negatives 0/205; ARC 0.395051 vs Base 0.446246; TruthfulQA 0.476817 vs 0.505687; sanity/reload passed; preferred teacher YES. | `docs/experiment_logs/ctcc_experiment_a_log.md` | `docs/reproduction_reports/ctcc_experiment_a_report.md` | None; Ba separately completed |
| CTCC Experiment Ba | FULLY CLOSED | generation parent `ctcc_ba_generation_20260829_195943` + `cont1`; Student `ctcc_ba_20260830_025244`; evaluation parent `ctcc_ba_eval_20260830_033556` + `cont1` | Exactly-20k SHA `621c9aed...12484`; Student Trigger 0/95, negatives 0/205; ARC 0.483788; TruthfulQA 0.450614; sanity/reload passed; private archives uploaded. | `docs/experiment_logs/ctcc_experiment_ba_log.md` | `docs/reproduction_reports/ctcc_experiment_ba_report.md` | None; Bb deferred, destination SHA pending |
| PN-FP Experiment A | CLOSED | `pnfp_exp_a_20260827_232033` | 30/30 epochs; eval_loss 0.0119302; watermarked 1019/1024 (99.5117%); base 1/1024 (0.0977%); reload passed; ordinary-generation utility severely degraded. | `docs/experiment_logs/pnfp_experiment_a_log.md` | `docs/reproduction_reports/pnfp_experiment_a_report.md` | None |
| PN-FP Experiment A2 | CLOSED — scientifically complete through immutable continuation | Training: `pnfp_exp_a2_20260828_025240`; evaluation: `pnfp_exp_a2_eval_20260828_105530` | 956/1024 (93.359375%); ARC and TruthfulQA utility gates passed; preferred PN-FP teacher. | `docs/experiment_logs/pnfp_experiment_a2_log.md` | `docs/reproduction_reports/pnfp_experiment_a2_report.md` | None |
| PN-FP Experiment Ba | CLOSED | `pnfp_exp_ba_20260828_111148` | A2 956/1024 → Ba 98/1024; 83.7890625-point drop; 10.251046% retention; utility and reload passed. | `docs/experiment_logs/pnfp_experiment_ba_log.md` | `docs/reproduction_reports/pnfp_experiment_ba_report.md` | None |
| PN-FP Experiment Bb | NOT RUN / deferred | Not created | UP/Dipper design only; no result. | `docs/experiment_logs/pnfp_experiment_bb_log.md` | Template only | Explicit future approval |
| EverTracer Experiment A | COMPLETED through immutable continuation | Root: `evertracer_a_20260828_223155`; cont1: `evertracer_a_20260828_223155_cont1`; cont2: `evertracer_a_20260828_223155_cont2` | Preferred teacher; corrected member-oriented AUC/TPR 1.0/1.0; utility, generation sanity, and reload passed. | `docs/experiment_logs/evertracer_experiment_a_log.md` | AutoDL cont2 report | None |
| EverTracer Experiment Ba | COMPLETED | `evertracer_ba_20260829_124055` | Teacher 1.0/1.0 → student 0.4987/0.06; Base 0.4417/0.05. ARC 0.505119; TruthfulQA MC2 0.493715; generation/reload passed. | AutoDL run report | AutoDL run report | None |

## EverTracer ModelScope archives

- A preferred teacher: private repo `MakiseKurisuEasonHan/WMKD-EverTracer-A-Teacher`; 9 model files, 6,442,815,628 bytes.
- Ba student: private repo `MakiseKurisuEasonHan/WMKD-EverTracer-Ba-Student`; 9 model files, 6,442,815,786 bytes.
- Both states are `uploaded_to_modelscope_awaiting_destination_hash_verification`. No full model download was performed for destination SHA256 verification.

## EverTracer A → Ba closure timeline

1. Fixed official EverTracer commit `70b402f7b7456c6d94e1fae2de554d77dd6cd921`, canonical 3B revision, XSum-only split, target/reference training, and 128-token verification protocol.
2. Root run `evertracer_a_20260828_223155` completed target/reference training and merging, then immutably failed at perturbation due to T5 online/cache resolution.
3. Continuation 1 `evertracer_a_20260828_223155_cont1` generated canonical neighborhoods and verification inference, then immutably failed at utility due to ARC offline-cache resolution.
4. Detector audit preserved `C=suspect PV-reference PV`, corrected member/non-member orientation, and retained the old teacher AUC 0.0 as implementation-error provenance.
5. Continuation 2 `evertracer_a_20260828_223155_cont2` reused target/reference/neighborhoods/scores, corrected aggregation without inference, resolved utility offline, and completed A with teacher AUC/TPR 1.0/1.0.
6. Ba generated EverTracer-specific answers. Raw prefixes 24k/26k/28k/30k were insufficient; 32,003 raw records yielded 20,173 unique valid records and exactly 20,000 were frozen.
7. Ba student completed 7,500 steps and all verification, utility, generation, reload, reporting, and notification stages.
8. Teacher and student uploads plus remote metadata verification completed in their fixed private ModelScope repositories; destination-side full SHA remains deferred.
9. Final local/GitHub archive completed before protected AutoDL cleanup. Cleanup removed only explicit smoke outputs and Ba `checkpoint-7500`, reclaimed 77.958 GiB, and preserved all protected artifacts. EverTracer A and Ba are FULLY CLOSED; Bb is NOT RUN/deferred.


## A2 immutable evaluation continuation `pnfp_exp_a2_eval_20260828_105530`

Parent training run `pnfp_exp_a2_20260828_025240` remains operationally FAILED after external dataset acquisition failure. The validated checkpoint and reusable evaluations plus this continuation establish the final result. Watermark gate: **passed**; utility gate: **passed**; judgement: **A2 is the preferred PN-FP teacher for future Ba**.


## A2-teacher formal Ba run `pnfp_exp_ba_20260828_111148`

Teacher A2 provenance: `pnfp_exp_a2_20260828_025240` + `pnfp_exp_a2_eval_20260828_105530`. Base/A2/Ba detection: 1/1024 (0.09765625%) / 956/1024 (93.359375%) / 98/1024 (9.5703125%); teacher→Ba drop 83.7890625 points; retention 10.251046%. ARC Base/A2/Ba: 0.448805461 / 0.443686007 / 0.478668942. TruthfulQA MC2 Base/A2/Ba: 0.505450760 / 0.467427921 / 0.463479842. Utility and reload gates passed. Judgement: **strong watermark degradation with partial retention under the tested setting**. The old A1-based run remains immutable FAILED.

## iSeal explicitly authorized final cleanup

The first conservative cleanup attempt remains recorded as rejected before execution. After separate explicit user authorization, exactly five audited paths were deleted: A2, A3, A4, and A5 non-preferred `teacher_merged` artifacts plus Ba `checkpoint-7500`. No candidate was skipped. Logical deletion total was 47,429,470,039 bytes; filesystem used space decreased by 47,429,681,152 bytes. A6 preferred Teacher, Ba `final_model`, canonical base, frozen20k, ModelScope manifests, raw generation, shared infrastructure/cache, and all other-watermark artifacts were preserved. iSeal remains FULLY CLOSED; Bb/A7 and the fifth watermark were not started.
## SCW AutoDL deployment, runtime preflight, and non-scientific speed test — 2026-08-31

- Deployed local HEAD `de4880db573a2c43aa27efe2f18a61f815166a43` to `/root/autodl-tmp/WMKD_Benchmark`; preserved the prior dirty checkout in the data-disk deployment backup. SCW config hashes matched local preparation.
- Verified official source commit `15bc1929569357130f2dbc0b09f91bbf4f4bd947`, Responsible AI SOURCE CODE License 1.1, canonical model revision `0cb88a4f764b7a12671c53f0838cd831a0843b95`, and four immutable dataset identities. Runtime preflight: READY; unique total/trainable 3,212,749,824/3,212,749,824, all BF16.
- Final representative run `scw_speed_20260831_03` completed 4/4 optimizer steps with 1 warm-up and 3 timed. Timed compute median was 4.693845 s; representative start-to-start cadence including steady data wait was 9.617187 s; packed throughput estimate was 3,407.23 tokens/s; projected 2,500-step training time was 24,042.97 s (6.68 h), excluding approximately 463.96 s one-time setup/terminal overhead.
- Peak allocated/reserved VRAM was 52,462,513,152/62,396,563,456 bytes; observed nvidia-smi peak was 60,168 MiB; peak process CPU RSS was 5,963,767,808 bytes. No OOM, NaN, Inf, offload, or training traceback occurred.
- After `train_end` and speed-only save suppression, Python hit a PyArrow/GIL finalization SIGABRT. Original FAILED status and recovered telemetry summary were both preserved. Bounded result: `RUNTIME_ADAPTATION_NEEDED`. Formal A, Base/Teacher evaluation, Ba, ModelScope, and cleanup were not started.

## SCW terminal-cleanup investigation — 2026-08-31

- Preserved immutable FAILED runs `scw_speed_terminalfix_20260831_01`, `_02`, and `_03`; every run completed exactly 4 optimizer steps, 64 microbatches, and `train_end`, with no OOM, NaN/Inf, CUDA failure, or training traceback.
- Restored official dependency pins from `pyarrow 25.0.1`/`aiohttp 3.14.3` to `pyarrow 21.0.0`/`aiohttp 3.12.15` plus the official aiohttp dependency stack. Scientific configuration hashes remained `37d5364f...` and `3c57c1be...`; official source stayed clean and unmodified.
- Python-level streaming source release, GC, fsspec loop/thread teardown/reset, and a late atexit GC all executed in `_03`; the child still died with SIGABRT 6 after atexit. Failed compatibility edits were reverted rather than committed.
- Terminal recommendation: `BLOCKED_RUNTIME_FINALIZATION`; **not** `READY_FOR_FORMAL_A`. Formal A and Ba were not started; GPU returned to 0 MiB/0% with no compute process.

## SCW materialized-stream local research — 2026-08-31

- Read pinned official dataset, preprocessing, shuffle, interleave, loss-label, Trainer, and stopping code. Streaming is a scale/runtime convenience but participates in realized order, so map-style re-interleave is not accepted as exact.
- Implemented a wrapper-only post-interleave tokenized materializer, immutable manifest, PyTorch-only sequential local loader, formal entry-point patch, and audit logic. The fixed training prefix is exactly 160,000 examples (40,000 microbatches); duplicates and stochastic observed proportions are preserved.
- Pure-CPU synthetic tests passed for seed determinism/sensitivity, order, labels/losses, proportions, duplicates, hashes, loader replay, count contract, and fail-closed exhaustion/corruption. No real dataset, model, GPU, AutoDL, La Trobe, Formal A, or Ba was used.
- Classification: conditional `RUNTIME_DATA_ACCESS_ADAPTATION`, not A2. Formal A remains blocked pending separately authorized real materialization/audit and a clean four-step local-materialized gate.

## SCW resumable shard recovery — 2026-08-31

- Gracefully stopped `scw_materialized_full_20260831_195500` at 0/160000 before gate/Formal A and preserved retry evidence as `BLOCKED_NONRESUMABLE_PARQUET_DOWNLOAD`.
- Verified HTTP Range resume from offset 1,048,576 and completed the exact LucieFr `RedPajama--fr--2017-51--033.parquet`: 824,184,452 bytes, SHA256 `a78e663cfddc361d3f54e634793b9cb3b0f028e10a8d40ad523324e6bd350228`, Parquet integrity PASS.
- Added generic on-demand resumable prefetch/cache serving. Targeted tests passed 8/8. A direct verified-local tiny check using official `tokenize_function` and `group_texts` produced 8 LucieFr watermark records at sequence length 512.
# 2026-08-31 — SCW finite-stream adaptation infrastructure

- Prior exact-online-stream materialization remained pre-scientific: records 0, gate not started, Formal A not started.
- Stopped further CDN/IP benchmarking and preserved all `.part`, verified Parquet cache, logs, provenance, and failed run directories.
- Added deterministic PCG64 schedule, per-source source-order official preprocessing pools, final schedule assembly, manifest limitation disclosure, fail-closed audit, frozen local loader, and detached build→audit→single gate→Formal A→evaluation→report→shutdown orchestration.
- Targeted Python 3.11 tests: 15 passed; `git diff --check`: PASS; canonical scientific YAML files unchanged.
# 2026-08-31 — SCW deterministic run post-mortem

- Run `scw_deterministic_full_20260831_214200` failed in `DETERMINISTIC_FINITE_STREAM_BUILD`, specifically before the first LucieFr record: `RuntimeError: no authoritative Parquet objects for LucieFr`.
- Persisted outputs: LucieFr pool 0/95,828; AlpacaGPT4 pool not created; OpenWebText pool not created; final stream not created. Audit, 4-step gate, Formal A, and Ba never started.
- The finalizer recorded `shutdown_requested=true` and `shutdown_command_issued=true`, then invoked the AutoDL shutdown wrapper. This caused the previous power-off.
- Automatic shutdown is now temporarily disabled; SUCCESS/FAILED/BLOCKED terminal paths require manual shutdown.
# 2026-08-31 — SCW A2 domestic finite-data preparation

- ModelScope research fixed A2 datasets once: Aya Collection French (Role0), `wyj123456/instruct` (Role1), and `mapjack/openwebtextSample` (Role2). All resolved through `cdn-lfs-cn-1.modelscope.cn` with Range support.
- Bounded local inputs: Aya French train shard 327,767,265 bytes/SHA256 `35c6904...60429`; instruction complete-line 64 MiB prefix 58,925 rows; OpenWebText Arrow shard 503,524,200 bytes/SHA256 `669ceafd...7d858`.
- Built frozen stream `scw_a2_frozen80k_20260831_230200`: exact role counts 47,773/16,291/15,936; stream SHA256 `4763b08342493bedacd1753e297e0e081568906c0bade310e2d79e1783cd35cd`.
- Audit PASS: 80,000 unique identities, schedule/hash/order/source/loss checks, exact one-pass 80k loader and exact two-pass 160k formal exposure replay. Formal A2 and Ba have not started at this preparation record.

## SCW A2 post-mortem — `scw_a2_full_20260831_214331`

- Formal training completed 2500/2500 with `train_end`; runtime 11570.9348 seconds and final aggregate train loss 5.289046603393555.
- The final Teacher was saved at `runs/scw/a2/scw_a2_20260831_214339/models/Llama-3.2-3B-Instruct_scw_a2_20260831_214339_French_WMKD_SCW_A`.
- Evaluation failed before the first Base generation output: the fixed French evaluation dataset was unavailable in offline mode (`OfflineModeIsEnabled`). Detector, utility, report, and scientific preference judgement were not run.
- The enabled terminal shutdown policy issued `/usr/bin/shutdown` after this evaluation failure. Automatic shutdown is now project-wide disabled; manual shutdown is required.

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

## 2026-09-01 — WMKD 5/7 closure integrity audit

Generated 10/10 canonical full experiment logs and the global index under `results/`. Persisted trajectory coverage: PN-FP Teacher/Student unavailable; EverTracer Teacher unavailable and Ba 7500 timing records; CTCC Teacher 286 trainer records and Ba 7500 timings; iSeal Teacher 1500 history records and Ba 7500 timings; SCW Teacher 250 trainer records and Ba 7500 timings. All detector/utility/archive source snapshots are retained. None of the five Ba Students has intermediate checkpoint-level detector evidence, so exact disappearance-step localization is unsupported. No experiment, generation, detector, utility, or upload was rerun.

### AutoDL bounded cleanup

After GitHub/source synchronization and small-evidence capture, deleted only two explicitly non-scientific speed-test namespaces and two incomplete `.part` files. Logical targets totaled 51,689,025,056 bytes; filesystem used space fell from 183,968,206,848 to 132,278,788,096 bytes (51,689,418,752 bytes reclaimed; 35% to 25% usage). All formal checkpoints/final models, SCW frozen20k, canonical Base, shared prompt/cache/utility resources, environments, manifests and ambiguous paths were retained. Automatic shutdown remained disabled and the instance remained running.

## 2026-09-01 — LLMPrint pre-formal preparation

LLMPrint preparation began under explicit authorization. The official source is pinned to `hifi-hyp/ACL-LLMPrint@3e577f98b2bb64780ec2995b074c5aeec9b017e1`; no explicit repository license was observed at audit time. Paper/source semantics, canonical-Llama compatibility, full construction parameters, 13-model validation-negative inventory, atomic run logging, and local static tests were recorded. Formal construction is 0/300, and no Ba or Student training exists. AutoDL execution evidence is not yet available because the post-restart SSH endpoint could not be reached; this is an infrastructure hold, not a scientific failure and not an A2 trigger.

### LLMPrint speed-test continuation `llmprint_speed_20260901_1329_cont2`

The final pre-formal scientific blocker was resolved before launch. The paper Primary detector is frozen to inclusive bits, sample standard deviation (`ddof=1`), and an unclipped `mu + 1.64 sigma` threshold; the pinned-release implementation is retained as a non-controlling supplementary detector. The final 13-slot validation-negative manifest preserves every official identity through a revision-pinned ModelScope transport mirror, with zero replacements and zero unresolved slots. Formal construction remains 0/300 at this record while remote runtime/readiness gates are checked; Ba, 20k generation, and Student training remain NOT STARTED.

AutoDL preflight passed: idle RTX PRO 6000, canonical Base 12/12 SHA256, and 300/300 fixed-tokenizer pairs from 773 candidates. Parent and cont1 terminated on engineering-only Python 3.12 dynamic-import and Transformers DynamicCache compatibility faults without producing a fingerprint. cont2 preserved `use_prefix_cache=true`, the fixed prompt/loss/seed/search settings, and all 1000 GCG steps while applying an immutable-cache batch compatibility layer. Pair 000 (`bike`, `rocket`) completed 1000/1000 in 212.42855 seconds; best loss 1.138671875, preference margin 1.1796875, reference bit 1, and peak allocated VRAM 7,048,545,280 bytes. Formal construction remains 0/300. Estimated 300-pair optimization time is 17 h 42 m, with 20–22 h operational reservation. Ba and Student training remain NOT STARTED.

### LLMPrint formal A construction `llmprint_a_20260901_061225`

All 14 readiness gates passed at Git commit `09d65c53075383f801cce054b8573f140ac52d82`. The canonical manifest matched, pair/source/config/panel provenance matched, the GPU was idle, the output namespace was new, atomic resume tests passed, and a non-scientific 4/4-iteration sanity completed under `CUBLAS_WORKSPACE_CONFIG=:4096:8` without a deterministic-runtime fatal error. Detached formal construction started at `2026-09-01T06:12:52.956184+00:00`; runner/scientific PIDs are 5683/5685. The first health check found status RUNNING, 0/300 atomic records, approximately 7.5 GiB process VRAM, active GPU work, growing log, inherited CUBLAS env in both processes, and no OOM, NaN, or Traceback. The PyTorch memory-efficient-attention nondeterminism warning is preserved without changing the frozen algorithm. Log: `/root/autodl-tmp/WMKD_Benchmark_data/logs/llmprint/llmprint_a_20260901_061225.log`; status: `/root/autodl-tmp/WMKD_Benchmark_data/runs/llmprint/a/llmprint_a_20260901_061225/status.json`. Ba, 20k generation, and Student training remain NOT STARTED.

At `2026-09-01T06:40:20.780274+00:00`, explicit user authorization replaced A with a bounded A2 redesign for runtime feasibility/project deadline. Only exact scientific PID 5685 received SIGTERM; runner 5683 then exited, GPU memory was released, and no residual child remained. A preserves 7/300 valid artifacts through `llmprint-pair-006`, but they are historical-only and cannot be reused for A2 or calibration. Final A classification: `TERMINATED_BY_USER_APPROVED_SCIENTIFIC_REDESIGN`, `scientific_result=NOT_ESTABLISHED`, not an infrastructure/OOM/method failure. A2 is 200 ordered fingerprints × 500 steps with all other settings and detector/panel rules unchanged. Ba remains NOT STARTED.

### LLMPrint formal A2 construction `llmprint_a2_20260901_064855`

Minimal readiness passed at immutable launch commit `ce8c03bd555c262e86c79b5249a23e7903a747da`. The LF-canonical A2 subset/config SHA256 values are `162e27bccf4be98a3e15596772490dac44503363ac5781ac5365fea2d08f4a10` and `4325b2a518aa5080dfb5cc070d57713bf6ee84efb9d72e8e4cbc89308920613a`. Detached A2 started at `2026-09-01T06:49:18.208351+00:00`; runner/scientific PIDs are 7155/7157. First snapshot was healthy at 0/200 with active GPU, CUBLAS env in both processes, no fatal/error patterns, and the known nondeterministic-attention warning preserved. Initial ETA is about 6 h 11 m based on prior formal runtime scaling; A2's own average awaits its first artifact. Ba remains NOT STARTED.

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

Pilot cont4 ran on an idle RTX PRO 6000 using unchanged Qwen, prompt/SHA, source/order, decoding, and seed policy. It completed 200 final records from 202 attempts in 63.6536 seconds (66.3435 output tokens/s; peak VRAM 7,226,526,720 bytes), with 2 first-attempt instruction-echo rejections, 21 natural exact copies, 0 identity fallbacks, 0 truncation, and 0 automated final leakage. Human audit found the same two `tech` second attempts were meta-task descriptions, so cont4 FAILS and stopped before full20k. No Student training, detector evaluation, utility run, or ModelScope archival started.

Pilot cont5 ran on an idle RTX PRO 6000 after 46/46 tests passed. It completed 200 automated final records from 204 attempts in 69.7023 seconds (60.7297 output tokens/s; peak VRAM 7,226,526,720 bytes), with 4 correctly rejected known meta-task attempts, 21 natural exact copies, 0 identity fallbacks, and 0 truncation/CUDA failures. Both `tech` attempt-3 candidates were `SOURCE_ANSWER.tech`; the validator recorded no rejection because this unbracketed boundary form is outside the fixed exact markers. Manual audit therefore fails cont5 and stops all subsequent stages.

The Passive-5 Shared Bb2 short-answer distribution audit ran CPU-only with CUDA disabled; no Qwen generation or model-weight load occurred. Canonical source validation passed at 20,000 records and all frozen dataset/file/sample-ID hashes matched. Frozen Qwen tokenizer non-special token counts were computed for every answer. Counts at `<=1/2/3/5` were 4,635/7,577/8,698/9,791; both recurrent `tech` failures were one token. The audit recommends but does not freeze `T=1`. Bb2 remains AUDIT_ONLY_NOT_STARTED.

Bb2 formal pilot `passive5_shared_bb2_20260903_163634` ran on an idle RTX PRO 6000 with the newly frozen semantic-preserving prompt and unchanged Qwen/decoding/source. Preflight passed 50/50 tests, source identities, and 19/19 parity. The pilot completed 200 records in 76.3491 seconds with 148 marked paraphrased, 52 Qwen identity outputs, 0 retries/fallbacks/truncations/CUDA failures, and peak VRAM 7,270,696,960 bytes. Human audit failed both `tech` samples: their output was transformation meta-commentary, not `tech`, despite zero automated leakage flags. Execution stopped before full20k and all downstream stages.
## Passive-5 Shared Bb3 `passive5_shared_bb3_20260903_164929`

<!-- PASSIVE5_SHARED_BB3_EXPERIMENT_20260903 -->

Bb3 pilot passed 200/200 with a 25-pair targeted human audit. Full20k completed in 7,484.502s: 4,635 atomic identities, 15,365 Qwen submissions, 13,061 Qwen paraphrases, 2,256 Qwen natural identities, 48 pipeline fallbacks, and 279 rejected attempts; final unresolved leakage/control-token leakage/truncation were 0/0/0. Paired dataset SHA is `549d38ca634c2c69a646e23d1bfc65ec019887e43070deec031f97459cc7be99`; frozen file SHA is `60bd4539b5d332b076a92072b86b51f8ddad3749a0a166f594233f5c1730dd88`.

After private dataset archive verification and 19/19 Ba parity, a fresh canonical Llama-3.2-3B-Instruct Student trained 7,500/7,500 steps in 2,022.706s with final loss 0.962497414; fresh reload found 0 non-finite parameters and returned `WMKD_RELOAD_PASS`. Frozen detector scores were LLMPrint 0.785, REEF 0.967286127, HuRef 99.998733521, AWM 0.999996107, and ZeroPrint rescaled 0.917022020; all remained positive. Bb3 Student utility was ARC-Challenge acc_norm 0.490614334 and TruthfulQA MC2 0.454416204; ordinary English and French sanity passed. The private final Student archive independently redownloaded and matched all 14 package files. Bb3 is COMPLETE; Bb and Bb2 remain `BLOCKED_AT_PILOT`.

Closure-only integrity audit at 2026-09-03T11:02Z performed no GPU scientific work and no upload. Live authenticated ModelScope reads confirmed all four canonical Passive-5 repositories exist, have the expected dataset/model type and file inventory, and are PRIVATE. The global full-log index contains 26 unique objects, including five Bb3 completed detector objects; no Bb or Bb2 object is mislabeled completed and all indexed paths exist. A canonical four-artifact inventory is stored at `results/passive5_modelscope_inventory.json`.

## 2026-09-03 — Durable repository-state audit before proactive Bb

Audited only the local WMKD_Benchmark repository and GitHub. The pre-edit baseline was local HEAD = fetched `origin/main` = `a633b232e1c09523e54b8a9537d84347d5e94d14`, ahead/behind `0/0`, clean. Corrected stale current-facing 21-object/Bb-not-started/pre-Bb-preparation claims while preserving dated historical records. Reasserted ten-method taxonomy, A/Ba closure, Passive Bb/Bb2 failure history, Passive Bb3 protocol/results/limitations, proactive lineage separation, four verified PRIVATE ModelScope artifacts, and 26/26 full JSON state.

No AutoDL/La Trobe connection, GPU task, download, generation, training, detector, utility, ModelScope write, cleanup, or proactive Bb execution occurred. Next allowed work is proactive 1–5 Bb protocol discussion and explicit freeze; execution remains prohibited without a new prompt.

Lightweight audit results: 288/288 JSON parsed; global index 26/26 unique with all paths and SHA256 values valid; ModelScope inventory 4/4 PRIVATE; Markdown local-reference sanity, Python compile, diff check, tracked-secret scan, and tracked-large-file scan passed. Pytest was unavailable and no dependency was installed. Unittest executed all importable lightweight tests (76 pass, 4 skip); seven test modules were unavailable because this Windows runtime lacks PyYAML/Torch/PyArrow or POSIX `resource`. Local classification found no suspicious category-D item and performed no deletion.

## 2026-09-03 — Proactive Bb 6000 readiness attempt

Froze the proactive 1–5 Bb protocol in durable docs. Initial SSH 6000 host audit found Ubuntu 22.04.5, idle RTX PRO 6000, 392 GiB free data disk, and a detached historical repository at `45d6f779` with bundle-backed origin. Subsequent SSH connections failed before safe Git bring-up and canonical artifact inventory could complete. No remote mutation, full20k preprocessing, training, detector, utility, download, archive write, cleanup, or GPU inference occurred. All five methods remain `NOT_READY`; see `results/proactive5_bb_readiness.json`.

Direct-endpoint continuation restored the same host at `connect.westd.seetacloud.com:48835`. Remote Git was moved non-destructively to clean canonical main `539b5a57`; old SCW code is protected by branch `historical/scw-deployment-45d6f77`. Actual inventory found three surviving, distinct, schema-compatible 20k parents: EverTracer `ca1aa9c...`, CTCC `621c9aed...`, iSeal `d51c22b9...`; PN-FP and SCW parents are absent. Qwen is absent. Added one shared infrastructure-only config/namespace parameterizer without changing frozen scientific logic. No formal preprocessing, training, detector, utility, download, archive, cleanup, or GPU inference occurred.

After one working-directory invocation correction and one CLI import compatibility fix, remote targeted tests passed 8/8 and static config preflight passed for the three surviving parents at HEAD `f99ca50`. Qwen-dependent branches were skipped. No formal or scientific output was produced.

Final-blocker continuation restored official frozen Qwen and matched all 12 recorded file hashes. Tiny non-formal runtime smoke passed 18/18 across EverTracer, CTCC, and iSeal, including atomic/non-atomic branches and canonical SFT adaptation. No full20k, training, formal detector, or utility ran. Private parent archive transfer was rejected before upload pending explicit external-data approval; PN-FP/SCW exact parents and detector inputs remain missing.

After explicit approval, archived the three Wave-1 canonical Ba frozen20k datasets to separate PRIVATE ModelScope repositories. All three fresh independent downloads matched source file/content/sample-ID SHA, count 20,000, and strict schema. Only frozen data and safe provenance were uploaded; iSeal secret/key material was excluded. Wave-1 readiness is READY for a later preprocessing prompt. No formal experiment stage ran.

## 2026-09-03/04 — EverTracer Experiment Bb preprocessing-only closure

Run `evertracer_bb_20260903_130000` used the frozen Qwen-token `<=1` atomic identity rule and unchanged Qwen UP prompt SHA `7f428478...414495`. It completed 20,000/20,000 successful records from 20,541 attempts in 5,208.235 seconds, with 541 retries, 78 bounded fallbacks, and no exhausted IDs. Final mode counts were 4,864 atomic identities, 12,099 Qwen paraphrases, 2,959 natural Qwen identities, and 78 fallbacks; truncation, prompt leakage, instruction echo, chat-control leakage, and generation failure were all zero.

The ordered paired20k content/file/sample-ID SHA256 values are `0f23881d...64c55`, `41a44ffc...e6853`, and `49d42164...6be73`. SFT adaptation produced exactly 20,000 records and 19/19 Ba/Bb parity passed. Strict credential scanning found zero hits; all five generic high-entropy candidates were hash-reviewed and inherited from the already archived Ba parent. After explicit approval, exactly four authorized files were uploaded to PRIVATE ModelScope dataset `MakiseKurisuEasonHan/WMKD_Benchmark_evertracer_bb_processed20k`; a new independent download matched physical/content/order hashes, count, schema, and manifest. No Student training, detector, utility, CTCC Bb, or iSeal Bb ran.

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

## Proactive Bb final integrity closure — 2026-09-05

Terminal objects: PN-FP Bb COMPLETE; EverTracer Bb COMPLETE; CTCC original Bb BLOCKED_AT_PREPROCESSING_ACCEPTANCE_GATE; CTCC Bb2 COMPLETE; iSeal Bb COMPLETE; SCW Bb COMPLETE. The strict audit covers 32 canonical full JSON objects. Ten stale preferred-Teacher/Ba-Student index SHAs were recalculated and repaired without changing scientific logs. Reports, archive metadata, status, safety checks, and three-end Git parity are recorded in `docs/reproduction_reports/proactive_bb_final_closure_integrity.md`. Historical failures and infrastructure continuations remain preserved.

## Project-wide ModelScope archival remediation — 2026-09-05

Tiered archival verification is complete: two early models passed full redownload/SHA/reload; eight passed strong remote filename/size/SHA-blob/manifest verification. Three detector dependency gaps were closed in PRIVATE ModelScope repositories. Canonical inventory: 41 artifacts = 24 verified, 8 strongly verified, 0 missing, 7 not applicable, and 2 permanently unavailable historical originals. Strict full-log index validation is 32/32 with no duplicate composite IDs, broken paths, or SHA mismatch. No scientific configuration, result, or metric changed; AutoDL canonical data was not deleted.

## 2026-09-06 Method 12 strict serial repair and closure

User changed policy to strict_serial_interactive, advance_on_engineering_block=false. Fixed missing protobuf with 4.25.8 in Method 12 runtime_overlay only; preserved failed TRAINING attempt 1, retried attempt 2 using existing source/model/data. Run instructional_fingerprinting_a_20260905_111830 completed 40 steps / 20 epochs, train_loss 2.2173110768198967. Fingerprint exact matches 10/10; Base and published-without-private-adapter 0/10; each group negative activations 0/150. SciQ zero-shot accuracy Base 0.937 vs published fingerprint model 0.937, delta 0; normalized accuracy 0.909 vs 0.911. Utility scope is the published model without private adapter and one native task, not the full paper suite. Fresh reload verified. Private ModelScope archive independently redownloaded and verified 60 files. ENGINEERING_STATUS=COMPLETE; FINGERPRINT_STATUS=CORE_REPRODUCTION_SUCCESSFUL; UTILITY_STATUS=COMPLETE; FINAL_SCIENTIFIC_STATUS=CORE_REPRODUCTION_SUCCESSFUL. Formal report/full log/global index committed and pushed in 18bebb0117c33dbfc0386491f3ac5fbad9f8320c. EaaW was not rerun.

After Method 12 closure, supervisor entered WAITING_FOR_REPAIR at UTF's existing config.json verified-transport failure; no UTF training started and files/evidence retained. CodeGenGuard's already-running preparation worker completed successfully; its receipt is consumed without launching another stage. Guardian/supervisor remain alive; shutdown gate cannot pass while UTF is waiting. Next permitted work is minimum engineering diagnosis/repair of UTF, with scientific changes requiring user decision.

## 2026-09-07T05:10:01.722478+00:00 User-requested safe pause

用户暂停（2026-09-06 请求，2026-09-07 保存）：PAUSED_BY_USER，暂停到下周；必须收到新的明确恢复指令才可继续。禁止下载、repair continuation、训练、检测、utility、advance 和自动关机。自动任务已 PAUSED；远端 SSH 不通，停止进程/GPU/关机路径尚未核实，不能宣称 SAFE PAUSE 已完成。详见 results/methods_11_15_pause_state_20260906.json。

No science run, no cleanup, no file deletion. Remote stop remains unverified due to SSH refusal/timeout. See pause handoff.


## UTF resume 2026-09-07

当前授权（2026-09-07）：用户明确解除暂停，仅恢复 Method 13 UTF Experiment A，STRICT SERIAL INTERACTIVE MODE。先修复 DeepSpeed 整数兼容并通过真实单步 preflight，再正式训练、detector、negative control、utility、reload、归档验证及 Git 闭环。不得启动 Method 14/15；auto_advance=false，auto_shutdown=false；UTF 闭环后 STOP。历史暂停证据保留。

已保存远端 attempt 3 原始证据及 SHA、Git diff；scoped stash + fast-forward a59d1a1，保留暂停历史并合并最新 runtime。整数根因为 Transformers 4.44 hidden-size formula；仅截断 prefetch bucket 15099494.4 -> 15099494。科学配置保持不变，单步成功前禁止正式训练。
