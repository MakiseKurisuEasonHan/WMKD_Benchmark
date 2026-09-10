# WMKD final paper-readiness summary

The completed benchmark is sufficient to begin paper writing. No required new scientific experiment was identified. This is an evidence audit, not new training, inference, evaluation or causal re-analysis.

10 methods × 8 core condition columns = 80 matrix cells, including references and explicit applicability N/A. This is not 80 independently trained models. Five passive detector views share one Student in each shared condition.

Five same-lineage active Ba trajectories contain 55/55 points; 487 per-point manifest entries passed SHA verification. All 68 indexed formal scientific objects exist, with no dangling path, duplicate logical object or unindexed formal object identified. Archived historical EOL differences and unrelated dirty EaaW worktree versions are preserved.

Six Bc full 7500-step runs, five active XBa and five active XBb formal objects are closed. Existing scientific results remain unchanged.

## Detector master

| method | native_metric | teacher_reference | clean_llama | same_lineage_ba | same_lineage_bb | same_lineage_bc | clean_qwen | cross_lineage_ba | cross_lineage_bb |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PN-FP | detected/1024 | 956 | 1 | 98 | 72 | 110 | 43 | 84 | 67 |
| EverTracer | member-oriented ROC-AUC | 1.0 | 0.4417 | 0.4987 | 0.4757 | 0.59 | N/A_CROSS_TOKENIZER | N/A_CROSS_TOKENIZER | N/A_CROSS_TOKENIZER |
| CTCC | trigger activations/95 | 95 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| iSeal | registered success/200 | 179 | 0 | 0 | 0 | 0 | N/A_CROSS_ARCHITECTURE | N/A_CROSS_ARCHITECTURE | N/A_CROSS_ARCHITECTURE |
| SCW | p-value | 0.0 | 0.9199569225311279 | 0.8440861701965332 | 0.9529914855957031 | 0.8819239735603333 | 0.7446491718292236 | 0.9158855080604553 | 0.9841499328613281 |
| LLMPrint | primary paper-style bit accuracy | 1.0 | 1.0 | 0.82 | 0.785 | 0.86 | 0.68 | 0.68 | 0.695 |
| REEF | centered linear CKA | 1.0 | 1.0 | 0.9542220066305829 | 0.9672861269249347 | 0.9859362800187441 | 0.4546738923165847 | 0.4712346890040632 | 0.47347651724262 |
| HuRef | ICS | 99.99999237060547 | 99.99999237060547 | 99.99898529052734 | 99.99873352050781 | 99.99800872802734 | -8.356179237365723 | -8.41477108001709 | -8.33336067199707 |
| AWM | official mean Wq/Wk unbiased linear CKA | 1.0 | 1.0 | 0.9999974135841643 | 0.9999961065394538 | 0.9999972975679806 | 0.0017953364917795106 | 0.0018811310743071122 | 0.0018529736315550899 |
| ZeroPrint | rescaled Pearson correlation | 1.0 | 1.0 | 0.8399372696876526 | 0.9170220196247101 | 0.927045077085495 | 0.6793505996465683 | 0.70185287296772 | 0.7015291452407837 |

EverTracer Qwen canonical values remain N/A. Exploratory XBa AUC=0.523, XBb AUC=0.5227, not directly comparable to frozen Llama detector metrics. iSeal Qwen is N/A, never zero.

PN-FP historical Ba=98/1024; reconstructed-parent Ba trajectory=99/1024; Bc=110/1024. The appropriate Bc hard-label comparator is 99/1024. No seed-general causal improvement claim is made.

SCW trajectory step4000=0.949506402015686; step6000=0.6830558776855469; step7500=0.895175039768219. Lower p is stronger; alpha=0.001.

## Utility master

