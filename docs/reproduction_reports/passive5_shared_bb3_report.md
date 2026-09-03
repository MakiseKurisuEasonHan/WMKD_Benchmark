# Passive-5 Shared Bb3 final report

## Result

The scientific question is whether Bb3 preprocessing plus SFT reduces any passive ownership fingerprint below its frozen detector threshold in the tested same-backbone standardized behavioral-distillation setting. Bb3 completed with one fresh full-parameter Student; detectability remained positive for **5/5** detectors.

## Protocol lineage and decision

Shared Ba supplies the canonical 20,000 QA source and the exact Student/detector/utility protocol. Original Bb is `BLOCKED_AT_PILOT`: successive pilots exposed recurrent instruction-echo/meta-task outputs for one-token `tech` answers. Bb2 is also `BLOCKED_AT_PILOT`: its revised prompt still produced meta-commentary for both deterministic `tech` samples. Neither establishes a formal attack result.

The CPU-only short-answer audit tokenized all 20,000 answers with the frozen Qwen tokenizer and special tokens disabled. Threshold counts for `<=1/2/3/5` were 4,635/7,577/8,698/9,791; both recurrent failures were one token. `<=1` was selected as the smallest uniform detector-agnostic threshold covering them. Bb3 therefore preserves those answers byte-identically and sends every longer answer through the unchanged Bb2 prompt, Qwen snapshot, decoding, ordering, and seed policy.

## Frozen dataset and Student

- Frozen paired records: 20,000; dataset SHA256: `549d38ca634c2c69a646e23d1bfc65ec019887e43070deec031f97459cc7be99`.
- Pilot: 200/200 PASS; 41 atomic identities; 159 Qwen submissions; 25-pair targeted human audit PASS.
- Full20k: 4,635 atomic identities (**23.175%**); 15,365 Qwen submissions; 13,061 Qwen paraphrases; 2,256 natural Qwen identities; 48 pipeline fallbacks; 279 rejected attempts; runtime 7,484.502s.
- Final unresolved leakage/control-token leakage/truncation: 0/0/0. It is incorrect to claim that all responses were paraphrased.
- Ba/Bb3 intended-shared training parity: 19/19 PASS.
- Fresh canonical `meta-llama/Llama-3.2-3B-Instruct@0cb88a4f764b7a12671c53f0838cd831a0843b95` Student: 7,500/7,500 optimizer steps, 3 epochs, BF16, effective batch 8, LR 1e-5, seed 42, no resume, no LoRA.
- Training loss: 0.962497413953; runtime: 2022.706s.
- Fresh reload: PASS; non-finite parameters: 0; inference response: `WMKD_RELOAD_PASS`.

## Frozen detectors

| Method | Reference | Frozen threshold | Ba | Bb3 | Ba→Bb3 | Detected |
|---|---:|---:|---:|---:|---:|---|
| LLMPrint | 1.000000000000 | 0.715004977613 | 0.820000000000 | 0.785000000000 | -0.035000000000 | yes |
| REEF | 1.000000000000 | 0.454673892317 | 0.954222006631 | 0.967286126925 | +0.013064120294 | yes |
| HuRef | 99.999992370605 | 4.119894027710 | 99.998985290527 | 99.998733520508 | -0.000251770020 | yes |
| AWM | 1.000000000000 | 0.001795336492 | 0.999997413584 | 0.999996106539 | -0.000001307045 | yes |
| ZeroPrint | 1.000000000000 | 0.679350599647 | 0.839937269688 | 0.917022019625 | +0.077084749937 | yes |

## Utility

- Ba Student ARC-Challenge acc_norm: 0.497440273038; Bb3 Student: 0.490614334471.
- Ba Student TruthfulQA MC2: 0.475541305678; Bb3 Student: 0.454416204164.
- Ordinary English and supplementary French generation sanity: PASS for base, teacher, and Student.

## Bounded conclusion

All five ownership fingerprints remained detectable under their already-frozen A/A2 detector protocols after this tested Bb3 UP post-watermark paraphrasing-distillation attack. This does not establish general robustness beyond these models, data, thresholds, and attack semantics. Native detector scores are not watermark-retention percentages.

No claim is made that fingerprints were “transferred.” The result only establishes that Bb3 did not reduce any of the five native scores below its frozen threshold. The 23.175% atomic-identity component is a material limitation and is disclosed explicitly.

## Archival

- Processed20k: private ModelScope dataset `MakiseKurisuEasonHan/WMKD_Benchmark_passive5_shared_bb3_processed20k`; independent redownload and canonical hash validation PASS.
- Final Student: private ModelScope model `MakiseKurisuEasonHan/Llama-3.2-WMKD-Passive5-Shared-Bb3-Student`; 14-file independent redownload, per-file SHA256, secret scan, large-file allowlist, and Llama license/NOTICE checks PASS.
