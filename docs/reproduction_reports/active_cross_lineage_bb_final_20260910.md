# Active Cross-Lineage Bb final scientific comparison

Five independent fresh Qwen2.5-3B-Instruct Students, revision 8f4992eda43eea7c770690ddc0de8f732da246f5. Each completed 7500 steps on frozen method-specific paraphrased 20k. No continuation between Students.

| Method | Detector | ARC clean / XBa / XBb | MC2 clean / XBa / XBb |
|---|---|---|---|
| pnfp | 43/1024 clean; 84/1024 XBa; 67/1024 XBb | 0.4402730375426621 / 0.4948805460750853 / 0.4684300341296928 | 0.5712170418936038 / 0.5019135695511419 / 0.4917632470586235 |
| evertracer | Canonical N/A; exploratory AUC XBa 0.523, XBb 0.5227; TPR 0.07 @ FPR 0.05 | 0.4402730375426621 / 0.5162116040955631 / 0.46075085324232085 | 0.5712170418936038 / 0.4509746503062132 / 0.46907694275763584 |
| ctcc | XBa 0/95; XBb 0/95 trigger, 0/205 negatives | 0.4402730375426621 / 0.4684300341296928 / 0.439419795221843 | 0.5712170418936038 / 0.4480919802572382 / 0.45344106594056727 |
| iseal | Level 3 canonical N/A for XBa/XBb | 0.4402730375426621 / 0.4948805460750853 / 0.49402730375426623 | 0.5712170418936038 / 0.4298307502074534 / 0.46736380064984684 |
| scw | p clean 0.7446491718292236; XBa 0.9158855080604553; XBb 0.9841499328613281; alpha 0.001, not detected | 0.4402730375426621 / 0.4906143344709898 / 0.4974402730375427 | 0.5712170418936038 / 0.4915920843760251 / 0.48478352312750794 |

## Interpretation boundaries

PN-FP shows partial endpoint acquisition above clean Qwen and below XBa; one run does not establish causation. CTCC has no observed trigger activation. SCW is not detected. EverTracer exploratory values are NOT DIRECTLY COMPARABLE to frozen Llama detector and cannot establish survival/failure/transfer. iSeal N/A is not an experimental failure. Endpoint measurements cannot establish a forgetting trajectory. Exact registered overlap does not exclude indirect exposure. PN-FP reconstructed-parent limitations remain.

Exact utility deltas and raw-source SHA provenance are in results/active_cross_lineage_bb/master_comparison.json. Every method has one verified preferred PRIVATE model archive; preferred retention means reproducibility value, not utility superiority or successful watermark transfer.

## Archive receipts

- pnfp: MakiseKurisuEasonHan/Qwen2.5-3B-WMKD-Active-PNFP-Cross-Lineage-Bb-Student; revision e1d1d250b12130c10f305e67f3539a227629ce80; SHA f81f6d6d477dfb6a5aa95be9080e813a21acb829fa08b31d3c128647d1a47240; MANIFEST_PLUS_SEGMENT PASS.
- evertracer: MakiseKurisuEasonHan/Qwen2.5-3B-WMKD-Active-EverTracer-Cross-Lineage-Bb-Student; revision eb1d3b656577259d59445e5e1362e1697ff3655a; SHA de3b8805d1ac286f0d9edd18af150659adbb7877d90b22ecd9422caf74073979; MANIFEST_PLUS_SEGMENT PASS.
- ctcc: MakiseKurisuEasonHan/Qwen2.5-3B-WMKD-Active-CTCC-Cross-Lineage-Bb2-Student; revision a2535f62042ed67e13918ba0c99fef0996f41041; SHA 66c664b14775149656d816d60f221b7a5a44f78dffc8fe33fa14ead88e1aabbd; MANIFEST_PLUS_SEGMENT PASS.
- iseal: MakiseKurisuEasonHan/Qwen2.5-3B-WMKD-Active-iSeal-Cross-Lineage-Bb-Student; revision fa4baa48e2a8754ad317552c8cbc8ace73cee971; SHA 882fa722eee80a941a56d994f8a911a016b810b98a70c5a8eb99238bd69e4e92; MANIFEST_PLUS_SEGMENT PASS.
- scw: MakiseKurisuEasonHan/Qwen2.5-3B-WMKD-Active-SCW-Cross-Lineage-Bb-Student; revision dc6da8daec0104ac24bc4b004cde5bd32a06d178; SHA cd7c9c3b7d6510b12a4b117eddff8709a0479ce729d24a28fe3e4ced4d3a25ff; MANIFEST_PLUS_SEGMENT PASS.
