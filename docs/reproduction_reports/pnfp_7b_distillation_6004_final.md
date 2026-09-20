# PN-FP 7B same-backbone distillation — Logit recovery

Status: COMPLETED

Teacher, Direct and Paraphrase are unchanged completed references; no re-evaluation was run.
Serialization dtype compatibility fix: Transformers4.44.2 Llama promotes BF16 lm_head logits to FP32; selected targets are explicitly cast to BF16 as in canonical3B Bc. Full vocabulary, positions, token alignment, T2 and CE/KD0.5 are unchanged.

| Condition | PN-FP hits/1024 | Recall % | Retention vs Teacher | ARC | TruthfulQA |
|---|---:|---:|---:|---:|---:|
| Teacher | 804 | 78.515625 | 100% | 42.064846% | 44.199762% |
| direct | 53 | 5.175781 | 6.592040% | 46.843003% | 42.404140% |
| paraphrase | 71 | 6.933594 | 8.830846% | 48.464164% | 43.801800% |
| logit | 144 | 14.062500 | 17.910448% | 44.624573% | 42.416776% |

## Final CPU-only audit (2026-09-20)

Logit is a completed formal result, not the earlier cache-assert failure: 7,500/7,500 steps; fresh-reload144/1024,14.0625% recall,17.91044776119403% retention versus804; ARC44.624573378840%,MC242.416776003683%. Refer to the exact JSON for full precision. No detector or utility was rerun in this audit.

Training-summary wall 3453.137674s; complete training subprocess 3502.650898s. Peak allocated GPU 38.785964GiB; sampled GPU 48.415039GiB; host RSS 19.656898GiB. Parameters finite, zero detector errors/invalid samples.

Final model manifest: `results/pnfp/scale_7b/logit_recovery_6004/logit_final_manifest.json`; manifest SHA256 `3c1b2bfa360ed388be9d12037a14a63af0cf6cc164c22f9d396094255564840b`. Safetensors file SHA256:

- `model-00001-of-00003.safetensors`: `4efbe4e024049d295b97ed8f0989829e5291b654e46cafb4504ab82658ef4897`
- `model-00002-of-00003.safetensors`: `24cbc950aec4d4b8977b6691026da71dec2c86d692b2379022da7df74596f7f5`
- `model-00003-of-00003.safetensors`: `5c67329ad51353aaa82a98c905361a67d64d1fd614f2d830e61ee44246c2398d`

[Unified final summary](7b_scale_extension_final_summary.md) distinguishes historical failed Teachers, the user-accepted804 Teacher, and all final Students. Full current CPU audit evidence is in `results/scale_7b_final_audit/`.
