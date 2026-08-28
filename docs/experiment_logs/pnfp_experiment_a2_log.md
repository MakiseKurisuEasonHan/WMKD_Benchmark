# PN-FP Experiment A2 Log

## Objective

A2 is a fresh embedding from the canonical unwatermarked 3B backbone. It tests the official utility-preserving regularizers with the same frozen 1,024 fingerprints used by A1. A1 remains immutable.

## Official regularization provenance

- Source: `SewoongLab/scalable-fingerprinting-of-llms@fdceaba14bd3e89340916a6a40e27c945d48460e`.
- WA: `finetune_multigpu.py::ModelAverageCallback`, argument `--forgetting_regularizer_strength`. It interpolates trainable weights toward frozen base weights at epoch end. The official schedule accumulates one optimizer update per epoch, so this is post-update interpolation. Paper/main and A2: `0.75`; CLI default: `0.75`; Python function default and README table: `0.0`.
- DM: `--benign_proportion`, `get_fingerprint_ds(... strategy="english", use_benign_response=True)`, and `fingerprint_dataloader.py::MixedDataCollator`. Batch 8 with beta 0.25 gives six fingerprint plus two sampled benign examples. Paper/main and A2: `0.25`; CLI default: `0.0`.
- Official `benign.json` has 100,096 records. The loader uses the first 16 tokens of `key` as context and the following token as target; its separate JSON `response` is unused on this path. This is base-model continuation distillation, not supervised labels.

## Official benign data retrieval

The official checkout is blobless and sparse. GitHub direct transfer repeatedly timed out at about 0.02 MB/s. A command-scoped `ghproxy.net` transport was substantially faster; provenance remains the official fixed commit.

- Size: `26,203,626` bytes.
- SHA256: `bd18da3b5a56002822a9789d83667452597ccc16979df3277fe2d04ff10a0201`.
- Official Git blob SHA-1: `e9113a584b6e149d7051bd3404ab97122dd55fe2` (matched).
- Path: `/root/autodl-tmp/WMKD_Benchmark_data/artifacts/pnfp/a2/official_data/benign.json`.

## Intended formal configuration — preparation-stage status at that time

At the preparation stage, the intended A2 configuration retained A1's exact 1,024 keys, lengths 16/16/1, 30 epochs, LR 5e-5, weight decay 1e-4, batch 8, BF16, seed 42, full parameters, LoRA off, and ZeRO-2 CPU offload. Deliberate differences were WA 0.75 and DM 0.25. Formal launch was not yet authorized at that time; the later formal execution is recorded below.

## Speed and utility smoke

Diagnostic `pnfp_a2_speed_smoke_20260828_023042` completed with exit code 0. It used the first 64 records of the unchanged A1 fingerprint file, 12 official optimizer updates (2 warmup, 10 measured), batch 8, six fingerprint plus two benign samples per normal microbatch, gradient accumulation 11, BF16, full parameters, ZeRO-2 CPU offload, WA 0.75, and DM 0.25. This smaller diagnostic dataset preserves the actual stack while avoiding 12 full 1,024-key epochs.

