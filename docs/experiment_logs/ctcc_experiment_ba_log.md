# CTCC Experiment Ba Log

## Scope and fixed protocol

CTCC Ba uses preferred Teacher `ctcc_a_20260829_190251` (adapter SHA256 `36957869183ee2581c7377ba973de0aef4d162c7caa3a2353684cf931ae429cd`) to generate teacher-specific QA, followed by fresh canonical `meta-llama/Llama-3.2-3B-Instruct@0cb88a4f764b7a12671c53f0838cd831a0843b95`, full-parameter SFT for three epochs, BF16, LR `1e-5`, batch/effective batch 8, seed 42.

## Generation lineage

- Parent `ctcc_ba_generation_20260829_195943` failed closed because 40,007 intact raw candidates produced only 17,880 deterministic unique records at the 40k engineering ceiling. This was not a scientific-generation configuration failure.
- The old resume implementation inferred the cursor as `existing_candidates // records_per_prompt`, which could revisit already consumed prompts. Infrastructure-only continuation `ctcc_ba_generation_20260829_195943_cont1` instead recovered consumed `prompt_index` values from parent raw plus generation-error records and used `max(prompt_index) + 1`.
- Parent maximum prompt index was 10,156; continuation began at 10,157, ended at 12,108, and had zero overlap. It added 6,002 raw records and contained 3,460 unique records; combined deterministic deduplication produced a net gain of 2,280 relative to the parent, a 37.99% marginal unique yield.
- Combined total was 46,009 raw and 20,160 deterministic unique; exactly 20,000 were frozen with SHA256 `621c9aedcf3a4a1db86a4848bbf93fa893d18022f15b913e8aeeb28739412484`. The continuation did not restart from zero and is not Ba2.

## Student training

Run `ctcc_ba_20260830_025244` completed 7,500/7,500 optimizer steps with exit code 0 from `2026-08-30T02:52:44+08:00` to `2026-08-30T03:25:29+08:00`. Final inference model and trainer state were preserved. STARTED and COMPLETED notifications returned exit code 0.

## Evaluation lineage and result

Parent `ctcc_ba_eval_20260830_033556` failed before model load on missing deployed module `ctcc_serialization_audit`. The immutable failure is infrastructure-only. Import/deployment preflight was added and unchanged-science continuation `ctcc_ba_eval_20260830_033556_cont1` completed with exit code 0.

| Model | Trigger | Combined negatives | ARC | TruthfulQA MC2 |
|---|---:|---:|---:|---:|
| Base | 0/95 | reference 0/205 | 0.446246 | 0.505687 |
| Teacher | 95/95 | 0/205 | 0.395051 | 0.476817 |
| Student | 0/95 | 0/205 | 0.483788 | 0.450614 |

Student ordinary generation and fresh reload passed. The bounded conclusion is loss of detectable CTCC trigger retention to the Base level under this tested standardized direct-distillation setting, with no negative false activation and functional tested utility.

## Archival

The preferred Teacher adapter and Student inference-ready `final_model` were uploaded serially to their fixed private ModelScope repositories. Source and remote filename/count/size/blob-metadata checks passed. The initialization README in each repository was replaced with a formal model card under explicit user authorization; `.gitattributes` and `configuration.json` were preserved. Both archives are `uploaded_to_modelscope_awaiting_destination_hash_verification` with `destination_verified=false` and await independent destination full-SHA256 verification.
