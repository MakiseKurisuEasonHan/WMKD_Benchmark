# iSeal Experiment A4 Report

A4 preserves A3's adapter-only architecture, frozen tied embedding/`lm_head`, repaired initialization, optimizer, key, detector, and all other scientific settings. Its sole change is 10 → 100 registered AG News training plaintexts. The 100-sample scale has provenance in the pinned repository's alternative `embed_adapter` path; it is not claimed as paper-mandated.

The immutable training set is shuffled indices `[0,10) ∪ [110,200)`, so A3's historical registered 10 are its prefix. Held-out remains the A2/A3 indices `[10,110)`. Both index and plaintext-hash overlap are zero. Manifest SHA256: `3e4d0770e744af0ddbbb7d6dc1e6173447d59fbe6076be1f57417992f2b0ff36`.

Sanity gate `iseal_a4_trainability_20260830_061612` passed: tied matrix/base gradients and updates were zero; step 3–4 `delta/A/B` task gradients were nonzero. Actual trainable tokens were 2,304 and unique adapter parameters 7,176,192.

Formal run `iseal_a4_20260830_061934` completed 750 steps / 15 epochs with final loss 0.8938665986. Checkpoint: `/root/autodl-tmp/WMKD_Benchmark_data/runs/iseal/a4/iseal_a4_20260830_061934/checkpoints/teacher_merged`.

| Metric | Base | A2 | A3 | A4 |
|---|---:|---:|---:|---:|
| Training samples | 0 | 10 | 10 | 100 |
| Registered mean BLEU¹ | 2.331481 | 79.416232 | 13.147504 | 30.802328 |
| Registered success¹ | 0% | 100% | 0% | 10% |
| Held-out mean BLEU | 2.329693 | 2.191498 | 2.737425 | 6.365625 |
| Held-out success | 0% | 0% | 0% | 0% |
| ARC acc_norm | 0.447099 | 0.319966 | 0.403584 | 0.408703 |
| TruthfulQA MC2 | 0.505645 | 0.478960 | 0.511518 | 0.519351 |
| Ordinary generation | 10/10 | 8/10 | 10/10 | 10/10 |

¹ Paired historical registered-10 subset. Full A4 registered-100 mean/median BLEU were 34.865706/34.568051, with 15/100 successes at threshold 50. Raw distributions are retained. Held-out median was 4.962635.

Fresh-process reload and detector/utility evaluation passed. Under the canonical adapter-only setting, increasing training coverage from 10 to 100 materially increased registered detectability and preserved healthy tested utility, but registered effectiveness remained insufficient at the fixed threshold and held-out generalization was not established. Therefore `A4 COMPLETE`, `preferred_teacher=NO`, `ready_for_ba=NO`; no A5 or Ba was started.

