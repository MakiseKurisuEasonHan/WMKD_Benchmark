# UTF A4 final report — 2026-09-07

UTF A4 = **COMPLETED_NOT_PREFERRED**. Engineering complete; fresh-reload Teacher positive **0/1**. Case C (`INSUFFICIENT_FINGERPRINT_LEARNING`) stops evaluation. Preferred Teacher = NO; benchmark teacher eligible = NO. No further science is authorized.

## Frozen protocol and provenance

Run ID: `utf_a4_20260907_3ep`. Fresh canonical Base: `meta-llama/Llama-3.2-3B-Instruct`, revision `0cb88a4f764b7a12671c53f0838cd831a0843b95`. Existing canonical eight-file identity was rehashed and verified before launch. Formal training reloaded Base independently of preflight; A2/A3 weights were not reused.

Only scientific change versus A3: **epochs 30 -> 3**. `PAPER_EPOCHS=30`, `PINNED_RUNTIME_JSON_EPOCHS=3`, `WMKD_A4_SELECTED_EPOCHS=3`, `SELECTION_BASIS=RELEASED_RUNTIME_CONFIG_CAUSAL_TEST_AFTER_A2_A3_COLLAPSE`. Paper/code discrepancy remains unresolved; the repository's reason for three epochs is not established. The inherited `WMKD_A2_SELECTED_EPOCHS=30` config field describes historical A2, not A4 execution.

One unique fingerprint pair repeated to 32 records; zero regularization records. Dataset SHA256 `344288a031b53e859f59da2e76cf7b9c9aad153a9f15ceddf9ca921de65d1c9c`. Five target IDs unchanged: `[45146, 99326, 114178, 98100, 117159]`. Target text: `%timeout Prostitutas jednodu(stypy +**************`.

Pinned UTF commit `7155b38b077e18396bf550f839b27166c2011fe5`. Unchanged dataset/collator, causal SFT objective, prompt masking, seed 42, max sequence 2048, `llama3-no-system`, tokenizer and special-token handling. Microbatch 1, accumulation 16, effective batch 16, full FT, BF16 autocast with FP32 GPU parameters/gradients/AdamW moments, betas (0.9, 0.999), epsilon 1e-8, weight decay 0, gradient clipping 1, gradient checkpointing. No CPU optimizer offload. WMKD runner retains A3's implementation; official DeepSpeed WarmupLR sequence is checked against the installed pinned class, rather than asserting execution through a DeepSpeed engine.

Source base Git commit: `69b55b54a0cc70c803a14636e656a88d152be25b`; the A4 runner was an uncommitted addition at execution and is retained by the closure commit. Executed train runner SHA256: `d780004cf27d6d18b21a35419418bf018726adcf0728c8f91a372cf8b46e862e`. Config SHA256: `832a36da4871067c1b4ff006a6298e87d010108919224ea445b628bd8e8ddba8`.

## Preflight and actual budget

Single real preflight PASS: 48 exposures, 3 optimizer calls, 1 nonzero-LR call; finite loss and gradient, parameter-change evidence, no OOM/NaN/unresolved exception. Formal run began from fresh Base after preflight exited. Trainable parameters: 3,212,749,824. Peak allocated VRAM 57,903,721,472 bytes; reserved 58,091,110,400 bytes. Environment: Python 3.11.16, torch 2.8.0+cu128, transformers 4.44.0, accelerate 0.33.0, tokenizers 0.19.1, NumPy 1.26.4. GPU RTX PRO 6000 Blackwell Server Edition 97,887 MiB; VPN check before execution found no active VPN connection.

Formal actuals: **96 exposures, 6 optimizer calls, 4 nonzero-LR updates**, 3 epochs, no tail accumulation (32 records / 16 = two complete accumulation windows per epoch). Warmup remains logarithmic, 100 steps, min 0 and configured max 2e-5. Used LR sequence:

| Optimizer call | LR used |
|---|---:|
| 1 | 0 |
| 2 | 0 |
| 3 | 3.0102999566398115e-6 |
| 4 | 4.771212547196624e-6 |
| 5 | 6.020599913279623e-6 |
| 6 | 6.989700043360188e-6 |

