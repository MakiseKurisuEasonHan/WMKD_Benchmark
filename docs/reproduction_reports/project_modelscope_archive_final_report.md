# Project ModelScope Archive Final Report

## A. Final archive summary

The canonical inventory contains **41** important artifacts: 24 `VERIFIED_ARCHIVED`, 8 `ARCHIVED_STRONGLY_VERIFIED`, 0 `MISSING_ARCHIVE`, 7 `NOT_APPLICABLE`, and 2 `PERMANENTLY_UNAVAILABLE`. All recoverable critical artifacts are archived. No scientific computation or metric changed during remediation.

Early-model tiering is explicit: PN-FP A2 Teacher and PN-FP Ba Student are the two full-redownload/SHA/reload samples; the other eight early models passed strong remote filename/size/SHA-blob/source-manifest/Git-record verification without full redownload.

## B. 30-experiment archive matrix

| Method | Slot | Classification | Notes |
|---|---|---|---|
| PN-FP | A/A2/A6 | VERIFIED_ARCHIVED |  |
| PN-FP | Ba | SAFE_WITH_PERMANENT_HISTORICAL_LIMITATION | Original Ba frozen20k is permanently unavailable; reconstructed Bb parent is separately verified |
| PN-FP | Bb/Bb2/Bb3 | VERIFIED_ARCHIVED |  |
| EverTracer | A/A2/A6 | ARCHIVED_STRONGLY_VERIFIED |  |
| EverTracer | Ba | ARCHIVED_STRONGLY_VERIFIED |  |
| EverTracer | Bb/Bb2/Bb3 | VERIFIED_ARCHIVED |  |
| CTCC | A/A2/A6 | ARCHIVED_STRONGLY_VERIFIED |  |
| CTCC | Ba | ARCHIVED_STRONGLY_VERIFIED |  |
| CTCC | Bb/Bb2/Bb3 | VERIFIED_ARCHIVED | CTCC slot uses completed Bb2; original Bb remains blocked |
| iSeal | A/A2/A6 | ARCHIVED_STRONGLY_VERIFIED |  |
| iSeal | Ba | ARCHIVED_STRONGLY_VERIFIED |  |
| iSeal | Bb/Bb2/Bb3 | VERIFIED_ARCHIVED |  |
| SCW | A/A2/A6 | ARCHIVED_STRONGLY_VERIFIED |  |
| SCW | Ba | SAFE_WITH_PERMANENT_HISTORICAL_LIMITATION | Original Ba frozen20k is permanently unavailable; recovered-exact Bb inputs are separately verified |
| SCW | Bb/Bb2/Bb3 | VERIFIED_ARCHIVED |  |
| LLMPrint | A/A2/A6 | NOT_APPLICABLE | A/A2 uses unmodified Base plus Git-safe detector package |
| LLMPrint | Ba | VERIFIED_ARCHIVED | Shared Passive-5 archive |
| LLMPrint | Bb/Bb2/Bb3 | VERIFIED_ARCHIVED | Shared Passive-5 archive |
| REEF | A/A2/A6 | NOT_APPLICABLE | A/A2 uses unmodified Base plus Git-safe detector package |
| REEF | Ba | VERIFIED_ARCHIVED | Shared Passive-5 archive |
| REEF | Bb/Bb2/Bb3 | VERIFIED_ARCHIVED | Shared Passive-5 archive |
| HuRef | A/A2/A6 | NOT_APPLICABLE | A/A2 uses unmodified Base plus Git-safe detector package |
| HuRef | Ba | VERIFIED_ARCHIVED | Shared Passive-5 archive |
| HuRef | Bb/Bb2/Bb3 | VERIFIED_ARCHIVED | Shared Passive-5 archive |
| AWM | A/A2/A6 | NOT_APPLICABLE | A/A2 uses unmodified Base plus Git-safe detector package |
| AWM | Ba | VERIFIED_ARCHIVED | Shared Passive-5 archive |
| AWM | Bb/Bb2/Bb3 | VERIFIED_ARCHIVED | Shared Passive-5 archive |
| ZeroPrint | A/A2/A6 | NOT_APPLICABLE | A/A2 uses unmodified Base plus Git-safe detector package |
| ZeroPrint | Ba | VERIFIED_ARCHIVED | Shared Passive-5 archive |
| ZeroPrint | Bb/Bb2/Bb3 | VERIFIED_ARCHIVED | Shared Passive-5 archive |

