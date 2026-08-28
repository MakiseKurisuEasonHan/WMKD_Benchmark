# PN-FP Experiment A2 Formal Report

## Identity

- Method: PN-FP (Perinucleus fingerprinting).
- Experiment: A2 — Utility-Preserving Teacher.
- Parent training run: `pnfp_exp_a2_20260828_025240`.
- Immutable evaluation continuation: `pnfp_exp_a2_eval_20260828_105530`.

## Objective

A2 tests whether the official PN-FP utility-preserving regularizers can retain a strong fingerprint while avoiding the severe ordinary-generation degradation observed in A1, producing a suitable teacher for direct-distillation Experiment Ba.

## Backbone and provenance

- Backbone: `meta-llama/Llama-3.2-3B-Instruct`.
- Fixed revision: `0cb88a4f764b7a12671c53f0838cd831a0843b95`.
- Initialization: fresh canonical unwatermarked weights.
- Official PN-FP source: `SewoongLab/scalable-fingerprinting-of-llms@fdceaba14bd3e89340916a6a40e27c945d48460e`.
- Fingerprints: the same frozen 1,024 A1 keys.

## Formal configuration

| Setting | Value |
|---|---:|
| Fingerprints | 1,024 |
| Key / generation / training response lengths | 16 / 16 / 1 |
| Epochs / optimizer steps | 30 |
| Learning rate | 5e-5 |
| Weight decay | 1e-4 |
| Per-device batch size | 8 |
| Precision | BF16 |
| Parameters | Full parameter |
| LoRA | Off |
| Seed | 42 |
| WA strength | 0.75 |
| DM benign proportion | 0.25 |
| Benign source | Official `benign.json` |
| Distributed optimizer | DeepSpeed ZeRO-2 CPU offload |

## WA and DM provenance

WA uses the official `finetune_multigpu.py::ModelAverageCallback` through `--forgetting_regularizer_strength`. At each official epoch/optimizer-update boundary it interpolates trained weights toward frozen base weights; A2 uses the paper/main value 0.75. DM uses official benign mixing through `--benign_proportion`, `get_fingerprint_ds(... strategy="english", use_benign_response=True)`, and `MixedDataCollator`; beta 0.25 gives six fingerprint and two benign samples in a normal batch of eight. The official `benign.json` SHA256 is `bd18da3b5a56002822a9789d83667452597ccc16979df3277fe2d04ff10a0201`.

## Training

Training completed 30/30 optimizer steps. Final `eval_loss` was 0.3678587. No OOM, CUDA error, or NaN was observed. The final checkpoint was saved, checkpoint validation succeeded, and reload validation passed.

## Operational interruption

The parent training run is operationally marked **FAILED**, but not because training or its reusable scientific artifacts failed. After training, checkpoint/reload validation, full PN-FP evaluation, base control, and ordinary-generation diagnostics had completed, the downstream ARC loader could not acquire `allenai/ai2_arc` from the Hub. The wrapper therefore failed at `arc_truthfulqa`. The immutable parent run remains unchanged.

## Evaluation continuation

The immutable evaluation-only run `pnfp_exp_a2_eval_20260828_105530` reused the validated checkpoint without retraining. It pinned ARC Challenge to `allenai/ai2_arc@210d026faf9955653af8916fad021475a3f00453` and TruthfulQA to `truthful_qa@741b8276f2d1982aa3d5b832d3ee81ed3b896490`, verified local files, and loaded both tasks with Hub and datasets offline modes enabled.

## Watermark results

| Model | Detected | Total | Rate | Invalid | Errors |
|---|---:|---:|---:|---:|---:|
| Canonical base | 1 | 1,024 | 0.09765625% | 0 | 0 |
| A1 | 1,019 | 1,024 | 99.511719% | 0 | 0 |
| A2 | 956 | 1,024 | 93.359375% | 0 | 0 |

A2 remains strongly distinguishable from the canonical base. Relative to A1, regularization reduces detection by 63 keys, or 6.15234375 percentage points.

## Utility results

| Benchmark | Canonical base | A2 | A2 − base |
|---|---:|---:|---:|
| ARC Challenge `acc_norm` | 0.44880546075085326 | 0.44368600682593856 | -0.005119453924914696 |
| TruthfulQA MC2 | 0.505450760153828 | 0.4674279212401518 | -0.03802283891367614 |

## Ordinary-generation diagnostic

The fixed diagnostic used 10 prompts per model. Canonical base had 3/10 max-token hits and 0 obvious repetitions; A1 had 10/10 max-token hits and 0 detector-flagged obvious repetitions, with independent diagnostics establishing severe continuation/repetition collapse; A2 had 3/10 max-token hits and 0 obvious repetitions. No additional coherence score or normal-termination metric was produced, so none is fabricated here.

## Scope and limitations

- This is a resource-bounded 3B reproduction on one RTX PRO 6000 rather than a full-scale replication of every paper setting.
- The current formal utility suite is ARC Challenge plus TruthfulQA MC2, not the full OpenLLM utility suite.
- Ordinary-generation evidence is bounded and uses 10 fixed prompts per compared model.
- A1 retained a stronger watermark but exhibited severe ordinary-generation degradation; A2 deliberately trades a modest amount of detection for substantially better bounded utility behavior.

## Final bounded conclusion

The watermark gate passed at 956/1024 and the utility gate passed against the canonical base. Within the stated evaluation scope, A2 is a strong, utility-preserving PN-FP teacher and is the **preferred PN-FP teacher for Ba**.
