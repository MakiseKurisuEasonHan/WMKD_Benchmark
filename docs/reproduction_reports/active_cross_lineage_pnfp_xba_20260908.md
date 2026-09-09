# PN-FP Cross-Lineage XBa

Fresh Qwen revision 8f4992eda43eea7c770690ddc0de8f732da246f5; reconstructed frozen PN-FP parent20k, 3epochs, 7500 full-parameter BF16 updates. No historical object overwritten.

Detector: 84/1024 vs clean Qwen43/1024, delta41/1024. Original text signatures retained; no secret regeneration. Teacher956/1024 and historical Ba98/1024 are references, not the new step0 or exact replay targets.

ARC: 0.4948805460750853 vs 0.4402730375426621, delta 0.05460750853242319. TruthfulQA MC2: 0.5019135695511419 vs 0.5712170418936038, delta -0.06930347234246192. Raw samples1172/817 verified.

Bounded finding: weak partial acquisition under this detector; no complete transfer, erasure, or mechanism claim. Final model retained locally. Archive decision deferred to campaign closure. No intermediate checkpoint saved; no existing artifact deleted.

Evidence: results/active_cross_lineage_ba/pnfp/full_experiment_log.json; detector_results.json; utility/raw_evaluator_output.json; model_provenance.json.
