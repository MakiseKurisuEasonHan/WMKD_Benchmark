# CTCC Active Cross-Lineage Ba

Status: COMPLETE (scientific evidence); campaign Git/archive closure pending.

Fresh Qwen2.5-3B-Instruct revision 8f4992eda43eea7c770690ddc0de8f732da246f5, frozen CTCC Ba20k; full-parameter BF16, 3 epochs, 7500 steps, LR1e-5, batch8, seed42. No continuation from another Student.

Frozen detector: trigger0/95, suppression0/100, normal0/105; combined negatives0/205; clean Qwen also0/95 and0/205. All300 raw rows retain frozen order/identity and have no generation error. LEVEL_1_VALID_CROSS_ARCHITECTURE. Fresh reload verified.

ARC Student=0.4684300341296928, Base=0.4402730375426621, delta=0.02815699658703069. TruthfulQA MC2 Student=0.4480919802572382, Base=0.5712170418936038, delta=-0.12312506163636561. Raw utility sample counts1172/817 verified.

Measured finding: no trigger activation on the frozen query set. This does not establish universal watermark absence or a causal mechanism.

Evidence: results/active_cross_lineage_ba/ctcc/{training_summary.json,model_provenance.json,final_detector.json,detector_results.json,utility_results.json,full_experiment_log.json}. Final model retained locally; no model upload or deletion.
