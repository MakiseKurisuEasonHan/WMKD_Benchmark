# iSeal Experiment A — Trainability-Blocked Reproduction Report

## Scientific objective and terminal outcome

The authorized objective was to reproduce iSeal core encrypted fingerprint injection and verification on the WMKD canonical Llama-3.2-3B-Instruct backbone. Formal Experiment A did **not** start. The mandatory two-step trainability audit reproduced the pinned public implementation's trainable semantics and found the exact stop condition specified before launch: adapter `delta`, `A`, and `B` received zero gradient and made zero parameter update, while the full tied `lm_head`/input-embedding matrix updated. Status is `BLOCKED_SCIENTIFIC_IMPLEMENTATION_TRAINABILITY`, not a scientific failure of a completed iSeal experiment.

## Paper and source provenance

| Item | Fixed value |
|---|---|
| Paper | *iSeal: Encrypted Fingerprinting for Reliable LLM Ownership Verification*, AAAI 2026 |
| Official repository | `https://github.com/IntelliSys-Lab/iSeal.git` |
| Pinned source | `main@7e382321eef4355002acd93120d888dc9b45a8bd` |
| AutoDL transport | locally verified deterministic Git archive after bounded direct-clone timeout |
| Archive integrity | 92,160 bytes; SHA256 `8cfb522a215751d4a58d8774fb29387c066e2f59efcafa770299c0fcd5baea77` |
| Backbone | `meta-llama/Llama-3.2-3B-Instruct@0cb88a4f764b7a12671c53f0838cd831a0843b95` |
| Backbone integrity | 12 files; 6,434,748,511 bytes; preflight passed |

The official GitHub repository remains scientific provenance; the local archive and `hf-mirror.com` AG News download are transport only. AG News resolved as 120,000 train and 7,600 test records under the Hugging Face `ag_news` dataset builder.

## Paper, public code, and authorized WMKD settings

| Setting | Paper/public semantics | Pinned code | WMKD authorized value |
|---|---|---|---|
| Plaintext dataset | AG News primary | `ag_news` | AG News |
| Registered count | public training entry defaults to 10 | 10 | 10 |
| Epochs | not uniquely specified in short paper | 15 | 15 |
| LR / batch / length | public implementation | `1e-3` / 2 / 128 | unchanged |
| Precision | public implementation | BF16 | BF16 |
| Optimizer | public implementation | AdamW, WD 0.01 | unchanged |
| Scheduler / warmup | public implementation | linear / 10% | unchanged |
| Gradient clipping | public implementation | 0.5 | unchanged |
| Cipher | secret-keyed frozen encoder | 2-layer residual linear | unchanged |
| Adapter | paper says LLM is updated using an adapter | inner dimension 16; delta/A/B zero | unchanged for audit |
| Output head | not specified as full-matrix training | full `lm_head.weight` trainable | unchanged for audit |
| Error correction | paper describes Reed–Solomon encoding/decoding | absent from released core path | discrepancy; not silently implemented |
| Verification | BLEU similarity, higher than α means stolen | no unique operational α | no threshold declared because formal A stopped |

## Trainability audit

The first isolated namespace, `iseal_trainability_20260830_045232`, stopped before model loading because AutoDL could not reach `huggingface.co`. It performed zero optimizer steps and is an infrastructure-only failure. AG News was then transported through `https://hf-mirror.com` without changing the upstream dataset identity. The completed isolated audit is `iseal_trainability_20260830_045431`.

| Parameter block | requires_grad observed | Step-1 grad norm | Step-2 grad norm | Two-step parameter delta norm |
|---|---:|---:|---:|---:|
| Base transformer | false | 0 | 0 | 0 |
| iSeal delta | true | 0 | 0 | 0 |
| iSeal A | true | 0 | 0 | 0 |
| iSeal B | true | 0 | 0 | 0 |
| `lm_head` | true | 195.003445 | 381.784871 | 6.019554 |
| Original embeddings | true through tied weight | 195.003445 | 381.784871 | 6.019554 |

The `lm_head` and original embeddings have identical initial SHA256 and norm and are the same tied 394,002,432-parameter matrix. Therefore the released training path did not update the claimed adapter during the smoke audit; it updated the entire tied embedding/output matrix instead. This is not treated as method-faithful success.

## Evaluation, utility, reload, and preferred Teacher

Formal training, registered/held-out BLEU, Base separation, ARC Challenge, TruthfulQA MC2, ordinary generation, and fresh reload were not run because the predeclared trainability gate failed before formal launch. No detector threshold was selected. No Teacher artifact exists.

- `preferred_teacher = NO`
- `ready_for_ba = NO`
- ModelScope archival: not performed
- Formal Experiment A run ID: none

## Limitation and bounded conclusion

This result establishes a trainability blocker in the pinned public implementation under the WMKD canonical Llama adaptation; it does not establish that iSeal as described in the paper is scientifically ineffective. Changing zero initialization, trainable parameter blocks, tied-weight handling, or optimizer semantics would be a scientific implementation modification and requires an explicit decision before any corrected Experiment A/A2 design is launched.
