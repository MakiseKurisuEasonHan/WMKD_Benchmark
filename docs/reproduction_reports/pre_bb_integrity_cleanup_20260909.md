# Pre-Bb integrity audit — 2026-09-09

Scientific execution is not started. Initial local/GitHub/AutoDL HEAD: b98c1b2ba50d4d21a06dda925911308505ce847d. AutoDL has no GPU and no project workers.

## Evidence integrity

Five active Ba trajectories contain all 11 required steps. All 55 detector_result objects equal their trajectory rows; all numeric CSV columns match JSON. Raw evidence counts pass: PNFP 1024 key rows, EverTracer 200 calibrated score rows, CTCC 300 generation rows, iSeal registered200/heldout100 rows, SCW 1000 query generations and permutation entries per checkpoint. No detector_errors recorded at any final trajectory point. These are integrity checks, not new detector evaluations.

795 trajectory evidence files are byte-identical between local and AutoDL and tracked in the confirmed GitHub commit. A new independent local ZIP with manifest is CRC and per-file SHA verified; see trajectory_package_receipt.json. Existing local ZIP archives also pass CRC checks. Dataset reconstruction limitations for PNFP/SCW remain unchanged. Teacher is never step0.

Trajectory final-model remote archives are not established by the current receipts; all trajectory checkpoint weights are therefore KEEP, despite complete scientific evidence. No archive result from XBa is reused as proof for a different same-lineage trajectory model.

## Full-log index

Original index:55 unique paths, no missing full log. An existing shared Passive-5 Bb3 full log was missing from the index; added as a shared training object without creating a scientific experiment or duplicating its five method-specific result views. Updated total:56. Other unindexed files are historical snapshots, superseded HuRef A (A2 is canonical), abandoned prelaunch objects or Methods11–15 versions. See unindexed_classification.json.

An old local EaaW A2 worktree full log differs from its indexed SHA. Its committed Git object matches the index; AutoDL canonical index remains valid. This excluded historical edit is preserved, not silently overwritten or included in cleanup. No current Methods1–10 or cross-lineage full log is missing.

## Model archives

Seven preferred cross-lineage Qwen Students have PRIVATE immutable-revision receipts: Passive Ba/Bb and Active PNFP/CTCC/EverTracer/iSeal/SCW Ba. PNFP/CTCC and Passive archives retain full-independent-download proof; the other three retain MANIFEST_PLUS_SEGMENT proof (10/10 chunks). No new remote full download is performed. Older archive receipts are inventoried; missing immutable-revision proof is not fabricated and prevents deleting a unique model.

## Cleanup gates

Only exact regular-file paths independently matched to the seven verified archives, plus pip HTTP cache, are proposed initially. Hardlinked archive staging weights and final weights count only once physically. Preserve every model config, source script, log, report, raw detector file, dataset, Teacher, clean Base and unverified unique model. Final execution requires this audit to be pushed, local ZIP evidence receipt saved and exact candidate validation PASS. Follow-up proposal and receipt record actual deletion paths and filesystem free-space changes.

## SCW measured late points

[
  {
    "step": 4000,
    "p_value": 0.949506402015686,
    "fingerprinted": false,
    "train_loss": 0.2882
  },
  {
    "step": 6000,
    "p_value": 0.6830558776855469,
    "fingerprinted": false,
    "train_loss": 0.2794
  },
  {
    "step": 7500,
    "p_value": 0.895175039768219,
    "fingerprinted": false,
    "train_loss": 0.2649
  }
]
