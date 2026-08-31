# Project Status

## Current phase

SCW is the active fifth method, but Experiment A is **NOT RUN / BLOCKED ON RUNTIME**. AutoDL deployment and runtime preflight remain READY with 3,212,749,824/3,212,749,824 unique trainable/total BF16 parameters. The original non-scientific speed run and terminal-fix validations `_01`, `_02`, and `_03` all completed 4/4 optimizer steps and `train_end`, then reproduced the same CPython-finalization `PyGILState_Release` SIGABRT. Exact official dependency pins and explicit Python-level dataset/fsspec teardown—including a late atexit GC—did not resolve it; failed compatibility edits were reverted. Best-supported diagnosis is an unresolved Python 3.12 native-extension/background-thread finalization-order defect, not training corruption. Formal A remains prohibited; no Teacher, Ba, ModelScope use, or cleanup exists. See `docs/methods/scw.md` and `docs/experiment_logs/scw_experiment_a_log.md`.

iSeal is FULLY CLOSED through A and Ba plus private ModelScope archival. Experiment A remains blocked before formal launch by the pinned public-code exact-zero gate; authorized A2-A6 culminated in preferred Teacher A6 (179/200 registered). Ba Student `iseal_ba_20260830_165442` completed 7,500 steps from the fresh canonical base. Registered success fell 179/200 → 0/200, equal to Base 0/200 (89.5-point drop; 0% thresholded retention); ARC/TruthfulQA were 0.481229/0.449818, ordinary generation 10/10, and fresh reload passed. Teacher/Student private archives passed remote metadata verification and await independent destination SHA256. Bb/A7 were not created.

CTCC is FULLY CLOSED through Experiments A and Ba plus private ModelScope archival. Experiment A run `ctcc_a_20260829_190251` established the preferred Teacher from all pinned public-artifact records (Trigger 461, Suppression 428, Normal 1000; total 1889) without augmentation. Official source is pinned to `Xuzhenhua55/CTCC@8db93218260bed31b8f18acc9c6ac3e1955d3a42`; the paper's 500/500/1000 total 2000 remains a paper-vs-public-artifact discrepancy.

The full released test contains 95 Trigger, 100 Suppression, and 105 Normal records. Teacher/Base trigger activation was 95/95 versus 0/95; Teacher combined-negative false activation was 0/205. CTCC Ba preserved the failed 40,007-raw parent, completed through infrastructure-only generation continuation `ctcc_ba_generation_20260829_195943_cont1`, froze exactly 20,000 QA (SHA256 `621c9aedcf3a4a1db86a4848bbf93fa893d18022f15b913e8aeeb28739412484`), and trained fresh-canonical Student `ctcc_ba_20260830_025244` for 7,500/7,500 steps. Fresh-reload evaluation continuation `ctcc_ba_eval_20260830_033556_cont1` produced Student Trigger 0/95, negatives 0/205, ARC 0.483788, TruthfulQA MC2 0.450614, and a passing ordinary-generation sanity check. The bounded result is that CTCC trigger retention fell to the Base level under this tested standardized direct-distillation setting while tested utility remained functional.

The CTCC preferred Teacher LoRA adapter and Ba inference-ready Student final model are uploaded to private ModelScope repositories `MakiseKurisuEasonHan/WMKD-CTCC-A-Teacher` and `MakiseKurisuEasonHan/WMKD-CTCC-Ba-Student`. Both are `uploaded_to_modelscope_awaiting_destination_hash_verification`: source manifests and remote filename/count/size/blob-metadata checks passed, but a future independent destination download is required for full SHA256 verification.

PN-FP reproduction and direct-distillation evaluation are CLOSED. A2 is the preferred utility-preserving teacher; Ba is complete with strong watermark degradation and partial retention. Bb was not run and remains deferred. No PN-FP GPU or transfer process is active.

EverTracer is FULLY CLOSED after protected cleanup. Experiments A and Ba are scientifically and operationally complete. A's preferred teacher achieved member-oriented AUC/TPR@FPR<=5% of 1.0/1.0. Ba run `evertracer_ba_20260829_124055` completed with student AUC/TPR 0.4987/0.06, indicating that direct distillation reduced the detector signal to near chance while reload and generation sanity passed. There is no EverTracer blocker; Bb remains NOT RUN/deferred.

