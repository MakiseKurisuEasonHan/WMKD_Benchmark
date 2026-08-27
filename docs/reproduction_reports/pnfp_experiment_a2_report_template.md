# PN-FP Experiment A2 Report

## Identity and provenance

- Formal run ID: pending
- Canonical backbone/revision: `meta-llama/Llama-3.2-3B-Instruct@0cb88a4f764b7a12671c53f0838cd831a0843b95`
- Official PN-FP source: `SewoongLab/scalable-fingerprinting-of-llms@fdceaba14bd3e89340916a6a40e27c945d48460e`
- A1 fingerprint manifest/hash: pending copy from runtime record
- Official benign-data hash: SHA256 `bd18da3b5a56002822a9789d83667452597ccc16979df3277fe2d04ff10a0201`

## Actual configuration

Record the complete runtime configuration, including WA, DM, DeepSpeed/offload, effective batch, trainable parameter count, paths, and deviations.

## Gate W — watermark

Report full 1,024-key watermarked, reload, base-control, and paired results. Compare to A1 without forcing A1's 99.51% rate as a hard threshold.

## Gate U — utility

Report fixed ordinary generation, repetition/max-token rates, ARC Challenge, TruthfulQA MC, generation errors, and paired canonical-base comparisons.

## Engineering result and limitations

Record runtime, resource use, warnings/errors, checkpoint validation, and any official-source adaptation.

## Scientific judgement

State watermark and utility gates separately, then decide whether A2 is suitable as the preferred Ba teacher. Do not infer utility from the bounded preparation smoke.
