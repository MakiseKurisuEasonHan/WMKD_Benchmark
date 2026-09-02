# ZeroPrint Experiment A2 report

**ZeroPrint core reproduction successful under the WMKD A2 frozen three-negative canonical protocol.** Preferred fingerprint: **yes**.

The Phi-only continuation repaired a Transformers cache API compatibility failure by mapping process-local `DynamicCache.seen_tokens` to the semantically equivalent `get_seq_length()`. It did not change the model, generation protocol, frozen panel, perturbations, Jacobian, or detector.

- Reference/self: 1.0
- Reference/reload: 1.0 (raw 1.0)
- google/gemma-2b: 0.6581349819898605 (raw 0.31626996397972107)
- Qwen/Qwen2.5-3B-Instruct: 0.6793505996465683 (raw 0.3587011992931366)
- microsoft/Phi-3-mini-128k-instruct: 0.5839913785457611 (raw 0.16798275709152222)
- Tau: 0.6793505996465683; margin: 0.3206494003534317; FP: 0/3; errors: 0

Bounded to the WMKD A2 frozen three-negative canonical protocol; not a full-paper negative-panel reproduction. model_modified=false; utility=N/A; Ba=NOT_STARTED.

## Final closure audit

<!-- PASSIVE5_FINAL_CLOSURE_AUDIT_20260902 -->

- Project/method/experiment: WMKD_Benchmark / ZeroPrint / A2
- Final preferred run: `zeroprint_a2_phi_cont4_20260902_104000`; preferred artifact: **yes** (`fingerprint_package`)
- Implementation provenance: official repository/commit and transport provenance remain recorded in the canonical provenance manifest.
- Canonical model: `meta-llama/Llama-3.2-3B-Instruct` at `0cb88a4f764b7a12671c53f0838cd831a0843b95`; model modified: false.
- Scientific/runtime configuration: two HumanEval originals plus eight frozen perturbations; 20 repeats/input; MPNet; ridge Jacobian alpha=0.001; rescaled Pearson; frozen three-negative panel Runtime closure used existing artifacts only and did not rerun science.
- Final result: Reference=1.0; frozen threshold=0.6793505996465683; false positives=0/3; status=SUCCESSFUL.
- Negative/control results: preserved verbatim in `detector_results.json` and the canonical full log.
- Environment/resources and artifact paths/SHA256: preserved in the full log, artifact manifest, and provenance manifest.
- Limitation: Bounded to the frozen three-negative A2 panel; Phi DynamicCache repair is runtime compatibility only, not scientific adaptation.
- Bounded conclusion: ZeroPrint core reproduction successful under the WMKD A2 frozen three-negative canonical protocol
