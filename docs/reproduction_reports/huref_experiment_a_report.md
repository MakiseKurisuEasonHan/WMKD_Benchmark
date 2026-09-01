# HuRef Experiment A report

## Outcome

**BLOCKED_PROTOCOL_AMBIGUITY — scientific result NOT_JUDGED.**

Cont1 `huref_a_cont1_20260901_210000` fixed official joint Mean Pooling (512-d), inference/detach, Llama GQA and config-derived Phi fused QKV/MLP mappings. `PROTOCOL_MEAN_POOLING_UNIT_TEST=PASS` with max_abs_diff=0. Reference A/B, Gemma and Qwen features were persisted, but no detector score is reported.

Phi extraction stopped before invariant computation because 95 frozen canonical token IDs exceed Phi vocab size 32064 (max ID 98956). Official HuRef uses model-specific sorted-token lists, while WMKD froze only a canonical manifest. A Phi-specific manifest or cross-tokenizer mapping was not frozen. No IDs were dropped, clipped, replaced, or remapped.

The old run `huref_a_20260901_201015` is `SUPERSEDED_BY_PROTOCOL_COMPLIANCE_CONTINUATION`. This cont1 is blocked, not a scientific detector failure. Preferred fingerprint: no. Model modified: false. Ba: NOT_STARTED.
