# AWM 7B representative passive-method extension

Status: formal calibration complete; new clean-reference data generation is being launched. No Student result yet. Latest user authorization explicitly forbids automatic shutdown at completion. LLMPrint remains paused58/200; its fingerprints,13 negatives, manifests and logs are preserved and are not modified by this campaign.

Clean reference and all three independently initialized Students use `meta-llama/Llama-2-7b-chat-hf`, revision `f5db02db724555f92da89c216ac04704f23d4590`. No PNFP Teacher, Student, generated data or logits are used. Only generic validated training/cache/benchmark infrastructure and the exact clean Base utility reference are reused.

## Frozen formal calibration

AWM canonical source `bc20ff8e63cec57f5da422ae065686ced275e76d`; all-layer Wq/Wk extraction, token-string vocabulary overlap, absolute-cosine dimension LAP/sign correction, full layer LAP when counts differ, official unbiased linear CKA and original mean aggregation remain unchanged.

| Condition | Native score |
|---|---:|
| Reference/self |1.0|
| Independent fresh reload |1.0|
| google/gemma-2b |0.0033861661672239685|
| Qwen/Qwen2.5-3B-Instruct |0.001993624881484024|
| microsoft/Phi-3-mini-128k-instruct |0.007566815861277831|

Frozen7B threshold = **0.007566815861277831**, the maximum of these three canonical negatives. Positive iff score strictly exceeds threshold; ties negative. No3B threshold reused. Calibration SHA256: `627107dc6c7db1569a43c2f94f67b5e7f9314bdcd2968c36f288f07b83b47a3f`. Frozen before any Student; no later recalibration.

The Phi3 snapshot lacks old remote-code Python files referenced by its config. The installed native Phi3 loader exposes the same verified weight tensors; the detector performs no model forward. Canonical config-derived fused Q|K|V shape checks remain in place. The first failed loader attempt is preserved under engineering_history, successful Gemma/Qwen results reused, and only the missing Phi3 result completed. This is loader compatibility, not a score/threshold/representation change. Calibration runtime reporting includes both attempts.

## Three independent distillations

Canonical Passive Ba/Bb/Bc: newly generated20k ordinary clean-reference responses, three epochs/7500updates, effective batch8, sequence1024,LR1e-5,cosine/225warmup,weight decay0,seed42,existing chat template and assistant-only masking. BF16 full parameter, activation checkpointing and bitsandbytes AdamW8bit0.50.0 retain the already accepted7B hardware adaptation; optimizer storage is not claimed identical to FP32 Adam.

Untargeted Qwen paraphrasing uses existing byte-verified ModelScope snapshot revision `8f4992eda43eea7c770690ddc0de8f732da246f5`; temperature0.7,top_p0.9,seed42,min64/ceil1.5×source/cap1536 and the existing atomic <=1-token identity rule. Requested prompt name `response_transformation_prompt.txt` resolves to the existing `configs/distillation/passive5_shared_bb_paraphrase_prompt_v1.txt` by exact SHA `085a77a7a32d06f31ec4a11a23977517fef64eee794817a5a1a9ed51a1e45676`; no byte change.

Bc: T2,CE0.5/KD0.5,KL(Teacher||Student),all shifted supervised positions,full-vocabulary BF16 targets. Count actual supervised tokens before disk admission; stream/shard and verify SHA before training. Cast selected returned FP32 logits to BF16 only for canonical serialization compatibility. Teacher is unloaded before Student training.

Each Student: final-only save, final SHA, fresh-reload native AWM detector against frozen threshold, ARC-Challenge and TruthfulQA-MC2 once, then next stage irrespective of high/low detector score. No tuning/retraining for stronger score. Each stage has disk/GPU gates and runtime telemetry; local guardian syncs evidence and commits stage results. Hard scientific/integrity/nonfinite/divergence/disk blocks stop the affected phase for review; ordinary engineering issues may be repaired without scientific changes.

Remote outputs: `/root/autodl-tmp/WMKD_Benchmark_data/awm_7b`; evidence `results/awm/scale_7b`. Exact config: `configs/watermark/awm_7b.json`. After all formal results and local verification: keep instance on, GPU idle, await user decision. No other passive method or LLMPrint continuation is authorized.
