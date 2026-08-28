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
- [x] Launch formal same-size 3B Ba run `pnfp_exp_ba_20260828_012228`; preserve its fail-fast evidence after teacher QA generation yielded 0 valid candidates and 64 parse failures.
- [x] Diagnose the failed teacher generation with bounded ordinary/CAN-style/JSON tests and add tested no-progress guards.
- [x] Establish A2 as the utility-preserving preferred PN-FP teacher after both watermark and utility gates passed.
- [x] Complete and formally close A2-based Ba run `pnfp_exp_ba_20260828_111148`; record strong watermark degradation with partial retention and a passed utility gate.
- [ ] Keep Bb and all Dipper/UP downloads deferred until a separate future approval.
- [x] Implement and test reusable experiment email notification infrastructure without touching the active PN-FP process.
- [x] Deploy standalone notification utilities outside the active AutoDL Git checkout.
- [x] Configure the Gmail App Password interactively on AutoDL and send one successful independent test email.
- [x] Start and verify the read-only detached watcher for the current PN-FP run.
- [x] Finalize Experiment A dedicated log, formal report, and machine-readable summary with mutually consistent authoritative results.
- [x] Harden SMTP with bounded retries, serial STARTTLS fallback, terminal pending queue, and CPU-only retry utility.
- [ ] Retry the legitimate missed Experiment A COMPLETED notification when the AutoDL credential becomes reachable; do not send STARTED.

## Medium priority

- [ ] Analyze the PN-FP Ba result further only if an additional scientific question is approved.
- [x] Upload the A2 canonical teacher to private ModelScope with immutable source/upload checks; destination-side verification remains a future transfer-stage gate.
- [ ] Decide whether and when to authorize PN-FP Bb; do not start Bb, UP, or Dipper without explicit approval.
- [ ] Move to the next watermark method when selected by the user.
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


## A2 immutable evaluation continuation `pnfp_exp_a2_eval_20260828_105530`

Parent training run `pnfp_exp_a2_20260828_025240` remains operationally FAILED after external dataset acquisition failure. The validated checkpoint and reusable evaluations plus this continuation establish the final result. Watermark gate: **passed**; utility gate: **passed**; judgement: **A2 is the preferred PN-FP teacher for future Ba**.


## A2-teacher formal Ba run `pnfp_exp_ba_20260828_111148`

Completed: A2 956/1024 (93.359375%) → Ba 98/1024 (9.5703125%), 83.7890625-point drop and 10.251046% retention; utility and reload gates passed. The result is strong degradation with partial retention under the tested setting. Preserve the immutable old A1-based failure; keep Bb, UP, and Dipper deferred.

## PN-FP final closure

- [x] Mark Experiments A, A2 and Ba CLOSED with bounded conclusions.
- [x] Preserve small scientific and transfer records before AutoDL cleanup.
- [x] Remove completed PN-FP large AutoDL run/readback artifacts while preserving the canonical base, environments, credentials and reusable infrastructure.
- [x] Record the future destination-side artifact verification protocol.
- [ ] Bb remains NOT RUN / deferred.
- [ ] Discuss and select the next watermark reproduction; do not start it without explicit approval.
