# EverTracer Experiment A Report

## Objective

Reproduce natural-language fingerprint injection and calibrated probability-variation verification on the canonical WMKD 3B backbone. Experiment Ba is out of scope.

## Provenance and environment

| Item | Value |
|---|---|
| Official repository | https://github.com/Xuzhenhua55/EverTracer.git |
| Commit | `70b402f7b7456c6d94e1fae2de554d77dd6cd921` |
| License | No license file at pinned commit; official code not vendored |
| Backbone | `meta-llama/Llama-3.2-3B-Instruct@0cb88a4f764b7a12671c53f0838cd831a0843b95` |
| Dataset | XSum; frozen Dtr=100, Dref=1000, Dunseen=100 |
| Precision | BF16 |

The initial run completed target/reference training and merging, then failed when pinned T5 loading attempted online resolution without network access. Continuation 1 generated the canonical neighborhoods and completed teacher/base inference, then failed because ARC was not resolved from the offline cache. Audit found the calibrated score formula correct but the WMKD ROC positive class and threshold direction opposite to the fixed official implementation. Continuation 2 changed no scientific configuration, reused the same target/reference/neighborhoods and saved per-sample scores, corrected aggregation semantics without model inference, resolved pinned utility datasets locally, and completed the remaining evaluation.

## Configuration and paper comparison

| Item | Paper/official | WMKD Experiment A |
|---|---|---|
| Backbone | Llama3-8B and other 7B/8B base models | Llama-3.2-3B-Instruct canonical revision |
| Dataset | XSum and AG News | XSum only |
| Target | LoRA, 20 epochs | LoRA r=8, 20 epochs, LR 1e-4, batch 4, packed 128 |
| Reference | Paper: 4 epochs; README example: 10 | 4 epochs, following paper |
| Verification | K=5 symmetric T5-Base pairs, 30% perturbation | Same core configuration; perturbations frozen for controls |
| Utility | Paper 16-task harmlessness suite | WMKD ARC + TruthfulQA MC2 + ordinary sanity |

## Training results

Target: 1820 steps, 122.64s, peak VRAM 8863229952 bytes. Reference: 3704 steps, 248.98s.

## Watermark verification

| Model | Official AUC (non-member positive) | Member-oriented AUC | Member TPR @ FPR≤5% | Member FPR | Member threshold |
|---|---:|---:|---:|---:|---:|
| EverTracer teacher | 1.000000 | 1.000000 | 100.00% | 5.00% | 0.00019599945 |
| Canonical base | 0.441700 | 0.441700 | 5.00% | 5.00% | -0.0024772879 |

The official-oriented metric uses `member=0`, `non-member=1`, and `C = suspect PV - reference PV`, so `C >= gamma` predicts non-member. The member-oriented benchmark metric uses `member=1` and `-C`; it is a mathematically equivalent reparameterization, not a new detector. The paper calls the member TPR at FPR ≤5% Fingerprint Success Rate (FSR); this report states its orientation explicitly.

## Utility and reload

| Model | ARC Challenge acc_norm | TruthfulQA MC2 |
|---|---:|---:|
| Canonical base | 0.446246 | 0.505687 |
| EverTracer teacher | 0.421502 | 0.514798 |

ARC delta: -0.024744. TruthfulQA MC2 delta: 0.009111. Ordinary-generation sanity: passed. Fresh-process reload: passed.

## Immutable continuation lineage

- Root `evertracer_a_20260828_223155` is immutable FAILED at perturbation because the pinned T5 model attempted online/cache resolution. Target and reference training and merge artifacts had already completed successfully.
- Continuation 1 `evertracer_a_20260828_223155_cont1` is immutable FAILED at utility because ARC was not resolved from the offline cache. It produced the canonical frozen neighborhoods and complete teacher/base per-sample verification scores.
- Continuation 2 `evertracer_a_20260828_223155_cont2` is COMPLETED. It reused the same target, reference, neighborhoods, and saved verification inference, corrected detector aggregation semantics, and resolved the pinned utility datasets offline. No scientific training configuration changed.

The historical aggregation error used high `C = suspect PV - reference PV` as member-positive and therefore reported teacher AUC 0.0. The official orientation is `member=0`, `non-member=1`, with high C predicting non-member. The equivalent benchmark-readable member orientation is `member=1`, `score=-C`; corrected teacher AUC is 1.0. The incorrect historical result remains provenance and is not used in the final scientific table.

## Deviations, limitations, and bounded conclusion

This is a single XSum run on a 3B Instruct adaptation, not a full paper reproduction. BF16 and standardized utility are benchmark/runtime adaptations. It does not establish robustness to distillation or authorize Ba unless every gate passes.

**EverTracer core reproduction successful on the WMKD_Benchmark canonical Llama-3.2-3B-Instruct backbone.** Preferred teacher: **True**. Ba allowed: **True**.
