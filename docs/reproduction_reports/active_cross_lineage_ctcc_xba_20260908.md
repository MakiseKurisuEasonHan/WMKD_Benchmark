# CTCC Active Cross-Lineage Ba

Status: COMPLETE (scientific evidence); campaign Git/archive closure pending.

Fresh Qwen2.5-3B-Instruct revision 8f4992eda43eea7c770690ddc0de8f732da246f5, frozen CTCC Ba20k; full-parameter BF16, 3 epochs, 7500 steps, LR1e-5, batch8, seed42. No continuation from another Student.

Frozen detector: trigger0/95, suppression0/100, normal0/105; combined negatives0/205; clean Qwen also0/95 and0/205. All300 raw rows retain frozen order/identity and have no generation error. LEVEL_1_VALID_CROSS_ARCHITECTURE. Fresh reload verified.

ARC Student=0.4684300341296928, Base=0.4402730375426621, delta=0.02815699658703069. TruthfulQA MC2 Student=0.4480919802572382, Base=0.5712170418936038, delta=-0.12312506163636561. Raw utility sample counts1172/817 verified.

Measured finding: no trigger activation on the frozen query set. This does not establish universal watermark absence or a causal mechanism.

Evidence: results/active_cross_lineage_ba/ctcc/{training_summary.json,model_provenance.json,final_detector.json,detector_results.json,utility_results.json,full_experiment_log.json}. Final model retained locally; no model upload or deletion.

## Preferred model archive — 2026-09-09

User explicitly approved preferred retention for reproducibility. This does not upgrade the detector verdict.

{
  "repo": "MakiseKurisuEasonHan/Qwen2.5-3B-WMKD-Active-CTCC-Cross-Lineage-Ba-Student",
  "revision": "62ccf1df246568fd50ecbbf787eac3ab92568b94",
  "archive_sha256": "d152dda37fd85ceb854316d9e2ebed87adaf443ae3ed7717c6ac474734307168",
  "file_count": 16,
  "total_bytes": 6187856979,
  "remote_verification": "PASS_ALL_FILES_SIZE_AND_SHA",
  "uploaded_at": "2026-09-09T07:24:29.716373+00:00",
  "verified_at": "2026-09-09T07:43:17.591784+00:00",
  "verification_mode": "FULL_INDEPENDENT_DOWNLOAD",
  "verification_status": "PASS",
  "segment_count": 0,
  "segment_matches": 0,
  "full_remote_download_performed": true,
  "reason_if_full_download_triggered": "Existing full verification retained; user CTCC exception"
}
