# EverTracer Ba checkpoint trajectory follow-up

Run: `evertracer_ba_trajectory_followup_20260907_historical_parent`. Scientific evidence complete; final Student retained locally. Model archive eligibility/necessity will be assessed only after the overnight campaign. No utility was run (not part of the frozen follow-up protocol).

Exact historical frozen 20k reused; JSONL SHA `a60da148b77f1f5992cef97797be7a5548be72865686dffbbc6478cd8ca477ca`; canonical-record SHA `ca1aa9c991ae58e1d5bbf32275f1738786db15c337bc4bb80fdc0813aa447142`. These identify different byte serializations, not a mismatch. Fresh canonical 3B Base revision `0cb88a4f764b7a12671c53f0838cd831a0843b95`, BF16 full FT, seed42, micro8/accum1, 3 epochs, LR1e-5, 7500 updates; historical formatter and detector unchanged.

|Step|Member-oriented AUC|TPR at empirical FPR≤0.05|FPR|Errors|
|---:|---:|---:|---:|---:|
|0|0.4417|0.05|0.05|0|
|25|0.4401|0.07|0.05|0|
|50|0.4385|0.07|0.05|0|
|100|0.4457|0.07|0.05|0|
|250|0.443|0.06|0.05|0|
|500|0.4618|0.08|0.05|0|
|1000|0.4768|0.07|0.05|0|
|2000|0.5027|0.09|0.05|0|
|4000|0.4999|0.06|0.05|0|
|6000|0.5009|0.05|0.05|0|
|7500|0.5016|0.05|0.05|0|

Measured fact: final AUC=0.5016, TPR=0.05; historical Ba reference AUC=0.4987, TPR=0.06. Teacher reference AUC=1, TPR=1. Step0 was measured afresh (AUC=0.4417), not copied. No detector errors/nonfinite values across all 11 points. Final independent fresh-reload score payload equals the step7500 payload exactly. CPU validation independently recomputed all frozen aggregation outputs and verified JSON/CSV/SHA, 60000 sample fetches and each 20k row once per epoch, preserved RNG and optimizer/scheduler identity.

Bounded interpretation: non-monotonic/noisy, with an increase towards chance-level AUC then near-chance plateau. No measured strong acquisition followed by forgetting; TPR variations 0.05–0.09 alone do not establish meaningful watermark transfer. No frozen model-level binary ownership threshold exists in this protocol; no new decision threshold was invented. Per-point numeric thresholds are outputs of the unchanged empirical-FPR ROC rule. Raw legacy verifier metrics use the older direction; reported metrics use the frozen corrected member orientation.

Exposure linkage: prior cross-method exposure audit observed zero exact whole-field matches to the 200 frozen verification originals. This limited test does not rule out partial-token, semantic or distributional exposure. Unsupported causal claims: absolute absence of all watermark information, proof of indirect transfer, or identifying exposure/optimization as a causal mechanism from this trajectory alone.

Evidence: `results/evertracer/experiment_ba_trajectory_followup/` permanently retains raw scores, per-point metadata/manifests, trajectory tables, actual sample order, logs and final reload. Original worker closure files are preserved in `worker_closure_snapshot/`. Training wall through closure ~3497s; callback-measured training compute 1616.60s (excludes detector/I/O). Full final resumable checkpoint retained at the recorded training_summary path.
