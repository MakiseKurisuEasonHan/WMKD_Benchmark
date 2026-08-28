# Project Status

## Current phase

Stage 3 — PN-FP A1 and A2 established; A2 is the preferred teacher. A2-based formal Ba run `pnfp_exp_ba_20260828_111148` is active at `teacher_qa_generation`. Bb and Dipper remain deferred.

The durable benchmark default is now a same-family, same-size, same-revision A/Ba/Bb design using canonical `meta-llama/Llama-3.2-3B-Instruct@0cb88a4f764b7a12671c53f0838cd831a0843b95`. Ba/Bb teachers are successful watermarked A checkpoints; students always start from fresh canonical unwatermarked weights. Any method-specific backbone deviation requires a recorded blocker and explicit user approval.

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
- A2-based Ba Direct Distillation run `pnfp_exp_ba_20260828_111148` is active. Teacher is the A2 final checkpoint; student initializes from fresh canonical unwatermarked 3B weights. The current stage is `teacher_qa_generation`, with an approximately 24,000 raw-candidate target followed by an exact 20,000 frozen-QA gate.
- Read-only observation at 2026-08-28 11:31:04 +08:00 recorded 2,344/24,000 raw candidates and 82 generation/parse failures; generation was advancing, GPU was healthy, and no final Ba result existed.
- The old A1-based failed Ba run `pnfp_exp_ba_20260828_012228` remains immutable. Bb and Dipper have not started.

## Blockers

- The local environment still cannot authenticate Git over the configured SSH GitHub remote; authenticated temporary HTTPS credentials can be used without changing `origin`.
- The active A2-based Ba run is not blocked at the last observed milestone. Its STARTED email timed out, but notification delivery is best-effort and did not affect the experiment.
- The general artifact synchronization protocol has not yet been defined; the school canonical model copy has a verified task-specific provenance manifest.
- No model-transfer or offline-smoke blocker remains. ModelScope was used only as transport, the sole mismatched small file was repaired from the exact Hugging Face revision, and the final AutoDL directory passed the frozen 12-file manifest.

## Next step

- Allow active run `pnfp_exp_ba_20260828_111148` to finish without concurrent GPU work, then analyze watermark retention and utility jointly. Keep the old failed Ba run immutable and keep Bb/Dipper deferred.


## A2 immutable evaluation continuation `pnfp_exp_a2_eval_20260828_105530`

Parent training run `pnfp_exp_a2_20260828_025240` remains operationally FAILED after external dataset acquisition failure. The validated checkpoint and reusable evaluations plus this continuation establish the final result. Watermark gate: **passed**; utility gate: **passed**; judgement: **A2 is the preferred PN-FP teacher for future Ba**.
