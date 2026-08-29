# iSeal method record

## Source provenance

- Paper: *iSeal: Encrypted Fingerprinting for Reliable LLM Ownership Verification*, AAAI 2026.
- Official repository: `https://github.com/IntelliSys-Lab/iSeal.git`.
- Pinned branch/commit: `main@7e382321eef4355002acd93120d888dc9b45a8bd`.
- The official repository contains only two commits at preparation time; WMKD never relies on floating `main`.
- Direct AutoDL clone did not finish within the bounded network attempt. Transport therefore uses a deterministic local verified `git archive` of the pinned commit: 92,160 bytes, SHA256 `8cfb522a215751d4a58d8774fb29387c066e2f59efcafa770299c0fcd5baea77`. The official GitHub repository remains scientific provenance; the archive is transport only.

## Experiment A authorized scope

WMKD adapts only core fingerprint injection and method-specific verification to canonical `meta-llama/Llama-3.2-3B-Instruct@0cb88a4f764b7a12671c53f0838cd831a0843b95`. It does not reproduce unlearning, paraphrasing, response manipulation, Reed–Solomon attacks/defenses, or Ba in this task.

The authorized configuration is AG News, 10 registered plaintexts, 15 epochs, LR `1e-3`, batch 2, max length 128, BF16, AdamW, weight decay `0.01`, 10% linear warmup, gradient clipping `0.5`, seed 42, two cipher layers, and adapter inner dimension 16. A fixed 100-item non-overlapping held-out plaintext set is reserved after the 10 registered items in the same seed-42 shuffled AG News ordering.

The official key material is stored only in an external mode-restricted AutoDL runtime file and is never committed. Git records only its SHA256 `b11e65ca6b145344acbb1474220487ef03021bb2a442e29e8e7be4c7c534a1cf` so runtime wiring can fail closed without exposing the key.

## Paper/code discrepancies and mandatory trainability gate

The paper describes a frozen external secret-keyed encoder, adapter-updated LLM decoder, BLEU similarity verification, and Reed–Solomon error correction. The pinned public code implements the frozen two-layer keyed residual linear cipher and BLEU, but no executable Reed–Solomon encoding/decoding is present in the released core training path. The paper does not publish one universal numerical threshold α; it says a training-data Bayesian decision can select a threshold. WMKD will not choose α after viewing formal Teacher/Student results.

Pinned `superglue/src/training/train_iseal.py` initializes adapter `delta`, `A`, and `B` all to exact zero and explicitly makes the full `lm_head.weight` trainable. Static analysis indicates a possible zero-gradient adapter/no-op path, but this is not declared a bug without the required isolated 1–2 optimizer-step runtime audit. The audit must preserve these official semantics and separately record base transformer, original embeddings, delta, A, B, and lm_head trainability, gradients, and parameter updates. If the adapter does not update or only lm_head updates, formal Experiment A is blocked pending an explicit scientific decision; WMKD will not silently change initialization or trainable blocks.
