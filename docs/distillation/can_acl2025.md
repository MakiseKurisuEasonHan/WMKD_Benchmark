# CAN ACL 2025 adaptation for PN-FP Ba/Bb

## Sources and attribution

- Paper: Pan et al., *Can LLM Watermarks Robustly Prevent Unauthorized Knowledge Distillation?*, ACL 2025, Anthology `2025.acl-long.648`.
- Official repository: `THU-BPM/Watermark-Radioactivity-Attack@9a2b01af1fadcece2893d32460ed9449093f8fb9` (the reviewed `main` HEAD, 2025-06-18).
- The official repository implements WN. Its README explicitly says UP and TP require a user-provided paraphrasing module. Our Bb method is therefore **paper-defined UP + project-owned Dipper integration**, not official author UP code.
- Dipper model: `kalpeshk2011/dipper-paraphraser-xxl@c1fbf7a958a2aab022e9e6f81f7a3139f9e6ee3c`; tokenizer: `google/t5-v1_1-xxl@3db68a3ef122daf6e605701de53f766d671c19aa`.

## Paper setting and benchmark adaptation

The CAN paper uses GLM-4-9B-chat teachers, Llama-7B and Llama-3.2-1B students, approximately 200,000 teacher QA pairs, full SFT through LLaMA-Factory for 3 epochs at learning rate `1e-5`, and Dipper for UP. It reports that UP is computationally expensive and reports experiments on eight NVIDIA H800 GPUs.

WMKD_Benchmark deliberately uses a resource-bounded configuration: a successful PN-FP Llama-3.2-3B-Instruct teacher, a fresh unwatermarked canonical Llama-3.2-3B-Instruct student at revision `0cb88a4f764b7a12671c53f0838cd831a0843b95`, and exactly 20,000 paired filtered samples on one RTX PRO 6000 96GB. CAN ACL 2025 used Llama-3.2-1B as one of its students; WMKD_Benchmark intentionally uses the same-size 3B teacher and student to control for model-capacity reduction and isolate the effect of direct knowledge distillation on watermark persistence. This is an intentional adaptation, not a complete CAN reproduction. We do not automatically scale to 200k; 50k may be discussed only if later utility results show essentially no meaningful transfer.

## Paired design

Teacher generation creates more than 20k raw candidates across general knowledge, reasoning, writing, summarization/editing, classification, mathematics, coding and reading comprehension. Filtering and deduplication produce stable IDs and one frozen manifest. Ba trains on `teacher_raw_answer`. Bb uses the same IDs and unchanged instruction/input, replacing only the target with `UP_paraphrased_answer`. Failed paraphrases remain recorded and stop the pipeline; samples are never silently dropped.

Dipper lexical diversity `60`, order diversity `0`, greedy/default decoding and answer-only operation are **WMKD_Benchmark operational adaptations**, not reported CAN hyperparameters. They must be preserved in the run config. Dipper's safetensors weights are about 45.6GB; download safetensors only, not duplicate PyTorch `.bin` weights.

## Evaluation and interpretation

The original unwatermarked 3B control, Ba and Bb students use the exact Experiment A PN-FP detector and frozen 1024 keys, with response length 16. Utility evaluation is ARC Challenge and TruthfulQA Multiple Choice. MTBench is initially excluded because of judge/API and time cost.

PN-FP is a trigger/fingerprint behavior, not an ordinary token-level output watermark. Ordinary QA answers may carry little fingerprint signal, so a large Ba detection drop is scientifically plausible. A successful report must separately assess watermark retention and useful knowledge transfer; watermark loss without utility improvement is not an unqualified successful distillation attack.

## Storage and retention

Read-only audit on 2026-08-28: the 1TB data disk used 20GB and had 981GB available. Major consumers were PN-FP artifacts 7.4GB, base models 6.0GB, and completed runs 6.0GB. The system disk used 11GB/30GB and had 20GB free.

For Ba, the canonical 3B base and watermarked 3B teacher already exist and require no duplicate storage. Estimated new usage is roughly 5–20GB for raw/frozen QA, 6GB for the final BF16 student, 45–70GB for one rolling full-training checkpoint plus optimizer/scheduler state, 5–15GB for evaluation caches, and under 2GB for logs/results. With a 20GB safety margin, plan for about 81–133GB additional storage. The data disk's 981GB free is sufficient. All large paths and caches must remain under `/root/autodl-tmp/WMKD_Benchmark_data`; `/root/.cache` is forbidden. Each trainer retains one rolling/recovery checkpoint plus the final loadable weights. Cleanup requires a later explicit safe stage.
