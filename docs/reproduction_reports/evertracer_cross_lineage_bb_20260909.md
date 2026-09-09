# EverTracer Active Cross-Lineage Bb

Run: evertracer_xbb_20260909. Fresh clean Qwen fixed revision 8f4992eda43eea7c770690ddc0de8f732da246f5. Frozen paraphrased 20k, full BF16 SFT, 7500 steps; successful process exits and fresh reload verified.

Canonical detector: N/A_CROSS_TOKENIZER. Exploratory diagnostic: AUC=0.5227, TPR=0.07, FPR=0.05. 200 original and 2000 frozen perturbation scores preserved.

EXPLORATORY_NON_COMPARABLE: not directly comparable with historical Llama detector; cannot establish watermark survival, failure or transfer. No detector recalibration or secret change.

ARC acc_norm=0.46075085324232085; TruthfulQA MC2=0.46907694275763584. Raw utility sample counts validated:1172/817.

Preferred final model retained for reproducibility. Private archive verified; this report is included in the campaign Git closure. Exact training config, launch source Git/runner SHA and model file SHA are in full_experiment_log.json and model_provenance.json.

## Final archive receipt

PRIVATE repo: MakiseKurisuEasonHan/Qwen2.5-3B-WMKD-Active-EverTracer-Cross-Lineage-Bb-Student

Immutable revision: eb1d3b656577259d59445e5e1362e1697ff3655a

Archive SHA256SUMS digest: de3b8805d1ac286f0d9edd18af150659adbb7877d90b22ecd9422caf74073979

MANIFEST_PLUS_SEGMENT PASS; 16 files, 10/10 fixed 2 MiB segment hashes; small-file full SHA verified. Full independent download NOT_PERFORMED. Source model preserved.
