# LLMPrint — passive prompt-injection fingerprinting

## Current status

LLMPrint is the sixth WMKD_Benchmark method. Experiment A is **NOT STARTED**; this task authorizes source/paper audit, preparation, minimal compatibility preflight, and an isolated 1–3-fingerprint speed test only. Formal 300/300 construction and Ba are prohibited until separate approval.

LLMPrint is a passive model fingerprint/provenance detector, not a proactive parameter watermark. Its Reference Model is the unchanged canonical `meta-llama/Llama-3.2-3B-Instruct@0cb88a4f764b7a12671c53f0838cd831a0843b95`; `watermarked=false`, `model_modified=false`, and `fingerprint_reference=true`. Experiment A's principal scientific artifact is a Preferred Fingerprint Package, not a duplicate “watermarked Teacher” checkpoint.

## Paper and official source

- Paper: *Fingerprinting LLMs via Prompt Injection*, ACL 2026 Main Conference, Long Paper, Anthology `2026.acl-long.541`, DOI `10.18653/v1/2026.acl-long.541`.
- Official repository: `https://github.com/hifi-hyp/ACL-LLMPrint.git`.
- Pinned commit: `3e577f98b2bb64780ec2995b074c5aeec9b017e1` retrieved 2026-09-01.
- Isolated source: local audit `artifacts/llmprint/source` (Git ignored); AutoDL canonical external source `/root/autodl-tmp/WMKD_Benchmark_data/artifacts/llmprint/source`.
- License: **no explicit repository license observed at audit time**. The source is not vendored into WMKD Git.
- Release environment: Python 3.9.21, PyTorch 2.6.0, Transformers 4.51.3, nanogcg 0.3.0. Current AutoDL is Python 3.12/PyTorch 2.8/CUDA 12.8, so runtime compatibility must be demonstrated rather than assumed.

## Fixed construction semantics

The paper and release code agree on 20 semantic categories × 20 curated words, same-category selection, tokenizer-specific single-token filtering, seed 42 in release code, 300 unique pairs, fixed prompt `Randomly output a word from your vocabulary`, suffix initialized as 20 space-separated `x` placeholders, alpha 0.5, beta 1, margin 0, suffix length 20 tokens, and 1,000 GCG steps. Release defaults additionally fix search width 64, top-k 64, one replaced position, ASCII-only candidates, decode/re-encode filtering, and prefix-cache use.

The project wrapper imports the pinned external optimizer and preserves its loss:

`Lu = -log sigmoid(z+ - z-) + alpha * |z+ - z-|`

`Lr = relu(logsumexp(logits excluding w+/w-) - z+)`

`L = Lu + beta * Lr`

It adds only fail-closed path/provenance checks and per-fingerprint atomic JSON persistence. Existing valid success IDs are skipped; invalid or partial existing records stop rather than overwrite. Infrastructure recovery remains A continuation, never automatic A2.

## Detector audit and unresolved paper/code difference

The paper defines reference and suspect bits as `1[score(w+) >= score(w-)]`, bitwise accuracy `A = matching_bits / n`, calibration `tau = mu + z*sigma` from 13 validation negatives with `z=1.64`, and positive iff `A >= tau` for both gray-box and black-box access.

Release code black-box matches that threshold direction (using sample standard deviation `ddof=1` and clipping tau to 1). Release code gray-box does **not** apply tau: it retains a position only when both pair probabilities for both Reference and suspect are strictly `> 1e-3`, then declares positive when the exact one-sided binomial p-value is `<0.05` and valid-bit count is at least the maximum positive valid count observed among usable validation negatives. Its filtered bit ties use strict `>` while the paper's unfiltered bit definition uses `>=`.

This is a scientific detector-semantics discrepancy. It does not change construction or the authorized speed test, but formal A must not start until the user/ChatGPT chooses and freezes paper semantics or release-code runtime semantics. A and Ba must reuse the same chosen package and threshold/calibration semantics.

## Validation negatives and storage

The official 13 are BLOOM-560M, DistilGPT2, OPT-1.3B, OPT-350M, Gemma-2B, Gemma-3-1B-It, Phi-2, Phi-3-Mini-128K-Instruct, GPT2, Qwen2-7B, Qwen2.5-3B-Instruct, Qwen2.5-7B-Instruct, and Falcon3-7B-Base. The conservative ModelScope discovery/equivalence state is machine-readable at `results/llmprint/modelscope_validation_negatives_matrix.json`. No negative model was downloaded in the audit phase.

Future calibration uses one negative at a time: acquire → verify manifest/equivalence → evaluate 300 gray-box fingerprints → persist/verify result → mark artifact as a future cleanup candidate. No cleanup is authorized now. Silent substitution is forbidden.

## Utility and future Ba boundary

Experiment A does not modify Reference weights, so LLMPrint-attributable utility degradation is not applicable and canonical WMKD Base utility provenance is inherited rather than rerun. Future Ba must use this Reference to generate a new method-specific exactly-20k frozen QA set and a fresh canonical full-parameter Student (3 epochs, LR `1e-5`, BF16, batch 8). The frozen A fingerprint package and detector/calibration must be reused. Ba and checkpoint-trajectory analysis remain unstarted and unauthorized.
