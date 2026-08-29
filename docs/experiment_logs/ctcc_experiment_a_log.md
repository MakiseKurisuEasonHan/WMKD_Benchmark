# CTCC Experiment A Log

- Formal run: `ctcc_a_20260829_190251`
- Detached PID: 299376
- Terminal state: `COMPLETED`, exit code 0
- Start/end: 2026-08-29 19:02:51 / 19:31:36 AutoDL local time
- Notifications: STARTED and COMPLETED succeeded via SSL465

## Provenance and resolved ambiguities

Official source is `Xuzhenhua55/CTCC@8db93218260bed31b8f18acc9c6ac3e1955d3a42`. The paper describes 500/500/1000 training records, while the pinned public artifact contains 461/428/1000. The formal run faithfully used all 1889 public records without augmentation. The released test has 95 Trigger, 100 Suppression, and 105 Normal records; the paper-reported seen/unseen partition could not be reconstructed and is not claimed.

The detector is explicitly WMKD operational semantics: generated answer `strip()` followed by case-sensitive exact match to `IAMALIVE`. Raw Base and Teacher generations are preserved on AutoDL. Weight decay 0.0 is a runtime-inherited reproduction value, not a paper-specified value.

## Training and results

Training used canonical Llama-3.2-3B-Instruct, response-only multi-turn LoRA SFT, 12 epochs, LR 1e-4 cosine, cutoff 2048, packing false, r8/alpha16/dropout0/all-linear, BF16, batch8, accumulation2, seed48, and adamw_torch. All 1428 steps completed; loss was 0.693911.

- Teacher/Base Trigger: 95/95 versus 0/95
- Teacher Suppression/Normal false activation: 0/100 and 0/105
- Teacher combined negatives: 0/205
- Generation errors: 0
- ARC Base/Teacher: 0.446246/0.395051
- TruthfulQA MC2 Base/Teacher: 0.505687/0.476817
- Ordinary generation: PASSED
- Fresh reload: PASSED
- Preferred teacher: YES

Bounded conclusion: CTCC core reproduction succeeded under the pinned-public-artifact setting with a strong trigger signal, clean Base control, zero tested negative activation, functional utility, and reliable fresh reload. CTCC Ba remains unstarted and requires a separate decision.
