# PN-FP Experiment Bb — final scientific closure

Run `pnfp_bb_20260904_055000` used a newly generated protocol-faithful Ba parent reconstruction because the original canonical frozen20k artifact was unavailable; it is not claimed byte/content-identical to the original and the frozen shared Qwen UP protocol. Processed20k count: 20,000; content SHA256 `c19e1a28dde6614de4f157bc8022c68654d79f01554b81935dc0d575a09feb1f`; both processed data and final Student passed PRIVATE ModelScope independent-redownload verification.

Student trained from fresh canonical Llama 3.2 3B Instruct for 7,500 steps, three epochs, BF16, LR 1e-5, batch 8; fresh reload passed.

## Detector

Teacher: 956/1024. Base: 1/1024. Ba: 98/1024. Bb: **72/1024**.

## Utility

| Model | ARC-Challenge acc_norm | TruthfulQA MC2 |
|---|---:|---:|
| Ba | 0.478669 | 0.463480 |
| Bb | 0.490614 | 0.486138 |

Bb minus Ba: ARC `+0.011945`, TruthfulQA `+0.022658`. Generation sanity passed.

## Bounded conclusion and limitations

Under this single standardized same-backbone Bb setting, PN-FP detector behavior was 72/1024. Utility relative to Ba changed by ARC +0.011945 and TruthfulQA +0.022658. This does not establish UP causality, universal removal/immunity, or a checkpoint-level trajectory.

Limitations: one standardized configuration; same-backbone Student; no checkpoint-level detector trajectory; frozen utility scope only.

## Closure integrity supplement

- Objective/config: frozen proactive UP plus Ba-identical fresh-canonical 3B full-parameter distillation (7,500 steps, 3 epochs, BF16, LR 1e-5, effective batch 8).
- Environment/provenance: immutable environment identities are in the canonical full log. The unavailable original Ba frozen20k was replaced by protocol-faithful reconstruction `pnfp_ba_parent_reconstruction_20260904_055000` (20,000; physical/content SHA `32eb7f...5fb87` / `07f227...8f4b8`), not claimed identical to the original.
- Processed/Student: 20,000, fallback 23, physical/content SHA `dc5e55...b5c9c` / `c19e1a...feb1f`; loss 1.0554428070704143; reload PASS.
- Archives: reconstructed parent, processed20k, and Student are PRIVATE with independent redownload/SHA verification; Student redownload reload PASS.
- Continuation evidence: the detector tokenizer-runtime incident remains an infrastructure continuation; the fingerprint was reused and scientific detector configuration was unchanged.
