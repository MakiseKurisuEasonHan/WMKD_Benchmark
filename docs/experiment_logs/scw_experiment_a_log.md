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
