# SCW Ba checkpoint trajectory follow-up

Run `scw_ba_trajectory_followup_20260907_reconstructed_parent`.

Scientific evidence validation PASS: all 11 points, frozen 1000-query order and permutation, alpha=0.001, raw statistical aggregation, JSON/CSV/SHA, final fresh-reload payload equality, and 60000 logical sample fetches (each 20k row once per epoch). Lower p-value means stronger evidence; all sampled points are negative. No strong acquisition or subsequent forgetting was observed at sampled points. This does not establish absence of all watermark information or an exposure/optimization causal mechanism.

| Step | p-value | Detected | Nearest logged loss |
|---:|---:|---|---:|
| 0 | 0.581310153008 | False | None |
| 25 | 0.830340087414 | False | 1.5583 |
| 50 | 0.604613542557 | False | 1.3581 |
| 100 | 0.852329730988 | False | 0.5416 |
| 250 | 0.824498534203 | False | 0.4974 |
| 500 | 0.876429796219 | False | 0.4385 |
| 1000 | 0.677678346634 | False | 0.5142 |
| 2000 | 0.502466738224 | False | 0.3964 |
| 4000 | 0.949506402016 | False | 0.2882 |
| 6000 | 0.683055877686 | False | 0.2794 |
| 7500 | 0.895175039768 | False | 0.2649 |

Step0 is newly measured fresh canonical Llama-3.2-3B-Instruct, not Teacher. Reconstructed parent SHA ad579f137a08654c011053ed803450d4c545454ba7b74396225a5d6f535517ed: protocol-faithful reconstruction, NOT historical exact replay. Historical Ba p=0.8440861701965332 is reference only. Frozen fullFT/BF16, seed42, batch8/accum1, 3epochs/7500updates, LR1e-5, AdamW/cosine/warmup0.03; detector semantics unchanged.

Continuity is verified checkpoint continuation, NOT one uninterrupted process. Original parent exited during step50 detector (cause UNKNOWN); original 1000 generations retained and reused. cont1 stopped before updates because logging_dir differed; cont2 exited before updates, cause UNKNOWN, OOM not established. cont3 restored checkpoint50 and trained to500, then frozen statistical detector had a recorded CUDA OOM after all1000 generations completed. User explicitly approved recovery. cont4 restored checkpoint500 weights/optimizer/scheduler/RNG with actual first-update gate PASS; first update501, no0-to500 retraining. Step500 generations were reused unchanged; original frozen statistical detector reran successfully. Before later isolated detectors, unused CUDA allocator cache was released without changing model/optimizer or detector mathematics. The logical sample journal is original[:400]+cont3[:3600]+cont4; original408 and cont33608 journals include audited8-record unconsumed lookahead and remain preserved. Step50/500 parent RNG equality is null, not fabricated. Original failure/review/repair evidence remains permanent.

Final model and resumable state are retained locally. No model upload or cleanup performed as part of this closure. Utility NOT_RUN (outside this trajectory protocol). Global index and Git closure remain pending; active Bb/Bb2 are PAUSED_BY_USER under the latest cross-lineage priority and no automatic shutdown is allowed.
