# HuRef Experiment A2 report

**HuRef core reproduction successful under the WMKD A2 tokenizer-specific top-K protocol.** Preferred fingerprint: **yes**.

A2 `huref_a2_20260902_044726_cont3` preserves A and cont1 as NOT_JUDGED history. Its sole scientific redesign is independent deterministic tokenizer-specific top-K=4096 lists for the same frozen corpus, matching the pinned official per-model sorted-list semantics. No cont1 feature was reused.

- Common corpus manifest SHA: `6bac33d8fbf3436595337c57f4689a8e7f62032f6309c2f10661aa3057b3f590`
- Protocol unit tests: `PASS`
- Feature dimension: 512
- Reference/self ICS: 99.999992370605
- Reference/reload ICS: 99.999992370605; max abs diff: 0.0
- google/gemma-2b ICS: -28.545040130615
- Qwen/Qwen2.5-3B-Instruct ICS: -8.356179237366
- microsoft/Phi-3-mini-128k-instruct ICS: 4.119894027710
- Negative mean: -10.927108446757
- Threshold (max frozen negative): 4.119894027710
- Separation margin: 95.880098342896
- False positives: 0/3
- Evaluation errors: 0

Bounded conclusion: this result concerns HuRef core reproduction under the WMKD A2 tokenizer-specific top-K protocol only. It does not establish robustness under attacks, transfer to other panels/corpora, or model modification. `model_modified=false`; utility is inherited canonical Base; Ba is NOT_STARTED.

## Final closure audit

<!-- PASSIVE5_FINAL_CLOSURE_AUDIT_20260902 -->

- Project/method/experiment: WMKD_Benchmark / HuRef / A2
- Final preferred run: `huref_a2_20260902_044726_cont3`; preferred artifact: **yes** (`fingerprint_package`)
- Implementation provenance: official repository/commit and transport provenance remain recorded in the canonical provenance manifest.
- Canonical model: `meta-llama/Llama-3.2-3B-Instruct` at `0cb88a4f764b7a12671c53f0838cd831a0843b95`; model modified: false.
- Scientific/runtime configuration: same frozen corpus plus deterministic tokenizer-specific top-K=4096; last two layers; WqWk/WvWo/WuWd; official joint mean pooling; ICS Runtime closure used existing artifacts only and did not rerun science.
- Final result: Reference=99.99999237060547; frozen threshold=4.119894027709961; false positives=0/3; status=SUCCESSFUL.
- Negative/control results: preserved verbatim in `detector_results.json` and the canonical full log.
- Environment/resources and artifact paths/SHA256: preserved in the full log, artifact manifest, and provenance manifest.
- Limitation: A2 changes token selection to tokenizer-specific top-K; A and A-cont1 remain NOT_JUDGED history.
- Bounded conclusion: HuRef core reproduction successful under the WMKD A2 tokenizer-specific top-K protocol
