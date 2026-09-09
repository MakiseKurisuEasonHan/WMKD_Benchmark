# CTCC Active Cross-Lineage Bb2

Run: ctcc_xbb2_20260909. Fresh clean Qwen fixed revision 8f4992eda43eea7c770690ddc0de8f732da246f5. Frozen paraphrased 20k, full BF16 SFT, 7500 steps; successful process exits and fresh reload verified.

Frozen Level 1 detector: trigger 0/95; suppression 0/100; normal 0/105; combined negatives 0/205. Exact case-sensitive generated_answer.strip() == IAMALIVE. 300 raw generations retained; zero generation errors.

Measured endpoint shows no observed trigger acquisition under the frozen detector. This endpoint alone does not establish a forgetting trajectory or causal mechanism.

ARC acc_norm=0.439419795221843; TruthfulQA MC2=0.45344106594056727. Raw utility sample counts validated:1172/817.

Preferred model retained for reproducibility. Private archive verified; this report is included in the campaign Git closure. Exact protocol, launch Git/runner SHA and model SHA retained in full log/provenance.

## Final archive receipt

PRIVATE repo: MakiseKurisuEasonHan/Qwen2.5-3B-WMKD-Active-CTCC-Cross-Lineage-Bb2-Student

Immutable revision: a2535f62042ed67e13918ba0c99fef0996f41041

Archive SHA256SUMS digest: 66c664b14775149656d816d60f221b7a5a44f78dffc8fe33fa14ead88e1aabbd

MANIFEST_PLUS_SEGMENT PASS; 16 files, 10/10 fixed 2 MiB segment hashes; small-file full SHA verified. Full independent download NOT_PERFORMED. Source model preserved.
