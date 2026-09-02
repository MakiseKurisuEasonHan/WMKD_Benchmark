# LLMPrint Experiment Ba report

**Ownership detectability remained positive after the tested direct-distillation attack.**

- Shared Student run: `passive5_shared_ba_20260902_114500_cont1`
- Evaluation continuation: `passive5_shared_ba_eval_cont2_20260902_164200`
- Dataset SHA256: `eb90c3e0c95e37d07bf0f099aaeabeedf1779bae7ef8a4aacf25e3fb8bed6ab7`
- Reference score: 1.000000000000
- Frozen threshold: 0.715004977613
- Student primary paper-style bit accuracy: 0.820000000000
- Student detected: yes
- Calibration reused: yes; recalibration: no
- Shared utility: ARC-Challenge acc_norm=0.497440273038; TruthfulQA MC2=0.475541305678

This conclusion is bounded to the frozen WMKD A/A2 detector and tested direct-distillation Student.

## Final wording and integrity audit

<!-- PASSIVE5_BA_FINAL_WORDING_AUDIT_20260902 -->

- Frozen A/A2 Reference score: 1.0; threshold: 0.7150049776126003.
- Shared Student: `passive5_shared_ba_20260902_114500_cont1`; dataset SHA256: `eb90c3e0c95e37d07bf0f099aaeabeedf1779bae7ef8a4aacf25e3fb8bed6ab7`.
- Student native score: 0.82; detected: yes; ownership detectability retained: **YES**.
- Shared utility pointer: `results/passive5_shared_ba/utility_results.json`.
- Limitation: the Shared Student uses the same canonical pretrained backbone/initialization family as the Reference. This result is bounded to the tested same-backbone direct-distillation setting and does not establish fingerprint transfer or general immunity to knowledge distillation.
