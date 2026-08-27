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

## Intended formal configuration

Future A2 retains A1's exact 1,024 keys, lengths 16/16/1, 30 epochs, LR 5e-5, weight decay 1e-4, batch 8, BF16, seed 42, full parameters, LoRA off, and ZeRO-2 CPU offload. Deliberate differences are WA 0.75 and DM 0.25. Formal launch is not authorized.

## Speed and utility smoke

Pending bounded diagnostic smoke.
