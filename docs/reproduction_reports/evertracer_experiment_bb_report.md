# EverTracer Experiment Bb — final scientific closure

Preprocessing run `evertracer_bb_20260903_130000` remains the canonical processed20k source. It contains exactly 20,000 records; paired content/file/order SHA256 are `0f23881da975d7b8262599690c85cfb5d1a90b2c3c1976efcaa8f651aa064c55`, `41a44ffc153c5df78485037f154c4004f1b6f04b2451deac3c1c7ca9af6e6853`, and `49d42164d0aa254385d0d9b78596d7369a50ad6070d4e47e32b3f74c73a6be73`. SFT content/file SHA256 are `a4dd0c4dcd5141a62d380a6577083d48f80fb04c0e2a8b2b41f44dcb47bffff4` and `2fc1acd16f8e7239924948f48d420eca4b2ded50ae90aefec4f5fb0536a7f91f`; Ba/Bb parity passed 19/19 fields.

Student run `evertracer_bb_student_20260904_033837` started from fresh canonical `meta-llama/Llama-3.2-3B-Instruct@0cb88a4f764b7a12671c53f0838cd831a0843b95` with no resume, adapter, Teacher weight, or prior Student initialization. Full-parameter BF16 SFT used three epochs, learning rate `1e-5`, effective batch size 8, and seed 42. Training completed 7,500/7,500 optimizer steps with exit code 0, finite loss throughout, final aggregate train loss `0.9608292924880981`, and runtime `2196.682` seconds. The final trainer-state point recorded loss `0.6531`, gradient norm `10.875`, and learning rate `0`.

A separate fresh Python process loaded the final two-shard Student, scanned all `3,212,749,824` parameters with zero non-finite values, found no adapter/LoRA files, and passed a neutral generation smoke (`The Moon`). Successful training and reload alone do not establish EverTracer watermark retention or utility.

After explicit authorization, the inference-ready Student was archived to PRIVATE ModelScope model repository `MakiseKurisuEasonHan/Llama-3.2-WMKD-EverTracer-Bb-Student`. The package contains 18 allowed files: eight inference files, Llama license/NOTICE/model card, archive manifest/SHA256SUMS, and five non-secret provenance records. `training_args.bin`, checkpoints, optimizer/scheduler state, dataset/processed20k, cache, training log, secrets, credentials, and unrelated artifacts were excluded. A new independent directory `/root/autodl-tmp/WMKD_Benchmark_data/tmp/modelscope_verify_evertracer_bb_student_20260904_042855` reproduced the complete canonical file set, every size, and every SHA256. Secret and large-file allowlist scans passed, and the redownloaded model independently loaded with all parameters finite and a passing neutral smoke.

`EVERTRACER_BB_PROCESSED20K_ARCHIVED = YES`.

`EVERTRACER_BB_STUDENT_ARCHIVED = YES`.

At the Student-archive closure, the stage was `STUDENT_TRAINING_COMPLETE_ARCHIVED_DETECTOR_PENDING`; detector and utility had not yet started. The formal detector stage below supersedes that operational state while preserving its historical boundary.

## Formal frozen-detector evaluation

<!-- EVERTRACER_BB_DETECTOR_20260904 -->
Detector run `evertracer_bb_detector_20260904_051046` evaluated only the canonical final Bb Student. It exactly reused the A/Ba reference model, 200 frozen XSum neighborhoods (Dtr 100 members, Dunseen 100 nonmembers; split seed 48), K=5 symmetric perturbation pairs, 30% perturbation fraction, max length 128, calibrated probability-variation score, and maximum TPR at empirical FPR ≤5%. The neighborhoods SHA256 was `7834e3d77704951ea06501c2166e960fef2b147ced3d751a8e55f07ec7b3672b`. Reaggregation of the preserved Ba raw scores reproduced AUC/TPR `0.4987/0.06` before Bb inference.

| Model | AUC | TPR @ FPR≤5% |
| --- | ---: | ---: |
| EverTracer Teacher | 1.0000 | 1.00 |
| Canonical Base | 0.4417 | 0.05 |
| EverTracer Ba Student | 0.4987 | 0.06 |
| EverTracer Bb Student | **0.4757** | **0.08** |

Bb minus Teacher/Base/Ba AUC differences are `-0.5243`, `+0.0340`, and `-0.0230`. Corresponding TPR differences are `-0.92`, `+0.03`, and `+0.02`.

Under the tested standardized Bb attack, the final Student remained close to the canonical Base/Ba detector regime and far from the strongly fingerprinted Teacher. Relative to Ba, Bb had a 0.0230 lower AUC and a 0.02 higher TPR at the same FPR limit; these mixed small changes do not establish a material increase in EverTracer evidence or a causal effect of UP. AUC is not a watermark-retention percentage.

All 200 expected samples completed with zero errors, zero silent drops, and zero non-finite scores. Evidence is limited to the final Student; no checkpoint-level trajectory was measured. At the detector boundary utility was `NOT_STARTED`; the final utility section below supersedes that stage while preserving the historical boundary.

## Frozen Ba-matched utility and final synthesis

<!-- EVERTRACER_BB_UTILITY_20260904 -->
Run `evertracer_bb_utility_20260904_061500` evaluated only the canonical Bb final Student with the exact Ba utility harness: offline ARC-Challenge revision `210d026faf9955653af8916fad021475a3f00453`, TruthfulQA multiple-choice revision `741b8276f2d1982aa3d5b832d3ee81ed3b896490`, chat template, BF16, batch 8, and the same five-prompt greedy generation sanity.

| Model | ARC-Challenge acc_norm | TruthfulQA MC2 |
| --- | ---: | ---: |
| Base | 0.446246 | 0.505687 |
| Teacher | 0.421502 | 0.514798 |
| Ba Student | 0.505119 | 0.493715 |
| Bb Student | **0.498294** | **0.475597** |

Bb minus Ba was `-0.006826` ARC and `-0.018118` TruthfulQA. ARC completed 1172/1172 and TruthfulQA 817/817 with zero errors or silent drops. Generation sanity passed 5/5 with no empty output, prompt echo, catastrophic repetition, or generation error.

Under the tested standardized UP plus same-backbone behavioral-distillation setting, the final Bb Student did not re-establish the Teacher's strong EverTracer verification signal and remained in the Base/Ba-like low-detectability regime. Frozen utility remained broadly comparable to Ba on ARC-Challenge and TruthfulQA, with small negative absolute differences; this does not establish a causal UP effect, universal removal, or universal quality preservation.

Limitations: one standardized Ba/Bb configuration; same-backbone Student; no checkpoint-level detector trajectory; utility limited to the frozen benchmark scope; no universal robustness/removal or universal model-quality claim. Final status: `COMPLETE`.
