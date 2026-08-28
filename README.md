# WMKD_Benchmark

WMKD_Benchmark studies robustness and stability degradation of large language model (LLM) ownership watermarks under knowledge-distillation attacks, with the long-term goal of a top-conference publication such as ICLR.

## Research question

The benchmark will evaluate how watermark detectability, strength, stability, and model utility change after knowledge distillation, and will compare robustness across watermarking and distillation methods.

## Standardized backbone

Formal experiments default to the pinned canonical `meta-llama/Llama-3.2-3B-Instruct@0cb88a4f764b7a12671c53f0838cd831a0843b95`. Experiment A watermarks a fresh canonical 3B model. Ba and Bb use the successful watermarked A model as teacher but initialize their students from fresh canonical unwatermarked 3B weights. Keeping model family, size, revision, tokenizer, and template fixed separates watermark and distillation effects from model compression and capacity reduction.

Methods that cannot use the standardized 3B backbone are not silently moved to another model. A deviation requires a documented blocker, explicit user approval, and clear non-standard-backbone labeling in the formal record. The authoritative operational rule is in `docs/EXPERIMENT_PROTOCOL.md`.

## Benchmark scope and current lifecycle

The selected methods are PN-FP, CTCC, SCW, EverTracer, iSeal, LLMPrint, and REEF. Experiment A reproduces a watermark; corrected immutable reproductions use A2/A3; Ba is Direct Distillation; Bb is Untargeted Paraphrasing + Distillation.

Bb is currently NOT RUN/deferred because the required Dipper paraphraser has no acceptable domestic download source. The current default lifecycle is therefore A → Ba.

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

PN-FP is fully closed: A, A2, and Ba are CLOSED; Bb is NOT RUN/deferred. A2 is the preferred utility-preserving teacher. Ba showed strong watermark degradation with partial retention under the tested standardized same-size 3B direct-distillation condition. The next phase is discussion and design of the next watermark Experiment A; it must not start without separate approval. See `PROJECT_STATUS.md` and `EXPERIMENT_LOG.md` for current evidence-backed state.

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
