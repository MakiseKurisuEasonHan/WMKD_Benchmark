# Passive Cross-Lineage Ba

Scientific measurements complete; Git closure pending. Bb not started.

Fresh Qwen2.5-3B-Instruct, ModelScope revision8f4992eda43eea7c770690ddc0de8f732da246f5. Frozen Ba20k, fullFT BF16 seed42 batch8 accum1 LR1e-5 3epochs7500updates. No Ba optimizer or state is eligible as Bb initialization.

| Detector | Clean Qwen | Ba | Delta | Threshold | Ba decision |
|---|---:|---:|---:|---:|---|
|LLMPrint|0.68|0.68|0.0|0.7150049776126003|False|
|REEF|0.4546738923165847|0.4712346890040632|0.016560796687478452|0.4546738923165847|True|
|HuRef|-8.356179237365723|-8.41477108001709|-0.05859184265136719|4.119894027709961|False|
|AWM|0.0017953364917795106|0.0018811310743071122|8.579458252760161e-05|0.0017953364917795106|True|
|ZeroPrint|0.6793505996465683|0.70185287296772|0.022502273321151733|0.6793505996465683|True|

| Utility | Clean Qwen | Ba | Delta |
|---|---:|---:|---:|
|arc_challenge_acc_norm|0.4402730375426621|0.514505119453925|0.07423208191126285|
|truthfulqa_mc2_acc|0.5712170418936038|0.4913761025929856|-0.0798409393006182|

Qwen participated in historical threshold calibration, so clean Qwen is not an independent held-out negative. Threshold crossings are measured decision changes, not proof of transferring three watermarks. Utility changes are mixed; TruthfulQA drop must be disclosed. Ba/Bb will be independently fresh initialized. No universal causal claim.

Raw samples, arrays, logs, manifests retained under results/passive_cross_lineage/. ModelScope not started.
