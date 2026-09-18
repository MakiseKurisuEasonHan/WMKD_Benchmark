# PN-FP 7B controlled trajectory diagnostic: rise and collapse confirmed

**Best: optimizer call13 (11th nonzero-LR update), in-memory339/1024 (33.1055%); fresh-reload334/1024 (32.6172%). Final call40:0/1024. PREFERRED_TEACHER=NO.** The model learns a subset of fingerprints, plateaus, then forgets them under the unchanged schedule. It does not establish an inability to learn any fingerprints, but also does not recover a strong Teacher near the historical3B956/1024 range. No Direct/Paraphrase/Logit distillation, new hyperparameters, optimizer ablation or shutdown.

## Controlled configuration

Fresh `meta-llama/Llama-2-7b-chat-hf@f5db02db724555f92da89c216ac04704f23d4590`, same frozen1024 manifest SHA `fa231b31aa10bf19dff0285eaff9457ad41a8f4ee2bcc9089a9d3ac76c1caaf7`; key16/response1, Perinucleus t0.8/k3, WA0.75, DM0.25, seed42, BF16 full6,738,415,616 trainable parameters, activation checkpointing, `bitsandbytes.optim.adamw.AdamW8bit`0.50.0. Sequence64, micro6fingerprint+2benign, accumulation171, LR5e-5, betas0.9/0.999, eps1e-8, weight decay1e-4 with original exclusions. Original DeepSpeed0.16.9 WarmupDecayLR standalone40-call horizon, including two initial zero-LR calls. Same chat template, loss and greedy exact first-token detector. 8-bit optimizer storage is an engineering adaptation, not canonical FP32 Adam implementation equivalence.

This was one rerun, with full1024 evaluation after every call's WA. Loss<0.005 was recorded rather than used as the sole diagnostic stop; all40 calls completed under the frozen horizon. Python/NumPy/Torch RNG and training mode were restored around detection and best saving. The prepared training dataset SHA matched exactly, core TrainingArguments matched, **all40 LR/loss values matched the prior formal run exactly**, and **all final safetensors hashes matched the prior failed final model**. The new run logs ordered input batch hashes; the prior run lacks those hashes, so direct old/new batch-hash comparison is unavailable.

## Complete measured trajectory

Loss is the accumulated mixed training loss for that optimizer call, before its update. Recall is measured after the optimizer update and WA, on the same full1024. Thus loss and recall are not simultaneous evaluations of identical pre/post-update weights. In-memory `model_path` fields identify the tokenizer source; the detector label identifies the live trained model.

| Update | Actual LR | Train loss | Recall /1024 | Recall % |
|---:|---:|---:|---:|---:|
| 1 | 0 | 23.592495 | 0/1024 | 0.0000% |
| 2 | 0 | 23.534855 | 0/1024 | 0.0000% |
| 3 | 5e-05 | 23.615442 | 246/1024 | 24.0234% |
| 4 | 5e-05 | 6.598258 | 182/1024 | 17.7734% |
| 5 | 4.8684211e-05 | 5.130043 | 329/1024 | 32.1289% |
| 6 | 4.7368421e-05 | 4.765505 | 325/1024 | 31.7383% |
| 7 | 4.6052632e-05 | 4.196766 | 315/1024 | 30.7617% |
| 8 | 4.4736842e-05 | 4.191790 | 319/1024 | 31.1523% |
| 9 | 4.3421053e-05 | 4.081629 | 329/1024 | 32.1289% |
| 10 | 4.2105263e-05 | 3.879400 | 334/1024 | 32.6172% |
| 11 | 4.0789474e-05 | 3.918794 | 332/1024 | 32.4219% |
| 12 | 3.9473684e-05 | 3.914001 | 329/1024 | 32.1289% |
| 13 | 3.8157895e-05 | 3.848032 | 339/1024 | 33.1055% |
| 14 | 3.6842105e-05 | 3.775902 | 338/1024 | 33.0078% |
| 15 | 3.5526316e-05 | 3.786768 | 336/1024 | 32.8125% |
| 16 | 3.4210526e-05 | 3.836048 | 337/1024 | 32.9102% |
| 17 | 3.2894737e-05 | 3.856629 | 336/1024 | 32.8125% |
| 18 | 3.1578947e-05 | 3.886150 | 335/1024 | 32.7148% |
| 19 | 3.0263158e-05 | 3.891358 | 327/1024 | 31.9336% |
| 20 | 2.8947368e-05 | 4.062815 | 327/1024 | 31.9336% |
| 21 | 2.7631579e-05 | 3.938518 | 328/1024 | 32.0312% |
| 22 | 2.6315789e-05 | 4.052161 | 322/1024 | 31.4453% |
| 23 | 2.5e-05 | 4.145144 | 324/1024 | 31.6406% |
| 24 | 2.3684211e-05 | 4.205828 | 317/1024 | 30.9570% |
| 25 | 2.2368421e-05 | 4.272560 | 309/1024 | 30.1758% |
| 26 | 2.1052632e-05 | 4.646696 | 290/1024 | 28.3203% |
| 27 | 1.9736842e-05 | 4.755862 | 288/1024 | 28.1250% |
| 28 | 1.8421053e-05 | 5.161430 | 284/1024 | 27.7344% |
| 29 | 1.7105263e-05 | 5.311269 | 262/1024 | 25.5859% |
| 30 | 1.5789474e-05 | 5.818547 | 220/1024 | 21.4844% |
| 31 | 1.4473684e-05 | 6.816924 | 114/1024 | 11.1328% |
| 32 | 1.3157895e-05 | 9.714112 | 28/1024 | 2.7344% |
| 33 | 1.1842105e-05 | 14.395761 | 5/1024 | 0.4883% |
| 34 | 1.0526316e-05 | 17.585192 | 3/1024 | 0.2930% |
| 35 | 9.2105263e-06 | 18.586813 | 2/1024 | 0.1953% |
| 36 | 7.8947368e-06 | 19.379753 | 1/1024 | 0.0977% |
| 37 | 6.5789474e-06 | 20.298502 | 0/1024 | 0.0000% |
| 38 | 5.2631579e-06 | 21.520788 | 0/1024 | 0.0000% |
| 39 | 3.9473684e-06 | 22.428370 | 0/1024 | 0.0000% |
| 40 | 2.6315789e-06 | 22.656378 | 0/1024 | 0.0000% |

