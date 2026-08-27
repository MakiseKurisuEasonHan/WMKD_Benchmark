# Project Status

## Current phase

Stage 3 — PN-FP Experiment A finalized; first formal same-size 3B Ba run failed at teacher QA generation; Bb deferred. No formal GPU run active.

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
- Ba Direct Distillation uses a watermarked 3B teacher plus fresh unwatermarked canonical 3B student. Formal run `pnfp_exp_ba_20260828_012228` passed preflight but produced 0 valid candidates and 64 parse failures from degenerate teacher output, then failed safely before dataset freeze or training.
- Bb remains prepared/deferred. No Dipper or UP work is running.

## Blockers

- The local environment still cannot authenticate Git over the configured SSH GitHub remote; authenticated temporary HTTPS credentials can be used without changing `origin`.
- AutoDL SSH recovered on 2026-08-28; the corrected Ba workflow is intentionally stopped pending explicit launch approval.
- The general artifact synchronization protocol has not yet been defined; the school canonical model copy has a verified task-specific provenance manifest.
- No model-transfer or offline-smoke blocker remains. ModelScope was used only as transport, the sole mismatched small file was repaired from the exact Hugging Face revision, and the final AutoDL directory passed the frozen 12-file manifest.

## Next step

- Preserve Experiment A and immutable failed Ba run `pnfp_exp_ba_20260828_012228`. Diagnose and review the teacher-generation/data-source correction before authorizing a new Ba run; do not resume or overwrite the failed run.
