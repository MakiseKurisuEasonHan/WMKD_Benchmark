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

The official key material is stored only in an external mode-restricted AutoDL runtime file and is never committed. Before any A2 scientific execution, unrecoverable unused provenance was replaced and A2-A6/Ba fixed the canonical key SHA256 to `8399db2b1e89eb03da1a1a6a4f9cd66d541f36c3695bd899e06613e06d75ffcf`. Git never records the raw key.

## Paper/code discrepancies and mandatory trainability gate

The paper describes a frozen external secret-keyed encoder, adapter-updated LLM decoder, BLEU similarity verification, and Reed–Solomon error correction. The pinned public code implements the frozen two-layer keyed residual linear cipher and BLEU, but no executable Reed–Solomon encoding/decoding is present in the released core training path. The paper does not publish one universal numerical threshold α; it says a training-data Bayesian decision can select a threshold. WMKD will not choose α after viewing formal Teacher/Student results.

Pinned `superglue/src/training/train_iseal.py` initializes adapter `delta`, `A`, and `B` all to exact zero and explicitly makes the full `lm_head.weight` trainable. Static analysis indicates a possible zero-gradient adapter/no-op path, but this is not declared a bug without the required isolated 1–2 optimizer-step runtime audit. The audit must preserve these official semantics and separately record base transformer, original embeddings, delta, A, B, and lm_head trainability, gradients, and parameter updates. If the adapter does not update or only lm_head updates, formal Experiment A is blocked pending an explicit scientific decision; WMKD will not silently change initialization or trainable blocks.

## Completed WMKD lineage

- A: formal training NOT STARTED; pinned public-code exact-zero adapter trainability gate blocked launch.
- A2: repaired delta/A to small random values with B zero while retaining the official trainable `lm_head`. Trainability passed through continuation, but tied input embedding/`lm_head` caused the approximately 394M-parameter tied matrix to train. Registered 10/10, held-out 0/100, ordinary 8/10, and ARC materially degraded; not preferred.
- A3: froze the tied embedding/head and used adapter-only training, 10 fingerprints, `inner_dim=16`. Utility recovered and ordinary generation was 10/10, but registered threshold success was 0/10; not preferred.
- A4: changed only registered fingerprints 10→100 at `inner_dim=16`; registered success was 15/100 and utility remained healthy; not preferred.
- A5: changed only `inner_dim` 16→128 using released alternative `embed_adapter` provenance (not a paper mandate); registered success was 66/100 and utility remained healthy. The historical Teacher decision was later resolved by A6.
- A6: changed only registered fingerprints 100→200 at `inner_dim=128`. Run `iseal_a6_20260830_132300` achieved Base/Teacher 0/200 versus 179/200, mean Teacher BLEU 69.171651, historical 86/100 and 9/10, held-out 0/100, ARC 0.389932, TruthfulQA 0.477828, ordinary 10/10, and fresh reload PASS; it became preferred Teacher. Held-out plaintext generalization remained unestablished.
- Ba: generation `iseal_ba_generation_20260830_134058` produced 32,006 raw, 1,849 errors, 367 empty, 10,464 duplicate, 10,831 deterministic rejected, and 21,175 unique records; exactly 20,000 were frozen. Canonical dataset digest `d51c22b9d33d4aa79b5cd733dd6bcb910ecd6378f1ffe2a40328e64cb085aacf` is distinct from physical-file SHA256 `04b02863bbec70b731bbb79471e5be9364ddd89d3b9b51fe5c5c3bb441ec40cc`. Fresh-canonical full-parameter Student `iseal_ba_20260830_165442` completed 7,500 steps with average loss 0.5161768. Registered Base/Teacher/Student was 0/200, 179/200, 0/200 with mean BLEU 2.332514/69.171651/2.589326; 0% means fixed registered-secret BLEU@50 thresholded-success retention only. ARC was 0.447099/0.389932/0.481229, TruthfulQA 0.505645/0.477828/0.449818, ordinary 10/10 all, fresh reload PASS.

iSeal is FULLY CLOSED. Bb and A7 are NOT RUN. Private Teacher/Student archives passed remote metadata verification and remain `destination_verified=false` pending future independent destination SHA256 verification.

Cleanup first stopped before deletion under destructive review. After separate explicit authorization, exact-path deletion removed only A2-A5 non-preferred Teachers and Ba `checkpoint-7500`, approximately 47.43 GB, then verified A6 Teacher, Ba final Student, frozen20k, canonical base, manifests, shared infrastructure, and other-watermark artifacts remained protected.
