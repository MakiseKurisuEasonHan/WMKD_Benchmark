# Applicability audit progress (not final classification)

Read-only source inspection during the 2026-09-08 09:05 UTC follow-up. No baseline inference or training was launched.

## PN-FP

Verified remote official source HEAD fdceaba14bd3e89340916a6a40e27c945d48460e at /root/autodl-tmp/WMKD_Benchmark_data/artifacts/pnfp/source.
`check_fingerprints.py::eval_backdoor_acc` receives key and signature strings, tokenizes the signature using the evaluated model tokenizer, sets generation length to the encoded signature length, and compares the full generated token sequence with the encoded signature. This is positive evidence for an original string-signature verification interface; the previously measured 75 key/6 target changes in the WMKD loader alone do NOT establish impossibility.
Next: inspect fingerprint loader/generate_random implementation, freeze exactly the historical Llama-decoded key/one-token signature strings, prove roundtrip identity and investigate special-token cases before classifying adaptation. Never re-truncate those strings with Qwen or regenerate fingerprints. Do not run the old naive Qwen wrapper.

## EverTracer

Verified official source HEAD 70b402f7b7456c6d94e1fae2de554d77dd6cd921 at /root/autodl-tmp/WMKD_Benchmark_data/sources/EverTracer.
`Fingerprinting/attack/attack_model.py`, lines 28–60: one tokenizer stored in AttackModel; llm_eval tokenizes texts once and passes identical token IDs/labels to suspect and reference. Existing WMKD scripts/evertracer_verify.py likewise shares the Llama tokenizer. This confirms the shared-tokenizer assumption occurs in official code, not merely WMKD plumbing. Separate per-model tokenization must not be declared equivalent without checking the original probability/calibration definition and archived paper. Next inspect remaining official verification documentation; do not silently normalize by bytes/tokens or recalibrate.

## iSeal / CTCC / SCW

Earlier inspected project interfaces: iSeal KeyedCipher uses square hidden-dimension linear maps and inputs_embeds; CTCC uses exact stripped IAMALIVE text; SCW detection separately tokenizes generated completion text with the frozen detector tokenizer. Final classification still requires recording source/config identity and applicable interface conditions. No new numerical baseline exists yet.

## Runtime

Local and remote HEAD afe54611b1243c761908a9c374905b7209ead99d. Observed GPU 0% / 0 MiB at start of this check. Existing pipeline state remains APPLICABILITY_AUDIT, shutdown unarmed. Official sources are already present; no download required for these source inspections.