## C. Artifact-level matrix

| Artifact ID | Method | Experiment | Role | Repository | Classification | Evidence |
|---|---|---|---|---|---|---|
| `pnfp.a2.teacher` | PN-FP | A2 | Teacher | `MakiseKurisuEasonHan/WMKD-PNFP-A2-Teacher` | `VERIFIED_ARCHIVED` | `results/archive_remediation/evidence/pnfp_a2_teacher_20260905_083623.json` |
| `pnfp.ba.student` | PN-FP | Ba | Student | `MakiseKurisuEasonHan/WMKD-PNFP-Ba-Student` | `VERIFIED_ARCHIVED` | `results/archive_remediation/evidence/pnfp_ba_student_20260905_083803.json` |
| `evertracer.a.teacher` | EverTracer | A | Teacher | `MakiseKurisuEasonHan/WMKD-EverTracer-A-Teacher` | `ARCHIVED_STRONGLY_VERIFIED` | `results/archive_remediation/evidence/evertracer_a_teacher_strong_remote_20260905_091738.json` |
| `evertracer.ba.student` | EverTracer | Ba | Student | `MakiseKurisuEasonHan/WMKD-EverTracer-Ba-Student` | `ARCHIVED_STRONGLY_VERIFIED` | `results/archive_remediation/evidence/evertracer_ba_student_strong_remote_20260905_091738.json` |
| `ctcc.a.teacher` | CTCC | A | Teacher adapter | `MakiseKurisuEasonHan/WMKD-CTCC-A-Teacher` | `ARCHIVED_STRONGLY_VERIFIED` | `results/archive_remediation/evidence/ctcc_a_teacher_strong_remote_20260905_091738.json` |
| `ctcc.ba.student` | CTCC | Ba | Student | `MakiseKurisuEasonHan/WMKD-CTCC-Ba-Student` | `ARCHIVED_STRONGLY_VERIFIED` | `results/archive_remediation/evidence/ctcc_ba_student_strong_remote_20260905_091738.json` |
| `iseal.a6.teacher` | iSeal | A6 | Teacher | `MakiseKurisuEasonHan/WMKD-iSeal-A6-Teacher` | `ARCHIVED_STRONGLY_VERIFIED` | `results/archive_remediation/evidence/iseal_a6_teacher_strong_remote_20260905_091738.json` |
| `iseal.ba.student` | iSeal | Ba | Student | `MakiseKurisuEasonHan/WMKD-iSeal-Ba-Student` | `ARCHIVED_STRONGLY_VERIFIED` | `results/archive_remediation/evidence/iseal_ba_student_strong_remote_20260905_091738.json` |
| `scw.a2.teacher` | SCW | A2 | Teacher | `MakiseKurisuEasonHan/WMKD-SCW-A2-Teacher` | `ARCHIVED_STRONGLY_VERIFIED` | `results/archive_remediation/evidence/scw_a2_teacher_strong_remote_20260905_091738.json` |
| `scw.ba.student` | SCW | Ba | Student | `MakiseKurisuEasonHan/WMKD-SCW-Ba-Student` | `ARCHIVED_STRONGLY_VERIFIED` | `results/archive_remediation/evidence/scw_ba_student_strong_remote_20260905_091738.json` |
| `pnfp.detector.keys` | PN-FP | A2/Ba/Bb | Detector fingerprint keys | `MakiseKurisuEasonHan/WMKD_Benchmark_pnfp_canonical_detector_keys` | `VERIFIED_ARCHIVED` | `results/archive_remediation/evidence/pnfp_detector_dependency_20260905_094239.json` |
| `evertracer.detector.reference_neighborhoods` | EverTracer | A/Ba/Bb | Reference model and frozen neighborhoods | `MakiseKurisuEasonHan/WMKD_Benchmark_evertracer_detector_dependencies` | `VERIFIED_ARCHIVED` | `results/archive_remediation/evidence/evertracer_detector_dependencies_20260905_094840.json` |
| `scw.detector.input1000` | SCW | A2/Ba/Bb | Recovered-exact detector input | `MakiseKurisuEasonHan/WMKD_Benchmark_scw_recovered_exact_detector_input` | `VERIFIED_ARCHIVED` | `results/archive_remediation/evidence/scw_detector_dependency_20260905_094550.json` |
| `evertracer.ba.dataset` | EverTracer | Ba | Ba frozen20k | `MakiseKurisuEasonHan/WMKD_Benchmark_evertracer_ba_frozen20k` | `VERIFIED_ARCHIVED` | `results/proactive5_bb_archives/evertracer_ba_frozen20k_modelscope_archive.json` |
| `ctcc.ba.dataset` | CTCC | Ba | Ba frozen20k | `MakiseKurisuEasonHan/WMKD_Benchmark_ctcc_ba_frozen20k` | `VERIFIED_ARCHIVED` | `results/proactive5_bb_archives/ctcc_ba_frozen20k_modelscope_archive.json` |
| `iseal.ba.dataset` | iSeal | Ba | Ba frozen20k | `MakiseKurisuEasonHan/WMKD_Benchmark_iseal_ba_frozen20k` | `VERIFIED_ARCHIVED` | `results/proactive5_bb_archives/iseal_ba_frozen20k_modelscope_archive.json` |
| `pnfp.bb.parent` | PN-FP | Bb | Reconstructed Ba parent | `MakiseKurisuEasonHan/WMKD_Benchmark_pnfp_ba_reconstructed_frozen20k` | `VERIFIED_ARCHIVED` | `results/pnfp/experiment_bb/full_experiment_log.json` |
| `pnfp.bb.dataset` | PN-FP | Bb | Processed20k | `MakiseKurisuEasonHan/WMKD_Benchmark_pnfp_bb_processed20k` | `VERIFIED_ARCHIVED` | `results/pnfp/experiment_bb/processed20k_archive.json` |
| `pnfp.bb.student` | PN-FP | Bb | Student | `MakiseKurisuEasonHan/Llama-3.2-WMKD-PNFP-Bb-Student` | `VERIFIED_ARCHIVED` | `results/pnfp/experiment_bb/student_archive.json` |
| `evertracer.bb.dataset` | EverTracer | Bb | Processed20k | `MakiseKurisuEasonHan/WMKD_Benchmark_evertracer_bb_processed20k` | `VERIFIED_ARCHIVED` | `results/evertracer/experiment_bb/evidence/modelscope_archive.json` |
| `evertracer.bb.student` | EverTracer | Bb | Student | `MakiseKurisuEasonHan/Llama-3.2-WMKD-EverTracer-Bb-Student` | `VERIFIED_ARCHIVED` | `results/evertracer/experiment_bb/evidence/student_modelscope_archive.json` |
| `iseal.bb.dataset` | iSeal | Bb | Processed20k | `MakiseKurisuEasonHan/WMKD_Benchmark_iseal_bb_processed20k` | `VERIFIED_ARCHIVED` | `results/iseal/experiment_bb/processed20k_archive.json` |
| `iseal.bb.student` | iSeal | Bb | Student | `MakiseKurisuEasonHan/Llama-3.2-WMKD-iSeal-Bb-Student` | `VERIFIED_ARCHIVED` | `results/iseal/experiment_bb/student_archive.json` |
| `scw.bb.parent` | SCW | Bb | Reconstructed Ba parent | `MakiseKurisuEasonHan/WMKD_Benchmark_scw_ba_reconstructed_frozen20k` | `VERIFIED_ARCHIVED` | `results/scw/experiment_bb/full_experiment_log.json` |
| `scw.bb.dataset` | SCW | Bb | Processed20k | `MakiseKurisuEasonHan/WMKD_Benchmark_scw_bb_processed20k` | `VERIFIED_ARCHIVED` | `results/scw/experiment_bb/processed20k_archive.json` |
| `scw.bb.student` | SCW | Bb | Student | `MakiseKurisuEasonHan/Llama-3.2-WMKD-SCW-Bb-Student` | `VERIFIED_ARCHIVED` | `results/scw/experiment_bb/student_archive.json` |
| `ctcc.bb2.dataset` | CTCC | Bb2 | Processed20k | `MakiseKurisuEasonHan/WMKD_Benchmark_ctcc_bb2_processed20k` | `VERIFIED_ARCHIVED` | `results/ctcc/experiment_bb2/processed20k_archive.json` |
| `ctcc.bb2.student` | CTCC | Bb2 | Student | `MakiseKurisuEasonHan/Llama-3.2-WMKD-CTCC-Bb2-Student` | `VERIFIED_ARCHIVED` | `results/ctcc/experiment_bb2/student_archive.json` |
| `passive.ba.dataset` | Passive-5 Shared | Ba | Shared frozen20k | `MakiseKurisuEasonHan/WMKD_Benchmark_passive5_shared_ba_frozen20k` | `VERIFIED_ARCHIVED` | `results/passive5_shared_ba/modelscope_frozen20k_archive.json` |
| `passive.ba.student` | Passive-5 Shared | Ba | Shared Student | `MakiseKurisuEasonHan/Llama-3.2-WMKD-Passive5-Shared-Ba-Student` | `VERIFIED_ARCHIVED` | `results/passive5_shared_ba/modelscope_student_archive.json` |
| `passive.bb3.dataset` | Passive-5 Shared | Bb3 | Shared processed20k | `MakiseKurisuEasonHan/WMKD_Benchmark_passive5_shared_bb3_processed20k` | `VERIFIED_ARCHIVED` | `results/passive5_shared_bb3/modelscope_dataset_archive.json` |
| `passive.bb3.student` | Passive-5 Shared | Bb3 | Shared Student | `MakiseKurisuEasonHan/Llama-3.2-WMKD-Passive5-Shared-Bb3-Student` | `VERIFIED_ARCHIVED` | `results/passive5_shared_bb3/modelscope_student_archive.json` |
| `passive.llmprint.fingerprint` | LLMPrint | A/A2 | Git-safe fingerprint package | `N/A` | `NOT_APPLICABLE` | `durable Git record` |
| `passive.reef.fingerprint` | REEF | A/A2 | Git-safe fingerprint package | `N/A` | `NOT_APPLICABLE` | `durable Git record` |
| `passive.huref.fingerprint` | HuRef | A/A2 | Git-safe fingerprint package | `N/A` | `NOT_APPLICABLE` | `durable Git record` |
| `passive.awm.fingerprint` | AWM | A/A2 | Git-safe fingerprint package | `N/A` | `NOT_APPLICABLE` | `durable Git record` |
| `passive.zeroprint.fingerprint` | ZeroPrint | A/A2 | Git-safe fingerprint package | `N/A` | `NOT_APPLICABLE` | `durable Git record` |
| `ctcc.bb.original.processed20k` | CTCC | Bb original | Processed20k | `N/A` | `NOT_APPLICABLE` | `durable Git record` |
| `ctcc.bb.original.student` | CTCC | Bb original | Student | `N/A` | `NOT_APPLICABLE` | `durable Git record` |
| `pnfp.ba.original_dataset` | PN-FP | Ba | Original canonical Ba frozen20k | `N/A` | `PERMANENTLY_UNAVAILABLE` | `durable Git record` |
| `scw.ba.original_dataset` | SCW | Ba | Original canonical Ba frozen20k | `N/A` | `PERMANENTLY_UNAVAILABLE` | `durable Git record` |

