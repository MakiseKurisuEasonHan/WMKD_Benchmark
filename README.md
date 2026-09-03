# WMKD_Benchmark

WMKD_Benchmark studies robustness/stability of large-language-model ownership watermarking and fingerprinting methods under knowledge distillation and related model-extraction attacks, with the long-term goal of an ICLR/top-conference paper.

## Research question

The benchmark will evaluate how watermark detectability, strength, stability, and model utility change after knowledge distillation, and will compare robustness across watermarking and distillation methods.

## Standardized backbone

Formal experiments default to the pinned canonical `meta-llama/Llama-3.2-3B-Instruct@0cb88a4f764b7a12671c53f0838cd831a0843b95`. Experiment A watermarks a fresh canonical 3B model. Ba and Bb use the successful watermarked A model as teacher but initialize their students from fresh canonical unwatermarked 3B weights. Keeping model family, size, revision, tokenizer, and template fixed separates watermark and distillation effects from model compression and capacity reduction.

Methods that cannot use the standardized 3B backbone are not silently moved to another model. A deviation requires a documented blocker, explicit user approval, and clear non-standard-backbone labeling in the formal record. The authoritative operational rule is in `docs/EXPERIMENT_PROTOCOL.md`.

## Benchmark scope and current lifecycle

The selected methods are PN-FP, EverTracer, CTCC, iSeal, SCW, LLMPrint, REEF, HuRef, AWM, and ZeroPrint. Experiment A reproduces or freezes the method-specific ownership signal; corrected immutable reproductions use A2/A3 and later suffixes only for scientific changes; Ba is Direct Distillation; Bb is Untargeted Paraphrasing followed by Distillation.

All ten methods have completed A/A2/A6 reproduction and Ba evaluation. On 2026-09-03 the user froze Bb as answer-only Untargeted Paraphrasing followed by Distillation (UP + Distillation) and selected passive methods 6–10—LLMPrint, REEF, HuRef, AWM, and ZeroPrint—as the first Bb cohort. Bb execution has not started and still requires a separate explicit execution prompt.

## Intended workflow

```text
Watermark reproduction
        ↓
Watermarked model
        ↓
Knowledge distillation attack
        ↓
Student model
        ↓
Watermark re-evaluation
        ↓
Cross-method benchmark
```

## Project status

The current benchmark contains ten methods: proactive PN-FP, EverTracer, CTCC, iSeal, and SCW; passive LLMPrint, REEF, HuRef, AWM, and ZeroPrint. The repository's global index currently contains 21 formal full-JSON objects covering the completed A/Ba closure, including the explicitly shared passive Ba object. See `PROJECT_STATUS.md`, `docs/EXPERIMENT_PROTOCOL.md`, `results/experiment_full_logs_index.json`, and `EXPERIMENT_LOG.md`.

## Repository layout

- `configs/`: version-controlled experiment configurations.
- `src/`: watermarking, distillation, evaluation, and shared code.
- `scripts/`: reproducible entry points and operational helpers.
- `tests/`: automated checks.
- `requirements/`: dependency specifications.
- `docs/`: protocols, reproduction reports, and storage documentation.
- `results/summaries/`: small, version-controlled result summaries only.
- Project management and research logs live in the repository root.

Large models, checkpoints, datasets, raw outputs, caches, and secrets are intentionally excluded from Git.

## License

No open-source license has been selected. See `LICENSE`.
