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
