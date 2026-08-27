# PN-FP Experiment Bb — Untargeted Paraphrasing + Distillation

Status: preparation complete; experiment not run.

Objective: compare answer-only UP against Ba using identical frozen sample IDs and a fresh copy of the exact same pinned 1B initialization.

Reference: Pan et al., ACL 2025 (`2025.acl-long.648`). Attribution: **paper-defined UP + project-owned Dipper integration**; the CAN repository does not provide official UP code. Planned training matches Ba. Dipper paraphrases only `teacher_raw_answer`; instruction/input/ID/count are immutable and any failure stops the pipeline without dropping a sample.

Resource-bounded deviation: 20k paired samples on one RTX PRO 6000. Dipper diversity settings are documented operational adaptations, not CAN-reported parameters. Current state: config, paired validator, failure preservation, schema, report template and guarded dry-run runner prepared. No Dipper generation, training or evaluation has started.
