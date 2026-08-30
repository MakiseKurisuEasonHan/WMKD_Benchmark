# iSeal Experiment A6 formal report

## Motivation and single-variable design

Pinned source is `IntelliSys-Lab/iSeal@7e382321eef4355002acd93120d888dc9b45a8bd`. Experiment A formal training was never started after the public exact-zero adapter failed its mandatory gate. A2 repaired initialization but retained the trainable tied head, giving strong registered memorization with degraded utility. A3 froze the tied embedding/head and trained only the adapter. A4 increased fingerprints 10→100 at inner dimension 16. A5 increased inner dimension 16→128 at fixed 100 fingerprints, reaching 66/100 registered success with healthy tested utility but leaving the Teacher decision open.

A6 is the final predeclared sample-count extension. Relative to A5, its sole scientific change is registered training plaintext count 100→200. Inner dimension remains 128; model, repaired initialization, optimizer, 15 epochs, batch 2, length 128, BF16, LR `1e-3`, weight decay `0.01`, 10% linear warmup, clipping `0.5`, seed 42, cipher, canonical runtime key, frozen transformer/tied matrix, detector threshold 50, generation, and utility protocols are unchanged.

## Dataset construction and audit

Seed-42 shuffled AG News indices are training `[0,10) + [110,300)`, held-out `[10,110)`. The first 100 training rows exactly equal A5's `[0,10) + [110,200)` records; A6 adds `[200,300)`. An independent row-level assertion verified identical A5-100 identities and identical held-out-100 identities. Training count is 200, held-out count 100, index overlap zero, and plaintext-hash overlap zero. Immutable manifest digest is `a68fff13eb0add1f64634e50235a232c3f00fcdcf5d543db942e40a5f3b7bbe9`.

## Trainability gate and parameters

Gate `iseal_a6_trainability_20260830_131945` passed. The 200 texts contain 3,865 unique trainable tokens versus A5's 2,304. Delta therefore grows from 7,077,888 to 11,873,280 parameters; A and B remain 393,216 each. Unique trainable total is 12,659,712, 4,795,392 (+60.98%) above A5. This confirms that more fingerprints mechanically increase fingerprint-specific trainable state through vocabulary coverage, though not one-to-one with sample count.

B gradient norms at steps 1-4 were 40.801715, 28.860617, 18.938108, and 22.589052. After B's effective update, delta gradients were 3.328792 and 8.522671 at steps 3/4; A gradients were 6.365261 and 15.265254. Transformer, original embedding, and tied `lm_head` gradients/updates were zero; all values were finite.

## Formal training and runtime

Detached run `iseal_a6_20260830_132300` completed 1,500/1,500 steps, 15 epochs, and exited 0. Final loss was `0.3154188097`. Runtime was 81.051 seconds (`0.054034 s/step`) versus A5's 46.212 seconds (`0.061616 s/step`): total runtime increased about 75.4% while steps doubled, demonstrating that trainable-state and full-model compute do not scale by a single mechanical factor. Checkpoint: `/root/autodl-tmp/WMKD_Benchmark_data/runs/iseal/a6/iseal_a6_20260830_132300/checkpoints/teacher_merged`.

## Fingerprint evaluation

| Set | Base mean | A5 mean | A6 mean | A6 median | Base success | A5 success | A6 success |
|---|---:|---:|---:|---:|---:|---:|---:|
| Full registered 200 | 2.332514 | — | 69.171651 | 69.276665 | 0/200 | — | 179/200 |
| Historical A5 registered 100 | 2.183026 | 56.048270 | 68.328577 | 68.223714 | 0/100 | 66/100 | 86/100 |
| Held-out 100 | 2.329693 | 5.944563 | 5.883516 | 4.592471 | 0/100 | 0/100 | 0/100 |

The added A6-only 100 had mean 70.014724, median 70.225801, and 93/100 successes. On the same historical 10, means were Base 2.331481, A2 79.416232, A3 13.147504, A4 30.802328, A5 55.527310, and A6 73.160127; A6 median was 77.067541 and success 9/10. Thus the gain is visible both on new records and the preserved A5 identities rather than being an aggregate-composition artifact. Raw paired scores are retained in `results/iseal/experiment_a6/fingerprint_and_generation.json`.

## Utility and fresh reload

| Metric | Base | A2 | A3 | A4 | A5 | A6 |
|---|---:|---:|---:|---:|---:|---:|
| ARC Challenge acc_norm | 0.447099 | 0.319966 | 0.403584 | 0.408703 | 0.401877 | 0.389932 |
| TruthfulQA MC2 | 0.505645 | 0.478960 | 0.511518 | 0.519351 | 0.518636 | 0.477828 |
| Ordinary generation | 10/10 | 8/10 | 10/10 | 10/10 | 10/10 | 10/10 |

A6 incurs bounded ARC and TruthfulQA declines relative to A5 but remains functionally healthy on the tested standardized utility suite and all fixed ordinary prompts. All results were produced after fresh-process checkpoint reload; `fresh_reload=PASS`.

## Preferred Teacher and bounded conclusion

A6 improves full and paired historical registered detection substantially over A5, retains clear Base separation, keeps ordinary generation 10/10, and passes fresh reload. Accordingly, final selection is `preferred_teacher=A6`, `preferred_teacher=YES`, and `ready_for_ba=YES`. This does not launch or authorize Ba automatically. A6 is the last authorized sample-scale experiment; no A7 was created.

Under the WMKD canonical 3B adapter-only `inner_dim=128` setting, increasing registered fingerprint training scale from 100 to 200 increased registered-secret fingerprint detectability while preserving functional tested model utility. Held-out plaintext generalization was not established.
