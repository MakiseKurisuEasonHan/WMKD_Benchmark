# iSeal Experiment A log

## Authorization and preparation

- Status: `BLOCKED_SCIENTIFIC_IMPLEMENTATION_TRAINABILITY` before formal Experiment A launch.
- Official source pinned to `IntelliSys-Lab/iSeal@7e382321eef4355002acd93120d888dc9b45a8bd`.
- Canonical backbone remains `meta-llama/Llama-3.2-3B-Instruct@0cb88a4f764b7a12671c53f0838cd831a0843b95`.
- The authorized formal configuration and paper/code discrepancies are recorded in `configs/watermark/iseal_experiment_a.yaml` and `docs/methods/iseal.md`.
- Formal A, Ba, attacks, ModelScope upload, and cleanup have not started.

## Immutable trainability-audit lineage

- `iseal_trainability_20260830_045232`: infrastructure-only failure before model loading/optimizer steps because `huggingface.co` was unreachable. No scientific artifact was produced.
- AG News was then resolved through the trusted `https://hf-mirror.com` transport while preserving upstream `ag_news` identity; generated splits were 120,000 train and 7,600 test.
- `iseal_trainability_20260830_045431`: completed two optimizer steps on 10 seed-42 registered AG News plaintexts and 271 token IDs.
- Adapter `delta`, `A`, and `B` each had exact-zero initialization, zero gradient at both steps, and zero parameter delta.
- The full tied `lm_head`/original-embedding matrix (394,002,432 parameters) had gradient norms `195.003445/381.784871` and parameter delta norm `6.019554`.
- Gate: `formal_experiment_a_allowed=false`. Formal A stopped as required. No initialization, tied-weight, trainable-block, or optimizer modification was made.
- Machine-readable evidence: `results/iseal/experiment_a/trainability_audit.json`, SHA256 `bbc3b9416e44484d8ab6414d0f3840237e00dedb23c763d69281848aa7feaab0`.
- Preferred Teacher: NO. Ready for Ba: NO. Next action requires an explicit scientific implementation decision.
