# PN-FP Experiment Ba — Direct Distillation

Status: preparation complete; experiment not run.

Objective: measure PN-FP fingerprint retention and useful knowledge transfer after direct full-parameter distillation from the successful Experiment A teacher into a fresh pinned 1B student.

Reference: Pan et al., ACL 2025 (`2025.acl-long.648`). Planned configuration: frozen paired 20k QA, 3 epochs, LR `1e-5`, BF16, seed 42, batch 8, full parameter, LoRA off; OOM fallback 8→4→2 only with recorded evidence. Utility scope: ARC Challenge and TruthfulQA MC; MTBench excluded initially.

Resource-bounded deviation: CAN uses about 200k pairs and reports eight H800 GPUs; Ba uses 20k on one RTX PRO 6000. Current state: config, deterministic freeze utility, schema, report template and guarded dry-run runner prepared. No formal QA generation, training or evaluation has started.
