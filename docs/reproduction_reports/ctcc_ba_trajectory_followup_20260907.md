# CTCC Ba checkpoint trajectory follow-up

Run `ctcc_ba_trajectory_followup_20260907_historical_parent`. Scientific evidence complete; final resumable model retained locally; archive assessment deferred until campaign completion.

Measured fact: all 11 points (0/25/50/100/250/500/1000/2000/4000/6000/7500) have trigger activation 0/95, suppression 0/100, normal 0/105, combined negative 0/205, generation errors 0. Step0 was freshly measured. Final fresh-process reload matches step7500 raw generations and metrics exactly. Historical Teacher reference 95/95; historical Ba and Base reference 0/95.

Exact historical 20k reused: raw JSONL SHA `4cc5943dbce69d5b0574b8534895afd4f8b158a473c5110c70fd1c22c991f4c6`; canonical records SHA `621c9aedcf3a4a1db86a4848bbf93fa893d18022f15b913e8aeeb28739412484`. These serializations differ by definition, not evidence corruption. Frozen 300 annotations SHA `48596b707de9d73cef625e7ec1e58afe6a7f176b6aeb59f393455818fdcb0f15`.

Fresh canonical Llama-3.2-3B-Instruct revision0cb88a4f764b7a12671c53f0838cd831a0843b95, BF16 fullFT, seed42, micro8/accum1, LR1e-5, 3 epochs/7500 updates; historical formatter and detector unchanged. Independent CPU validation: all JSON/CSV/SHA, 60000 ordered fetches (each20k row once per epoch), optimizer/scheduler/RNG continuity evidence, per-point raw equality recomputation, final reload and nonempty generation sanity PASS. Utility NOT_RUN (not in the follow-up protocol).

Bounded interpretation: never acquired under this frozen operational detector; no measured early acquisition or forgetting. Limitation: WMKD case-sensitive generated_answer.strip()==IAMALIVE is not the official CTCC detector; zeros do not prove absence of all latent watermark information.

Exposure audit found zero exact full-trigger/target-string matches under its recorded checks; this does not establish no partial/semantic exposure or prove a causal mechanism. Unsupported claims: proving all ordinary-output indirect transfer impossible, or assigning causality to training budget from this single trajectory.

Local computer power interruption occurred after server training finished; no training restart/continuation was necessary. Evidence sync resumed from a complete verified archive. One initial deployment command had a pre-execution quoting SyntaxError, corrected without scientific changes and recorded in cpu_detector_regression.json. Original worker closure snapshots and all raw evidence remain permanent.
