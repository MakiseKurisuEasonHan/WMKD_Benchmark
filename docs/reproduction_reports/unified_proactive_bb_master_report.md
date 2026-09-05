# WMKD unified proactive Bb — final master report

Strictly re-audited: 2026-09-05. This report covers the five original proactive Bb methods plus the separately authorized CTCC Bb2 variant. Conclusions are limited to the frozen same-backbone benchmark scope.

## A. Protocol

Each original Bb used method-specific Ba answers, frozen answer-only atomic-identity/Qwen untargeted-paraphrasing preprocessing, a fresh canonical `meta-llama/Llama-3.2-3B-Instruct@0cb88a4f764b7a12671c53f0838cd831a0843b95` Student, three-epoch full-parameter distillation (7,500 optimizer steps), the method's frozen detector, and Ba-matched ARC-Challenge/TruthfulQA utility. No scientific threshold, prompt, seed, detector semantics, or training configuration was tuned from Bb outcomes.

## B–G. Method results

| Object | Preprocessing / parent | Student | Detector | Utility (ARC / TruthfulQA) | Final status |
| --- | --- | --- | --- | --- | --- |
| PN-FP Bb `pnfp_bb_20260904_055000` | reconstructed parent 20k; Bb 20k; fallback 23 | 7,500; loss 1.0554428070704143; reload PASS | 72/1024; Base 1, Teacher 956, Ba 98; errors 0 | 0.4906143344709898 / 0.48613790979493243; sanity PASS | COMPLETE |
| EverTracer Bb `evertracer_bb_20260903_130000` | 20k; fallback 78 | 7,500; loss 0.9608292924880981; reload PASS | AUC 0.4757, TPR 0.08; Teacher 1/1, Base .4417/.05, Ba .4987/.06 | 0.49829351535836175 / 0.47559656098277925; sanity PASS | COMPLETE |
| CTCC Bb `ctcc_bb_20260904_055000` | stopped at 17,269 resolved / 18,264 journal rows; fallback 202 > limit 200 | NOT_RUN | NOT_RUN | NOT_RUN | BLOCKED_AT_PREPROCESSING_ACCEPTANCE_GATE |
| CTCC Bb2 `ctcc_bb2_20260905_011104` | reused 17,269; new 2,731; final 20k; fallback 236 (1.18%); parity PASS | 7,500; loss 1.10743791624705; reload PASS | 0/95 triggers; 0/205 negative activations; 0 errors | 0.48976109215017066 / 0.44850679576156427; sanity PASS | COMPLETE |
| iSeal Bb `iseal_bb_20260904_055000` | 20k; fallback 31 | 7,500; loss 1.0406477853139242; reload PASS | 0/200; mean BLEU 2.3018129521270327; median 1.98992578128578; errors 0 | 0.48976109215017066 / 0.46152410492343565; sanity 10/10 PASS | COMPLETE |
| SCW Bb `scw_bb_20260904_055000` | reconstructed parent 20k; Bb 20k; fallback 51 | 7,500; loss 0.9257782194137574; reload PASS | p=0.9529914855957031, alpha=.001, n=1000, not fingerprinted | 0.5042662116040956 / 0.4861866050235854; sanity PASS | COMPLETE |

## H. Detector synthesis

EverTracer, iSeal, SCW, and operational CTCC Bb2 remained in their respective Base/Ba-like low-detectability regimes. PN-FP retained a residual 72/1024 signal: below Teacher 956/1024 and Ba 98/1024, but above Base 1/1024. Method-specific metrics are not converted into one percentage.

## I. Utility synthesis

All completed objects passed generation sanity. ARC and TruthfulQA remained broadly comparable within the frozen scope; this is not universal quality-preservation evidence.

## J. Parent reconstruction limitations

Original canonical PN-FP and SCW Ba frozen20k artifacts were unavailable. Their Bb parents are new `protocol_faithful_reconstruction` objects, archived and independently verified, and are not claimed identical to the unavailable originals.

## K. CTCC Bb/Bb2 distinction

Original Bb remains immutably blocked because `202 > 200`, before downstream execution. Bb2 removes only the global fallback-count acceptance gate; it does not alter per-sample UP, Student, detector, or utility semantics. Durable Bb2 evidence records parity `PASS`, not a numeric 19/19. Its detector is WMKD's operational `generated_answer.strip() == "IAMALIVE"`, not an official CTCC detector.

## L. Artifact archives

Twelve proactive artifacts are recorded as PRIVATE ModelScope repositories with upload and independent redownload/SHA verification: PN-FP/SCW reconstructed parents; EverTracer/iSeal/PN-FP/SCW/CTCC Bb2 processed20k datasets; and their five final Students. Student redownload reload is PASS. Original CTCC Bb has no downstream archive.

## M. Full-log integrity

All 32 indexed scientific objects have a canonical `full_experiment_log.json`. The strict closure recalculated every SHA and repaired ten stale historical preferred-Teacher/Ba-Student index hashes. Final requirements are 32 unique composite IDs, zero broken paths, zero duplicates, and zero SHA mismatches.

## N. Git/project closure

Final Local/GitHub/AutoDL parity, ahead/behind, worktree cleanliness, and tests are recorded in `proactive_bb_final_closure_integrity.md` and the final handoff.

## O. Bounded scientific conclusions

These results do not establish universal removal, universal robustness, retained-watermark percentage, checkpoint-level disappearance, or causal removal by UP. They report final-Student behavior only under the frozen configurations and stated limitations.

## Automatic shutdown history

The previous finalizer considered the index valid under a scoped validator and triggered the authorized shutdown. A later strict 32-object audit found ten stale historical index SHAs; this closure repairs that metadata-only issue without changing scientific results. No shutdown-success timestamp is invented.
