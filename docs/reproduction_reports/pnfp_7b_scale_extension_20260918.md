# PN-FP 7B scale extension (2026-09-18)

**Current status10:16UTC: BLOCKED_HOST_RAM_CANONICAL_CPU_OFFLOAD. No optimizer update completed; no formal Teacher or distillation launched; GPU has no workers.** Weights and frozen fingerprints retained, no LoRA/sweep/shutdown. This supersedes running snapshots below.

## Authority and protocol

The latest user instruction supersedes mechanical replay of the 3B A2 epoch schedule. Use one canonical full-parameter pilot, then fresh formal Teacher if healthy; max40 epochs with unrounded mixed-data training loss <0.005 early stopping. No broad hyperparameter search, no automatic LoRA substitution, no distillation before successful Teacher.

Protocol: `configs/watermark/pnfp_7b_scale_extension.json`. Paper: https://arxiv.org/html/2502.07760v1#A4 ; released code: https://github.com/SewoongLab/scalable-fingerprinting-of-llms/tree/fdceaba14bd3e89340916a6a40e27c945d48460e . Released code uses AdamW/DeepSpeed CPUAdam and an eval-loss callback; this extension retains the released optimizer implementation but explicitly implements the user-requested train-loss stop. These differences are disclosed, not described as exact paper replay.

## Model and transport

Canonical `meta-llama/Llama-2-7b-chat-hf@f5db02db724555f92da89c216ac04704f23d4590`; ModelScope transport `shakechen/Llama-2-7b-chat-hf@299e68d813ff6f146741f8e8477ed0a57ded4765`. All ten downloaded files match recorded canonical hashes. Total13,479,251,708 bytes; unquantized safetensors, standard trainable Transformers LlamaForCausalLM. HF access from this host was unavailable; canonical hash reference is preserved earlier project provenance, with fresh downloaded-file SHA verification.

Chat sample64MiB/12.4258s =5.40076MB/s; parallel range download approximately13.2MB/s. Download is complete. No Base, GGUF or quantized weights were acquired. Llama3.2→Llama2 includes architecture/generation differences, so this is not a pure parameter-count ablation.

## Runtime and engineering

AutoDL6003, RTX PRO6000 Blackwell96GB; torch2.8.0+cu128, transformers4.44.2, DeepSpeed0.16.9. Workspace `/root/autodl-tmp/WMKD_Benchmark`; experiment root `/root/autodl-tmp/WMKD_Benchmark_data/scale_7b`. Canonical repository commit d840b76637afaf6c699598832eee7d9c8c8d0d8d was transferred by Git bundle because remote GitHub authentication was unavailable. No unrelated historical evidence overwritten.

Two generation-only engineering failures preceded training: auxiliary discarded English-response capacity was too short for Llama2; variable chat-template lengths could not be concatenated. The wrapper preserves the official source checkout, explicitly selects the instruction-tuned branch, keeps unused auxiliary capacity16, left-pads chat inputs with masks, and preserves stable filtering of whitespace-invalid keys. Perinucleus formula/t/k and final response1 are unchanged. Failed logs are retained; these were not extra training pilots.

Frozen ordered candidate source contains1093 valid pairs (1100 requested candidates); training and detector consume the same first1024. Source SHA256 `fa231b31aa10bf19dff0285eaff9457ad41a8f4ee2bcc9089a9d3ac76c1caaf7`. Key16/response1, temperature0.5, perinucleus t0.8/k3, seed42. No8192/24576 fingerprint generation.

## Pilot

At10:05:44UTC, supervisor4581 launched canonical full-parameter pilot: BF16, LR5e-5, weight decay1e-4, microbatch6 fingerprint+2 benign, accumulation171, sequence64, WA0.75/DM0.25, original40-update scheduler horizon, max5 pilot updates. Final-only model save; no intermediate optimizer checkpoints. Subsequent evaluation is existing first-token greedy detector1024, fixed first64 canonical ARC-Challenge examples and existing10 ordinary prompts. The64-example proxy is diagnostic, not a tinyBenchmarks estimator.

Timing, VRAM, loss, recall and utility remain pending until actual execution. Do not infer success from launch. Remote `pilot_state.json`, `runs/speed/steps.jsonl`, `runs/speed/train_loss.jsonl`, `runs/speed/summary.json`, `pilot_evaluation/` are the recovery/evidence paths. No formal Teacher or distillation has started at this snapshot.

At10:07:47UTC, initial optimizer initialization exited SIGKILL(-9), before training-begin telemetry or any optimizer update. Cgroup memory limit110GiB/high108GiB, high events162, kernel oom_kill0: host memory pressure is suspected, not a confirmed kernel OOM. Initialization evidence is retained in `engineering_history/training_initialization_attempt0`. The sole retry moves the immutable BF16 WA reference to GPU, preserving values and the official averaging expression; no scientific parameter changes. Supervisor5330 restarted the same pilot at10:10:09UTC using the already frozen fingerprints.

At10:13:36UTC, the retry also exited SIGKILL(-9), during the first accumulated update. It passed optimizer initialization and entered training, but produced no completed-update telemetry/loss/checkpoint. Cgroup high events rose to105507; kernel oom_kill remained0. Source inspection of installed DeepSpeed0.16.9 `stage_1_and_2.py` confirms CPU master weights, FP32 gradient partition, Adam's two states, and an additional accumulated-gradient cache. For6,738,415,616 parameters, even18 bytes/parameter is121,291,481,088 bytes (112.96GiB), above110GiB before other host memory. This is an implementation-specific host-RAM blocker, not proof that all full-parameter approaches are impossible on96GB VRAM. Merely disabling pinned memory does not remove these persistent tensors.

## Requested pilot measurements

| Item | Observed result |
| --- | --- |
| Model/source/revision | Exact canonical Chat and fixed ModelScope revisions above; all10 hashes verified |
| Fingerprints | Fixed first1024, key16/response1, t0.8/k3, seed42 |
| Training | BF16 full parameter, WA0.75/DM0.25, micro6+2, accum171, seq64, LR5e-5, WD1e-4; max40/train-loss<0.005 |
| sec/update | Unavailable: zero completed optimizer updates |
| Peak VRAM | Not measured to completion; observed sample31881MiB, not a peak claim |
| Disk | df14GiB used/57GiB available; model13.479GB; no pilot checkpoint |
| Loss/recall | Unavailable; no completed update, detector/proxy not run |
| Convergence estimate | Unavailable; no valid timing or loss curve |

Next viable options are more host RAM (e.g.160GiB, with headroom checked at runtime), or a separately validated implementation that relocates accumulated gradients/optimizer buffers while preserving their precision and update semantics. No such DeepSpeed-internal redesign was silently applied. All failed attempt logs, exact runtime configuration and hardware receipt are under `results/pnfp/scale_7b/receipts/`. No final-model archive exists because no Teacher was produced.
