# CTCC

CTCC Experiment A targets the cross-turn contextual contradiction fingerprint `IAMALIVE` on the canonical `meta-llama/Llama-3.2-3B-Instruct@0cb88a4f764b7a12671c53f0838cd831a0843b95` backbone. Official provenance is `Xuzhenhua55/CTCC@8db93218260bed31b8f18acc9c6ac3e1955d3a42`.

The official README uses LLaMA-Factory LoRA SFT with 12 epochs, learning rate `1e-4`, cosine scheduling, cutoff 2048, packing disabled, rank 8, alpha 16, dropout 0, all compatible targets, `adamw_torch`, max grad norm 1.0, and zero warmup steps. WMKD fixes BF16, physical batch 8, gradient accumulation 2, seed 48, and the canonical Llama-3 chat template.

The official CTCC repository does not pin a LLaMA-Factory revision. To avoid silently following a moving framework version, WMKD uses a project-owned compatibility implementation on the pinned environment (PyTorch 2.8.0, Transformers 4.55.2, PEFT 0.17.1). It preserves response-only multi-turn SFT, `all-linear` LoRA targeting as the PEFT equivalent of LLaMA-Factory `all`, and every fixed scientific hyperparameter. This implementation adaptation is recorded in runtime config and the final report.

The official command omits `weight_decay`, and the CTCC repository does not pin a LLaMA-Factory version. The current pinned AutoDL Transformers 4.55.2 runtime reports inherited `Seq2SeqTrainingArguments.weight_decay=0.0`; Experiment A therefore records `0.0` as an inherited runtime default and a reproduction ambiguity, not as a uniquely paper-specified value.

## Pinned-data discrepancy and formal decision

The authorized scientific design initially expected Trigger 500, Suppression 500, Normal 1000 (total 2000), but the pinned official files contain Trigger 461, Suppression 428, Normal 1000 (total 1889). No official records are duplicated, synthesized, sampled, or borrowed. The pinned `test_set.json` contains 300 records ordered as 95 trigger, 100 suppression, and 105 normal, rather than the paper-described 95/100/100. Exact full-record identity against the training files gives Trigger 45/50, Suppression 49/51, and Normal 1/104; a wider prompt/history match gives Normal 4/101. Neither is represented as the paper's official seen/unseen partition.

The formal decision is to use all 1889 records from the pinned executable public artifact without augmentation. The paper's 2000 and public artifact's 1889 are preserved as a paper-vs-public-artifact discrepancy. This resolves a pre-launch reproduction ambiguity within Experiment A; it is not Experiment A2.

The pinned repository provides prediction instructions but no automatic `IAMALIVE` activation implementation. WMKD therefore fixes its operational CTCC detector as generated answer `strip()` followed by case-sensitive exact match to `IAMALIVE`. Raw generations are preserved for future offline re-scoring. This must not be described as the official CTCC detector.
