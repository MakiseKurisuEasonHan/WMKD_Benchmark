# PN-FP Experiment A Log

This file is the durable scientific history and source of truth for PN-FP Experiment A. Raw process output is stored under the immutable AutoDL run directory, not copied here.

## Objective

Embed 1,024 PN-FP perinucleus fingerprints into the fixed Llama-3.2-3B-Instruct backbone by full-parameter BF16 training, compare reloaded watermarked detection with the unwatermarked base, and preserve the resulting model for later distillation research.

## Planned and actual configuration

| Field | Formal value | Current actual value |
|---|---:|---:|
| Backbone | Llama-3.2-3B-Instruct | Canonical local model path |
| Revision | `0cb88a4f764b7a12671c53f0838cd831a0843b95` | Same |
| Fingerprints | 1024 | 1024 |
| Key / generation / training response length | 16 / 16 / 1 | 16 / 16 / 1 |
| Epochs / LR / weight decay | 30 / 5e-5 / 1e-4 | 30 / 5e-5 / 1e-4 |
| Per-device batch | 8 initially | 8; no OOM observed at launch |
| Precision / seed | BF16 / 42 | BF16 / 42 |
| Training | Full parameter; LoRA off | 3,212,749,824 / 3,212,749,824 parameters trainable; LoRA off |
| Serialization | Llama chat template for generation, training, and evaluation | Same |
| PN-FP sampling | threshold 0.8; k=3 | Same |
| Model averaging | 0.0 | 0.0 |

DeepSpeed ZeRO-2 CPU offload is used only as the official implementation's memory mechanism; it does not freeze or approximate model parameters. The official source is `SewoongLab/scalable-fingerprinting-of-llms` commit `fdceaba14bd3e89340916a6a40e27c945d48460e`.

## Paper comparison and scope

The paper demonstrates much larger fingerprint scales on Llama-3.1-8B. Experiment A is a bounded core reproduction on the benchmark-standardized Llama-3.2-3B-Instruct 3B revision with 1,024 fingerprints. It is not a complete reproduction of all paper experiments or utility/persistence ablations.

## Preparation and runner

- Stage 1 established the canonical AutoDL model at `/root/autodl-tmp/WMKD_Benchmark_data/models/base/Llama-3.2-3B-Instruct` and verified all 12 files against the frozen manifest.
- The project runner is `scripts/run_pnfp_experiment_a.sh`; the detached pipeline and structured evaluator are project-owned scripts.
- The current AutoDL image does not provide `tmux`; the launcher therefore uses the protocol-permitted equivalent `nohup + setsid` mode and persists its detached PID. It retains automatic `tmux` support when available.
- Runs use `/root/autodl-tmp/WMKD_Benchmark_data/runs/pnfp/<run_id>/` with configuration, logs, status, checkpoints, evaluation, and results subdirectories.
- `pnfp_exp_a_20260827_231202`: immutable failed run. Minimum preflight passed, including BF16, one idle RTX PRO 6000, active runtime configuration, and all 3,212,749,824 parameters trainable. Fingerprint generation then failed before training because the Stage 1 sparse checkout had excluded official support file `generated_data/word_list.txt`. Raw evidence is preserved under the run directory; no OOM occurred.
- Fix: restored only the 75,879-byte `generated_data/word_list.txt` from the already-fixed official source commit. No official pre-generated fingerprint JSON was restored or reused; the official checkout remains clean at the same commit.
- `pnfp_exp_a_20260827_231325`: immutable failed run, launched 2026-08-27 23:13:25 AutoDL local time. Fresh fingerprint generation ran, but the official Instruct branch skipped 12 keys whose detokenized text ended in whitespace, leaving 1,012 instead of the required 1,024. The training entry point rejected the dataset before any optimizer step. No OOM occurred.
- Fix for the next run: generate 1,100 candidate keys so the official whitespace validity filter can operate, require at least 1,024 valid generated records, then use exactly the first fixed 1,024 for both training and paired evaluation. Candidate oversampling is a compatibility measure, not an increase in the formal fingerprint count.
- `pnfp_exp_a_20260827_231639`: immutable failed run. It generated 1,087 valid candidates, fixed the first 1,024, and reached DeepSpeed initialization with the exact declared training configuration. Before the first optimizer step, CPUAdam reported that `ninja` was unavailable. Inspection showed `ninja==1.13.0` and its executable were already installed inside the isolated environment, but the detached/DeepSpeed subprocess PATH did not expose the environment's `bin` directory. No OOM or optimizer step occurred.
- Fix for the next run: explicitly prepend the isolated environment `bin` directory to detached PATH and make `ninja` discovery a mandatory preflight assertion.
- `pnfp_exp_a_20260827_232033`: successful corrected formal run, launched 2026-08-27 23:20:33 AutoDL local time with detached PID 88165 (`nohup_setsid`). Minimum preflight and fresh fingerprint generation passed; 1,087 valid candidates were generated and the first 1,024 were fixed. Batch-8 full-parameter training completed all 30 epochs without OOM. Final `eval_loss` was 0.0119302. The final model was saved under `/root/autodl-tmp/WMKD_Benchmark_data/runs/pnfp/pnfp_exp_a_20260827_232033/checkpoints/official/saved_models/a0a21e74c9f8f189aee68a315cb668b4/final_model`.

## Results, judgement, and artifacts

The final checkpoint reloaded successfully. Watermarked detection was 1019/1024 (`0.9951171875`, 99.5117%); the unwatermarked base control was 1/1024 (`0.0009765625`, 0.0977%). The paired absolute difference was `0.994140625`, or 99.4141 percentage points. Both evaluations recorded zero invalid samples and zero errors. The bounded judgement is **PN-FP core reproduction successful**.

The read-only watcher correctly detected COMPLETED. Its original single Gmail SMTP_SSL attempt failed with `TimeoutError: timed out`; the scientific experiment and status remained completed. The original failure record did not identify whether the timeout occurred during connect/SSL, login, send, or socket read. Notification delivery was subsequently hardened with bounded retries, STARTTLS fallback and a persistent terminal-event queue.

## Next step

Experiment A is complete. Preserve the final checkpoint and raw immutable run. Continue with Experiment Ba only after AutoDL SSH recovers; Ba currently has no run ID and has not started.
