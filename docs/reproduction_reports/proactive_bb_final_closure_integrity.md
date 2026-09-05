# Proactive Bb final closure integrity

Audit date: 2026-09-05. Scope: Git-safe metadata, reports, canonical JSON, archive records, local/GitHub/AutoDL parity. No GPU task, scientific computation, transfer, or protocol change was performed.

## A. Scientific status

- PN-FP Bb: COMPLETE (`pnfp_bb_20260904_055000`).
- EverTracer Bb: COMPLETE (`evertracer_bb_20260903_130000`).
- CTCC original Bb: BLOCKED_AT_PREPROCESSING_ACCEPTANCE_GATE (`ctcc_bb_20260904_055000`, fallback 202 > 200; downstream NOT_RUN).
- CTCC Bb2: COMPLETE (`ctcc_bb2_20260905_011104`), distinct variant removing only the global fallback-count gate.
- iSeal Bb: COMPLETE (`iseal_bb_20260904_055000`).
- SCW Bb: COMPLETE (`scw_bb_20260904_055000`).

## B. Final detector results

PN-FP 72/1024 (errors 0); EverTracer AUC 0.4757 / TPR 0.08; CTCC Bb NOT_RUN; CTCC Bb2 0/95 triggers and 0/205 negative activations (errors 0); iSeal 0/200, mean BLEU 2.3018129521270327, median 1.98992578128578 (errors 0); SCW p=0.9529914855957031 at alpha 0.001, n=1000, not fingerprinted.

## C. Final utility results

| Object | ARC-Challenge acc_norm | TruthfulQA MC2 | Sanity |
| --- | ---: | ---: | --- |
| PN-FP Bb | 0.4906143344709898 | 0.48613790979493243 | PASS |
| EverTracer Bb | 0.49829351535836175 | 0.47559656098277925 | PASS |
| CTCC Bb | NOT_RUN | NOT_RUN | NOT_RUN |
| CTCC Bb2 | 0.48976109215017066 | 0.44850679576156427 | PASS |
| iSeal Bb | 0.48976109215017066 | 0.46152410492343565 | 10/10 PASS |
| SCW Bb | 0.5042662116040956 | 0.4861866050235854 | PASS |

## D. Reconstruction disclosures

PN-FP and SCW use protocol-faithful reconstructed Ba parents; they are not claimed identical to unavailable originals. CTCC Bb2 does not replace blocked original Bb. Bb2 parity is durably PASS, but no numeric 19/19 is stored.

## E. Archive status

Existing metadata records all twelve expected proactive archives as PRIVATE, uploaded, and independently redownload/SHA verified: two reconstructed parents, five completed processed20k packages, and five completed Students. Model redownload reload is PASS. No transfer occurred during closure.

## F. Full experiment logs

The index declares and contains 32 objects. Every entry resolves to one parseable canonical `full_experiment_log.json`; unavailable/not-run data remains explicit, not invented. The six Bb/Bb2 objects have separate identities and correct terminal statuses.

## G. Index strict integrity

The previous scoped validator missed ten stale SHA values covering PN-FP, EverTracer, CTCC, iSeal, and SCW preferred-Teacher/Ba-Student logs. This closure recalculated all 32 and updated only those stale index values. Final gate: declared 32, actual 32, unique composite IDs 32, duplicates 0, broken paths 0, mismatches 0, JSON parse PASS.

## H. Reports

Formal reports exist for PN-FP Bb, EverTracer Bb, CTCC Bb, CTCC Bb2, iSeal Bb, SCW Bb, and the unified master report.

## I. Git

Final Local/GitHub/AutoDL parity and worktree cleanliness are verified after the closure commit and reported in the final handoff. Force/reset/clean/history rewrite are prohibited.

## J. Tests

Closure checks cover JSON parse, strict index integrity, Python compilation, relevant unit tests, diff/conflict checks, secret-like material, tracked size/forbidden payloads, legacy-project paths, and Markdown references. Exact results are reported in the final handoff.

## K. Remaining scientific work

NONE for proactive Bb. Original CTCC Bb remains formally blocked by design.

## L. Remaining metadata work

NONE after all strict gates and three-end Git parity pass.

## M. Safe closure decision

`SAFE_TO_CLOSE_PROACTIVE_BB = YES` only when the post-commit strict validator and Local/GitHub/AutoDL parity pass. No universal-removal, universal-robustness, retention-percentage, checkpoint-level, causal-UP, or universal quality-preservation claim is made.