Best checkpoint replacements occurred only at calls3,5,10,13. Strict improvement selected the best; ties retained the earlier checkpoint. Recall then fell339→220(call30)→114(call31)→28(call32)→5(call33)→3→2→1→0(call37), remaining0 through40. No checkpoint selected by loss and no utility-driven checkpoint search occurred.

## Best fresh reload: discrepancy preserved

Saved best manifest identifies call13. Its ten files were rehashed successfully. Fresh detector evaluated all1024 with invalid0/errors0 and obtained334 matches, not339. There are23 changed predicted tokens:7 matches lost,2 gained,14 changed between different incorrect predictions. `reload_comparison.json` retains every difference. No reload equivalence is claimed and no detector/template/precision changes or extra inference experiments were introduced to force agreement. A read-only source check found the training code explicitly casts the loaded model toBF16, while the existing standalone detector loads directly with `torch_dtype=bfloat16`; whether this or other numerical state explains the mismatch was **not established**. Use334/1024 as the saved-checkpoint detector result.

## Utility: once on selected best

One complete paired existing benchmark suite after best reload, unchanged chat template/BF16/batch8/scoring: ARC-Challenge test1172 and TruthfulQA-MC2 validation817. No intermediate checkpoint utility evaluations. The harness's `a2` JSON key refers to the diagnostic best model.

| Metric | Clean base | Best checkpoint | Delta, percentage points |
|---|---:|---:|---:|
| ARC-Challenge acc_norm | 36.6041% | 39.7611% | +3.1570 |
| TruthfulQA-MC2 | 45.7547% | 44.6587% | -1.0960 |

These two tests do not show broad utility collapse: ARC improves while MC2 decreases modestly. No claim of universal utility preservation or statistical significance is made. The low recall relative to the requested strong-Teacher range prevents preferred selection regardless.

## Measured overhead and resources

- Full1024 trajectory detector,40 measurements: **634.798s = 10.580min**, mean15.870s/check.
- Four best checkpoint writes/hash/retention operations: **116.800s = 1.947min**.
- Instrumented training including trajectory work: 2068.916s; including final save/hash: **2098.461s = 34.974min**.
- Increase versus prior formal train+save wall: 741.973s = 12.366min. This aggregate includes different checkpoint I/O, batch-hash work and runtime variation; prior formal already used eight128-key probes. The direct detector timer is the clean measure of trajectory evaluation overhead.
- GPU sampled2s peak: 51.993GiB; allocated 51.025GiB; training processRSS 29.418GiB; cgroup sampled peak including checkpoint I/O/cache 57.095GiB. No OOM/NaN/Inf; sampled peaks can miss transients.
- Peak disk usage 51.781GiB; remaining 18.219GiB of70GiB. GPU idle after evaluation.

## Retained assets and boundary

Best: `/root/autodl-tmp/WMKD_Benchmark_data/scale_7b/trajectory_adamw8bit_v1/best_model`. Final: `/root/autodl-tmp/WMKD_Benchmark_data/scale_7b/trajectory_adamw8bit_v1/final_model`. Each13,479,234,655bytes (12.554GiB), standard HF safetensors with tokenizer. Both manifests' files were SHA-verified. Three superseded best checkpoints were deleted only after verified replacement writes in this diagnostic directory; all step manifests, results and retention receipts remain. Original failed Teacher model and prior evidence remain untouched. No optimizer-state checkpoints, model upload or shared-cache cleanup.

Evidence: `results/pnfp/scale_7b/trajectory/receipts/`; complete table also in `trajectory_table.md` and `receipts/trajectory_table.csv`. Source archive SHA0dc521b0827474d540abe5aba4fbfdb8e4a899eb3305a82dcd971ef46889ccc0. Frozen config and resolved runtime are preserved; global index has a separate diagnostic object and leaves the old formal failure unchanged.

Diagnostic goal is complete: reproducible rise and later collapse demonstrated, best recovered and freshly evaluated. Its ~33% recall is not a strong preferred7B Teacher under the user's stated goal. Root cause and remedies remain untested; no automatic new trial or distillation. Git safe launch commitb17f840 and final evidence are local; prior GitHub authentication blocker remains, with no push success claimed.