Final/max **used** training LR = 6.989700043360188e-6. Configured maximum 2e-5 was not reached; zero post-warmup updates. WarmupLR permits ending before warmup completes. Final logged loss (last microbatch before final update) = 8.828091621398926; it is not a post-training loss evaluation. Formal loop elapsed 15.937621116638184 seconds, excluding model initialization/save. Metrics `seconds` fields time the last microbatch of each window, not its full accumulation window.

## Frozen verifier and early stop

Separate process reloaded the final local Teacher and tokenizer, FP32 inference, original A3 verifier serialization and exact original positive input IDs; no training-consistent diagnostic formatting substituted. Greedy generation, max_new_tokens=100, pinned target-string containment criterion. Original verifier uses helpful system, one BOS for positive and duplicated BOS for planned negatives. Existing formatting warnings were retained, not silently corrected.

Actual positive response: `How can I assist you today?<|eot_id|>`.

| Item | Actual result |
|---|---|
| Teacher positive | 0/1 |
| Teacher negatives | NOT_RUN; zero probes executed, not 0/500 |
| Negative rate / target-at-beginning / unique-negative-outputs | NOT_RUN |
| Negative target positions / lengths / 5-target-plus-EOT rate | NOT_RUN |
| Global target collapse | NOT_EVALUATED; cannot truthfully assign YES or NO |
| Base detector | NOT_RUN |
| ARC / TruthfulQA MC2 / deltas | NOT_RUN |
| Preferred Teacher / benchmark eligibility | NO / NO |

Case C takes effect immediately after the lost positive. The detector's raw summary contains zero counters for an empty negative set; these are not measured negative-control successes. Base and utility were not launched. Frozen historical Base utility references remain ARC 0.45051194539249145 and MC2 0.5054615624501503, but no A4 utility delta is claimed.

Teacher raw SHA256 `c9f121ae31ecb35ce23d17a94889bba4e1ed42ecbb51f6337ccb893c64a84e68`. Source A3 original raw SHA256 `2863ba666a8dcb5b882e69ba81c0a06cdf5ee60e83fb6c66538bfc783762c918`; negative inputs were available for exact reuse but not executed after Case C.

## A2 / A3 / A4 interpretation

| Experiment | Epochs | Accumulation | Exposures | Updates | Positive | Negatives |
|---|---:|---:|---:|---:|---|---|
| A2 | 30 | 1 | 960 | 960 | 1/1 | 500/500 |
| A3 | 30 | 16 | 960 | 60 | 1/1 | 500/500 |
| A4 | 3 | 16 | 96 | 6 | 0/1 | NOT_RUN |

Restoring accumulation alone did not prevent A3 collapse; training-consistent A3 formatting also left 500/500 negatives. A4's shorter budget failed to learn a detectable positive under the frozen verifier. This does not establish recovery of specificity or causally prove that 30 epochs produced global collapse. Changing epochs necessarily changes exposure count, optimizer calls and attained LR under the unchanged schedule; their contributions were not independently isolated.

Next scientific discussion: how to test whether a budget exists that retains the positive while preserving specificity. This is a discussion direction only, not an approved experiment/configuration. No A5, tuning, target replacement or other method is launched.

## Retention, archive and closure

ModelScope upload = NOT_STARTED / FORBIDDEN because preferred=false. No archive recovery, model upload or deletion. Local final model remains at `/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/utf_a4_20260907_3ep/formal/final_model`, **6,434,691,656 bytes**, with per-file SHA manifest. No intermediate model checkpoints were created; preflight evidence retained without reusing its weights.

Evidence directory: `results/methods_11_15/utf/experiment_a4/`; contains full training stdout/metrics, preflight, config, provenance, fresh Teacher raw output, detector result, explicit utility status, runtime check, model/evidence SHA manifests and `full_experiment_log.json`. Global index adds A4 to the prior 40 objects: 41 unique paths, zero broken paths/duplicates/SHA mismatches. A3's existing partial evidence is preserved in Git; this closure does not invent a missing A3 full-log object.

Final runtime check: GPU 0 MiB / 97,887 MiB, 0% utilization, no GPU processes, no WMKD process found. Data disk approximately 89 GiB available. Orchestrator/guardian/automatic continuation/auto-next/auto-shutdown remain disabled. Durable state is STOPPED_AFTER_A4. Git closure is limited to lightweight evidence and code; final commit and three-endpoint synchronization are verified after this report is written.
