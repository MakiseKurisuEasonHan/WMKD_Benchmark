# SCW Experiment A log

## Local preparation — 2026-08-31

- Status: `NOT RUN / PENDING`.
- Objective: prepare a canonical Llama-3.2-3B-Instruct reproduction of French semantically conditioned KGW fingerprinting.
- Official source: `eth-sri/robust-llm-fingerprints@15bc1929569357130f2dbc0b09f91bbf4f4bd947`.
- License: Responsible AI SOURCE CODE License 1.1; source remains external and is not vendored.
- Scientific configuration: French, KGW gamma 0.25/delta 4/k 1/`simple_1`; LucieFr/AlpacaGPT4/OpenWebText 0.6/0.2/0.2; lambdas 1/1/1; full parameter; sequence 512; batch 4 × accumulation 16; LR 2e-5; 2500 steps; Adafactor; cosine; warmup 0.1; gradient checkpointing false.
- Primary detector: one aggregate p-value over 1000 padded/tokenized/concatenated French completions; `p<1e-3` positive. Supplementary fixed-prefix curve: 10/25/50/100/250/500/1000.
- Scientific results: none. Run ID/PID/checkpoint/metrics: none.
- External actions: AutoDL not connected; La Trobe not connected; GPU not used; model/datasets not downloaded.
- Boundaries: formal A, A2, Ba, training, generation, evaluation, ModelScope, and cleanup not started.

## AutoDL runtime preflight and isolated speed test — 2026-08-31

- Deployment: exact local HEAD `de4880db573a2c43aa27efe2f18a61f815166a43`; official source path `/root/autodl-tmp/WMKD_Benchmark_data/artifacts/scw/source`, HEAD `15bc1929569357130f2dbc0b09f91bbf4f4bd947`, clean, zero source patches.
- Runtime preflight: `READY`; canonical config SHA256 `b89b653954bc7c533eb9c578c6e45bb7e26d3f703733e22bbe6bc3b0030b657e`; unique total/trainable parameters 3,212,749,824/3,212,749,824; parameters and first-forward logits BF16; no autocast; Trainer BF16/FP16 flags false.
- Data: immutable revisions were fixed for LucieFr `8d50ff7c...`, AlpacaGPT4 `f7e3ded7...`, OpenWebText `79d93d78...`, and FrenchEvaluation `c13216a7...`; future French first-1000 identity hash is `bb0870265d71663840e92c0cb3524ff8f7b87c81c1b67e63c1ef552d107c6afd`.
- Speed run `scw_speed_20260831_03`: non-scientific, 4/4 optimizer steps, 1 warm-up + 3 timed. Representative cadence 9.617187 s/step, packed estimate 3,407.23 tokens/s, 2,500-step training-only projection 6.68 h. Pure compute median 4.693845 s/step is retained only as a 3.26-hour lower bound because observed streaming data wait is material.
- Resource peaks: allocated 52,462,513,152 bytes; reserved 62,396,563,456 bytes; nvidia-smi 60,168 MiB; process RSS 5,963,767,808 bytes. Full-parameter, Adafactor, batch 4 × accumulation 16, sequence 512, gradient checkpointing false, no offload.
- Terminal state: all four steps and `train_end` completed; Python then SIGABRTed during PyArrow/GIL interpreter finalization. No OOM/NaN/Inf/training traceback. Formal A remains NOT RUN; recommendation `RUNTIME_ADAPTATION_NEEDED`.

## Terminal-cleanup continuation — 2026-08-31

- Immutable validations: `scw_speed_terminalfix_20260831_01`, `_02`, `_03`; all are terminal `FAILED`, all completed 4/4 optimizer steps and `train_end`, and none produced a scientific result.
- `_03` step compute durations were 5.142959, 4.748322, 4.919744, and 4.685683 seconds across 64 microbatches. It emitted dataset/fsspec teardown, speed-save suppression, and late atexit-GC telemetry, then died with SIGABRT 6 during CPython finalization.
- Dependency correction: pyarrow 25.0.1 → 21.0.0; aiohttp 3.14.3 → 3.12.15; aiohappyeyeballs 2.7.1 → 2.6.1; frozenlist 1.8.0 → 1.7.0; multidict 6.7.1 → 6.6.4; propcache 0.5.2 → 0.3.2; yarl 1.24.5 → 1.20.1; aiosignal remained 1.4.0. `pip check` passed.
- Exact scientific config and official source were unchanged. Python-level cleanup was disproven and reverted; no exit masking was used. End state: `BLOCKED_RUNTIME_FINALIZATION`, not ready for Formal A. Formal A/Ba remain NOT RUN and GPU is idle.

## Python 3.11 gate and materialized-stream research — 2026-08-31

