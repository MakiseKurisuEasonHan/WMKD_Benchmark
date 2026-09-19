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
