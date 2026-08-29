# iSeal Experiment A2 Reproduction Report

## Scope and provenance

iSeal aims to inject keyed fingerprint behavior through an embedding adapter while retaining ordinary model utility. The pinned source is `IntelliSys-Lab/iSeal@7e382321eef4355002acd93120d888dc9b45a8bd`; the canonical backbone is `meta-llama/Llama-3.2-3B-Instruct@0cb88a4f764b7a12671c53f0838cd831a0843b95`.

Experiment A formal training was never started: the public-code mandatory gate showed that simultaneous exact-zero `delta/A/B` initialization left the advertised adapter path gradient-inactive. A2 made only the approved trainability correction: `delta ~ Normal(0, 0.02)`, PyTorch default-equivalent Kaiming-uniform `A`, and exact-zero `B`. Official full tied `lm_head` trainability was retained. The canonical runtime key is represented only by SHA256 `8399db2b1e89eb03da1a1a6a4f9cd66d541f36c3695bd899e06613e06d75ffcf`; raw material remained outside Git and outputs.

## Trainability lineage

The parent gate `iseal_a2_trainability_20260830_053009` remains FAIL because its predeclared two steps ended immediately after the first effective `B` update. Continuation `iseal_a2_trainability_20260830_053009_cont1` extended only diagnostic duration to four steps while preserving all scientific semantics.

| Step | Effective LR | delta grad | A grad | B grad | tied head grad |
|---:|---:|---:|---:|---:|---:|
| 1 | 0 | 0 | 0 | 7.611014 | 178.591134 |
| 2 | 0.001 | 0 | 0 | 16.493048 | 370.611277 |
| 3 | 0.000666667 | 1.115025 | 2.106129 | 4.884193 | 115.113718 |
| 4 | 0.000333333 | 2.839157 | 5.314771 | 15.446130 | 223.584244 |

At step 2, tiny `delta/A` movement was weight-decay-only and was not counted. At steps 3–4 both received nonzero task gradients under positive LR and accumulated substantial updates. The base transformer remained unchanged. Overall gate status is **PASS via continuation**.

## Formal training

Run `iseal_a2_20260830_054641` completed 15 epochs / 75 steps with batch 2, BF16, AdamW, LR 1e-3, weight decay 0.01, seven warmup steps, linear decay, clipping 0.5, seed 42, two cipher layers, and adapter inner dimension 16. Final loss was `0.1101867482`. The merged Teacher checkpoint is stored outside Git at `/root/autodl-tmp/WMKD_Benchmark_data/runs/iseal/a2/iseal_a2_20260830_054641/checkpoints/teacher_merged`.

## Fingerprint evaluation

The predeclared operational detector is sentence BLEU with threshold 50; higher scores are more fingerprint-positive. Base and Teacher used identical plaintext ordering, canonical key/cipher, encrypted inputs, preprocessing, and decoding semantics.

| Group | Base mean BLEU | Teacher mean BLEU | Base success | Teacher success |
|---|---:|---:|---:|---:|
| Registered (10) | 2.331481 | 79.416232 | 0% | 100% |
| Held-out AG News (100) | 2.329693 | 2.191498 | 0% | 0% |

Registered-pair effectiveness is established with clear Base separation. Held-out plaintext generalization is not established.

## Utility, ordinary generation, and reload

| Metric | Base | A2 Teacher | Delta |
|---|---:|---:|---:|
| ARC Challenge acc_norm | 0.447099 | 0.319966 | -0.127133 |
| TruthfulQA MC2 acc | 0.505645 | 0.478960 | -0.026684 |

Fresh-process loading of the merged checkpoint passed and all detector/utility inference completed. Ordinary generation was functional for 10/10 Base prompts but only 8/10 Teacher prompts, so the ordinary-generation gate failed. ARC also regressed materially.

## Bounded conclusion

A2 successfully repaired adapter trainability and established strong registered-pair fingerprint effectiveness. It did not establish held-out generalization and caused material ARC plus observable ordinary-generation regression. Therefore `preferred_teacher=NO`, `ready_for_ba=NO`, and the final state is **A2 COMPLETE**. No Ba experiment was started.

