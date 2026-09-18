# PN-FP 7B distillation 6004 — active run

Status: RUNNING. Direct Teacher generation started; Students NOT_STARTED at launch snapshot. This is not a completed result report.

New disk total634,581,417,984 bytes, available578,946,330,624 bytes (539.19GiB). Cgroup RAM limit118,111,600,640 bytes (110GiB), despite host free reporting1TiB. GPU RTX PRO6000 Blackwell96GB. Idle driver reported0MiB/100% without compute processes; small CUDA matmul succeeded in0.355s. No reset or unrelated process termination.

Teacher all10 files and Base all10 files match saved SHA manifests. Frozen fingerprints and user-selected original paraphrase prompt match. No Teacher retraining, no fingerprint regeneration. Existing Qwen snapshot missing; its later pinned revision was verified byte-identical across every file to original benchmark snapshot and will be restored only at the paraphrase stage.

Direct uses existing generator and freeze implementation:24k initial candidates, if needed existing +2k policy capped40k, freeze20k. Original LR1e-5,3epochs/7500updates,batch8,cosine225warmup,seed42,maxlength1024,assistant labels preserved. Each Student independently loads same clean7B revision. AdamW8bit0.50.0 and activation checkpointing are engineering adaptations; optimizer implementation is not canonical FP32 Adam equivalence.

No frozen attack dataset exists on clone, so exact Bc position count is pending Direct freeze. Before any logits, CPU uses original SFTDataset and labels[1:]!=-100 to count positions, then total_tokens*32000*2. Full-vocab BF16 shards contain raw uint16 bit patterns; no quantization/top-k. Streaming reads only current minibatch, all shard SHA checked. Disk gate includes final models and overhead and allows at most85% of current free bytes. The old worst-case1024position budget is not used to decide this run.

CPU engineering tests passed: canonical CE/KL forward+gradient test; BF16 store/read target, loss and gradient bitwise roundtrip; Teacher/Base vocabulary equality and chat sequence comparison. All large GPU stages run serially, logged nvidia-smi/df-equivalent byte counters, processRSS/GPU sampled peaks, runtime, exact configs, final-only model manifests. No watermark-specific tuning.

Remote generation supervisor PID1754, actual generator1755. Remote serial campaign PID2350. Local evidence/commit/shutdown guardian PID62328. Autonomous closeout: terminal result/failure report, model SHA verification, local evidence SHA sync, local Git commit, noninteractive push attempt, verify noGPU worker, then /bin/bash /usr/bin/shutdown (official script previously needs interpreter). Instance is not released. Models not deleted. Transport failures retry; Git push pending does not block shutdown.

Final result report will be docs/reproduction_reports/pnfp_7b_distillation_6004_final.md. Recovery entry results/pnfp/scale_7b/distillation_6004/campaign_state.json. Do not launch a second runner or regenerate datasets while these processes are live.

Engineering note: only real CUDA OOM allows bounded internal microbatch8→4→2 while retaining the original sampled batch8 and supervised-token weighted objective; mathematical loss/gradient parity passed. Failed evidence remains. Current canonical Bb <=1-token identity rule remains, with user-selected original085a prompt. Controller reloads while waiting do not interrupt Teacher generation; currentPID is in campaign_state.json.

Final launch controllerPID2988; local guardianPID50036. GeneratorPID1755 was never restarted. On complete success only, exact manifest-listed reproducible BF16 cache shards are removed after final model verification; manifests and datasets remain. Formal stage full logs are added to global index during local closeout.
