# PN-FP Experiment A Log

This file is the durable scientific history and source of truth for PN-FP Experiment A. Raw process output is stored under the immutable AutoDL run directory, not copied here.

## Objective

Embed 1,024 PN-FP perinucleus fingerprints into the fixed Llama-3.2-3B-Instruct backbone by full-parameter BF16 training, compare reloaded watermarked detection with the unwatermarked base, and preserve the resulting model for later distillation research.

## Planned and actual configuration

| Field | Formal value | Current actual value |
|---|---:|---:|
| Backbone | Llama-3.2-3B-Instruct | Pending formal launch |
| Revision | `0cb88a4f764b7a12671c53f0838cd831a0843b95` | Pending formal launch |
| Fingerprints | 1024 | Pending formal launch |
| Key / generation / training response length | 16 / 16 / 1 | Pending formal launch |
| Epochs / LR / weight decay | 30 / 5e-5 / 1e-4 | Pending formal launch |
| Per-device batch | 8 initially | Pending formal launch |
| Precision / seed | BF16 / 42 | Pending formal launch |
| Training | Full parameter; LoRA off | Pending formal launch |
| Serialization | Llama chat template for generation, training, and evaluation | Pending formal launch |
| PN-FP sampling | threshold 0.8; k=3 | Pending formal launch |
| Model averaging | 0.0 | Pending formal launch |

DeepSpeed ZeRO-2 CPU offload is used only as the official implementation's memory mechanism; it does not freeze or approximate model parameters. The official source is `SewoongLab/scalable-fingerprinting-of-llms` commit `fdceaba14bd3e89340916a6a40e27c945d48460e`.

## Paper comparison and scope

The paper demonstrates much larger fingerprint scales on Llama-3.1-8B. Experiment A is a bounded core reproduction on the benchmark-standardized Llama-3.2-3B-Instruct 3B revision with 1,024 fingerprints. It is not a complete reproduction of all paper experiments or utility/persistence ablations.

## Preparation and runner

- Stage 1 established the canonical AutoDL model at `/root/autodl-tmp/WMKD_Benchmark_data/models/base/Llama-3.2-3B-Instruct` and verified all 12 files against the frozen manifest.
- The project runner is `scripts/run_pnfp_experiment_a.sh`; the detached pipeline and structured evaluator are project-owned scripts.
- Runs use `/root/autodl-tmp/WMKD_Benchmark_data/runs/pnfp/<run_id>/` with configuration, logs, status, checkpoints, evaluation, and results subdirectories.
- Formal launch: pending.

## Results, judgement, and artifacts

Training, OOM status, checkpoint, reload, watermarked result, base result, paired result, scientific judgement, final report, machine-readable summary, archive, and Git completion are pending formal execution.

## Next step

Validate the runner with minimum non-training checks, commit/push the stable runner and protocol, synchronize AutoDL, and launch the first immutable formal run at batch size 8.
