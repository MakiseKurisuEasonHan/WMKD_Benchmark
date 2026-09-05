# CTCC Experiment Bb2 — final scientific closure

`ctcc_bb2_20260905_011104` is a distinct follow-up variant. Original CTCC Bb remains `BLOCKED_AT_PREPROCESSING_ACCEPTANCE_GATE` at 202 > 200. Bb2 removes only that experiment-level aggregate gate; the frozen per-sample UP transformation and downstream protocol are unchanged.

Original Bb resolved outputs reused: 17269. Final processed records: 20,000. Identity fallbacks: 236 (1.180000%).

Student: 7,500 steps, three epochs, BF16, LR 1e-5, effective batch 8; fresh reload and PRIVATE archive verification passed.

Detector (WMKD operational equality detector, not official CTCC): Teacher 95/95; Base 0/95; Ba 0/95; Bb2 0/95 triggers; negatives 0/205.

Utility: ARC 0.489761 (delta +0.005973); TruthfulQA MC2 0.448507 (delta -0.002107). Generation sanity passed.

## Protocol, environment, provenance, and archives

Bb2 removed only the global `identity_fallback_count <= 200` experiment-level gate. It hash-verified and reused 17,269 original-Bb resolved records, processed 2,731 new records, and completed 20,000 with 236 fallbacks (1.18%); physical/content SHA are `db5928...f52ed` / `416531...9ab8`.

Parity is durably `PASS`; no canonical numeric `fields_checked=19` exists, so no 19/19 claim is made. The fresh canonical 3B Student completed 7,500 steps/3 epochs with loss 1.10743791624705 and reload PASS. Detector semantics are exactly `generated_answer.strip() == "IAMALIVE"`; results are 0/95 triggers, 0/205 negative activations, zero errors. Exact utility is ARC 0.48976109215017066 and TruthfulQA 0.44850679576156427; sanity PASS.

Processed20k and Student archives are PRIVATE and passed independent redownload/SHA verification; Student redownload reload PASS. Runtime, configuration, manifests, and paths are in the canonical full log. The detector is operational WMKD evidence, not the official CTCC detector.
