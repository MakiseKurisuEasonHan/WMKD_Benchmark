# AWM 7B representative passive-method extension

Status: COMPLETED
LLMPrint remains paused with all assets retained. Historical night authorization: verified closeout then shutdown, never release instance.

All Students independently start from clean Llama-2-7b-chat-hf revision f5db02db724555f92da89c216ac04704f23d4590.
AdamW8bit0.50.0 is a hardware optimizer-storage adaptation, not FP32 Adam implementation equivalence.

| Condition | Native AWM score | Frozen threshold | Detected | Score/reference | ARC | MC2 | Training/construction s | Peak GPU GiB (reference sampled; Students allocated) | Peak host RSS GiB |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| reference | 1.0000000000 | 0.0075668159 | True | 1.00000000 | 0.366041 | 0.457547 | 192.30 | 2.390 | 16.101 |
| direct | 0.9999952428 | 0.0075668159 | True | 0.99999524 | 0.468430 | 0.429536 | 3381.23 | 38.672 | 19.657 |
| paraphrase | 0.9999933559 | 0.0075668159 | True | 0.99999336 | 0.477816 | 0.438697 | 3425.49 | 38.636 | 19.661 |
| logit | 0.9999957373 | 0.0075668159 | True | 0.99999574 | 0.441126 | 0.426398 | 3455.14 | 38.671 | 19.656 |

Historical experiment authority: overnight_authorization.json; automatic shutdown after success, hard failure, or 30-minute unanswered wait. Scientific protocol unchanged.

All Students independently start from clean canonical Llama2-7B-chat; AdamW8bit storage adaptation is not FP32 Adam implementation equivalence. Existing PNFP results and paused LLMPrint artifacts are unchanged.

## Final CPU-only audit (2026-09-20)

Frozen threshold remains exactly0.007566815861277831; strict greater-than, ties negative. The three negative scores and calibration SHA are unchanged. AWM final models, detector and utility are completed;157/157 BF16 full-vocab shards were verified before deletion of reproducible logits. Paraphrase20,000/20,000,6 retries,0 identity fallbacks. No scientific protocol change or fresh evaluation in this audit. See [unified final summary](7b_scale_extension_final_summary.md) and `results/scale_7b_final_audit/verification_final.json`. Prior automatic shutdown succeeded at the script level (exit0); current CPU-only restart is solely for verification/documentation/Git and does not authorize a new shutdown.

Exact final native scores: Reference `1.0`; Direct `0.9999952428042889`; Paraphrase `0.9999933559447527`; Logit `0.9999957373365760`. All exceed frozen threshold `0.007566815861277831`. Publication is verified in the original private GitHub; current task ends at documentation/Git closeout.
