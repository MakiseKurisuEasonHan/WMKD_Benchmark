# PN-FP 7B full-parameter AdamW8bit pilot

**Final: PILOT_COMPLETED_STOPPED_FOR_USER_REVIEW. Four AdamW8bit calls completed (two original-schedule LR0 warmup calls, two nonzero-LR updates). No Teacher or checkpoint; process exit0 and GPU idle verified.**

Scope: latest user authorizes one real short 8-bit Adam-family optimizer pilot, never formal Teacher. Stop on failure; continue beyond first call only with at least10GiB measured headroom. No LoRA, Adafactor or further CPU-offload/BF16-state tuning. Earlier failure evidence is unchanged.

## Compatibility and engineering adaptation

Isolated bitsandbytes0.50.0 installed in `/root/autodl-tmp/WMKD_Benchmark_data/scale_7b/bnb_0500`; original environments retained. A real8192-element BF16 CUDA parameter test passed on RTX PRO6000 Blackwell SM12.0 with torch2.8.0+cu128, CUDA12.8. AdamW8bit completed a nonzero-LR update, changed7257 elements, maintained finite parameters, and created both moment tensors as uint8 on cuda:0. This is a kernel compatibility check, not a second model-training pilot. Official hardware reference: https://huggingface.co/docs/bitsandbytes/installation ; optimizer reference: https://huggingface.co/docs/bitsandbytes/reference/optim/adamw . Actual kernel execution, not documentation alone, is the compatibility gate.

Exact optimizer: `bitsandbytes.optim.adamw.AdamW8bit`0.50.0, non-paged, fixed blockwise implementation, min_8bit_size4096 (0.50.0 removes legacy block_wise/percentile_clipping arguments). LR5e-5/betas0.9,0.999/eps1e-8 and original Trainer weight-decay groups retained (WD1e-4, LayerNorm/bias exemptions). Original released training uses AdamW semantics; this remains the same Adam family and decoupled-decay objective, with quantized moment storage. Small states below4096 elements retain the library's default FP32 storage. Quantization metadata remains floating point. This is not numerical equivalence to original FP32 Adam states and not model-weight quantization.

One-GPU Trainer directly owns the optimizer, without DeepSpeed/ZeRO master/flat-state copies or offload. Same official CustomTrainer, data collator, WA formula and CPU-source reference values (reference stored on GPU). BF16 model and forward/backward, full parameter set, activation checkpointing enabled. The original DeepSpeed0.16.9 WarmupDecayLR object is retained independently of its engine:40-update horizon, nominal warmup0 effectively2. First two calls have LR0; at most4 calls allow two nonzero-LR updates. Early stopping remains unrounded mixed-data training loss<0.005.

Frozen1024 fingerprints SHA fa231b31aa10bf19dff0285eaff9457ad41a8f4ee2bcc9089a9d3ac76c1caaf7, canonical model `meta-llama/Llama-2-7b-chat-hf@f5db02db724555f92da89c216ac04704f23d4590`, key16/response1/Perinucleus t0.8/k3, WA0.75/DM0.25, seed42, seq64, micro6fingerprints+2benign, accumulation171. Loss and detector unchanged.

Conservative persistent storage estimate: BF16 model+gradients+WA reference37.65GiB, two8-bit moments12.55GiB, plus small quantization metadata. Reserve8GiB for activation/runtime; expected total about58GiB. Actual peak, first-step completion, finite-state checks and10GiB headroom gate govern continuation, not this estimate.

## Execution

Supervisor10154 launched `/root/autodl-tmp/WMKD_Benchmark_data/scale_7b/adamw8bit_pilot_v1` after nvidia-smi idle and df57GiB-free checks. No retries or auto-Teacher path exists. Runtime inspects actual moment dtypes/devices and Adam step counters, verifies all parameters trainable, records exact PyTorch allocation/reservation peaks and process peak RSS, samples device/cgroup memory every1s, and stops after the short budget. If healthy, existing1024-sample detector is called on the in-memory pilot model without saving a checkpoint. Launch is not success; metrics pending.

The first launch stopped before optimizer construction due to wrapper-supplied legacy `percentile_clipping`/`block_wise` keywords removed in0.50.0. The previously successful CUDA kernel probe did not pass these keywords. This wrapper error was corrected to the installed class signature without changing optimizer choice or scientific configuration; no model optimizer had been created and no update completed. Original logs remain in `adamw8bit_pilot_v1`; supervisor10764 continues initialization in separate `adamw8bit_pilot_v1_cont1`. No retry after a real optimizer failure is authorized.

## Actual results

All6,738,415,616 parameters are trainable BF16. Actual optimizer groups preserve WD1e-4 for6,738,149,376 parameters and WD0 for266,240 norm/bias parameters. Both moment arrays are uint8 on GPU (13,476,831,232 total moment bytes, plus quantization metadata). No NaN/Inf detected in monitored microbatch losses, full model parameters, or inspected floating optimizer states.

| Call | LR used | sec/update | Unrounded mixed training loss | Sampled changed parameter elements |
| --- | --- | --- | --- | --- |
| 1 | 0 | 25.5738 | 23.592495 | 0 |
| 2 | 0 | 25.0874 | 23.534855 | 0 |
| 3 | 5e-5 | 24.6886 | 23.615442 | 17713 |
| 4 | 5e-5 | 24.5725 | 6.598258 | 14624 |

The two nonzero-LR calls average24.6305s/update. Update timing includes the171 accumulated microbatches and optimizer step, but excludes subsequent epoch evaluation and WA callback. Loss is measured during that update's forward passes, before its optimizer change; it is not a post-update evaluation loss. BF16/8-bit moments and parameter changes are directly verified, rather than inferred from Trainer step counters alone.

| Memory metric | Peak |
| --- | --- |
| NVIDIA total GPU usage,1s sampling | 53241MiB =51.9932GiB |
| PyTorch allocated, exact allocator counter | 51.0252GiB |
| PyTorch reserved, exact allocator counter | 51.3281GiB |
| Host process peak RSS | 29.4183GiB |
| Host cgroup memory including cache/other runtime,1s sampling | 40.3414GiB |
| Minimum conservative headroom at recorded update boundaries | 42.9901GiB |

First step completed and cleared the10GiB gate before the remaining three calls. Peak disk usage sampled15,147,450,368 bytes; df after completion15GiB used/56GiB free. No intermediate/final pilot model or optimizer checkpoint was saved.

Existing greedy first-token detector evaluated all frozen1024 on the **in-memory trained pilot model**:182/1024 =17.7734375%, invalid0, errors0. The detector JSON's `model_path` is the canonical tokenizer source; its explicit label and result note identify the in-memory pilot weights. This preliminary recall after only two nonzero-LR updates is not a preferred Teacher result or a controlled improvement estimate; no clean baseline or utility suite was run in this scope.

The engineering memory/speed test succeeds on this hardware. Scientific convergence, final watermark strength and utility preservation remain unestablished. Full Teacher requires a new user decision and has not started. Evidence is in `results/pnfp/scale_7b/adamw8bit_pilot/`; all prior CPU/BF16-state failure evidence remains unchanged.
