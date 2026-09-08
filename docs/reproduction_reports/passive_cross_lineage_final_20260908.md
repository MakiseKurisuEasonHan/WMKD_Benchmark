# Passive Cross-Lineage Ba/Bb final scientific comparison

Ba and Bb each completed one fresh Qwen full-parameter training: 20k, 3 epochs, 7500 updates, BF16, LR1e-5, batch8, seed42. Bb uses frozen paraphrased_answer only; never resumed Ba. Qwen revision 8f4992eda43eea7c770690ddc0de8f732da246f5. Ba Git closed in 8a0871c8; Bb scientific Git closure: 341884d3c874b3949699c13f2f1dd02f832d60cb. Both final Students are preferred retained artifacts by explicit user scientific decision; both PRIVATE ModelScope archives independently verified. This classification does not claim causal watermark transfer.

## Measured detectors

|Method|Clean Qwen|Ba|Bb|Bb minus Ba|Threshold|Ba/Bb positive|
|---|---:|---:|---:|---:|---:|---|
|LLMPrint|0.68|0.68|0.695|0.015|0.715004977613|False/False|
|REEF|0.454673892317|0.471234689004|0.473476517243|0.00224182823856|0.454673892317|True/True|
|HuRef|-8.35617923737|-8.41477108002|-8.333360672|0.08141040802|4.11989402771|False/False|
|AWM|0.00179533649178|0.00188113107431|0.00185297363156|-2.8157442752e-05|0.00179533649178|True/True|
|ZeroPrint|0.679350599647|0.701852872968|0.701529145241|-0.000323727726936|0.679350599647|True/True|

## Utility

|Metric|Clean|Ba|Bb|Ba-clean|Bb-clean|Bb-Ba|
|---|---:|---:|---:|---:|---:|---:|
|arc_challenge_acc_norm|0.440273037543|0.514505119454|0.494880546075|0.0742320819113|0.0546075085324|-0.0196245733788|
|truthfulqa_mc2_acc|0.571217041894|0.491376102593|0.512156746325|-0.0798409393006|-0.0590602955689|0.0207806437317|

## Bounded scientific answers

1. No frozen detector was positive on clean Qwen; threshold ties are negative for REEF/AWM/ZeroPrint.
2. REEF, AWM and ZeroPrint first crossed their historical thresholds after Ba and remain positive after Bb.
3. LLMPrint and HuRef remain negative after both.
4. Bb raises LLMPrint/REEF/HuRef scores relative to Ba; lowers AWM/ZeroPrint slightly. No universal paraphrasing attenuation. No repeated-seed uncertainty estimate supports calling small changes significant.
5. Historical same-lineage Ba/Bb3 scores are higher within every detector family and all five decisions positive. This is descriptive, not a statistical significance claim.
6. Near-reference same-lineage parameter fingerprints versus low cross-lineage scores are consistent with initialization/lineage confounding; architecture and tokenizer also change, so lineage is not isolated causally.
7. Output/representation changes remain compatible with behavioral effects of SFT, but generic adaptation and training-data effects are not excluded.
8. Qwen participated in historical threshold calibration. Clean Qwen is not an independent held-out negative, limiting generalization of threshold-crossing conclusions.
9. ARC improves versus clean while MC2 declines for both Students. These two benchmarks do not support global collapse, but utility is not unchanged and MC2 degradation is material. No broad no-collapse claim.
10. Some frozen fingerprint scores cross thresholds after cross-lineage SFT. This is limited operational evidence, not proof of causal watermark transfer or success of three watermark methods.

## Evidence and limits

Raw detector arrays/generations and utility samples permanently retained under results/passive_cross_lineage/bb and in evidence archive. ARC 1172 and MC2 817 raw samples verified. LLMPrint 200 pair order verified; ZeroPrint 200 unique input/repeat pairs and frozen seed/prompt order verified. Final weight SHA matches checkpoint7500. Same-lineage references come from results/passive5_shared_ba/detector_summary.json and results/passive5_shared_bb3/detector_summary.json with SHA in master JSON. Clean Llama was not separately reevaluated in this campaign; its column is explicitly unmeasured rather than copied from Teacher.

Active Bb/Bb2 trajectories remain paused. No retraining, new watermark, cleanup or shutdown performed.

## Verified final archives

- ba: MakiseKurisuEasonHan/Qwen2.5-3B-WMKD-Passive5-Cross-Lineage-Ba-Student; immutable revision da51d39a060ec3ef15f1aa9b84ffc43288202050; 16 files, 6187855464 bytes; ARCHIVE_SHA256=cb622ff18928b69a4e811ec01bd0f7688afd1a929b668b166dc1b08dd93377ab. Fresh independent download: all sizes and SHA match.
- bb: MakiseKurisuEasonHan/Qwen2.5-3B-WMKD-Passive5-Cross-Lineage-Bb-Student; immutable revision 5f8d9c36f1e127ea265368ebcd9aa567815f62da; 16 files, 6187855466 bytes; ARCHIVE_SHA256=77405117245d1654c84aff637b52be3f2449fa744095104223d945dfbafd35fb. Fresh independent download: all sizes and SHA match.

ARCHIVE_SHA256 is the SHA256 of SHA256SUMS, which binds the individual files and provenance manifest. Original AutoDL final models remain retained. Account inventory before upload: 21 repositories and 47 weight files, no duplicate matching final weights. Exact utility deltas remain in comparison/final_utility_comparison.json and each archive manifest. No new experiment, cleanup or shutdown.
