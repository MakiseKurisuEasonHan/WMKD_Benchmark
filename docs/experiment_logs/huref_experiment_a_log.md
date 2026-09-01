# HuRef Experiment A Log

Status: PREPARATION/SMOKE ONLY. Formal A and Ba NOT STARTED. Official commit `9c34548a`; smoke results belong under `results/huref/smoke/` and cannot establish reproduction.

## 2026-09-01 bounded smoke

`huref_smoke_20260901` completed in 5.51993 s at compatibility-only scale: 8 deterministic tokenizer IDs, last two layers 26/27, six `[8,8]` WqWk/WvWo/WuWd terms, Mean Pooling, and ICS self score 1.0. Llama GQA required the declared engineering mapping `repeat_interleave_kv_heads_to_query_heads`; no encoder was needed. Peak allocated VRAM was 6,988,555,264 bytes and `model_modified=false`. The 8-token result cannot predict the official 4096-token quadratic path, so formal A is `TIME_BUDGET_RISK` until the sorted-token list and bounded scaling evidence are frozen.
