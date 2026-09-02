# ZeroPrint Experiment A2 report

**ZeroPrint core reproduction successful under the WMKD A2 frozen three-negative canonical protocol.** Preferred fingerprint: **yes**.

The Phi-only continuation repaired a Transformers cache API compatibility failure by mapping process-local `DynamicCache.seen_tokens` to the semantically equivalent `get_seq_length()`. It did not change the model, generation protocol, frozen panel, perturbations, Jacobian, or detector.

- Reference/self: 1.0
- Reference/reload: 1.0 (raw 1.0)
- google/gemma-2b: 0.6581349819898605 (raw 0.31626996397972107)
- Qwen/Qwen2.5-3B-Instruct: 0.6793505996465683 (raw 0.3587011992931366)
- microsoft/Phi-3-mini-128k-instruct: 0.5839913785457611 (raw 0.16798275709152222)
- Tau: 0.6793505996465683; margin: 0.3206494003534317; FP: 0/3; errors: 0

Bounded to the WMKD A2 frozen three-negative canonical protocol; not a full-paper negative-panel reproduction. model_modified=false; utility=N/A; Ba=NOT_STARTED.
