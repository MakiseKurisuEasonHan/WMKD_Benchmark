# REEF Experiment A reproduction report

## Final result

**REEF core reproduction successful under the frozen WMKD canonical protocol.** Preferred fingerprint: **yes**.

## Protocol-compliance continuation

Old run `reef_a_20260901_200836` is **SUPERSEDED_BY_PROTOCOL_COMPLIANCE_RERUN** because it used `hidden_states[-1]`. Final run `reef_a_protocol_cont1_20260901_202500` directly hooks canonical `model.layers.27` and each negative model's audited final decoder block, extracting raw hook `output[0]` at the last token. Scientific configuration was unchanged.

## Detector

- Reference/self: 1.000000000000
- Reference/reload: 1.000000000000; max absolute representation difference: 0
- google/gemma-2b: 0.304995743635
- Qwen/Qwen2.5-3B-Instruct: 0.454673892317
- microsoft/Phi-3-mini-128k-instruct: 0.317170666270
- Negative mean: 0.358946767407
- Tau: 0.454673892317
- Margin: 0.545326107683
- False positives: 0/3
- Evaluation errors: 0

Model modified: false. Utility: not applicable/inherited canonical Base. Ba: NOT_STARTED.

## Final closure audit

<!-- PASSIVE5_FINAL_CLOSURE_AUDIT_20260902 -->

- Project/method/experiment: WMKD_Benchmark / REEF / A
- Final preferred run: `reef_a_protocol_cont1_20260901_202500`; preferred artifact: **yes** (`fingerprint_package`)
- Implementation provenance: official repository/commit and transport provenance remain recorded in the canonical provenance manifest.
- Canonical model: `meta-llama/Llama-3.2-3B-Instruct` at `0cb88a4f764b7a12671c53f0838cd831a0843b95`; model modified: false.
- Scientific/runtime configuration: model.layers.27 raw forward-hook output[0] at last token over 200 frozen TruthfulQA probes; centered linear CKA Runtime closure used existing artifacts only and did not rerun science.
- Final result: Reference=1.0; frozen threshold=0.4546738923165847; false positives=0/3; status=SUCCESSFUL.
- Negative/control results: preserved verbatim in `detector_results.json` and the canonical full log.
- Environment/resources and artifact paths/SHA256: preserved in the full log, artifact manifest, and provenance manifest.
- Limitation: Bounded to the frozen three-negative WMKD panel; the hidden_states[-1] run remains superseded.
- Bounded conclusion: REEF core reproduction successful under the frozen WMKD canonical protocol
