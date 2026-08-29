# iSeal Experiment A3 Report

## Lineage and rationale

Experiment A formal training was not started after the pinned public-code trainability gate failed. A2 repaired only simultaneous-zero adapter initialization, trained successfully, and achieved strong registered fingerprinting but degraded utility. A3 is a new ablation/adaptation—not a pure public-code reproduction—that freezes the 394,002,432-parameter tied input-embedding/`lm_head` matrix while retaining A2's repaired `delta/A/B` initialization and every other scientific setting. It tests whether the large tied-matrix update caused A2's utility regression.

## Gate and training

Gate `iseal_a3_trainability_20260830_060044` passed. Across all four steps, the base transformer and tied embedding/head had exactly zero gradient and update. `B` gradients were 7.611014, 16.493048, 7.541493, and 18.002456. After the first effective `B` update, `delta/A` gradients became 2.217279/4.163332 at step 3 and 1.754724/3.281861 at step 4. All values were finite. Unique trainable adapter parameters: 930,816.

Formal run `iseal_a3_20260830_060344` completed 15 epochs / 75 optimizer steps with final loss 0.9921874404. All A2 settings, including key SHA256 `8399db2b1e89eb03da1a1a6a4f9cd66d541f36c3695bd899e06613e06d75ffcf`, were preserved. The checkpoint is `/root/autodl-tmp/WMKD_Benchmark_data/runs/iseal/a3/iseal_a3_20260830_060344/checkpoints/teacher_merged`. For reloadable serialization, the trained input-side adapter residual was merged into input embeddings while the frozen output head was retained as an untied copy; this preserves the trained A3 computation without changing the frozen head.

## Base–A2–A3 results

| Metric | Base | A2 | A3 |
|---|---:|---:|---:|
| Registered mean BLEU | 2.331481 | 79.416232 | 13.147504 |
| Registered success @50 | 0% | 100% | 0% |
| Held-out mean BLEU | 2.329693 | 2.191498 | 2.737425 |
| Held-out success @50 | 0% | 0% | 0% |
| ARC Challenge acc_norm | 0.447099 | 0.319966 | 0.403584 |
| TruthfulQA MC2 | 0.505645 | 0.478960 | 0.511518 |
| Ordinary generation | 10/10 | 8/10 | 10/10 |
| Trainable parameters | 0 | 394,933,248 | 930,816 |
| Tied head trainable | No | Yes | No |

A3 registered median BLEU was 10.075397; held-out median was 2.435577. Individual BLEU distributions are retained in the machine results. Fresh-process reload and all evaluations passed.

## Conclusion

Under the WMKD canonical 3B adaptation, adapter-only iSeal training materially recovered ARC, slightly exceeded Base TruthfulQA, and restored ordinary generation relative to A2. It did not preserve A2's registered fingerprint effectiveness: no registered sample crossed the fixed BLEU-50 threshold. Held-out plaintext generalization was not established. Therefore A3 is complete but `preferred_teacher=NO` and `ready_for_ba=NO`; no Ba run was started.

