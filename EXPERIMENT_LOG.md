# Experiment Log

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
