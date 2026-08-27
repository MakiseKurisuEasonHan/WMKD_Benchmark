# PN-FP Experiment Ba — Direct Distillation

Status: preparation complete; experiment not run.

Objective: measure PN-FP fingerprint retention and useful knowledge transfer after direct full-parameter distillation from the successful watermarked Experiment A 3B teacher into a fresh unwatermarked canonical 3B student.

Reference: Pan et al., ACL 2025 (`2025.acl-long.648`). Planned configuration: frozen paired 20k QA, 3 epochs, LR `1e-5`, BF16, seed 42, batch 8, full parameter, LoRA off; OOM fallback 8→4→2 only with recorded evidence. Utility scope: ARC Challenge and TruthfulQA MC; MTBench excluded initially.

Resource-bounded deviation: CAN uses about 200k pairs and reports eight H800 GPUs; Ba uses 20k on one RTX PRO 6000. Current state: config, deterministic freeze utility, schema, report template and guarded dry-run runner prepared. No formal QA generation, training or evaluation has started.

## Formal launch preparation — 2026-08-28

- User authorized Ba-only formal execution; Bb and all Dipper work remain deferred.
- AutoDL was briefly reachable: Experiment A teacher/fingerprint artifacts were present, GPU was idle, data disk had 981GB free, and the existing PN-FP environment reported PyTorch 2.7.1+cu128, Transformers 4.44.2, Accelerate 0.32.1, Datasets 2.20.0 and PyYAML 6.0.1.
- Added the formal resumable teacher-QA generator, full-parameter BF16 student trainer, serial Ba pipeline, OOM-only batch fallback and detached launcher.
- Deployment and launch have not occurred because the AutoDL SSH endpoint became unreachable during upload attempts. No GPU process was started.

## Same-size design correction — 2026-08-28

- Cancelled and removed an incomplete, project-owned 1B transport download before any formal run, teacher QA generation, GPU work or Ba STARTED notification.
- Corrected the Ba student to a fresh logical load of the existing canonical unwatermarked `meta-llama/Llama-3.2-3B-Instruct@0cb88a4f764b7a12671c53f0838cd831a0843b95`; the teacher remains the distinct watermarked Experiment A checkpoint.
- CAN ACL 2025 used Llama-3.2-1B as one of its students. WMKD_Benchmark intentionally uses same-size 3B teacher and student to remove model-capacity reduction as a confounder and isolate direct knowledge distillation.
- Stop point retained: Ba has no run ID and has not started.
