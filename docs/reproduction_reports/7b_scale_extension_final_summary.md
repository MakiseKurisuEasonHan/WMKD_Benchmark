# 7B scale extension: PN-FP and AWM — final verified summary

Scope: **7B same-backbone scale extension for one representative active method (PN-FP) and one representative passive method (AWM)**, specifically same-backbone Llama-2-7B-chat → independently fresh Llama-2-7B-chat Students. Cross-lineage was paused before training. LLMPrint remains paused at 58/200; neither is a completed result in this table.

This closeout reads existing artifacts and hashes files on a CPU-only AutoDL instance. It does not regenerate data, retrain, recalibrate, or rerun detector/utility. Git publication status is recorded separately in `results/scale_7b_final_audit/git_publication_status.json`.

## Model, hardware, and protocol

- Canonical model: `meta-llama/Llama-2-7b-chat-hf@f5db02db724555f92da89c216ac04704f23d4590`; 6,738,415,616 parameters. ModelScope transport: `shakechen/Llama-2-7b-chat-hf@299e68d813ff6f146741f8e8477ed0a57ded4765`. Transport revision is not substituted for canonical upstream identity; per-file hashes bind the downloaded files.
- Training hardware: one NVIDIA RTX PRO 6000 Blackwell Server Edition, 96 GB; 22 CPU cores / 110 GiB cgroup RAM. Teacher work used the earlier smaller data disk; final distillation used cloned 6004 with a 591 GiB data disk. CUDA/PyTorch stack: torch 2.8.0+cu128; training Transformers 4.44.2; AWM detector used the separately recorded 4.51.3 compatibility runtime.
- BF16 full-parameter training, activation checkpointing, `bitsandbytes.optim.adamw.AdamW8bit` 0.50.0. Optimizer-state storage is a hardware adaptation; **not numerical/implementation equivalence to canonical FP32 Adam**.
- Each Student independently starts from clean canonical Llama weights; 20,000 method-specific QA examples, three epochs / 7,500 steps, effective batch 8, maximum sequence 1,024, LR 1e-5, cosine schedule, 225 warmup updates, seed 42, weight decay 0, original chat template and assistant-response masking.
- Paraphraser: canonical Qwen2.5-3B-Instruct with recorded ModelScope provenance; temperature .7, top-p .9, seed 42, length min64 / multiplier1.5 / cap1536. Frozen prompt SHA `085a77a7a32d06f31ec4a11a23977517fef64eee794817a5a1a9ed51a1e45676`. Method-specific Teacher outputs remain separate.
- Bc: same-tokenizer full-vocabulary logits, T=2, CE=.5 and T²KL=.5, all shifted supervised response positions. FP32 forward output is selected then cast to canonical BF16 cache storage (serialization compatibility fix). No top-k approximation.
- Utility: ARC-Challenge normalized accuracy (1,172 examples) and TruthfulQA-MC2 (817), using the recorded evaluator/config. Clean Llama reference: ARC 36.60409556%, MC2 45.75471579%.

## PN-FP Teacher selection

Frozen 1,024 fingerprints: key16 / response1, Perinucleus t=.8, k=3, seed42. WA=.75 trajectory reached best fresh-reload 334/1024 (32.6171875%) and later collapsed to 0/1024. WA=.50 pilot reached 654/1024 (63.8671875%). The WA=.50 extension selected call21 / non-zero update19: fresh-reload **804/1024 (78.515625%)**, with DM=.25. It stopped after update22 because three checks failed to improve materially. Final loss<.005 was not used to claim convergence.
The original extension assessment remained `EXTENSION_COMPLETE_NOT_PREFERRED` because its automatic ≥80% candidate gate was not met. The user subsequently **accepted this 804/1024 checkpoint as the unique formal Teacher** and authorized distillation. The old assessment is historical, not the current selection status. See `preferred_teacher_selection.json`; no historical measurement is overwritten.
The extension restored Adam history by deterministic replay from clean initialization, matched 291 checkpoint tensors bitwise at the extension boundary, then continued; original optimizer-state files were not independently retained/hashed. Teacher parameters: BF16 full FT, WA=.50, DM=.25, 8-bit AdamW; frozen fingerprints were not regenerated.

## Unified measured results

| Method | Condition | Native ownership score | Detected / retention vs Teacher | ARC-Challenge | TruthfulQA-MC2 |
|---|---|---|---|---:|---:|
| PN-FP | Teacher | 804/1024 (78.515625%) | 100.000000% retention | 42.064846% | 44.199762% |
| PN-FP | Direct | 53/1024 (5.175781%) | 6.592040% retention | 46.843003% | 42.404140% |
| PN-FP | Paraphrase | 71/1024 (6.933594%) | 8.830846% retention | 48.464164% | 43.801800% |
| PN-FP | Logit | 144/1024 (14.062500%) | 17.910448% retention | 44.624573% | 42.416776% |
| AWM | Reference | 1.0000000000000000 | Yes | 36.604096% | 45.754716% |
| AWM | Direct | 0.9999952428042889 | Yes | 46.843003% | 42.953599% |
| AWM | Paraphrase | 0.9999933559447527 | Yes | 47.781570% | 43.869722% |
| AWM | Logit | 0.9999957373365760 | Yes | 44.112628% | 42.639766% |

PN-FP retention is hits / 804, not raw recall. AWM uses native weight-space similarity with strict score > frozen threshold; the metrics must not be compared numerically across methods. PN-FP Logit retains **144/1024 = 14.0625% recall / 17.910448% of Teacher hits**, higher than Direct and Paraphrase but far below the Teacher.

