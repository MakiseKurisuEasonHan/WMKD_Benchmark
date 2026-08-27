# TODO

## High priority

- [x] Initialize the independent local project structure.
- [x] Add repository documentation and project-management logs.
- [x] Add strict ignore rules for secrets and large artifacts.
- [x] Create and verify the private GitHub repository and synchronized `main` branch.
- [x] Initialize the La Trobe lightweight mirror and dedicated large-artifact warehouse.
- [x] Approve PNFP as the first watermark reproduction target and record Experiment A settings.
- [x] Initialize the AutoDL compute checkout and isolated data/cache structure.
- [x] Create and validate the PNFP-specific AutoDL environment.
- [x] Archive the fixed Llama-3.2-3B-Instruct revision in canonical La Trobe storage and verify all 12 files by size and SHA256.
- [x] Evaluate the ModelScope Llama-3.2-3B-Instruct candidate and reject it after a downloaded canonical-file mismatch confirmed it is not byte-identical.
- [x] Complete the fixed Llama model transfer to AutoDL and verify all SHA256 values.
- [x] Run offline tokenizer/model load and short generation smoke after transfer verification.
- [x] Explicitly authorize formal PNFP Experiment A training in a separate task.
- [x] Define the durable formal experiment protocol and dedicated PN-FP log convention.
- [x] Launch corrected PN-FP Experiment A through the independent runner (`pnfp_exp_a_20260827_232033`).
- [x] Complete PN-FP Experiment A checkpoint reload, watermarked/base evaluation, paired metrics, and summary.
- [x] Prepare paired PN-FP Ba/Bb configs, dataset/UP validation, schemas, logs, report templates, and guarded dry-run runners.
- [x] Pin the official CAN repository at `9a2b01af1fadcece2893d32460ed9449093f8fb9`.
- [x] Cancel and remove the incorrect partial 1B student download before any formal Ba run or notification.
- [ ] After explicit approval, deploy the corrected Ba configuration, reuse/verify the canonical pinned Llama-3.2-3B-Instruct, run minimum preflight, and launch detached Ba.
- [ ] Keep Bb and all Dipper/UP downloads deferred until a separate future approval.
- [x] Implement and test reusable experiment email notification infrastructure without touching the active PN-FP process.
- [x] Deploy standalone notification utilities outside the active AutoDL Git checkout.
- [x] Configure the Gmail App Password interactively on AutoDL and send one successful independent test email.
- [x] Start and verify the read-only detached watcher for the current PN-FP run.
- [x] Finalize Experiment A dedicated log, formal report, and machine-readable summary with mutually consistent authoritative results.
- [x] Harden SMTP with bounded retries, serial STARTTLS fallback, terminal pending queue, and CPU-only retry utility.
- [ ] Retry the legitimate missed Experiment A COMPLETED notification when the AutoDL credential becomes reachable; do not send STARTED.

## Medium priority

- [ ] Define dependency-management and environment-reproduction conventions.
- [ ] Define storage and synchronization policies for future large artifacts.
- [ ] Add method-specific reproducibility instructions after research decisions are approved.

## Completed

- Local initialization scaffold created on 2026-08-27.
- Private GitHub repository created and connected on 2026-08-27.
- La Trobe school-server storage endpoint initialized on 2026-08-27.
- AutoDL compute endpoint and isolated data root initialized on 2026-08-27.
- PNFP official source and isolated environment prepared on 2026-08-27; model transfer was still blocked at that preparation stage.
- Fixed Llama-3.2-3B-Instruct canonical school-server archive completed and fully verified on 2026-08-27.
- Fixed Llama-3.2-3B-Instruct AutoDL snapshot completed and fully verified on 2026-08-27; offline tokenizer/model/generation smoke passed without starting training.
