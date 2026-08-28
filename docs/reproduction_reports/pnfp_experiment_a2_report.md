# PN-FP Experiment A2 Formal Report

Training run `pnfp_exp_a2_20260828_025240` remains operationally **FAILED** at external ARC acquisition. Training, checkpoint, reload, watermark, base control, and ordinary-generation artifacts were validated and reused.

Evaluation continuation: `pnfp_exp_a2_eval_20260828_105530`.

A2 watermark: 956/1024 (93.359375%); base: 1/1024 (0.097656%); A1: 1019/1024 (99.511719%).

Ordinary generation: `{"base_summary": {"calls": 10, "max_token_hits": 3, "obvious_repetition": 0}, "a1_summary": {"calls": 10, "max_token_hits": 10, "obvious_repetition": 0}, "a2_smoke_summary": {"calls": 10, "max_token_hits": 3, "obvious_repetition": 0}}`

ARC base/A2/delta: 0.448805 / 0.443686 / -0.005119.

TruthfulQA MC2 base/A2/delta: 0.505451 / 0.467428 / -0.038023.

Watermark gate: **passed**. Utility gate: **passed**.

Scientific judgement: **A2 is the preferred PN-FP teacher for future Ba**.
