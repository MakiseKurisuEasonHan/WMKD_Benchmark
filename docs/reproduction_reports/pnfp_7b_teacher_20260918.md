# Formal PN-FP 7B AdamW8bit Teacher

Latest user authorizes fresh formal Teacher with frozen1024 fingerprints, canonical Llama-2-7b-chat-hf@f5db02db724555f92da89c216ac04704f23d4590, key16/response1/Perinucleus t0.8/k3, seed42, WA0.75/DM0.25, BF16, activation checkpointing, all6,738,415,616 parameters trainable, bitsandbytes.optim.adamw.AdamW8bit0.50.0, max40 epochs and unrounded mixed train-loss<0.005 early stop. No optimizer/memory ablations. 8-bit moment storage is an engineering adaptation, not equivalent to canonical FP32 Adam implementation.

Frozen config: `configs/watermark/pnfp_7b_teacher.json`. The verified pilot implementation is reused through an assertion-checked wrapper; the exact executed source, its SHA and original pilot source SHA are preserved remotely. Fresh canonical initialization, same optimizer groups/LR/betas/eps/scheduler/template/data/loss/detector. No pilot checkpoint exists or is used. Original40-step learning-rate horizon including two LR0 calls is unchanged. Early stopping is never triggered merely by recall exceeding90%.

Supervisor12119, training worker12128; isolated output `/root/autodl-tmp/WMKD_Benchmark_data/scale_7b/teacher_adamw8bit_v1`. Prelaunch GPU idle0MiB, data disk56GiB free, no output collision. Final model only, no optimizer-state checkpoints. Every5 epochs, fixed first128 fingerprints use the existing detector in memory after WA, with Python/NumPy/Torch RNG and training mode restored. These subset checks do not affect stopping or replace final full1024 evaluation.

After final save: per-file SHA manifest, fresh-reload full detector, then existing full paired ARC-Challenge/TruthfulQA-MC2 benchmark utility once. Pinned public dataset files are restored locally with canonical hashes, scoring unchanged. Only if watermark and utility pass final assessment may same-lineage Direct MD be prepared; it must not start before the Teacher summary. No automatic distillation launch exists in the supervisor.

## Current execution

Training running. First loss23.59249496459961 exactly matches the successful pilot; first update25.3221s. Final results pending; do not interpret launch as success. Recovery: remote `state.json`, `steps.jsonl`, `recall_step_*.json`, `result.json`, `final_model_manifest.json`, `detector.json`, `utility.json` and per-stage resource/exit logs.

## Git

Original worktree has unrelated historical edits/untracked assets and was not cleaned. A clean detached worktree `.pnfp-safe-publish` was created at180ee0f and verified empty `git status --porcelain`. Non-forced push of pending safe commits to existing private main was attempted with interactive credential prompts disabled; it failed with `Cannot prompt because user interactivity has been disabled` / `unable to get password from user`. No remote branch update is claimed. Credentials were not printed or transferred to AutoDL. Scientific execution continues independently.
