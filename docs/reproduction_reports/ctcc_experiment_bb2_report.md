# CTCC Experiment Bb2 — final scientific closure

`ctcc_bb2_20260905_011104` is a distinct follow-up variant. Original CTCC Bb remains `BLOCKED_AT_PREPROCESSING_ACCEPTANCE_GATE` at 202 > 200. Bb2 removes only that experiment-level aggregate gate; the frozen per-sample UP transformation and downstream protocol are unchanged.

Original Bb resolved outputs reused: 17269. Final processed records: 20,000. Identity fallbacks: 236 (1.180000%).

Student: 7,500 steps, three epochs, BF16, LR 1e-5, effective batch 8; fresh reload and PRIVATE archive verification passed.

Detector (WMKD operational equality detector, not official CTCC): Teacher 95/95; Base 0/95; Ba 0/95; Bb2 0/95 triggers; negatives 0/205.

Utility: ARC 0.489761 (delta +0.005973); TruthfulQA MC2 0.448507 (delta -0.002107). Generation sanity passed.