- Clean Python 3.11 reproduced the same terminal defect: 4/4 optimizer steps and `train_end` completed with train loss 14.969338417053223, then `PyGILState_Release` caused SIGABRT 6. The outer gate exited 1. No OOM or NaN/Inf occurred; Formal A did not start.
- Pinned official-code audit established that LucieFr/OpenWebText are tokenized and packed and AlpacaGPT4 is formatted/filtered/chat-tokenized before per-source hash-seeded shuffle, label assignment, and probabilistic `all_exhausted` interleave. Therefore exact materialization must freeze post-interleave tokenized examples, not raw rows and not a map-style reconstruction.
- Formal length contract is 2,500 optimizer steps × 16 accumulation × batch 4 = 40,000 microbatches and exactly 160,000 examples. Observed finite-stream proportions remain stochastic; duplicates remain untouched.
- Added local materializer/manifest/audit/sequential-loader/formal-wrapper code and synthetic equivalence tests. Classification is conditionally `RUNTIME_DATA_ACCESS_ADAPTATION`, not A2. Real materialization and the four-step local-materialized gate remain NOT RUN and require separate AutoDL authorization. Ba remains NOT RUN.
# Deterministic finite-stream pre-scientific failure — 2026-08-31

`scw_deterministic_full_20260831_214200` terminated during LucieFr pool path discovery: `no authoritative Parquet objects for LucieFr`. Pool progress was 0/95,828; other pools and the final stream were not created. Audit/Gate/Formal A/Ba were not started. The run's automatic shutdown caused the instance power-off. Auto-shutdown is temporarily disabled pending explicit user re-authorization.
# SCW Experiment A2 protocol — 2026-08-31

Experiment A is archived as a pre-formal official-data infrastructure attempt with no scientific result. A2 replaces the three datasets with ModelScope Aya French, `wyj123456/instruct`, and `mapjack/openwebtextSample`, while retaining the canonical model, French/KGW condition, 0.6/0.2/0.2 role probabilities, losses, optimizer, LR, effective batch, sequence length, and 2,500 steps. A2 uses 80,000 unique records in deterministic PCG64(42) order and repeats the identical order once to supply 160,000 exposures. This is an idea reproduction, not an exact SCW reproduction.

## SCW A2 post-mortem — `scw_a2_full_20260831_214331`

Training reached 2500/2500 and `train_end`, and the final Teacher files were saved. Evaluation stopped at Base French generation before producing records because `jpacifico/French-Alpaca-dataset-Instruct-55K` was unavailable with offline mode enabled. Fresh reload, detector, utility, preference judgement, and reporting were not completed. The terminal policy issued `/usr/bin/shutdown`; automatic shutdown is now disabled project-wide pending explicit user re-authorization.

## SCW A2 evaluation cont2 `scw_a2_eval_cont2_20260901_021640`

Training remained immutable and complete. Cont1 failed at Base detector because the runtime tokenizer lacked a pad token. cont2 reused both immutable 1000-record generation files and applied runtime-only EOS-as-PAD with left padding; Base/Teacher p-values `0.9199569225311279` / `0.0`; preferred Teacher `True`. Ba was not started. Auto-shutdown remained disabled.

## SCW A2 final closure — report/summary cont3

<!-- SCW_A2_FINAL_CLOSURE_CONT3_20260901 -->
Strict A remains a pre-formal infrastructure attempt: Formal training never started and no scientific result was established. A2 run `scw_a2_20260831_214339` completed 2500/2500 and produced the immutable Teacher. Cont1 preserved Base/Teacher 1000-record generations but failed at detector padding infrastructure. Cont2 applied runtime-only left EOS-as-PAD and completed evaluation: Base/Teacher primary p-values `0.9199569225311279 / 0.0`, ARC `0.4505119454 / 0.4488054608`, TruthfulQA MC2 `0.5051617516 / 0.5032315125`, ordinary/French sanity PASS/PASS, and preferred Teacher **YES**. The bounded conclusion is successful SCW core method/idea reproduction under the adapted domestic-data, 80k-pool, deterministic two-pass A2 setting—not exact or full-paper reproduction. Ba remains NOT STARTED. Next step: separately archive the final Teacher to ModelScope, verify the archive, then discuss Ba without starting it automatically.

## SCW A2 preferred Teacher ModelScope archive

<!-- SCW_A2_MODELSCOPE_ARCHIVE_20260901 -->
The immutable SCW A2 preferred Teacher was archived to private repo `MakiseKurisuEasonHan/WMKD-SCW-A2-Teacher`. Upload completed with 9 files / 6,442,815,654 bytes and zero retries. Remote filename, size, and metadata identity verification passed for 9/9 files and all bytes. Source archive manifest SHA256: `0e2bd96ef266fc791e182e793507bfc0db7fe994f1d37ce440adaef923b5dbe1`; Teacher manifest SHA256: `27f68ea443ca1dbc9f02036ac560a12db5cb063ceec589a0144be5586da97b7b`. Status: `uploaded_to_modelscope_awaiting_destination_hash_verification` with `destination_verified=false` because a full destination redownload was intentionally not performed. Preferred Teacher remains YES; Ba remains NOT STARTED. Exact next step: design and explicitly authorize SCW Ba; do not start it automatically.
