# LLMPrint Experiment A2 formal closure report

## Outcome

**LLMPrint core reproduction successful under WMKD A2 reduced-construction setting.**

- Fingerprint package: 200/200 immutable artifacts; 0 missing, duplicate, or invalid.
- Reference: fresh reload of `meta-llama/Llama-3.2-3B-Instruct@0cb88a4f764b7a12671c53f0838cd831a0843b95`.
- Validation negatives: 13/13 frozen identities and pinned ModelScope revisions, evaluated serially.
- Primary paper detector: reference score `1.000000`, mu `0.640000`, sample sigma `0.045735`, tau `0.715005`, false positives `0`.
- Supplementary release detector: reference valid_n `195`, p-value `1.9913649e-59`, calibrated min_n `118`, positive `True`.
- Preferred artifact type: fingerprint package. Model weights were not modified and no Teacher checkpoint was created.
- Ba: NOT STARTED.

## Gate verdicts

- fingerprint_integrity: PASS
- reference_fresh_reload: PASS
- negative_panel_13_of_13: PASS
- primary_calibrated: PASS
- reference_primary_positive: PASS
- usable_separation: PASS
- no_severe_false_positive_anomaly: PASS
- supplementary_release_recorded: PASS
- zero_unresolved_evaluation_errors: PASS

## Final closure audit

<!-- PASSIVE5_FINAL_CLOSURE_AUDIT_20260902 -->

- Project/method/experiment: WMKD_Benchmark / LLMPrint / A2
- Final preferred run: `llmprint_a2_closure_20260902_cont2_resume6`; preferred artifact: **yes** (`fingerprint_package`)
- Implementation provenance: official repository/commit and transport provenance remain recorded in the canonical provenance manifest.
- Canonical model: `meta-llama/Llama-3.2-3B-Instruct` at `0cb88a4f764b7a12671c53f0838cd831a0843b95`; model modified: false.
- Scientific/runtime configuration: 200 immutable fingerprints; 500/500 GCG steps; 20-token suffix; inclusive >= primary bits; sample std ddof=1; tau=mu+1.64*sigma without clipping Runtime closure used existing artifacts only and did not rerun science.
- Final result: Reference=1.0; frozen threshold=0.7150049776126003; false positives=0/13; status=SUCCESSFUL.
- Negative/control results: preserved verbatim in `detector_results.json` and the canonical full log.
- Environment/resources and artifact paths/SHA256: preserved in the full log, artifact manifest, and provenance manifest.
- Limitation: Reduced-construction A2 (200 fingerprints, 500 GCG steps), not the abandoned 300x1000 construction.
- Bounded conclusion: LLMPrint core reproduction successful under the frozen WMKD protocol.
