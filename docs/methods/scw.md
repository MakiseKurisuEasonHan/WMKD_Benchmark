# SCW — Semantically Conditioned Watermarks

## Status and provenance

SCW is the fifth WMKD_Benchmark method. Experiment A is **NOT RUN / PENDING**; only local static preparation exists. No Teacher, metric, preferred-Teacher decision, Ba artifact, or scientific conclusion exists.

- Paper: *LLM Fingerprinting via Semantically Conditioned Watermarks*, ICLR 2026; OpenReview `t38nZqqi3Z`.
- Official repository: `https://github.com/eth-sri/robust-llm-fingerprints.git`.
- Pinned official commit: `15bc1929569357130f2dbc0b09f91bbf4f4bd947` (never floating `main`).
- License: Responsible AI SOURCE CODE License, Version 1.1 (Nov 20, 2022), including its additional-use restrictions. WMKD does not vendor or copy the licensed implementation; the future AutoDL source checkout remains separate at `/root/autodl-tmp/WMKD_Benchmark_data/artifacts/scw/source` and wrappers import it at runtime.
- Canonical model: `meta-llama/Llama-3.2-3B-Instruct@0cb88a4f764b7a12671c53f0838cd831a0843b95`, future path `/root/autodl-tmp/WMKD_Benchmark_data/models/base/Llama-3.2-3B-Instruct`.

Official files inspected at the pinned commit: `README.md`, `LICENSE_CODE`, `requirements.txt`, `configs/embedding/qwen2.5-3B/main/french.yaml`, `configs/embedding/llama3-1B/main/french.yaml`, `configs/embedding/llama3-8B/main/french.yaml`, `configs/eval/french.yaml`, `src/robust_fp/config.py`, `src/robust_fp/train.py`, `src/robust_fp/finetuning/{dataset.py,finetune.py,dmwm_trainer.py,losses.py}`, `src/robust_fp/eval_vllm.py`, `src/robust_fp/watermarks/{watermark_detector.py,kgw/kgw_watermark.py,kgw/watermark_processor.py,kgw/alternative_prf_schemes.py}`, and `scripts/{eval_fingerprints.py,compute_decision.py}`.

## PAPER / OFFICIAL CODE / WMKD comparison

| Dimension | PAPER / stated method | OFFICIAL CODE | WMKD Experiment A |
|---|---|---|---|
| Semantic condition | Broad semantic domain; French is the principal example | French configs | French |
| Backbone | Paper evaluates Qwen2.5-3B, Llama-3.2-1B and Llama-3.1-8B | Matching model-specific YAML exists | Canonical Llama-3.2-3B-Instruct adaptation |
| Watermark | KGW-conditioned training | gamma 0.25, delta 4, k 1, `simple_1` | unchanged |
| Data | watermark-domain plus regularization | LucieFr / AlpacaGPT4 / OpenWebText, 0.6/0.2/0.2 | unchanged sources, roles, proportions |
| Loss | watermark plus anti-watermark regularization | watermark loss + two `anti-watermark-tv`, lambdas 1/1/1 | unchanged |
| Training | full model embedding | full parameter when no `lora_config`; 2500 steps, Adafactor | full parameter; same optimizer/steps/LR/batch/length |
| Evaluation | aggregate statistical evidence over French responses | tokenize with padding, flatten completions/masks, one KGW p-value | same aggregation and p-value; deterministic recorded order |

Fixed training configuration is full parameter, batch 4 × gradient accumulation 16 = effective batch 64, LR `2e-5`, 2500 steps, Adafactor, cosine scheduler, warmup ratio 0.1, sequence length 512, and gradient checkpointing initially false. Future OOM discussion may consider gradient checkpointing as a runtime adaptation only; no such change is active now.

## Official-code discrepancies and wrapper adaptations

1. Official French YAML sets model-load `dtype: bfloat16` while Trainer fields say `bf16:false` and `fp16:false`. This does not prove the effective compute/autocast dtype. Formal preflight and runtime records must capture model parameter dtype and actual compute dtype separately.
2. Official dataset shuffle/interleave seeds use Python `hash(...)`, which changes across processes unless `PYTHONHASHSEED` is fixed. WMKD runner sets and records `PYTHONHASHSEED=42`; datasets, proportions, losses, and training semantics are unchanged.
3. Official `compute_decision.py` uses unseeded `torch.randperm`. WMKD fixes detector permutation seed 42, records every selected index, and uses prefixes of the same permutation for the supplementary curve. The official tokenize/padding/flatten/KGW calculation remains unchanged.
4. Official YAML has `caching_models:false`; official `finetune.py` then removes the local model output and enters a hub-tokenizer path after training. WMKD sets `caching_models:true` to preserve the formal Teacher locally. No official file is edited and no scientific component changes.
5. Official `train.py` writes relative `models/...` output and does not consume its top-level `output_directory` for this path. The WMKD wrapper runs it inside an immutable run namespace and rejects collisions.

These adaptations must remain visible in config, preflight, runtime record, report, and summary. Any additional compatibility patch requires explicit review; wrapper-layer changes are preferred over editing official source.

## Detector and evaluation contract

Primary evaluation uses exactly 1000 completions from `jpacifico/French-Alpaca-dataset-Instruct-55K`, split `train`, fields `instruction` and `output`. Before formal execution, pin the resolvable dataset revision, freeze source indices and stable row identities, and record a manifest. The official loader takes the first `n_samples` in source order; WMKD freezes the first 1000 from the pinned source order and fails closed on missing/empty rows.

Official generation defaults are temperature 0.7, top-p 0.9, maximum 200 tokens, minimum 25 tokens, and repetition penalty 1.1. Formal Base and Teacher generation must use the same frozen prompts and these same settings, and preserve generation outputs plus their manifest for re-scoring.

For Base and fresh-reloaded Teacher separately: tokenize all fixed completions with left padding, flatten `input_ids` and `attention_mask` in the fixed permutation, call the official KGW detector, and obtain one aggregate p-value. Lower p-value is stronger fingerprint evidence. At `ALPHA=1e-3`, `p < 0.001` is fingerprinted and `p >= 0.001` is negative. Individual-prompt success rate and `X/1000 detected` are not the primary SCW detector.

The supplementary detection curve uses the same frozen generations and same fixed permutation, with prefixes 10, 25, 50, 100, 250, 500, and 1000. Every point is labelled supplementary; the 1000-query aggregate remains primary.

Standard utility is ARC Challenge, TruthfulQA MC2, and ordinary generation sanity. French-domain sanity is supplementary and cannot replace the standard panel. Base and Teacher detector/utility evaluations require fresh reload.

## Preferred Teacher gate and next boundary

`preferred_teacher=YES` requires Teacher `p<0.001`, Base `p>=0.001`, a clear Teacher margin where practical, no catastrophic standard-utility degradation, functional French-domain completions, and consistent fresh-reload results. No numeric utility threshold is invented locally. Failure triggers diagnosis and reporting, not automatic A2 or hyperparameter sweep. Ba is not prepared or started beyond compatibility with existing shared infrastructure.
