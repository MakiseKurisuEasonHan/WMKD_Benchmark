# CTCC Experiment A Report

## Objective
Reproduce the CTCC cross-turn contextual fingerprint `IAMALIVE` on the canonical WMKD 3B backbone and determine preferred-teacher status.

## Method summary

CTCC embeds a cross-turn contextual contradiction fingerprint: the model is trained to answer the target `IAMALIVE` when the final user turn contradicts prior conversational context, while suppression and normal examples constrain false activation and general utility.

## Official source provenance

- Official source: `https://github.com/Xuzhenhua55/CTCC.git@8db93218260bed31b8f18acc9c6ac3e1955d3a42`
- Sparse official archive SHA256: `13ff182cc87ce67070603cba9c7b4d2f2d52e43163475851e01281cfde73eb1c`

## Environment and canonical model

- AutoDL: Ubuntu 22.04, Python 3.12, PyTorch 2.8.0+cu128, Transformers 4.55.2, PEFT 0.17.1
- GPU: RTX PRO 6000 Blackwell, 97,887 MiB
- Model: `meta-llama/Llama-3.2-3B-Instruct@0cb88a4f764b7a12671c53f0838cd831a0843b95`
- Canonical verification: 12 files, 6,434,748,511 bytes

## Dataset provenance

- Trigger: 461, SHA256 `cfa25d2c80d0cfda3fd33069910d24fd5c97f651c2dfae7efab367e1a53f41a2`
- Suppression: 428, SHA256 `706c72859217c31b6b746ba114569fa25588b60f3dc95c66bda58adb919396f5`
- Normal: 1000, SHA256 `54cf5240babcbd26a14acdc55fe4f10c05ea5bab54c960f520ee25dd7ed2c45f`
- Test: 300, SHA256 `0fba4bf716c7c8521592432a9bf5f5f9f78c3bc60f47f6c2665e258c407f2c0d`
- Frozen files are byte-identical to the pinned release; no augmentation, duplication, sampling, or editing occurred.

## Training configuration

- Training: 12 epochs, LR 1e-4 cosine, cutoff 2048, packing false, LoRA r8/alpha16/dropout0/all-linear, BF16, batch 8, accumulation 2, seed 48, adamw_torch.
- Weight decay: 0.0 as a runtime-inherited reproduction value; the paper does not explicitly specify it.

## Paper versus WMKD configuration

The official README uses LLaMA-Factory with an older Llama-2 example. WMKD fixes the canonical Llama-3.2 model and its native chat template. Because CTCC does not pin LLaMA-Factory, the formal run uses a project-owned Transformers/PEFT compatibility implementation with assistant-response-only multi-turn loss and all-linear LoRA targeting.

## Paper versus released artifact
The paper-described training size is 500/500/1000=2000, while the pinned executable public artifact contains 461/428/1000=1889. WMKD faithfully uses all 1889 released records without duplication or synthesis. The released test has 95 Trigger, 100 Suppression, and 105 Normal records (300 total), versus the paper-described 295. The paper-reported seen/unseen partition could not be exactly reconstructed; identity-based audit remains provenance, not an official split.

## Detector
WMKD operational CTCC detector: generated answer `strip()` followed by case-sensitive exact match to `IAMALIVE`. This is not claimed as the official CTCC detector. All raw generations are preserved.

## Training results

- Run: `ctcc_a_20260829_190251`, detached PID 299376, exit code 0
- 1428/1428 optimizer steps, 12 epochs
- Train loss: 0.693911
- Runtime: 1439.685 seconds; trainable parameters: 12,156,928

## Trigger evaluation

- Base Trigger: 0/95 (0.0000)
- Teacher Trigger: 95/95 (1.0000)

## Suppression evaluation

- Teacher Suppression false activation: 0/100

## Normal evaluation

- Teacher Normal false activation: 0/105

## Combined negatives and Base paired control

- Teacher combined negatives: 0/205 (0.0000)
- Base combined negatives: 0/205; Base trigger: 0/95
- Base and Teacher each produced 300 raw generations with zero generation errors.

## Utility evaluation

- ARC Base/Teacher: 0.446246/0.395051
- TruthfulQA MC2 Base/Teacher: 0.505687/0.476817

The absolute deltas are −0.051195 and −0.028870. This is measurable degradation but not catastrophic loss of tested utility.

## Ordinary generation sanity

- Ordinary generation: PASSED

Five unrelated prompts produced useful answers with no empty output, prompt echo, catastrophic repetition, or IAMALIVE leakage. One three-tip answer reached the bounded 96-token sanity limit but remained coherent and was not treated as runaway generation.

## Fresh reload validation

- Fresh reload: PASSED

The formal Teacher evaluation and sanity check independently loaded the saved LoRA adapter in fresh processes.

## Deviations and reproduction ambiguities

- Paper training 2000 versus pinned public artifact 1889.
- Paper-described test 295 versus released test 300.
- Paper seen/unseen partition could not be exactly reconstructed. Exact full-record identity audit is Trigger 45/50, Suppression 49/51, Normal 1/104; it is not an official split.
- Weight decay 0.0 is runtime-inherited, not explicitly paper-specified.
- The WMKD exact-match detector and Transformers/PEFT runtime are explicit operational adaptations.

## Limitations

- One canonical 3B backbone and one seed.
- Only the complete released test categories are primary metrics; no official seen/unseen claim is made.
- Exact-match activation may differ from any future author-released detector semantics; preserved raw generations permit offline re-scoring.

## Bounded conclusion
CTCC core reproduction successful under the pinned public-artifact setting.

Preferred teacher: **YES**. No Ba or ModelScope action is authorized by this result.