## D. Early model verification

Full-redownload verified: PN-FP A2 Teacher and PN-FP Ba Student. Both passed per-file SHA and fresh-process reload; their temporary verification copies were deleted after durable evidence was saved.

Strong-remote verified: EverTracer A/Ba, CTCC A/Ba, iSeal A6/Ba, and SCW A2/Ba. Every canonical file matched remote filename, size, SHA256/blob identity, historical source manifest, and Git archive record. These eight are not claimed as full-redownload verified.

## E. PN-FP detector package

The exact existing detector payload with canonical SHA `922d3aec3b6bbac62dcdcf617b41e08a1384e7875db77aa6c4f9a278e03a8612` is archived privately at `MakiseKurisuEasonHan/WMKD_Benchmark_pnfp_canonical_detector_keys`. The detector uses 1,024 canonical items. Independent redownload, package SHA, schema, and PRIVATE visibility passed; key content is not reproduced here.

## F. EverTracer detector package

The exact canonical `reference_merged` and 200-record frozen neighborhoods are private at `MakiseKurisuEasonHan/WMKD_Benchmark_evertracer_detector_dependencies`. Reference model 9/9 filename/size/SHA-blob identities match source merge manifest `bca1ea3d6f68c2ced8cb55d969e4710ef6b1f6921f5f9267c721ac06b5fa0aaf`. Neighborhood SHA `7834e3d77704951ea06501c2166e960fef2b147ced3d751a8e55f07ec7b3672b` and count 200 passed independent redownload.

