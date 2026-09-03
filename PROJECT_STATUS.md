# Project Status

## Current phase — 2026-09-03

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
