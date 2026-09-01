# Full Experiment Logs Audit — 2026-09-01

## Scope and integrity rule

This closure audit covers the preferred Teacher and standardized Ba Student for PN-FP, EverTracer, CTCC, iSeal, and SCW. Canonical logs use schema `wmkd.full-experiment-log.v1`; the global index uses `wmkd.full-experiment-log-index.v1`. Each log embeds its machine-readable source documents and their SHA256 values. Missing historical facts are left unavailable and are never inferred from chat history, loss, gradient norm, or timing.

## Canonical object inventory

| Method | Role | Experiment | Full JSON | Persisted training trajectory | Detector | Utility | ModelScope | Formal intermediate checkpoints | Disappearance localization |
|---|---|---:|---|---:|---|---|---|---|---|
| PN-FP | preferred Teacher | A2 | `results/pnfp/preferred_teacher/full_experiment_log.json` | unavailable | available | available | private archive recorded | none inventoried on current AutoDL | N/A (Teacher) |
| PN-FP | Ba Student | Ba | `results/pnfp/ba_student/full_experiment_log.json` | unavailable | available | available | private archive recorded | none inventoried on current AutoDL | **NO**; Teacher-before vs final-Student-after only |
| EverTracer | preferred Teacher | A | `results/evertracer/preferred_teacher/full_experiment_log.json` | unavailable | available | available | private archive recorded | none inventoried on current AutoDL | N/A (Teacher) |
| EverTracer | Ba Student | Ba | `results/evertracer/ba_student/full_experiment_log.json` | 7,500 step timings | available | available | private archive recorded | final model only | **NO**; Teacher-before vs final-Student-after only |
| CTCC | preferred Teacher | A | `results/ctcc/preferred_teacher/full_experiment_log.json` | 286 trainer history records | available | available | private archive recorded | step 1400 and final 1428 adapters | N/A (Teacher) |
| CTCC | Ba Student | Ba | `results/ctcc/ba_student/full_experiment_log.json` | 7,500 step timings | available | available | private archive recorded | final step 7500 with optimizer state | **NO**; no intermediate detector evaluation |
| iSeal | preferred Teacher | A6 | `results/iseal/preferred_teacher/full_experiment_log.json` | 1,500 history records | available | available | private archive recorded | none inventoried on current AutoDL | N/A (Teacher) |
| iSeal | Ba Student | Ba | `results/iseal/ba_student/full_experiment_log.json` | 7,500 step timings | available | available | private archive recorded | final model only | **NO**; Teacher-before vs final-Student-after only |
| SCW | preferred Teacher | A2 | `results/scw/preferred_teacher/full_experiment_log.json` | 250 trainer log records plus 2,500-step runtime telemetry retained on AutoDL | available | available | private archive recorded | final step 2500 with optimizer state | N/A (Teacher) |
| SCW | Ba Student | Ba | `results/scw/ba_student/full_experiment_log.json` | 7,500 step timings | available | available | private archive recorded | final step 7500 with optimizer state | **NO**; no intermediate detector evaluation |

## Completeness and limitations

- All 10/10 canonical JSON files exist and share the required top-level structure.
- Full source summaries, manifests, archive verification, continuation/failure evidence, detector semantics, utility results, artifact lineage, and bounded conclusions are preserved without cross-method reinterpretation.
- PN-FP Teacher/Student and EverTracer Teacher have no persisted per-step trajectory in the currently available source hierarchy. Their logs explicitly record this gap.
- Step timing or training loss is not watermark evidence. None of the five Ba experiments persisted detector measurements at intermediate Student checkpoints; consequently none can strictly locate the optimizer step at which detectability changed.
- CTCC Teacher checkpoints at steps 1400/1428 describe Teacher construction, not Ba disappearance. CTCC/SCW Ba final checkpoints contain optimizer state but do not provide an earlier detector time series.
- Future analysis can compare Teacher-before and final-Student-after for all five methods, analyze final retention/degradation and utility deltas, and correlate training dynamics descriptively where telemetry exists. It cannot claim a causal or exact disappearance step without a future, separately authorized offline checkpoint-generation/detector study.

## Source priority and conflicts

The builder follows immutable artifacts → machine-readable summaries → reports → experiment logs → trainer state/telemetry → project records. No unresolved numerical conflict was silently selected during generation. Raw source snapshots remain embedded so downstream analysis can audit normalized fields.
