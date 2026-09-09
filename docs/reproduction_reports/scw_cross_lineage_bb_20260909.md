# SCW Active Cross-Lineage Bb

Run: scw_xbb_20260909. Fresh clean Qwen fixed revision 8f4992eda43eea7c770690ddc0de8f732da246f5. Frozen paraphrased 20k, full BF16 SFT, 7500 steps; successful process exits and fresh reload verified.

Frozen Level 1 SCW detector: 1000 queries, p=0.9841499328613281, alpha=0.001, fingerprinted=False. Lower p means stronger evidence. All 1000 generations and statistical raw outputs retained. No recalibration or threshold change.

The endpoint is not detected by this test. It does not establish forgetting or a causal mechanism.

ARC acc_norm=0.4974402730375427; TruthfulQA MC2=0.48478352312750794. Raw utility sample counts validated:1172/817.

Preferred model retained for reproducibility. Private archive verified; this report is included in the campaign Git closure. Exact protocol, launch Git/runner SHA and model SHA retained in full log/provenance.

## Final archive receipt

PRIVATE repo: MakiseKurisuEasonHan/Qwen2.5-3B-WMKD-Active-SCW-Cross-Lineage-Bb-Student

Immutable revision: dc6da8daec0104ac24bc4b004cde5bd32a06d178

Archive SHA256SUMS digest: cd7c9c3b7d6510b12a4b117eddff8709a0479ce729d24a28fe3e4ced4d3a25ff

MANIFEST_PLUS_SEGMENT PASS; 16 files, 10/10 fixed 2 MiB segment hashes; small-file full SHA verified. Full independent download NOT_PERFORMED. Source model preserved.
