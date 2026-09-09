# PN-FP Active Cross-Lineage Bb

Run: pnfp_xbb_20260909. Fresh canonical Qwen revision 8f4992eda43eea7c770690ddc0de8f732da246f5; 20,000 frozen paraphrased records; full BF16 SFT, 3 epochs, LR 1e-5, effective batch 8, seed 42, 7500 steps.

Frozen full-signature detector: 67/1024 (0.0654296875); zero errors/invalid samples. Clean Qwen 43/1024; XBa 84/1024.

ARC = 0.4684300341296928; TruthfulQA MC2 = 0.4917632470586235. Exact reference values and deltas are in results/active_cross_lineage_bb/pnfp/comparison.json, tied to canonical raw SHA records.

Measured XBb endpoint lies above clean Qwen and below XBa under the frozen full-signature rule. One run supports a weaker measured endpoint for the paraphrased condition, not causal proof or complete watermark transfer. PNFP reconstructed-parent limitations retained.

Training, fresh reload, detector and utility evidence complete. Model retained locally. Preferred final model approved for reproducibility. Archive verification and campaign Git closure remain pending; this report does not claim ModelScope upload completion. No retraining or detector changes.


## Preferred ModelScope archive verified

Repo: MakiseKurisuEasonHan/Qwen2.5-3B-WMKD-Active-PNFP-Cross-Lineage-Bb-Student

Immutable revision: `e1d1d250b12130c10f305e67f3539a227629ce80`

Archive SHA256 (SHA256SUMS digest): `f81f6d6d477dfb6a5aa95be9080e813a21acb829fa08b31d3c128647d1a47240`

PRIVATE; 16 source files; MANIFEST_PLUS_SEGMENT PASS; 10/10 fixed 2 MiB segments matched, small files fully SHA-verified. Full independent model download NOT_PERFORMED. Source final model retained. Git metadata closure pending.

## Final archive receipt

PRIVATE repo: MakiseKurisuEasonHan/Qwen2.5-3B-WMKD-Active-PNFP-Cross-Lineage-Bb-Student

Immutable revision: e1d1d250b12130c10f305e67f3539a227629ce80

Archive SHA256SUMS digest: f81f6d6d477dfb6a5aa95be9080e813a21acb829fa08b31d3c128647d1a47240

MANIFEST_PLUS_SEGMENT PASS; 16 files, 10/10 fixed 2 MiB segment hashes; small-file full SHA verified. Full independent download NOT_PERFORMED. Source model preserved.
