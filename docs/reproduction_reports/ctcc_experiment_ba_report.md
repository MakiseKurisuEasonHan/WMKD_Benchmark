# CTCC Experiment Ba Reproduction Report

## Outcome

CTCC Ba is complete. The preferred CTCC A Teacher activated the operational exact-match trigger on 95/95 trigger records; the fresh-canonical direct-distillation Student activated it on 0/95, equal to Base 0/95. Student false activation was 0/205 combined negative records, ARC accuracy was 0.48378839590443684, TruthfulQA MC2 was 0.4506136480297226, and ordinary generation passed.

This supports only the bounded conclusion that CTCC's tested trigger behavior was not retained by the Student under the fixed same-family, same-size, hard-label direct-distillation recipe. It is not a universal claim about CTCC, other students, datasets, or attacks.

## Provenance

- Official CTCC source: `Xuzhenhua55/CTCC@8db93218260bed31b8f18acc9c6ac3e1955d3a42`.
- Teacher: `ctcc_a_20260829_190251`; LoRA adapter SHA256 `36957869183ee2581c7377ba973de0aef4d162c7caa3a2353684cf931ae429cd`.
- Frozen QA: exactly 20,000; SHA256 `621c9aedcf3a4a1db86a4848bbf93fa893d18022f15b913e8aeeb28739412484`.
- Student: `ctcc_ba_20260830_025244`; canonical revision `0cb88a4f764b7a12671c53f0838cd831a0843b95`; full-parameter SFT, three epochs, LR `1e-5`, BF16, batch 8, 7,500 steps.
- Evaluation: immutable failed parent `ctcc_ba_eval_20260830_033556` plus infrastructure-only continuation `ctcc_ba_eval_20260830_033556_cont1`.

## Integrity and deviations

The generation continuation corrected only the resume cursor and raised the total-raw fail-safe guard; prompt protocol, sampling, parser, filter, deduplication, Teacher, and deterministic freeze remained unchanged. The evaluation continuation corrected only import deployment and added fail-fast preflight before fresh reload. Neither is Ba2 or a scientific-configuration change.

ModelScope archival includes only the preferred Teacher LoRA adapter and Student inference-ready final model. Both repositories are private and remain `uploaded_to_modelscope_awaiting_destination_hash_verification`, with `destination_verified=false` until an independent destination download completes full SHA256 comparison.
