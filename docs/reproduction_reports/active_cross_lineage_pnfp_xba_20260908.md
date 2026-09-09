# PN-FP Cross-Lineage XBa

Fresh Qwen revision 8f4992eda43eea7c770690ddc0de8f732da246f5; reconstructed frozen PN-FP parent20k, 3epochs, 7500 full-parameter BF16 updates. No historical object overwritten.

Detector: 84/1024 vs clean Qwen43/1024, delta41/1024. Original text signatures retained; no secret regeneration. Teacher956/1024 and historical Ba98/1024 are references, not the new step0 or exact replay targets.

ARC: 0.4948805460750853 vs 0.4402730375426621, delta 0.05460750853242319. TruthfulQA MC2: 0.5019135695511419 vs 0.5712170418936038, delta -0.06930347234246192. Raw samples1172/817 verified.

Bounded finding: weak partial acquisition under this detector; no complete transfer, erasure, or mechanism claim. Final model retained locally. Archive decision deferred to campaign closure. No intermediate checkpoint saved; no existing artifact deleted.

Evidence: results/active_cross_lineage_ba/pnfp/full_experiment_log.json; detector_results.json; utility/raw_evaluator_output.json; model_provenance.json.

## Preferred model archive — 2026-09-09

User explicitly approved preferred retention for reproducibility. This does not upgrade the detector verdict.

{
  "repo": "MakiseKurisuEasonHan/Qwen2.5-3B-WMKD-Active-PNFP-Cross-Lineage-Ba-Student",
  "revision": "4d7a589c21c927773876b2776e3eb794f1444b49",
  "archive_sha256": "d7b026ce9bc01975cac7d5b110929781861c4b2ce1bd26546dbe4a32d67d56ad",
  "file_count": 16,
  "total_bytes": 6187856918,
  "remote_verification": "PASS_ALL_FILES_SIZE_AND_SHA",
  "uploaded_at": "2026-09-09T07:02:14.402703+00:00",
  "verified_at": "2026-09-09T07:14:15.878172+00:00",
  "verification_mode": "FULL_INDEPENDENT_DOWNLOAD",
  "verification_status": "PASS",
  "segment_count": 0,
  "segment_matches": 0,
  "full_remote_download_performed": true,
  "reason_if_full_download_triggered": "Existing full verification retained"
}