The EverTracer A preferred teacher and Ba student were uploaded to their fixed private ModelScope repositories. Both archives are `uploaded_to_modelscope_awaiting_destination_hash_verification`; full destination SHA256 remains deferred to a future download on another machine.

The canonical cross-session rules are consolidated in `docs/EXPERIMENT_PROTOCOL.md`. The selected benchmark methods are PN-FP, CTCC, SCW, EverTracer, iSeal, LLMPrint, and REEF. Current default lifecycle is A → Ba; A2/A3 are reserved for scientific-configuration corrections, while unchanged-science engineering recovery uses immutable continuation lineage. Bb remains NOT RUN/deferred while all seven methods' A and Ba are prioritized first; a future explicitly approved UP implementation is not inherently limited to Dipper.

The durable benchmark default is a same-family, same-size, same-revision A/Ba/Bb design using canonical `meta-llama/Llama-3.2-3B-Instruct@0cb88a4f764b7a12671c53f0838cd831a0843b95`. Every method's Ba must use that method's own preferred teacher to generate its own answers; another watermark's teacher, QA, frozen 20k, or student must never be reused. Students always start from fresh canonical unwatermarked weights. Any method-specific backbone or Ba deviation requires a recorded blocker and explicit user approval.

Completed methods: **4/7** (PN-FP, EverTracer, CTCC, and iSeal). Remaining: **SCW, LLMPrint, REEF**. The fifth watermark and next discussion target is **SCW**, but SCW has not been cloned, downloaded, configured, or started. The canonical Llama remains preserved. The current AutoDL operational baseline is Ubuntu 22.04, Python 3.12, PyTorch 2.8.0, CUDA 12.8, RTX PRO 6000 96 GB ×1, Intel Xeon Platinum 8470Q with 22 vCPUs, 110 GB RAM, 30 GB system disk, and approximately 500 GB data capacity (50 GB free + 450 GB paid). The instance is currently pay-as-you-go; this operational state is not scientific protocol. Older 208-vCPU/approximately-1-TiB records are historical.

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
- Current method: SCW. Deployment and runtime-effective preflight are complete, but three bounded terminal-fix validations reproduced the post-`train_end` SIGABRT. Formal A remains NOT RUN. Do not launch 2,500 steps; the next engineering decision must test a clean supported Python runtime/environment (preferably Python 3.11) or obtain an upstream native-extension fix before another GPU run.
- After separate explicit user authorization, final AutoDL cleanup deleted only the five audited exact paths: A2-A5 non-preferred Teacher artifacts and Ba `checkpoint-7500`. Logical size removed was 47,429,470,039 bytes; filesystem used space decreased by 47,429,681,152 bytes. Canonical base, A6 Teacher, Ba final Student, frozen20k, ModelScope manifests, shared infrastructure/cache, raw generation, and all other-watermark artifacts remain protected.


## A2 immutable evaluation continuation `pnfp_exp_a2_eval_20260828_105530`

Parent training run `pnfp_exp_a2_20260828_025240` remains operationally FAILED after external dataset acquisition failure. The validated checkpoint and reusable evaluations plus this continuation establish the final result. Watermark gate: **passed**; utility gate: **passed**; judgement: **A2 is the preferred PN-FP teacher for future Ba**.


## A2-teacher formal Ba run `pnfp_exp_ba_20260828_111148`

Teacher A2 provenance: `pnfp_exp_a2_20260828_025240` + `pnfp_exp_a2_eval_20260828_105530` (956/1024 = 93.359375%). Frozen QA: 20,000 samples, SHA256 `6ad11ff25826c32d71641c7433993070a8865e9e64e99841856e09b61d861a72`. Base/Ba: 1/1024 (0.09765625%) / 98/1024 (9.5703125%); teacher→Ba drop 83.7890625 points; retention 10.251046%. ARC Base/A2/Ba: 0.448805461 / 0.443686007 / 0.478668942. TruthfulQA MC2 Base/A2/Ba: 0.505450760 / 0.467427921 / 0.463479842. Utility and reload gates passed. Judgement: **PN-FP is vulnerable under the tested direct-distillation setting, with strong degradation and partial retention**. The old A1-based run remains immutable FAILED.
