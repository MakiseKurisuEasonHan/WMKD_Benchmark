# PNFP / Perinucleus Fingerprinting

## Official provenance

- Paper: *Scalable Fingerprinting of Large Language Models*
- Authors: Anshul Nasery, Jonathan Hayase, Creston Brooks, Peiyao Sheng, Himanshu Tyagi, Pramod Viswanath, and Sewoong Oh
- Paper: `https://arxiv.org/abs/2502.07760`
- Official repository: `https://github.com/SewoongLab/scalable-fingerprinting-of-llms.git`
- Fixed source commit: `fdceaba14bd3e89340916a6a40e27c945d48460e`
- AutoDL external-source path: `/root/autodl-tmp/WMKD_Benchmark_data/artifacts/pnfp/source`
- Planned environment path: `/root/autodl-tmp/WMKD_Benchmark_data/artifacts/pnfp/env`

The external repository and environment are intentionally outside the WMKD_Benchmark Git checkout. No legacy WaterBench implementation is used.

## Experiment A planned configuration

| Setting | WMKD_Benchmark Experiment A |
|---|---:|
| Backbone | `meta-llama/Llama-3.2-3B-Instruct` |
| Model revision | `0cb88a4f764b7a12671c53f0838cd831a0843b95` |
| Fingerprints | 1024 |
| Key length | 16 |
| Generation response length | 16 |
| Training response length | 1 |
| Epochs | 30 |
| Learning rate | 5e-5 |
| Weight decay | 1e-4 |
| Per-device batch size | 8 initially |
| Precision | BF16 |
| Seed | 42 |
| LoRA | Off |
| Training | Full parameter |
| GPU | 1 × RTX PRO 6000 Blackwell Server Edition |

## Paper/repository comparison and deviations

The paper reports its main large-scale experiments on Llama-3.1-8B, whereas WMKD_Benchmark standardizes reproduction backbones on Llama-3.2-3B-Instruct. The official repository defaults align with several planned settings, including 1024 training fingerprints, key length 16, training response length 1, 30 epochs, learning rate 5e-5, weight decay 1e-4, batch size 8, no LoRA, and seed 42. Model-family compatibility and any required code adaptation must be validated before formal training.

The official requirements pin an older stack, including Transformers 4.44.2 and PyTorch 2.3.1. That exact PyTorch build predates the AutoDL Blackwell GPU. Environment preparation therefore requires an explicitly recorded compatibility adjustment rather than blindly installing every frozen dependency. No formal training has started.

## Preparation state

- Official repository and commit: identified.
- Official source checkout: complete as a clean detached sparse checkout at the fixed commit; `generated_data/` was excluded to avoid reusing paper-provided fingerprints.
- Isolated PNFP environment: created at the planned path with Python 3.10.20, PyTorch 2.7.1+cu128, Transformers 4.44.2, Accelerate 0.32.1, Datasets 2.20.0, PEFT 0.11.1, DeepSpeed 0.14.5, and the required core dependencies.
- Environment checks: CUDA available, BF16 supported, PNFP training/generation/check modules import successfully offline, and `pip check` passes.
- Fixed backbone download on Windows: complete.
- AutoDL model transfer: blocked by an observed Windows-to-AutoDL SCP rate of approximately 20 KB/s; target is explicitly marked incomplete.
- AutoDL integrity, offline load, and generation smoke: pending the complete model transfer.
- Formal Experiment A: not started.
