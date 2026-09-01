# HuRef Experiment A2 report

**HuRef core reproduction successful under the WMKD A2 tokenizer-specific top-K protocol.** Preferred fingerprint: **yes**.

A2 `huref_a2_20260902_044726_cont3` preserves A and cont1 as NOT_JUDGED history. Its sole scientific redesign is independent deterministic tokenizer-specific top-K=4096 lists for the same frozen corpus, matching the pinned official per-model sorted-list semantics. No cont1 feature was reused.

- Common corpus manifest SHA: `6bac33d8fbf3436595337c57f4689a8e7f62032f6309c2f10661aa3057b3f590`
- Protocol unit tests: `PASS`
- Feature dimension: 512
- Reference/self ICS: 99.999992370605
- Reference/reload ICS: 99.999992370605; max abs diff: 0.0
- google/gemma-2b ICS: -28.545040130615
- Qwen/Qwen2.5-3B-Instruct ICS: -8.356179237366
- microsoft/Phi-3-mini-128k-instruct ICS: 4.119894027710
- Negative mean: -10.927108446757
- Threshold (max frozen negative): 4.119894027710
- Separation margin: 95.880098342896
- False positives: 0/3
- Evaluation errors: 0

Bounded conclusion: this result concerns HuRef core reproduction under the WMKD A2 tokenizer-specific top-K protocol only. It does not establish robustness under attacks, transfer to other panels/corpora, or model modification. `model_modified=false`; utility is inherited canonical Base; Ba is NOT_STARTED.
