# EverTracer Active Cross-Lineage Ba

Scientific evidence COMPLETE; campaign Git/archive closure pending. Fresh canonical Qwen2.5-3B-Instruct revision8f4992eda43eea7c770690ddc0de8f732da246f5; original frozen Ba20k, 7500 full-parameter updates, 3 epochs, seed42, BF16, LR1e-5, batch8.

Canonical detector: N/A_CROSS_TOKENIZER. LEVEL_2_EXPLORATORY_NON_COMPARABLE.

Exploratory diagnostic AUC0.523, TPR0.07 at FPR0.05, selected member-oriented threshold0.011513830561923802. Frozen200 originals/2000 perturbations, unchanged100/100 labels and historical reference scalars; Qwen tokenizer128 cap, exp(-mean next-token loss). Raw identity, finite scores and exact reaggregation PASS. No perturbations regenerated or secret recalibrated.

EXPLORATORY_NON_COMPARABLE: NOT DIRECTLY COMPARABLE TO HISTORICAL LLAMA DETECTOR; cannot establish watermark survival, failure or transfer.

ARC=0.5162116040955631, Base=0.4402730375426621, delta=0.07593856655290099; TruthfulQA MC2=0.4509746503062132, Base=0.5712170418936038, delta=-0.12024239158739058. Utility raw counts1172/817.

Evidence: results/active_cross_lineage_ba/evertracer/{full_experiment_log.json,utility_results.json,model_provenance.json,exploratory_detector/}. Model retained locally. No claim of watermark survival/failure/transfer from this exploratory metric.

## Preferred model archive — 2026-09-09

User explicitly approved preferred retention for reproducibility. This does not upgrade the detector verdict.

{
  "repo": "MakiseKurisuEasonHan/Qwen2.5-3B-WMKD-Active-EverTracer-Cross-Lineage-Ba-Student",
  "revision": "5768251299ef75850c207344a06f4807c9c6800e",
  "archive_sha256": "d4b5e3a20181fb9a3ad8f8793e8ec0dc3c67d6ed8b16281e14fc72c30b0ccfaa",
  "file_count": 16,
  "total_bytes": 6187857250,
  "remote_verification": "REMOTE_MANIFEST_AND_SEGMENT_VERIFICATION_PASS",
  "uploaded_at": "2026-09-09T07:53:27.766168+00:00",
  "verified_at": "2026-09-09T07:53:41.609894+00:00",
  "verification_mode": "MANIFEST_PLUS_SEGMENT",
  "verification_status": "PASS",
  "segment_count": 10,
  "segment_matches": 10,
  "full_remote_download_performed": false,
  "reason_if_full_download_triggered": null
}
