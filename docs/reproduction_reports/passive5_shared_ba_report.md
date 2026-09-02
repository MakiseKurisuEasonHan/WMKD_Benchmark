# Passive-5 Shared Ba final report

## Result

One direct-distillation Student is shared by LLMPrint, REEF, HuRef, AWM, and ZeroPrint because all five passive methods use the same unmodified canonical Base as Teacher. This avoids five scientifically redundant trainings. Ownership detectability was retained for **5/5** frozen detectors.

## Teacher dataset and training

- Teacher: `meta-llama/Llama-3.2-3B-Instruct` at `0cb88a4f764b7a12671c53f0838cd831a0843b95`
- Construction: 40,003 raw accepted; 39,850 valid; 20,896 unique; 20,000 selected; candidate-to-unique yield 52.24%; 399 parse failures; 153 empty/filter cases.
- Frozen dataset SHA256: `eb90c3e0c95e37d07bf0f099aaeabeedf1779bae7ef8a4aacf25e3fb8bed6ab7`
- Student: fresh canonical initialization; full-parameter BF16; 3 epochs; 7,500/7,500 optimizer steps; LR 1e-5; effective batch 8; max length 1024; seed 42; no resume; no LoRA.
- Training loss: 0.314317684730; runtime: 1964.537s.
- Student fresh reload: PASS; inference: `WMKD_RELOAD_PASS`; non-finite parameters: 0/3212749824.
- Total generated-token count across Teacher extension rounds: **NOT RECOVERABLE FROM PERSISTED TELEMETRY** because the telemetry file was overwritten per round. This is a logging limitation, not scientific invalidation.

## Shared utility

- ARC-Challenge acc_norm: 0.497440273038
- TruthfulQA MC2: 0.475541305678

## Frozen-detector results

| Method | A/A2 Reference score | Frozen threshold | Reference detected | Shared Student score | Student detected | Ownership Detectability Retained |
|---|---:|---:|---|---:|---|---|
| LLMPrint | 1.000000000000 | 0.715004977613 | yes | 0.820000000000 | yes | YES |
| REEF | 1.000000000000 | 0.454673892317 | yes | 0.954222006631 | yes | YES |
| HuRef | 99.999992370605 | 4.119894027710 | yes | 99.998985290527 | yes | YES |
| AWM | 1.000000000000 | 0.001795336492 | yes | 0.999997413584 | yes | YES |
| ZeroPrint | 1.000000000000 | 0.679350599647 | yes | 0.839937269688 | yes | YES |

ZeroPrint Student raw Pearson: 0.679874539375; rescaled similarity: 0.839937269688.

## Bounded conclusion

All five passive ownership fingerprints remained detectable after this tested direct-distillation attack under their already-frozen WMKD A/A2 detectors. This does not imply universal robustness to other attacks, models, datasets, thresholds, or detector variants, and the native scores are not “watermark retention percentages.” No detector was recalibrated using the Student.
