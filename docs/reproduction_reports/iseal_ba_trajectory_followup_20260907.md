# iSeal Ba checkpoint trajectory follow-up

Run `iseal_ba_trajectory_followup_20260907_historical_parent`. Scientific evidence complete; final resumable model retained. Archive necessity/preferred assessment deferred until campaign completion.

Fresh canonical Llama-3.2-3B-Instruct revision0cb88a4f764b7a12671c53f0838cd831a0843b95; historical fullFT/BF16, seed42, micro8/accum1, LR1e-5, 3 epochs/7500 steps and formatter unchanged. Exact historical 20k: physical SHA `04b02863bbec70b731bbb79471e5be9364ddd89d3b9b51fe5c5c3bb441ec40cc`; canonical records SHA `d51c22b9d33d4aa79b5cd733dd6bcb910ecd6378f1ffe2a40328e64cb085aacf`. Registered200/heldout100 plaintext SHA/order matched historical manifest and Ba raw outputs before launch; original cipher key SHA verified without exposing key. Detector unchanged historical iseal_a2_evaluate.py, sentence BLEU>=50, frozen cipher/TextDataset128/tokenization.

|Step|Registered success/200|Mean BLEU|Median BLEU|Held-out success/100|
|---:|---:|---:|---:|---:|
|0|0|2.332514052|2.009208475|0|
|25|0|2.355855655|2.069724461|0|
|50|0|2.354638161|2.037040717|0|
|100|0|2.309472507|1.985096617|0|
|250|0|2.455192772|2.174992208|0|
|500|0|2.601365666|2.312136739|0|
|1000|0|2.600376241|2.266926952|0|
|2000|0|2.595569635|2.251497739|0|
|4000|0|2.589712909|2.273074489|0|
|6000|0|2.581606320|2.289404237|0|
|7500|0|2.589417504|2.260249086|0|

Measured facts: all 11 points have zero registered/heldout threshold positives and no detector errors/nonfinite values. Step0 is actual fresh Base. Final fresh-reload groups and metrics equal step7500 exactly. Historical Teacher reference179/200, mean69.171651; historical Ba reference0/200, mean2.589326. The new trajectory final mean2.589418 is close but not claimed byte-identical replay.

Independent integrity PASS: JSON/CSV/SHA, score aggregation and median/threshold recomputation, 300-row hash/order stability, 60000 sampler fetches with each20k row once per epoch, optimizer/scheduler/RNG continuity evidence, final reload and generation sanity. Original paired-Base and ten ordinary prompts in historical detector script were retained; no ARC/TruthfulQA utility run.

Bounded interpretation: never acquired under frozen BLEU50 criterion. Small low-BLEU fluctuations/plateau are not meaningful ownership acquisition; no strong acquisition then forgetting observed. Exposure audit's zero exact whole-field registered-plaintext hash matches does not rule out partial/semantic exposure. Unsupported causal claims: absolute absence of all watermark information, proof that indirect transfer is impossible, or attributing results causally to one training parameter.

All raw scores, trajectory tables, logs, provenance/manifests and worker closure snapshots are permanent. CPU historical regression is historical output replay, not a newly measured checkpoint. Secret remains outside Git.