- Measured post-warmup optimizer-step interval: mean 10.825 s, median 10.946 s, range 10.126–11.123 s. Each interval includes 11 training microbatches, official epoch evaluation, and WA.
- Mean post-warmup WA time: 1.094 s/update. Trainer training runtime: 139.869 s. End-to-end load, preprocessing, training, save, and teardown: 242 s. Final-model write after training was approximately 13.5 s.
- Effective diagnostic accumulated batch: 64 fingerprint + 22 benign examples = 86 examples/update. Formal A2 will use 1,024 fingerprint + 342 benign examples = 1,366 examples/update and 171 accumulation microbatches.
- Trainer-reported fingerprint throughput: 5.491 samples/s. Approximate actual mixed-example throughput was 7.38 samples/s. GPU telemetry: 100% peak utilization, 59.4% mean among nonzero samples, 23.4% over the full load/preprocess/save window; peak VRAM 29,995 MiB. Peak host RAM used was 77.21 GiB.
- No OOM, NaN, CUDA error, traceback, or retry occurred. The official Instruct benign-tokenization path emitted many `Response not found` warnings and used its documented manual concatenation fallback; this is an implementation warning to retain in formal reporting, not a fatal error.
- Checkpoint reload/generation succeeded. On 10 fixed prompts, both base and A2-smoke had 3/10 max-token hits and 0/10 obvious repetition; sampled outputs were coherent. This does not establish formal utility.
- Tiny watermark sanity: 64/64 detected, zero invalid samples and zero evaluation errors. This is not a formal detection result and must not be used for tuning.
- Diagnostic directory: `/root/autodl-tmp/WMKD_Benchmark_data/runs/pnfp/pnfp_a2_speed_smoke_20260828_023042` (6.1 GiB). Data disk after smoke: 975 GiB free.

Scaling the measured microbatch/evaluation/WA components gives about 152 seconds per formal epoch and 76 minutes for 30 training epochs. A1 measured 26.5 minutes without WA/DM, confirming that the regularized stack is materially slower. Expected fixed-fingerprint checkpoint/reload/control work is only a few minutes based on A1; ARC Challenge and TruthfulQA MC timing has not yet been measured on this stack. Planning range including those required utility evaluations: optimistic 1 h 25 min, expected 1 h 40 min, conservative 2 h 15 min. Main uncertainty is utility-evaluation runtime and whether full-scale benign tokenization/cache behavior differs from smoke.

Preparation-stage judgement at that time: formal A2 was technically ready but had not started and required explicit user approval.


## A2 immutable evaluation continuation `pnfp_exp_a2_eval_20260828_105530`

Parent training run `pnfp_exp_a2_20260828_025240` remains operationally FAILED after external dataset acquisition failure. The validated checkpoint and reusable evaluations plus this continuation establish the final result. Watermark gate: **passed**; utility gate: **passed**; judgement: **A2 is the preferred PN-FP teacher for future Ba**.

## Formal A2 training

- Parent training run: `pnfp_exp_a2_20260828_025240`.
- Completed all 30/30 optimizer steps with final `eval_loss = 0.3678587`.
- The final checkpoint was saved and reload validation passed. No OOM, CUDA error, or NaN was observed.
- The training run's operational terminal status is **FAILED** only because the downstream ARC dataset acquisition failed after training, checkpoint validation, full 1,024-key PN-FP evaluation, canonical-base control, and ordinary-generation diagnostics had completed.
- The failed run remains immutable; its validated checkpoint was not retrained or modified.

## Immutable evaluation continuation

- Evaluation-only run: `pnfp_exp_a2_eval_20260828_105530`.
- ARC Challenge and TruthfulQA MC2 were fixed to local, revision-recorded datasets and loaded fully offline. No retraining occurred.
- PN-FP: A2 956/1024 (93.359375%); canonical base 1/1024 (0.09765625%); A1 1019/1024 (99.511719%).
- ARC Challenge: base 0.44880546075085326; A2 0.44368600682593856; delta -0.005119453924914696.
- TruthfulQA MC2: base 0.505450760153828; A2 0.4674279212401518; delta -0.03802283891367614.

## Final scientific conclusion

The watermark gate and utility gate both passed. A2 retains strong PN-FP detection while avoiding A1's severe ordinary-generation degradation. **A2 is the preferred PN-FP teacher for future Ba.**

## Artifact and closure status

The eight canonical files total 6,434,691,753 bytes and were uploaded to private repo `MakiseKurisuEasonHan/WMKD-PNFP-A2-Teacher`. Source SHA256 plus remote filename/count/size/blob consistency passed. The correct upload-time state is `uploaded_to_modelscope_awaiting_destination_hash_verification`; the upload run did not fully re-download all model bytes to AutoDL. Experiment A2 is CLOSED.
