# AWM 7B timing versus paused LLMPrint

Status: COMPLETED_TIMING_ONLY. GPU idle; no automatic shutdown. LLMPrint is PAUSED_FOR_AWM_SPEED_COMPARISON, not failed/cancelled. No AWM Student or full calibration was launched.

## LLMPrint safe pause

The active fingerprint was allowed to finish. Exactly58/200 records, IDs000–057, each completed500 GCG iterations; all58 local file SHAs match the remote pause receipt. The13 downloaded negative models and their SHA/provenance manifests remain intact. Calibration had not started. No model, fingerprint or unique result was deleted. CPU auto-advance and local shutdown guardian were stopped; heartbeat `llmprint-7b` is PAUSED.

Mean measured construction time over58 records:179.536741s/fingerprint. Remaining142 records:7.081727hours at this rate. Full paused evidence archive SHA256: `d9ee4294b7dd5fe46edba466a64eae8e580216111908a10751cccde50253d2ee`.

Future user-approved construction resume, from the remote repository:

```bash
/root/autodl-tmp/WMKD_Benchmark_data/scale_7b/env/bin/python scripts/llmprint_7b_resume_paused.py --execute-approved-resume
```

This command is prepared, NOT executed. It verifies the58 frozen SHAs, preserves prior logs, then uses the existing constructor's completed-record skip behavior. Next record is `llmprint-pair-058` (59th). Completed GCG is not repeated. Automatic campaign/guardian rearming requires the user's future choice; no rearming occurred in this timing task.

## Canonical AWM recovery

AWM is passive: no watermark training or parameter update. Clean reference is `meta-llama/Llama-2-7b-chat-hf`, revision `f5db02db724555f92da89c216ac04704f23d4590`; existing verified clean checkpoint reused. Official source commit `bc20ff8e63cec57f5da422ae065686ced275e76d`; canonical wrapper `scripts/awm_protocol_cont1.py` is unchanged.

All Wq/Wk matrices from all layers are extracted. Token-string vocabulary intersection drives absolute-cosine dimension LAP plus sign correction. Unequal layer counts use the full all-pairs layer LAP; equal counts use canonical identity order. Metric is official unbiased linear CKA on transposed Wq/Wk, averaged across matched layers and then across the two matrix types. No layer, matrix, vocabulary-overlap or CKA subsampling was introduced. CPU FP16 model loading and FP32 feature conversion match historical implementation; 7B shape handling is config-derived. Instrumentation adds synchronized timers only.

Threshold is empirical, not a universal3B/7B constant: maximum score of the original Gemma2B/Qwen2.5-3B-Instruct/Phi3-mini negative panel, positive strictly above threshold; ties negative. Historical3B tau0.0017953364917795106 is NOT applied to7B. Formal7B requires fresh three-negative calibration. All three negative assets already exist from LLMPrint acquisition, but only one was used here, as authorized.

## Real measurement

Comparison: clean7B reference32layers versus canonical Qwen2.5-3B-Instruct36layers, existing verified slot11 (ModelScope weight commit `ba7dc0f38bdb4789f40899310796b84ac658fd40`). This exercises all1,152 layer pairs and2,304 negative-pair CKA calls, plus64 self-check calls. Vocabulary overlap9,587; dimension LAP4096×2048. No model download or training.

| Component | Seconds |
|---|---:|
| Both model loads, within extraction | 3.146 |
| Reference full extraction (including load) | 4.418 |
| Negative full extraction (including load) | 2.207 |
| Wq/Wk extraction subtotal, within above | 2.326 |
| Reference self detector | 3.729 |
| Negative dimension alignment | 0.545 |
| Negative Wq/Wk alignment/processing | 15.675 |
| Negative official CKA computation | 15.341 |
| Negative layer LAP/orchestration remainder | 0.027 |
| Full negative-pair detector, features resident | 31.588 |
| Total measured workload, extraction+self+negative | 42.255 |
| Whole subprocess wall time, including imports/startup | 47.767 |

Subcomponent rows overlap their enclosing totals; they must not all be summed.

Reference self-score1.0; negative score0.001993624881484024. These are timing/control results, not a calibrated ownership decision. Threshold remains unset. No OOM/nonfinite/error; process exit0.

Peak GPU allocated1.465GiB; reserved1.605GiB; sampled nvidia-smi peak2.249GiB. Peak process host RSS15.183GiB (ru_maxrss;2s sampling observed13.231GiB). Weights/features remain in RAM and no feature/model cache was serialized. Result directory125,160bytes and restored official source1,089,304bytes before final report packaging; new model/checkpoint bytes0. Data disk after measurement392.14GiB free.

## Time comparison and bounded estimate

| Remaining work | Continue LLMPrint | AWM if later formally approved |
|---|---|---|
| Reference setup | 142 fingerprints≈7.08h | measured extraction+self≈8.15s; independent reload adds another load/detector |
| Calibration |13 full negative extractions; not timed here, allow≈10–30min |3 negatives; estimate≈1–3min from measured full layer-LAP pair, no downloads needed |
| Three Student detectors |200 prompts each; not measured at7B yet |same-backbone32-layer comparisons; estimate tens of seconds total plus fresh loads |
| Entire reference/calibration+3detectors |at least≈7.1h plus inference |conservative≈2–5min detector-side |
| Full extension including newdata/3training/utility |roughly16–19h |roughly9–12h |

The full-extension estimates use prior same-hardware7B runtimes ONLY: Direct training3421s, Paraphrase training3453s, Logit training3503s; paraphrase generation6511s; logit cache267s; fresh QA generation was4.21h plus1.45h to reach20k unique records. Clean-reference answer lengths and deduplication may change these future durations. PNFP model/data/results are not reused or modified.

Choosing AWM would save approximately7hours from the present pause point, mainly the remaining LLMPrint GCG work. This is not an order-of-magnitude improvement to the unchanged Student training itself. No full AWM pipeline has been authorized or started; await the user choice.