| method_or_shared_run | condition | arc_challenge_acc_norm | truthfulqa_mc2 | precision |
| --- | --- | --- | --- | --- |
| PN-FP | Bb | 0.4906143344709898 | 0.48613790979493243 | FULL_RECORDED_PRECISION |
| PN-FP | Ba historical | 0.478668942 | 0.463479842 | LIMITED_PRECISION |
| PN-FP | Bc | 0.4786689419795222 | 0.46854952594042604 | FULL_RECORDED_PRECISION |
| PN-FP | XBa | 0.4948805460750853 | 0.5019135695511419 | FULL_RECORDED_PRECISION |
| PN-FP | XBb | 0.4684300341296928 | 0.4917632470586235 | FULL_RECORDED_PRECISION |
| EverTracer | Bb | 0.49829351535836175 | 0.47559656098277925 | FULL_RECORDED_PRECISION |
| EverTracer | Ba | 0.5051194539249146 | 0.493714619952569 | FULL_RECORDED_PRECISION |
| EverTracer | Clean Llama (EverTracer historical protocol) | 0.4462457337883959 | 0.5056865097575013 | FULL_RECORDED_PRECISION |
| EverTracer | Teacher | 0.42150170648464164 | 0.5147979684440541 | FULL_RECORDED_PRECISION |
| EverTracer | Bc | 0.4974402730375427 | 0.5007002980392387 | FULL_RECORDED_PRECISION |
| EverTracer | XBa | 0.5162116040955631 | 0.4509746503062132 | FULL_RECORDED_PRECISION |
| EverTracer | XBb | 0.46075085324232085 | 0.46907694275763584 | FULL_RECORDED_PRECISION |
| CTCC | Bb2 | 0.48976109215017066 | 0.44850679576156427 | FULL_RECORDED_PRECISION |
| CTCC | Ba historical | 0.48378839590443684 | 0.4506136480297226 | FULL_RECORDED_PRECISION |
| CTCC | Bc | 0.4641638225255973 | 0.4680824775764402 | FULL_RECORDED_PRECISION |
| CTCC | XBa | 0.4684300341296928 | 0.4480919802572382 | FULL_RECORDED_PRECISION |
| CTCC | XBb2 | 0.439419795221843 | 0.45344106594056727 | FULL_RECORDED_PRECISION |
| iSeal | Bb | 0.48976109215017066 | 0.46152410492343565 | FULL_RECORDED_PRECISION |
| iSeal | Ba historical | 0.4812286689419795 | 0.4498178809933709 | FULL_RECORDED_PRECISION |
| iSeal | Bc | 0.44368600682593856 | 0.456499231887167 | FULL_RECORDED_PRECISION |
| iSeal | XBa | 0.4948805460750853 | 0.4298307502074534 | FULL_RECORDED_PRECISION |
| iSeal | XBb | 0.49402730375426623 | 0.46736380064984684 | FULL_RECORDED_PRECISION |
| SCW | Bb | 0.5042662116040956 | 0.4861866050235854 | FULL_RECORDED_PRECISION |
| SCW | Ba historical | 0.48976109215017066 | 0.4747341900819149 | FULL_RECORDED_PRECISION |
| SCW | Bc | 0.4948805460750853 | 0.49111074033404445 | FULL_RECORDED_PRECISION |
| SCW | XBa | 0.4906143344709898 | 0.4915920843760251 | FULL_RECORDED_PRECISION |
| SCW | XBb | 0.4974402730375427 | 0.48478352312750794 | FULL_RECORDED_PRECISION |
| Passive-5 Shared | Ba | 0.4974402730375427 | 0.4755413056783935 | FULL_RECORDED_PRECISION |
| Passive-5 Shared | Bb3 | 0.4906143344709898 | 0.45441620416416634 | FULL_RECORDED_PRECISION |
| Passive-5 Shared | Bc | 0.5110921501706485 | 0.50010974239234 | FULL_RECORDED_PRECISION |
| Clean Llama | Shared Bb3 baseline context | 0.44880546075085326 | 0.505450760153828 | FULL_RECORDED_PRECISION |
| Clean Qwen | Clean Qwen | 0.4402730375426621 | 0.5712170418936038 | FULL_RECORDED_PRECISION |
| Passive-5 Shared | XBa | 0.514505119453925 | 0.4913761025929856 | FULL_RECORDED_PRECISION |
| Passive-5 Shared | XBb | 0.4948805460750853 | 0.5121567463246797 | FULL_RECORDED_PRECISION |

All full-precision values and per-cell artifact SHA/JSON pointers are retained in the machine-readable JSON. Historical baseline contexts and limited-precision records must not be silently pooled. Passive utility is listed once per shared Student.

## Archive and synchronization limits

35 preferred model archives have existing receipts. Modern 18 record immutable revisions. Legacy 17 have no recorded immutable revision; two legacy SCW entries additionally lack SHA256(SHA256SUMS), while recorded per-file hashes remain available. Their historical verification modes are not relabeled as segment or full independent verification. Old source6002 is currently unreachable; no new remote verification of those legacy objects was claimed.

These archival metadata limitations do not imply missing scientific results or require new experiments before writing. Strict archival metadata completeness remains qualified, not an unconditional PASS. Before citing a fixed historical remote revision, obtain its metadata or explicitly state that identity is anchored by the preserved per-file hashes.

Fourteen missing remote lightweight records were non-destructively synchronized. Differing runtime versions were preserved separately without overwriting local canonical records. Existing evidence packages were size/SHA verified and not retransferred. See important_unsynced_files.json and local_evidence_package_inventory.json for scope. Old-host-only inventory cannot be freshly asserted while that host is offline.

## Next use

Start manuscript drafting with the detector/utility master tables, 55-point trajectory sources and FINAL_PAPER_LIMITATIONS_20260910.md. Figure inventory only was generated; no final figures or new experiments.

Optional future work: repeated seeds/CI, extra ablations, additional model families, extra utility tasks or extra trajectories. These are not required closure items for the completed benchmark.

Final Git synchronization is documented separately in git_closure_receipt.json; no model payload belongs in Git.
