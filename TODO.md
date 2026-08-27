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
- [ ] Monitor PN-FP Experiment A without launching another large GPU task.
- [ ] Complete checkpoint reload, watermarked evaluation, base control, paired metrics, report, and summary.

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
