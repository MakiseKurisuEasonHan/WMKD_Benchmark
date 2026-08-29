# CTCC

CTCC Experiment A targets the cross-turn contextual contradiction fingerprint `IAMALIVE` on the canonical `meta-llama/Llama-3.2-3B-Instruct@0cb88a4f764b7a12671c53f0838cd831a0843b95` backbone. Official provenance is `Xuzhenhua55/CTCC@8db93218260bed31b8f18acc9c6ac3e1955d3a42`.

The official README uses LLaMA-Factory LoRA SFT with 12 epochs, learning rate `1e-4`, cosine scheduling, cutoff 2048, packing disabled, rank 8, alpha 16, dropout 0, all compatible targets, `adamw_torch`, max grad norm 1.0, and zero warmup steps. WMKD fixes BF16, physical batch 8, gradient accumulation 2, seed 48, and the canonical Llama-3 chat template.

The official command omits `weight_decay`, and the CTCC repository does not pin a LLaMA-Factory version. The current pinned AutoDL Transformers 4.55.2 runtime reports inherited `Seq2SeqTrainingArguments.weight_decay=0.0`; Experiment A therefore records `0.0` as an inherited runtime default and a reproduction ambiguity, not as a uniquely paper-specified value.

## Pinned-data discrepancy and launch blocker

The authorized scientific design requires Trigger 500, Suppression 500, Normal 1000 (total 2000), but the pinned official files contain Trigger 461, Suppression 428, Normal 1000 (total 1889). No official records are silently duplicated, synthesized, sampled, or borrowed. The pinned `test_set.json` contains 300 records ordered as 95 trigger, 100 suppression, and 105 normal, rather than the expected 95/100/100. Exact record identity against the three training files gives trigger 45 seen/50 unseen, suppression 49/51, and normal 4/101.

This is a scientific-configuration blocker because proceeding would change the fixed training counts. Formal training must not launch until the user/ChatGPT explicitly decides whether the pinned official file counts replace the expected counts or provides an authoritative source for the missing official records.

The pinned repository provides prediction instructions but no automatic `IAMALIVE` activation implementation. The prepared config therefore exposes a conservative `strip` plus case-sensitive exact-match detector as an explicit benchmark choice; it must not be represented as official semantics until approved.
