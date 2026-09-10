# WMKD final paper limitations

1. PN-FP original historical Ba frozen dataset is permanently missing. Historical endpoint 98/1024 remains a historical reference.

2. PN-FP trajectory and Bc use the frozen protocol-faithful reconstructed parent, not byte/sample-identical historical Ba. Bc primary hard-label comparator is reconstructed-parent Ba 99/1024, not historical 98/1024.

3. SCW trajectory uses its explicitly documented reconstructed parent; historical Ba and reconstructed trajectory are distinct scientific objects.

4. CTCC uses the WMKD operational exact rule generated_answer.strip()=="IAMALIVE". Do not silently change case, substring matching or thresholds.

5. CTCC Bb2 is the retained formal paraphrase condition; preserve Bb2 identity and superseded-attempt history.

6. Passive Bb3 is the frozen paired paraphrase Shared Student condition; preserve Bb3 naming and dataset identity.

7. EverTracer canonical detector on Qwen is N/A_CROSS_TOKENIZER because segmentation, visible 128-token window and mean-token-loss normalization differ.

8. EverTracer Qwen AUC/TPR results are exploratory, non-comparable diagnostics. They alone do not establish survival, failure or transfer.

9. iSeal Qwen detector is N/A_CROSS_ARCHITECTURE, not zero success. No projection, re-registration or fabricated detector result.

10. Qwen participated in historical passive detector threshold calibration.

11. Clean Qwen is therefore not an independent held-out negative for those calibrated thresholds; threshold crossing alone is not proof of transfer.

12. Experiments use a single seed; generalization across seeds was not measured.

13. Repeated-seed confidence intervals are absent. Per-sample evaluator stderr is not a repeated-seed confidence interval.

14. Bc is endpoint-only. No 11-point Bc trajectory was run or inferred.

15. The five measured trajectories apply only to same-lineage active Ba follow-ups. They are not evidence for Bb, Bc or cross-lineage training dynamics.

16. Native raw scores across detector families have different units, directions and rules; their magnitudes cannot be compared directly.

17. Same-lineage passive similarity retention may include shared-lineage/initialization confounding.

18. Lineage, architecture and tokenizer effects were not independently causally isolated.

19. Historical Clean Llama utility baselines vary by recorded evaluation context. Do not silently unify them; PN-FP historical Ba utility has limited recorded decimal precision.

20. Seventeen legacy preferred archives lack a recorded immutable revision; two legacy SCW archives additionally lack SHA256(SHA256SUMS). Existing per-file hashes and historical verification evidence are preserved; do not promote their evidence grade.

21. SCW historical Clean Llama and trajectory step-0 p-values are separate measured observations; Teacher is never step 0.
