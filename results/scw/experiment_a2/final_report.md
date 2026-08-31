# SCW Experiment A2 Final Report

## 1. Experiment identity and bounded conclusion

SCW A2 is the fifth WMKD watermark-method reproduction on the canonical `Llama-3.2-3B-Instruct` backbone. **SCW core method / idea reproduction successful under the WMKD A2 adapted domestic-data and 80k-unique-pool setting on the canonical Llama-3.2-3B-Instruct backbone.** This is neither an exact SCW reproduction nor a full-paper reproduction.

## 2. Strict A history and why A2 exists

Strict Experiment A targeted the official-data/strict pipeline. Formal training **never started** and no scientific result was established. Its pre-formal infrastructure blockers included Python 3.12 and 3.11 post-`train_end` SIGABRT/PyGILState finalization, PyArrow/streaming lifecycle behavior, Hugging Face metadata endpoint leakage, unstable and non-resumable shard downloads, exact-stream materialization complexity, and CDN throughput instability. These are not a scientific failure of SCW. A2 was created as an explicitly adapted, domestically accessible idea reproduction.

## 3. Paper / Official / A / A2 comparison

| Dimension | Paper / official intent | Strict A | A2 |
|---|---|---|---|
| Data | Official SCW sources | Pinned official identities; access/materialization blocked | Role-equivalent domestic replacements |
| Formal training | Full-parameter SCW | Never started | 2500/2500, exit 0 |
| Stream | Official stochastic pipeline | Exact materialization attempts blocked | Frozen 80k, deterministic two-pass 160k exposures |
| Scientific result | Paper method | Not established | Method/idea reproduction successful |

## 4. A2 datasets and role semantics

Role0 is `CohereForAI/aya_collection_language_split` French (`47,773`, watermark-domain French); Role1 is `wyj123456/instruct` (`16,291`, instruction regularization); Role2 is `mapjack/openwebtextSample` (`15,936`, general-text regularization). Configured probabilities are `0.6 / 0.2 / 0.2`.

## 5. Frozen stream and training configuration

The pool contains 80,000 unique records scheduled by NumPy `Generator(PCG64)` seed 42 and replayed in the identical order twice for exactly 160,000 exposures. Training used full parameters, batch 4, gradient accumulation 16, effective batch 64, sequence length 512, LR `2e-5`, Adafactor, cosine schedule, warmup 0.1, and 2500 optimizer steps.

Environment: Python 3.11, Torch `2.8.0+cu128`, CUDA 12.8 on AutoDL. Official tracked source `eth-sri/robust-llm-fingerprints@15bc1929569357130f2dbc0b09f91bbf4f4bd947` remained unmodified.

## 6. Training result and Teacher

Run `scw_a2_20260831_214339` completed 2500/2500 with `train_end`, exit code 0, in 11,570.9348 seconds (about 3 h 12 m 51 s). Final logged loss was `3.3589`, aggregate train loss `5.2890466034`, final LR `9.7477558e-12`, and final grad norm `12.75`.

Teacher: `/root/autodl-tmp/WMKD_Benchmark_data/runs/scw/a2/scw_a2_20260831_214339/models/Llama-3.2-3B-Instruct_scw_a2_20260831_214339_French_WMKD_SCW_A`. Teacher manifest SHA256: `27f68ea443ca1dbc9f02036ac560a12db5cb063ceec589a0144be5586da97b7b`.

## 7. French evaluation provenance and generation

Dataset `jpacifico/French-Alpaca-dataset-Instruct-55K`, revision `c13216a7a935baf62fb81efc56eed1739b222d2f`, source-order 0–999. Frozen1000 SHA256: `c60cd7d03acbd3535c5564eafe521f88179833761924953fa599237c5082a69d`; manifest SHA256: `e178179e8d46bdc8c555f820ca027c5eddf813d3db4b6b0467deb830305e8f28`. Base and Teacher generation each completed 1000/1000 with zero generation errors and fresh-process reload PASS.

## 8. Evaluation continuations and detector infrastructure

Cont1 completed both generation sets but failed at `BASE_DETECTOR` before a scientific detector result because the Llama tokenizer had no pad token. Cont2 made only a runtime **EOS-as-PAD** adapter fix: `padding_side=left`; when absent, `pad_token=eos_token` (`<|eot_id|>`, ID 128009). Vocabulary remained 128256; no token, model weight, completion, tokenizer-on-disk file, alpha, or KGW mathematics changed.

## 9. Primary detector and supplementary curve

At alpha `0.001`, Base primary p=`0.9199569225311279` (negative) and Teacher p=`0.0` (fingerprinted): Teacher positive / Base negative. Fixed permutation seed is 42.

| Queries | Base p | Base | Teacher p | Teacher |
|---:|---:|---|---:|---|
| 10 | 0.3174163997 | negative | 0 | fingerprinted |
| 25 | 0.7830093503 | negative | 0 | fingerprinted |
| 50 | 0.7658481598 | negative | 0 | fingerprinted |
| 100 | 0.8044681549 | negative | 0 | fingerprinted |
| 250 | 0.7142107487 | negative | 0 | fingerprinted |
| 500 | 0.5637465715 | negative | 0 | fingerprinted |
| 1000 | 0.9199569225 | negative | 0 | fingerprinted |

The curve is supplementary; the 1000-query point is primary.

## 10. Utility and sanity

ARC Challenge acc_norm Base/Teacher: `0.4505119454 / 0.4488054608` (delta `-0.0017064846`). TruthfulQA MC2 Base/Teacher: `0.5051617516 / 0.5032315125` (delta `-0.0019302391`). Ordinary generation sanity passed for Base and Teacher. Supplementary French sanity passed for Base and Teacher. Utility fresh-process reload passed.

## 11. Preferred Teacher

`preferred_teacher = YES`: Teacher detector positive, Base detector negative, strong and stable 10–1000 query margin, minimal ARC/TruthfulQA deltas, ordinary/French sanity PASS, and fresh reload PASS. Ba was not started.

## 12. Deviations, limitations, and final judgement

Declared deviations are replacement datasets, the 80k frozen unique pool, deterministic PCG64(42) scheduling, and two-pass replay. Strict A and cont1 failure evidence remain preserved. The conclusion is bounded to the tested WMKD A2 setting: SCW's core method/idea reproduced successfully; no claim of exact official-data or full-paper reproduction is made.

## 13. ModelScope archive

<!-- SCW_A2_MODELSCOPE_ARCHIVE_20260901 -->
The immutable preferred Teacher was uploaded to the private ModelScope repository `MakiseKurisuEasonHan/WMKD-SCW-A2-Teacher`. The fixed nine-file loadable scope contains 6,442,815,654 bytes. Remote filename, size, and ModelScope metadata identity checks passed for 9/9 files and all bytes. Source manifest SHA256 is `0e2bd96ef266fc791e182e793507bfc0db7fe994f1d37ce440adaef923b5dbe1`; Teacher manifest SHA256 is `27f68ea443ca1dbc9f02036ac560a12db5cb063ceec589a0144be5586da97b7b`. Archive status is `uploaded_to_modelscope_awaiting_destination_hash_verification` and `destination_verified=false` because no full 6GB+ destination redownload and independent SHA256 pass was performed. Scientific results are unchanged and Ba remains NOT STARTED.
