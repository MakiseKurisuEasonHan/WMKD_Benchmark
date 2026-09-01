# ZeroPrint Experiment A Log

Status: PREPARATION/SMOKE ONLY. Formal A and Ba NOT STARTED. Official commit `16a02aa`; smoke results belong under `results/zeroprint/smoke/` and cannot establish reproduction.

## 2026-09-01 bounded smoke

`zeroprint_smoke_20260901` completed in 6.80394 s using two HumanEval-like prompts, one deterministic perturbation each, four greedy 8-token generations, MPNet embeddings `[4,768]`, a finite-difference Jacobian path, mean aggregation, and correlation self-check. Peak allocated VRAM was 6,438,586,880 bytes and `model_modified=false`. The official config was reconfirmed as HumanEval, 2 base queries, 4 augmentations, 20 repeats, `all-mpnet-base-v2`, Jacobian, mean, and correlation. ModelScope resolve supplied a structurally valid 200-key MPNet PyTorch ZIP, but its bytes/SHA differed from the checked-out LFS pointer; both original pointers were preserved and the discrepancy is a provenance warning. Formal A requires an official-budget generation-speed gate and frozen negative calibration.
