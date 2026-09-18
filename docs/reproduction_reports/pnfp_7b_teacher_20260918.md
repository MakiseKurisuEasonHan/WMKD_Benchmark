# PN-FP 7B formal Teacher: completed, watermark not detected

The authorized fresh formal run completed all40 optimizer calls (38 nonzero-LR updates). Fresh-reload detector is **0/1024**, invalid0/errors0. **PREFERRED_TEACHER=NO**, successful-Teacher benchmark eligibility=NO. Utility was largely preserved, but the watermark objective failed. Direct MD was not prepared or started because its Teacher-success condition was not met. No optimizer ablation, scientific tuning, extra epochs, replacement model or shutdown followed.

## Frozen protocol and adaptation

Model `meta-llama/Llama-2-7b-chat-hf@f5db02db724555f92da89c216ac04704f23d4590`; the same frozen1024 fingerprint manifest, SHA `fa231b31aa10bf19dff0285eaff9457ad41a8f4ee2bcc9089a9d3ac76c1caaf7`. Key16/response1, Perinucleus t0.8/k3, seed42, WA0.75/DM0.25, chat template, BF16 model/forward/backward/grads, activation checkpointing. All6,738,415,616 parameters trainable. No fingerprint regeneration.

Exact optimizer `bitsandbytes.optim.adamw.AdamW8bit`0.50.0, nonpaged blockwise8-bit state, min8bit4096, LR5e-5, betas0.9/0.999, eps1e-8; weight decay1e-4 with original norm/bias exclusions. Single-GPU Trainer without ZeRO/offload. Optimizer moment storage is a hardware engineering adaptation, **not equivalent to canonical FP32 Adam implementation**. Model weights remain unquantized BF16.

Sequence64; microbatch6 fingerprint+2 benign, accumulation171, one full-batch-style update per epoch. Original DeepSpeed0.16.9 WarmupDecayLR standalone scheduler and40-call horizon retained, including two zero-LR calls. Max40; unrounded mixed training loss<0.005 early stop. Final-only save. Existing exact first-token greedy detector. The resolved runtime config and exact executed source disambiguate generic TrainingArguments optimizer/scheduler defaults and inactive legacy pilot fields.

## Training and detector

- Stop: `MAX_40_EPOCHS`; early-stop threshold was never reached.
- Train loss: 23.592495 initially, minimum 3.775902, final 22.656378.
- Mean nonzero update: 24.7570s (excludes epoch evaluation/save overhead).
- Training wall: 1325.680s (22.09min); including final save/hash: 1356.488s.
- GPU sampled peak: 51.9932GiB; PyTorch allocated 51.0252GiB, reserved 51.3398GiB.
- Host training process RSS peak: 29.4177GiB; cgroup sampled2s peak: 40.2044GiB. Sampling can miss transient peaks.
- No detected NaN/Inf or OOM. Final full1024 detector fresh-reload: **0 matches**, invalid0/errors0.

Light checks used the same first128 after WA, every5 updates, with RNG/model training mode restored. They never controlled stopping and are not checkpoint selection results.

| Update | Subset recall |
|---|---:|
| 5 | 48/128 |
| 10 | 44/128 |
| 15 | 43/128 |
| 20 | 43/128 |
| 25 | 39/128 |
| 30 | 31/128 |
| 35 | 0/128 |
| 40 | 0/128 |

The intermediate learning gain disappeared by the final epochs. These observations do not establish a causal explanation; no unapproved optimizer/memory ablation or recovery from intermediate weights was performed.

## One complete paired benchmark utility

Existing `pnfp_a2_benchmark_eval.py`: ARC-Challenge test1172 and TruthfulQA-MC2 validation817, chat template, BF16, batch8, unchanged scoring and evaluation seeds. The initial loader lacked ARC train, which lm-eval0.4.3 requires during task construction even at zero-shot. That attempt failed before scoring; its log/code are preserved. Same-revision canonical ARC train/validation splits were restored with pre-existing SHA checks, then one full paired evaluation completed in 205.93s. Training and detector were not repeated.

| Metric | Clean base | Final Teacher | Change (percentage points) |
|---|---:|---:|---:|
| ARC-Challenge acc_norm | 36.6041% | 36.3481% | -0.2560 |
| TruthfulQA-MC2 | 45.7547% | 45.7953% | +0.0406 |

No material degradation is apparent in these two point estimates; this is not a guarantee about all capabilities and cannot compensate for0/1024 watermark detection.

## Artifacts and closure

Final model retained on AutoDL: `/root/autodl-tmp/WMKD_Benchmark_data/scale_7b/teacher_adamw8bit_v1/final_model`. Size 13,479,234,655bytes (12.5535GiB), standard HF safetensors. All final files were rehashed successfully; frozen fingerprint SHA also rechecked. Dataset/model bodies were excluded from the lightweight evidence package, SHA304aca36dab35014d849b2e24f4903c8c7b1457253714c98e5cd077a9051df50. Full raw detector/utility, logs, training args, optimizer identity, source/config provenance, resource samples and verification are in `results/pnfp/scale_7b/teacher/receipts/`.

Peak data-disk use 26.6643GiB; after evaluation 43.3357GiB free of70GiB. No intermediate checkpoints or optimizer-state saves; no model/cache cleanup was necessary or performed. GPU idle verified; no Student/MD worker. No model upload because this Teacher is not preferred. This Llama-2-7B-chat extension versus the historical Llama-3.2-3B-Instruct run is not a pure parameter-count-only ablation.

## Git and next boundary

Safe pilot evidence is committed as180ee0f; formal launch/recovery as5381929, with final evidence committed separately. Unrelated dirty worktree files remain untouched. A clean detached worktree at180ee0f was verified before a non-forced private GitHub push attempt; HTTPS Git credential lookup failed. Existing SSH authentication was also tested against GitHub's verified official host key and rejected (`Permission denied (publickey)`). No push success or remote branch update is claimed. Existing private origin is unchanged; no credentials were exposed or transferred.

Current work is terminal: preserve the final model and evidence, do not launch Direct MD, do not retune or restart. A new scientific decision is required before another Teacher experiment.
