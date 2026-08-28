# Project Status

## Current phase

PN-FP reproduction and direct-distillation evaluation are CLOSED. A2 is the preferred utility-preserving teacher; Ba is complete with strong watermark degradation and partial retention. Bb was not run and remains deferred. No PN-FP GPU or transfer process is active.

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
- Experiment A1 completed with 1019/1024 detection but severe ordinary-generation degradation.
- Experiment A2 completed scientifically through training plus immutable evaluation continuation, achieved 956/1024, passed both gates, and is the preferred utility-preserving teacher.
- Experiment Ba run `pnfp_exp_ba_20260828_111148` completed its engineering pipeline. A2→Ba detection fell from 93.359375% to 9.5703125% (83.7890625-point drop; 10.251046% retention) while the utility gate passed. The bounded scientific result is strong degradation with partial retention under this tested setting.
- The old A1-based failed Ba run `pnfp_exp_ba_20260828_012228` remains immutable. Bb, UP, and Dipper have not started.

## Blockers

- No PN-FP scientific blocker remains. Notification delivery remains best-effort and outside scientific success criteria.
- The artifact protocol now separates immutable source/upload checks from destination-side full SHA256; see `docs/storage/artifact_transfer_protocol.md`.

## Next step

- Discuss and select the next watermark reproduction. Do not start another method until separately approved.


## A2 immutable evaluation continuation `pnfp_exp_a2_eval_20260828_105530`

Parent training run `pnfp_exp_a2_20260828_025240` remains operationally FAILED after external dataset acquisition failure. The validated checkpoint and reusable evaluations plus this continuation establish the final result. Watermark gate: **passed**; utility gate: **passed**; judgement: **A2 is the preferred PN-FP teacher for future Ba**.


## A2-teacher formal Ba run `pnfp_exp_ba_20260828_111148`

Teacher A2 provenance: `pnfp_exp_a2_20260828_025240` + `pnfp_exp_a2_eval_20260828_105530` (956/1024 = 93.359375%). Frozen QA: 20,000 samples, SHA256 `6ad11ff25826c32d71641c7433993070a8865e9e64e99841856e09b61d861a72`. Base/Ba: 1/1024 (0.09765625%) / 98/1024 (9.5703125%); teacher→Ba drop 83.7890625 points; retention 10.251046%. ARC Base/A2/Ba: 0.448805461 / 0.443686007 / 0.478668942. TruthfulQA MC2 Base/A2/Ba: 0.505450760 / 0.467427921 / 0.463479842. Utility and reload gates passed. Judgement: **PN-FP is vulnerable under the tested direct-distillation setting, with strong degradation and partial retention**. The old A1-based run remains immutable FAILED.
