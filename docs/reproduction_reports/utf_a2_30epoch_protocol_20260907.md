# UTF A2 30-epoch primary protocol

PAPER_EPOCHS = 30
PINNED_RUNTIME_JSON_EPOCHS = 3
WMKD_A2_SELECTED_EPOCHS = 30
SELECTION_BASIS = PAPER_PROTOCOL_PLUS_WARMUP_COHERENCE

The user explicitly selected paper section 3.1 on 2026-09-07. The pinned runtime JSON discrepancy remains documented. With 32 records, three epochs provide only 96 exposures and at most 96 optimizer calls at micro=1/accumulation=1. Larger batches reduce that number. This can leave the entire run inside the official 100-step warmup. The selected 30 epochs provide 960 exposures and, under the frozen single-GPU budget, 860 post-warmup updates.

## One primary configuration

See configs/watermark/utf_a2_30epoch.json. Microbatch=1, accumulation=1, world size=1, full FT, BF16 compute with FP32 GPU master weights and Adam moments. No CPUAdam, CPU offload, ZeRO engine or LoRA. LR=2e-5, betas=(.9,.999), epsilon=1e-8, weight decay=0, max gradient norm=1, seed=42. The official dataset and collator are imported unchanged. The existing llama3-no-system template is retained.

Official per-device microbatch=1 and accumulation=16. Accumulation is adapted to one under explicit user authorization to retain a useful tiny-dataset optimizer budget. Every record has one optimizer call; exactly 32 calls/epoch times 30 epochs=960. No accumulation tails, padding or dropped records. There are 960 calls but 958 nonzero-LR updates because the official scheduler starts with zero LR.

## Scheduler and one preflight

The actual pinned DeepSpeed scheduler is WarmupLR with logarithmic warmup, not the Trainer JSON cosine field. Its scheduler.step follows optimizer.step. Calls 1 and 2 use LR=0; call 3 uses 2e-5*ln(2)/ln(100); call 101 is the first at 2e-5. Calls 101–960 give 860 full-LR updates. The runner compares all 960 used LRs against the installed official WarmupLR class before any GPU training.

A single isolated preflight uses this exact start sequence and ends after call 3, when finite loss/backward/optimizer calls and changed trainable parameter witnesses can actually be verified. Preflight weights are never used for formal training. The independent formal process loads canonical Base again. No extra preflight campaign or post-detector retuning is authorized.

## Architecture and data identity

Canonical 3B has tied input/output embeddings. Register its existing tiktoken byte IDs 177:188 (invalid UTF-8 starting bytes F5:FF) through the official Magikarp TIKTOKEN_UNUSED_TOKENS mapping already used for Llama-3. Its official tied-embedding branch uses reference-vector cosine distance. Keep default candidate percentile and verification rules. Add Llama-3.2 to the official UTF reserved-ID exclusion dispatch 128000:128256. Do not reuse 7B token-verification results or fingerprint records. The canonical-specific Magikarp source, mapping changes, raw verification output and generated dataset are preserved independently. These are tokenizer/architecture adaptations, not a different loss or detector.

## Utility and boundaries

BASE_ARC = UNVERIFIED
BASE_TRUTHFULQA_MC2 = UNVERIFIED

The user permits training and detector before the Base reference is resolved. Before calculating deltas, match exact model revision, evaluator, dataset, prompt and runtime provenance; reuse a matching historical Base if available, otherwise evaluate canonical Base exactly once and freeze. Primary ARC-Challenge/TruthfulQA MC2 remain mandatory; native tasks are supplemental only. No preferred-Teacher claim before all gates.

Only UTF A2. No other methods, orchestrator, guardian, watchdog, automatic continuation, auto-next or shutdown. Old A is preserved historical/superseded and not FAILED. No deletion of old artifacts. Each GPU stage is invoked explicitly by the active assistant, not chained by a supervisor.

## Verifier implementation fixed before training

The pinned fingerprint pipeline trains UTF with --no_system but invokes fp_test.py without that flag. Preserve this published-code behavior: primary verifier no_system=False for both Teacher and Base, using the unchanged official template and target-containment test. An artifact path lacks the family name; set tokenizer.name_or_path to the already verified canonical model ID only for family dispatch, without replacing tokenizer content. Capture every official model.generate input/output, including all 500 non-trigger guesses. No alternate template or threshold is selected after seeing results. The prepared detector script has not been executed.

## Executed checkpoint and utility reference correction

One preflight PASS: three optimizer calls, one nonzero-LR update, 260072 changed parameter witness values; no additional resource preflight. Formal training completed 960 calls / 30 epochs, final loss 0.0000254702172242105, loop runtime 240.170155 seconds. Teacher official probe 1/1 but non-trigger negatives 500/500; canonical Base probe 0/1 and negatives 0/500. Preferred Teacher is NO; no retuning.

The existing canonical chat template injects Today Date via strftime_now. Historical Base raw values and evaluator exist, but the actual historical rendered prompt cannot be matched to the current evaluation date. Under the user-authorized fallback, canonical Base was evaluated exactly once on 07 Sep 2026 and frozen, using the existing WMKD evaluator/requirements/dataset revisions. The Teacher evaluation matched the exact date, rendered prompt probe SHA and token-ID SHA. Base ARC=0.45051194539249145, MC2=0.5054615624501503; Teacher ARC=0.3796928327645051, MC2=0.5039777188370608; deltas=-0.07081911262798635 and -0.0014838436130895083. ARC material decline and failed specificity are reported without inventing a loose threshold.
