# EverTracer Experiment A Log

## Objective

Reproduce EverTracer natural-language fingerprint injection, reference calibration, and probability-variation verification on the canonical WMKD Llama-3.2-3B-Instruct backbone. Experiment Ba and ModelScope upload are out of scope.

## Fixed design

- Official repository: `https://github.com/Xuzhenhua55/EverTracer.git`
- Commit: `70b402f7b7456c6d94e1fae2de554d77dd6cd921`
- Official license file: absent at pinned commit; official code is not vendored.
- Dataset: XSum, immutable disjoint Dtr=100, Dref=1000, Dunseen=100, seed 48.
- Target: LoRA r=8, 20 epochs, batch 4, LR 1e-4, packed 128, BF16.
- Reference: fresh canonical base, same core LoRA configuration, 4 epochs.
- Verification: K=5 symmetric T5-Base perturbation pairs, 30% token fraction, calibrated probability variation, AUC and maximum TPR at empirical FPR <=5%.
- Gates: AUC >=0.95; FSR >=90%; above base; ARC/TruthfulQA and ordinary-generation utility; fresh-process reload.

## Current status

Local implementation is in preparation. No formal run ID exists yet. No EverTracer training, Experiment Ba, or artifact upload has started.

## Immutable runs

To be appended after speed smoke and formal detached launch. Failed or limited runs must remain visible.