## AWM calibration and cache evidence

Reference self/reload score=1.0. Canonical all-layer Wq/Wk extraction, vocabulary/dimension alignment, full layer matching where required, and unbiased linear CKA are unchanged. Official source commit `bc20ff8e63cec57f5da422ae065686ced275e76d`.
- google/gemma-2b: 0.0033861661672239685
- Qwen/Qwen2.5-3B-Instruct: 0.0019936248814840241
- microsoft/Phi-3-mini-128k-instruct: 0.0075668158612778313

Frozen threshold **0.007566815861277831 = max of these three fixed negative scores**; ties are negative. Calibration SHA `627107dc6c7db1569a43c2f94f67b5e7f9314bdcd2968c36f288f07b83b47a3f` was frozen before Student training and remains unchanged.
AWM cache: 157/157 shards, 520,187 supervised positions, full vocabulary32,000, BF16; 33,291,968,000 bytes. Shard hashes/manifest were verified; reproducible raw logits were deleted only after all final Students/results were verified. Dataset, manifests and final models remain. Paraphrase:20,000 successes, 6 retries, zero identity fallback; no scientific changes.

## Runtime and memory

| Method | Student | Training-summary seconds | Whole training subprocess seconds | Peak allocated GPU GiB | Peak sampled GPU GiB | Peak host RSS GiB |
|---|---|---:|---:|---:|---:|---:|
| PN-FP | Direct | 3394.786 | 3421.198 | 38.786 | 53.040 | 19.657 |
| PN-FP | Paraphrase | 3426.772 | 3452.740 | 38.722 | 53.005 | 19.662 |
| PN-FP | Logit | 3453.138 | 3502.651 | 38.786 | 48.415 | 19.657 |
| AWM | Direct | 3381.235 | 3409.528 | 38.672 | 46.960 | 19.657 |
| AWM | Paraphrase | 3425.495 | 3454.567 | 38.636 | 49.407 | 19.661 |
| AWM | Logit | 3455.138 | 3510.376 | 38.671 | 44.817 | 19.656 |

The two runtime definitions differ: the subprocess includes loading/preparation/exit overhead. RSS comes from the process high-water mark; GPU sampling and PyTorch allocated peaks measure different quantities and are not interchangeable.
Teacher extension training-loop wall=1600.345s; whole training process including replay/trajectory/utility=1709.475s; final standalone detector=22.651s. Peak allocated51.373GiB, sampled52.618GiB, processRSS29.418GiB, cgroup78.028GiB. AWM calibration subprocess time including the preserved, repaired Phi3 loader attempt=192.30s; this is not watermark training. Its reported 2.390GiB aggregate GPU peak includes sampling, unlike the allocated-only Student column.

## Artifact verification and project consistency

Full final-file SHA lists: `results/scale_7b_final_audit/verification_inputs.json`; fresh CPU-only remote verification: `verification_final.json`. The final model identity is the complete per-file manifest, not a fabricated single checkpoint hash. Runtime table manifest paths and manifest SHA256 are in `unified_results.json`.
PN-FP Teacher and six final Students are kept separately; clean reference is unchanged. LLMPrint58 completed GCG fingerprints and all13 negative-model directories are preserved and checked against their original manifests. No LLMPrint restart, cross-lineage execution, model/data download, or experiment rerun is part of this audit.
Same-lineage 3B results are historical references and were not changed. Project status/TODO/decisions/logs now point to this scale-extension summary. Old failure/pilot/initial no-shutdown entries are historical; they are not new execution instructions.

## Limitations and bounded conclusion

In this **7B same-backbone extension for PN-FP and AWM**, PN-FP ownership hits decrease strongly after Direct, Paraphrase, and Logit distillation; Logit has higher retention than Direct/Paraphrase but still substantially fewer hits than the Teacher. AWM native weight-space scores remain near1.0 after all three training conditions.
These are single-seed, method-specific endpoint observations, not significance tests or universal active/passive claims. The two methods use different Teacher/data conditions and different native metrics. Every Student begins from the same pretrained backbone lineage; near-reference AWM scores may reflect initialization/parameter similarity, not causal transmission of a new ownership signal. Utility remains broadly usable on these two recorded benchmarks: ARC increases versus clean while MC2 declines; the two benchmarks do not prove global utility preservation. This is not all passive methods, all active methods, all7Bmodels, or a cross-lineage evaluation.

Primary reports: [PN-FP](pnfp_7b_distillation_6004_final.md), [Teacher trajectory/extension](pnfp_7b_wa050_extension_20260919.md), [AWM](awm_7b_extension.md).

## Current closeout and publication status (2026-09-20)

CPU-only verification PASS:22 artifact groups, 270 files hashed,81 critical evidence files identical between AutoDL and local; no science workers. Prior AWM shutdown script exit0 is now independently recovered from disk; current CPU-only restart remains on. No new evaluation/training/download or cleanup was performed.

**Git publication verified:** normal SSH push to the original private repository succeeded, preserving all 42 local commits. Five required files were independently read from GitHub at published commit `3a6a924a0875e19f3704ef68699d345e0962b8ae` and their Git blob SHAs matched. GitHub is now the canonical source for the completed 7B reports and evidence (large model weights remain at their manifest locations). Previous authentication failures are retained as historical receipts. No force push or history rewrite.
