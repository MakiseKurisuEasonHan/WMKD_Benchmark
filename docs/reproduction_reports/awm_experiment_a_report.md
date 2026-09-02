# AWM Experiment A report

**AWM core reproduction successful under frozen WMKD canonical protocol.** Preferred fingerprint: **yes**.

Cont1 `awm_a_cont1_20260902_052000_cont3` supersedes `awm_a_20260901_200911` after exact Phi fused-QKV and official layer-LAP repairs. Scientific configuration is unchanged.

- Unit tests: AWM_PROTOCOL_UNIT_TESTS=PASS
- Reference/self: 1.0
- Reference/reload: 1.0
- google/gemma-2b: 0.0016877207373100747
- Qwen/Qwen2.5-3B-Instruct: 0.0017953364917795106
- microsoft/Phi-3-mini-128k-instruct: 0.0017162630297856854
- Negative mean: 0.0017331067529584236
- Tau: 0.0017953364917795106
- Margin: 0.9982046635082205
- FP: 0/3; errors: 0

model_modified=false; utility=N/A; Ba=NOT_STARTED.

## Final closure audit

<!-- PASSIVE5_FINAL_CLOSURE_AUDIT_20260902 -->

- Project/method/experiment: WMKD_Benchmark / AWM / A
- Final preferred run: `awm_a_cont1_20260902_052000_cont3`; preferred artifact: **yes** (`fingerprint_package`)
- Implementation provenance: official repository/commit and transport provenance remain recorded in the canonical provenance manifest.
- Canonical model: `meta-llama/Llama-3.2-3B-Instruct` at `0cb88a4f764b7a12671c53f0838cd831a0843b95`; model modified: false.
- Scientific/runtime configuration: token-string vocabulary overlap; absolute-cosine dimension LAP; sign correction; official layer LAP; Wq.T/Wk.T unbiased linear CKA; official aggregation Runtime closure used existing artifacts only and did not rerun science.
- Final result: Reference=1.0; frozen threshold=0.0017953364917795106; false positives=0/3; status=SUCCESSFUL.
- Negative/control results: preserved verbatim in `detector_results.json` and the canonical full log.
- Environment/resources and artifact paths/SHA256: preserved in the full log, artifact manifest, and provenance manifest.
- Limitation: Bounded to the frozen three-negative WMKD panel; the pre-compliance implementation run remains superseded.
- Bounded conclusion: AWM core reproduction successful under frozen WMKD canonical protocol
