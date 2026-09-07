# UTF A2 initial checkpoint — 2026-09-07

Status: WAITING_FOR_SCIENTIFIC_DECISION. This is a preparation checkpoint, not a completed scientific experiment. No A2 preflight, training, detector, utility, checkpoint or new model archive has been produced.

## Scope and process evidence

Only UTF A2 is authorized. Old UTF A remains historical / superseded, not FAILED. OLD_UTF_A_CANONICAL_BENCHMARK_ELIGIBLE = NO because its backbone differs from the newly frozen comparison. Preserve all old models, preflight attempts, repairs and logs.

The old remote supervisor PID 2051 was ownership-checked and SIGTERM-terminated under the preceding explicit user decision; exit was verified. Local pipeline sync helper PID 32236 was ownership-checked and stopped. No new orchestrator, guardian, watchdog, auto-continuation or shutdown mechanism was created. Related remote process checks were empty; identity receipt records the final check. This does not claim an audit of unrelated system services.

## Canonical model

Model: meta-llama/Llama-3.2-3B-Instruct
Revision: 0cb88a4f764b7a12671c53f0838cd831a0843b95
Path: /root/autodl-tmp/WMKD_Benchmark_data/models/base/Llama-3.2-3B-Instruct
Existing SCW canonical manifest was reused. All eight runtime files, including both weight shards, match historical sizes and SHA256. No model download. Receipt: results/utf_a2_identity_check_20260907.json. Config SHA: 39fb36dc5416f445ebc4e71cb71fbcf6727e80a35836d8ba1a1474c318467b7a.

## Pinned official protocol audit

Source: https://github.com/imjccai/fingerprint/tree/7155b38b077e18396bf550f839b27166c2011fe5
Paper: https://aclanthology.org/2025.llmsec-1.1.pdf

The default single-fingerprint route constructs one unique unused-token input/target pair repeated into 32 training records, not 32 distinct fingerprint pairs. Inputs have 11–15 unused tokens and the target has five. Regularization defaults to zero. The objective is standard causal supervised cross-entropy with prompt labels masked. Full fine-tuning is the reference route; no LoRA conversion has been chosen.

Scientific conflict: paper section 3.1 specifies 30 epochs, while pinned config/train_config.json specifies three. fingerprint_pipeline.py exposes an epoch default of 30, but fingerprint/pipeline.py reads the JSON into the effective arguments and training uses that JSON. Thus the CLI default cannot establish 30 executed epochs. A user question is pending; no selection is assumed.

Reference JSON: microbatch 1, accumulation 16, LR 2e-5, weight decay 0, max gradient norm 1, seed 42, BF16, gradient checkpointing, maximum sequence length 2048. Official DeepSpeed configuration specifies an Adam optimizer and WarmupLR with 100 warmup steps, overriding the Trainer JSON cosine scheduler in that route. Removing CPU offload must not silently substitute a different learning-rate schedule. A2 optimizer implementation and exact batch/accumulation remain unfrozen pending the epoch decision. Exposures are 96 for three epochs or 960 for 30; optimizer steps and first nonzero-LR parameter update must be computed from the final implementation, not inferred from Trainer's counter.

The official verifier uses greedy generation and target-string containment (not a newly invented exact-token detector). Positive probes deduplicate input strings. Official negative checks use 500 random non-trigger inputs; exclude special tokens, use input lengths 11–15 and max_new_tokens 100. Report raw counts/rates for Teacher, canonical Base and meaningful negatives without changing the rule after observing results.

Llama-3 template handling exists; special-token dispatch needs a minimal Llama-3.2 architecture adaptation. No training implementation or new fingerprint data has been generated while the scientific decision is pending.

## Utility provenance finding

Primary tasks remain ARC-Challenge acc_norm and TruthfulQA MC2 acc, with the existing WMKD evaluator and identical evaluation semantics. Native SciQ/LAMBADA cannot replace them.

The quoted Base approximation .4087/.4951 is not verified. results/iseal/experiment_a4/utility.json records .4087030716723549 as A4 Teacher ARC, not Base. Its Base is ARC .447098976109215 and MC2 .5056446616844986. Other historical methods record slightly different Base values; none is selected opportunistically. Reuse requires the exact evaluator/runtime/dataset/template provenance match. No Base evaluation was rerun and no utility delta exists for A2.

## Resource checkpoint and next action

GPU at identity check: RTX PRO 6000 Blackwell Server Edition, 0/97887 MiB, 0% utilization. Data disk free: 119975616512 bytes (about 111.74 GiB). Model was not loaded onto GPU. Trainable parameter count, measured peak VRAM/RAM, runtime estimate and preflight loss are NOT_MEASURED.

PREFLIGHT = NOT_RUN. Primary config = NOT_FROZEN. Next: user chooses the authoritative epoch setting; then resolve and document one primary configuration and utility reference, implement the minimal 3B adaptation, perform one real optimizer-update preflight with changed-parameter evidence, and only after PASS and no unresolved RED ambiguity start formal UTF A2. Stop after UTF; never advance or auto-shutdown.
