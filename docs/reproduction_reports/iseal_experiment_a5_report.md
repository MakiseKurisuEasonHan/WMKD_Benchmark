# iSeal Experiment A5 formal report

## Scope and lineage

Experiment A formal training was never started because the pinned public-code exact-zero `delta/A/B` adapter failed its mandatory trainability gate. A2 repaired only initialization and retained trainable tied `lm_head`; it memorized all 10 registered fingerprints but degraded utility. A3 froze the tied input embedding/`lm_head` and trained only `delta+A+B`; utility recovered but registered detection was weak. A4 retained A3 semantics and changed only training coverage from 10 to 100 fingerprints; registered success improved to 15/100 with healthy utility.

A5 asks whether additional adapter capacity improves registered detectability under the same 100-fingerprint adapter-only protocol. Relative to A4, the sole scientific change is `adapter_inner_dim: 16 -> 128`. The value 128 occurs in pinned commit `7e382321eef4355002acd93120d888dc9b45a8bd` in the released alternative `embed_adapter/Embed.py` training call and the `InstructionFingerprint` default. This is released-code provenance, not a claim that the paper mandates 128.

## Fixed protocol

A5 uses canonical Llama-3.2-3B-Instruct revision `0cb88a4f764b7a12671c53f0838cd831a0843b95`, AG News, seed 42, the exact A4 100 registered and 100 held-out identities, 15 epochs, batch 2, length 128, BF16, AdamW LR `1e-3`, weight decay `0.01`, 10% linear warmup, clip `0.5`, two cipher layers, the same canonical runtime key (only irreversible SHA256 recorded), repaired `delta` Normal(0, 0.02), default Kaiming-uniform A, zero B, frozen transformer, and frozen tied embedding/`lm_head`. Manifest construction digest is `3e4d0770e744af0ddbbb7d6dc1e6173447d59fbe6076be1f57417992f2b0ff36`; training/held-out index and plaintext-hash overlap are zero.

Detector semantics remain sacreBLEU sentence BLEU with `13a` tokenization, higher-is-positive, fixed threshold 50. Generation and utility prompts are unchanged.

## Trainability sanity

Gate `iseal_a5_trainability_20260830_063618` passed. Trainable parameters were delta 7,077,888, A 393,216, and B 393,216, for 7,864,320 unique parameters. A4 had 7,176,192, so capacity increased by 688,128 (+9.59%); this does not imply an eightfold increase in full 3B forward/backward compute.

At steps 1-4, effective LRs were 0, 0.001, 0.000666667, and 0.000333333. B task-gradient norms were 24.474107, 16.766384, 17.897372, and 29.706725. After B's first effective update, delta gradients became 3.793274 and 3.357820 at steps 3/4, while A gradients became 7.271361 and 6.079908. The apparent step-2 delta/A movement (`0.000532533` / `0.000065348`) occurred with zero task gradient and is weight-decay-only, not adapter progression. Transformer, original embedding, and tied `lm_head` gradients and updates remained exactly zero; no NaN/Inf occurred. Full raw audit is in `results/iseal/experiment_a5/trainability_audit.json`.

## Formal training and runtime

Detached run `iseal_a5_20260830_063925` completed 750/750 optimizer steps and 15 epochs with exit code 0. Final loss was `0.7015870214`. Wall time was 46.212 seconds (`0.061616 s/step`), versus A4's 47.165 seconds (`0.062887 s/step`); the observed difference is small timing noise rather than evidence of a speedup. The checkpoint is outside Git at `/root/autodl-tmp/WMKD_Benchmark_data/runs/iseal/a5/iseal_a5_20260830_063925/checkpoints/teacher_merged`.

## Fingerprint results

| Set | Base mean | A4 mean | A5 mean | A5 median | Base success | A4 success | A5 success |
|---|---:|---:|---:|---:|---:|---:|---:|
| Registered 100 | 2.183026 | 34.865706 | 56.048270 | 57.985269 | 0/100 | 15/100 | 66/100 |
| Held-out 100 | 2.329693 | 6.365625 | 5.944563 | 4.619985 | 0/100 | 0/100 | 0/100 |

On the fixed historical registered-10 subset, mean BLEU was Base 2.331481, A2 79.416232, A3 13.147504, A4 30.802328, and A5 55.527310. A5 median was 59.207487 and success was 6/10. Per-sample registered and held-out raw scores are retained in `results/iseal/experiment_a5/fingerprint_and_generation.json`.

The A4-to-A5 capacity change increased registered mean by 21.182564 points and threshold successes by 51 samples. Held-out mean decreased by 0.421062 and held-out success remained zero, so unseen-plaintext generalization was not established.

## Utility and fresh reload

| Metric | Base | A2 | A3 | A4 | A5 |
|---|---:|---:|---:|---:|---:|
| ARC Challenge acc_norm | 0.447099 | 0.319966 | 0.403584 | 0.408703 | 0.401877 |
| TruthfulQA MC2 | 0.505645 | 0.478960 | 0.511518 | 0.519351 | 0.518636 |
| Ordinary generation | 10/10 | 8/10 | 10/10 | 10/10 | 10/10 |

All detector, utility, and ordinary-generation measurements were executed in a fresh process after reloading the merged checkpoint. `fresh_reload = PASS`. Tested utility remains healthy relative to A3/A4, with a modest ARC decrease versus A4 and essentially unchanged TruthfulQA and ordinary generation.

## Teacher decision and bounded conclusion

`preferred_teacher = REQUIRES_DECISION` and `ready_for_ba = NO (pending decision)`. Registered separation is substantially stronger and the mean/median exceed the fixed threshold, but coverage remains partial at 66/100; held-out success remains 0/100. The protocol explicitly reserves this combination for user review of whether registered-secret ownership semantics make the checkpoint acceptable. No A6 or Ba run was started.

Under the WMKD canonical 3B adapter-only 100-fingerprint setting, increasing the released-code-provenance adapter inner dimension from 16 to 128 increased registered fingerprint detectability while preserving tested utility. Held-out plaintext generalization was not established.