## G. SCW detector package

The recovered-exact 1,000-record input is private at `MakiseKurisuEasonHan/WMKD_Benchmark_scw_recovered_exact_detector_input`. SHA `c60cd7d03acbd3535c5564eafe521f88179833761924953fa599237c5082a69d`, count, parse/schema, and independent redownload passed.

## H. Permanently unavailable originals

PN-FP original canonical Ba frozen20k and SCW original canonical Ba frozen20k were lost before archival and remain `PERMANENTLY_UNAVAILABLE`. They were not regenerated. Later reconstructed/recovered-exact Bb parents are distinct verified artifacts.

## I. Passive NOT_APPLICABLE rationale

LLMPrint, REEF, HuRef, AWM, and ZeroPrint A/A2 use the unmodified pinned canonical Base plus small Git-safe detector/fingerprint packages. Duplicating the Base into five ModelScope repos is unnecessary. Shared Ba and Bb3 datasets/Students remain verified private archives.

## J. Server deletion survivability

All recoverable models, datasets, processed20k artifacts, reconstructed parents, and external detector dependencies can be restored from GitHub plus PRIVATE ModelScope. PN-FP and SCW remain `SAFE_WITH_PERMANENT_HISTORICAL_LIMITATION` solely for the two already-lost original Ba datasets; all other methods are `SAFE`. This statement does not authorize deletion of AutoDL data.

## K. Remaining limitations

Eight early models use strong remote verification rather than full independent redownload. Two representative early models received full redownload/SHA/reload. PRIVATE ModelScope availability and account access remain external operational dependencies.

## Final flags

`ALL_RECOVERABLE_CRITICAL_ARTIFACTS_ARCHIVED = YES`
`ALL_RECOVERABLE_CRITICAL_MODELS_ARCHIVED = YES`
`ALL_RECOVERABLE_CRITICAL_DATASETS_ARCHIVED = YES`
`ALL_CRITICAL_DETECTOR_DEPENDENCIES_ARCHIVED = YES`
`ALL_COMPLETED_BB_ARTIFACTS_VERIFIED_ARCHIVED = YES`
`EARLY_A_BA_ARCHIVES_STRONGLY_VERIFIED = YES`
`EARLY_A_BA_FULL_REDOWNLOAD_SAMPLE_COUNT = 2`
`STRICT_FULL_LOG_INDEX_32_32_PASS = YES`
`LOCAL_GITHUB_AUTODL_SYNC = YES`
`SERVER_CAN_BE_DELETED_WITHOUT_NEW_RECOVERABLE_SCIENTIFIC_DATA_LOSS = YES`
