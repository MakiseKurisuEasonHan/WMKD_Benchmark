# EverTracer Experiment A Log

## Objective

Reproduce EverTracer natural-language fingerprint injection, reference calibration, and probability-variation verification on the canonical WMKD Llama-3.2-3B-Instruct backbone. Experiment Ba and ModelScope upload are out of scope.

## Fixed design

- Official repository: `https://github.com/Xuzhenhua55/EverTracer.git`
- Commit: `70b402f7b7456c6d94e1fae2de554d77dd6cd921`
- Official license file: absent at pinned commit; official code is not vendored.
- Dataset: XSum revision `7d4d486c2f8ef850b1a11aead99b894ff3dd7da9`, immutable disjoint Dtr=100, Dref=1000, Dunseen=100, seed 48.
- Target: LoRA r=8, 20 epochs, batch 4, LR 1e-4, packed 128, BF16.
- Reference: fresh canonical base, same core LoRA configuration, 4 epochs.
- Verification: `google-t5/t5-base@a9723ea7f1b39c1eae772870f3b547bf6ef7e6c1`, official 128-token packed input window, K=5 symmetric perturbation pairs, 30% token fraction, calibrated probability variation, AUC and maximum TPR at empirical FPR <=5%.
- Gates: AUC >=0.95; FSR >=90%; above base; ARC/TruthfulQA and ordinary-generation utility; fresh-process reload.

## Current status

Formal run `evertracer_a_20260828_223155` is detached and RUNNING on AutoDL at WMKD commit `507183234afc231c8a821e77f4b48f4590cc8e06`, PID 185252. Preflight passed 16/16 checks, the STARTED email was delivered over SSL465, and the run entered `RUNNING_TARGET`. Experiment Ba and ModelScope upload have not started.

## Immutable runs

- Speed smoke: `/root/autodl-tmp/WMKD_Benchmark_data/runs/evertracer_smoke/smoke_20260828_2153`.
  - Target/reference: 8 steps each; 0.1709/0.1598 seconds per step; both peaked at 8,863,229,952 bytes VRAM.
  - T5: four records, 40 variants, 5.414 seconds, zero fill retries, 486,969,856 bytes peak VRAM.
  - Verification: four calibrated records, 5.299 seconds, 13,040,928,256 bytes peak VRAM. Its AUC/FSR are non-scientific because the adapters had only eight steps and each class had two samples.
  - Utility: ARC Challenge and TruthfulQA MC2, five samples per task and 53 likelihood requests, exit 0.
  - Fresh reload ordinary generation: five prompts, passed.
- Formal run: `/root/autodl-tmp/WMKD_Benchmark_data/runs/evertracer/evertracer_a_20260828_223155` (RUNNING; immutable namespace).

## AutoDL deployment note

The primary AutoDL checkout was found to contain preserved PN-FP-era local commits and uncommitted files. EverTracer must use a separate project-owned deployment checkout at the pinned WMKD Git commit; do not reset, stash, clean, or overwrite the primary checkout.

The first dependency resolution attempt stopped before installation because `lm-eval==0.4.9.1` requires `datasets<4.0` while the initial project requirement specified `datasets==4.0.0`. The compatibility pin was corrected to `datasets==3.6.0`; this does not alter the pinned XSum dataset revision, split, samples, or EverTracer algorithm.

XSum download attempt 1 and T5 download attempt 1 ended with resumable `IncompleteRead` errors; attempt 2 completed the same pinned revisions. The frozen XSum manifest records fingerprint `5a1b0a50e80b133b` and disjoint file hashes. T5 contains five required files totaling 893,828,754 bytes; `model.safetensors` SHA256 is `a90903540cc02cbeb7ff9f823f1a80eb778c7e22426a0e620b01c77a5ec8f5b4`.
# Infrastructure continuation

- Parent formal run `evertracer_a_20260828_223155` remains immutable FAILED at `PREPARING_VERIFICATION / perturb` after target/reference training and merging completed successfully.
- The failure was an engineering cache-visibility/online-resolution failure: pinned `google-t5/t5-base@a9723ea7f1b39c1eae772870f3b547bf6ef7e6c1` attempted Hub access while AutoDL networking was unavailable.
- Continuation `evertracer_a_20260828_223155_cont1` reuses the same target/reference artifacts, does not repeat training or merging, and loads the pinned local snapshot with network fallback disabled.
- Scientific configuration remains unchanged: block size 128, K=5, perturbation fraction 30%, Dtr=100, Dref=1000, Dunseen=100, and the same canonical backbone/revision.
- Offline smoke passed under `HF_HUB_OFFLINE=1` and `TRANSFORMERS_OFFLINE=1`: 2 records, 20 variants, zero generation retries, no network/Hub request in the log, and valid manifest output.
- Detached continuation started at `2026-08-29T11:15:29+08:00` with runner PID 252427. STARTED email succeeded via SSL 465; initial stage is `PREPARING_VERIFICATION`.
