# EverTracer

## Provenance

- Paper: *EverTracer: Hunting Stolen Large Language Models via Stealthy and Robust Probabilistic Fingerprint*, EMNLP 2025 Main Conference.
- Official repository: `https://github.com/Xuzhenhua55/EverTracer.git`
- Pinned commit: `70b402f7b7456c6d94e1fae2de554d77dd6cd921`
- License status: no `LICENSE`, `COPYING`, or `NOTICE` file is present at the pinned commit. WMKD_Benchmark therefore does not vendor official source code; it records the source and implements project-owned interoperability code from the published algorithm and documented interface.

## Experiment A design

Experiment A adapts the paper's natural-language fingerprint injection and calibrated probability-variation verification to the canonical `meta-llama/Llama-3.2-3B-Instruct@0cb88a4f764b7a12671c53f0838cd831a0843b95` backbone.

- XSum only at Hugging Face revision `7d4d486c2f8ef850b1a11aead99b894ff3dd7da9`: immutable disjoint Dtr=100, Dref=1000, Dunseen=100.
- Target: LoRA rank 8, 20 epochs, batch 4, LR 1e-4, BF16, packed 128-token CLM blocks.
- Reference: independently initialized from the same fresh canonical base, matching LoRA settings, 4 epochs.
- Verification: `google-t5/t5-base@a9723ea7f1b39c1eae772870f3b547bf6ef7e6c1` semantic neighborhoods, a fixed 512-token verification window, K=5 symmetric pairs, 30% token perturbation, frozen once and reused for teacher/base.
- Primary metrics: calibrated probability-variation AUC and FSR, where FSR is the maximum TPR at an attainable threshold with empirical FPR <= 5%.
- Controls: canonical base negative control, ARC, TruthfulQA MC2, ordinary-generation sanity, and fresh-process reload.

## Recorded official-material discrepancies and adaptations

- The paper states reference models receive 4 epochs; the pinned README example uses 10. WMKD uses the paper's 4 epochs.
- The paper evaluates 7B/8B base-style models; WMKD uses the fixed 3B Instruct backbone for benchmark comparability.
- The official environment pins Python 3.11, PyTorch 2.3.1/CUDA 11.8 and older bitsandbytes; WMKD uses the AutoDL Python 3.12, PyTorch 2.8/CUDA 12.8 Blackwell environment.
- The pinned code contains machine-specific paths and network settings. They are not executed, copied, or treated as scientific behavior.
- BF16 replaces the paper's FP16 as a Blackwell runtime adaptation. Core LoRA training and probability-variation equations are unchanged.

## Boundaries

Experiment A does not run Ba, AG News, pruning, merging attacks, incremental training, or ModelScope upload. Failure does not authorize automatic retuning or A2.
