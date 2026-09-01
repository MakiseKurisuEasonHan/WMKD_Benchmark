# AWM Experiment A Log

Status: PREPARATION/SMOKE ONLY. Formal A and Ba NOT STARTED. Official commit `bc20ff8e`; smoke results belong under `results/awm/smoke/` and cannot establish reproduction.

## 2026-09-01 bounded smoke

`awm_smoke_20260901` completed in 5.80222 s. Llama layer 27 mapped to Wq `[3072,3072]` and Wk `[1024,3072]`; identity LAP and the pinned official unbiased linear-CKA implementation returned 1.0 for Wq, Wk, and the reported mean over 64 deterministic rows. Peak allocated VRAM was 6,484,990,464 bytes and `model_modified=false`. Formal A remains blocked on exact layer aggregation, negative identities, threshold/calibration, and the repository's absent explicit license.
