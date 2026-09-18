# PN-FP 7B GPU BF16-state pilot

**Final status: STOPPED_ON_GPU_OOM. Zero completed optimizer updates; no retry after OOM, no Teacher, no checkpoint, no GPU worker.**

Latest authority: only an independent short GPU-resident full-parameter pilot, then STOP for user review. No Teacher, offload, LoRA, quantized optimizer, model replacement, or hyperparameter sweep. Earlier CPU-offload evidence remains unchanged.

## Verified support and implementation

Installed DeepSpeed0.16.9 does not contain the requested BF16 master/state options. An independent `ds_bf16_0196` package directory holds DeepSpeed0.19.6, selected through PYTHONPATH; the original environment is intact. Its real config parser accepts both flags and verifies both offload fields are absent. Runtime source SHA256 values are recorded in `gpu_bf16_support_preflight.json`.

Official documentation: https://www.deepspeed.ai/docs/config-json/ . The `bf16` section supports `bf16_master_weights_and_grads=true` and `bf16_optimizer_states=true` with ZeRO stages1/2/3 without offload. This is also verified against installed source, not inferred from ignored JSON fields.

Frozen config: `configs/watermark/pnfp_7b_gpu_bf16_pilot.json`. ZeRO2, BF16 model/master/grad/moments, explicit BF16 gradient accumulation, no optimizer/parameter offload, no communication overlap,20M-element communication buckets, activation checkpointing with use_reentrant=false. Same canonical Chat checkpoint, fixed1024 fingerprints SHA fa231b31aa10bf19dff0285eaff9457ad41a8f4ee2bcc9089a9d3ac76c1caaf7, key16/response1/t0.8/k3, seed42, WA0.75/DM0.25, seq64, micro6+2/accum171. Max40 scheduler horizon preserved; pilot stops after3 optimizer calls, including the first nonzero-LR update (or trainloss<0.005). No checkpoint is saved: user requested memory/speed verification, not a Teacher.

The released training pipeline uses AdamW semantics (decoupled decay); this pilot retains that Adam-family behavior, LR5e-5, WD1e-4, betas0.9/0.999, eps1e-8. No silent change to coupled-decay Adam. Moving moments, master weights and gradient accumulation from FP32 to BF16 is an explicitly authorized numerical engineering adaptation. Objective and trainable parameter set are unchanged, but reduced mantissa precision can round away small updates and alter moment/gradient accumulation, so numerical equivalence or convergence equivalence is not claimed.

## Static GPU estimate

6,738,415,616 parameters; each BF16 full copy is13,476,831,232 bytes (12.55GiB). Conservative six-copy budget includes model, separate master, gradient, two moments, and WA reference:75.31GiB. Reserve8GiB for activation/checkpointing, DeepSpeed buffers, CUDA/runtime overhead. Observed capacity97887MiB (95.59GiB) leaves approximately12.28GiB static margin. Actual allocation aliases, allocator reservation and transient peaks require runtime measurement.

## Execution

Supervisor7820 launched the separate directory `/root/autodl-tmp/WMKD_Benchmark_data/scale_7b/gpu_bf16_pilot_v1`. Before launch nvidia-smi showed no GPU worker, df showed57GiB free. Resource sampling records cgroup host memory and nvidia-smi device use once per second; training records exact PyTorch peaks, process peak RSS, Adam step counters, actual moment dtype/device, loss, update seconds and a parameter-change sample. Results pending; launch alone is not success.

Initial GPU launch stopped before training because0.19.6 rejects warmup_num_steps0, whereas0.16.9 silently clamps0 to2. Explicit warmup2 is a compatibility repair, not a changed effective schedule: all40 optimizer-call learning rates were compared and are exactly equal. Calls1/2 use LR0, call3 uses5e-5, so the short pilot budget is3 calls to measure a nonzero-LR update. Initial launch logs remain in the original directory; supervisor8759 uses separate `gpu_bf16_pilot_v1_cont1`. This engineering continuation does not restart any completed optimizer update.

## Actual result and static-estimate correction

At10:52:17UTC the first optimizer call raised CUDA OutOfMemoryError inside `torch.optim.adam._init_group`, allocating `exp_avg_sq = torch.zeros_like(...)`. This was allocation of the second Adam moment, not completed training or a convergence failure. The worker exited and no retry was launched, as requested.

| Metric | Evidence |
| --- | --- |
| GPU peak sampled each1s | 91,573MiB =89.4268GiB |
| Host cgroup peak sampled each1s | 45,205,430,272 bytes =42.1008GiB, includes runtime/cache, not process-only RSS |
| OOM allocation request | 12.55GiB for second Adam moment |
| OOM diagnostic | GPU94.97GiB, free5.54GiB; process89.42GiB; PyTorch allocated75.32GiB plus12.54GiB reserved-but-unused |
| Completed optimizer updates | 0 |
| sec/update | N/A: no completed update |
| Update training loss | N/A: no completed-update loss was recorded |
| Moment verification | BF16 flags, GPU master tensor dtype/device and BF16 accumulation verified; full moment-state inspection after update was not reached |
| Disk | approximately14GiB used/57GiB free; no pilot checkpoint |
| Final state | GPU idle; Teacher/utility/detector not run; no LoRA/8-bit/offload fallback |

The six-copy75.31GiB static estimate underestimated the live optimizer-step footprint: allocated memory was already75.32GiB before the second12.55GiB moment could be created. Additional live gradient/optimizer buffers and allocator reservation were not adequately covered by the8GiB allowance. The diagnostic also reports12.54GiB reserved-but-unused, so this is an OOM of the tested implementation/allocation path, not proof that every GPU-resident BF16 Adam implementation is impossible. No allocator changes, buffer redesign, optimizer replacement or retry were attempted after this OOM.

Local evidence: `results/pnfp/scale_7b/gpu_bf16_pilot/`, with independent initial scheduler-failure and OOM-attempt directories. Old CPU-offload logs/environment/config remain intact. Await user review before any new execution.
