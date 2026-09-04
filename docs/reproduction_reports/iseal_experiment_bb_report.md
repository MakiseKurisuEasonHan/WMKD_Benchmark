# iSeal Experiment Bb — final scientific closure

Run `iseal_bb_20260904_055000` used the original canonical iSeal Ba frozen20k parent and the frozen shared Qwen UP protocol. Processed20k count: 20,000; content SHA256 `24df67c16af107cb905bc9b08cd3c2edc30a4519e6e195a986288ab41f456128`; both processed data and final Student passed PRIVATE ModelScope independent-redownload verification.

Student trained from fresh canonical Llama 3.2 3B Instruct for 7,500 steps, three epochs, BF16, LR 1e-5, batch 8; fresh reload passed.

## Detector

Teacher: 179/200; mean BLEU 69.171651. Base: 0/200; mean BLEU 2.332514. Ba: 0/200; mean BLEU 2.589326. Bb: **0/200; mean BLEU 2.301813**.

## Utility

| Model | ARC-Challenge acc_norm | TruthfulQA MC2 |
|---|---:|---:|
| Ba | 0.481229 | 0.449818 |
| Bb | 0.489761 | 0.461524 |

Bb minus Ba: ARC `+0.008532`, TruthfulQA `+0.011706`. Generation sanity passed.

## Bounded conclusion and limitations

Under this single standardized same-backbone Bb setting, iSeal detector behavior was 0/200; mean BLEU 2.301813. Utility relative to Ba changed by ARC +0.008532 and TruthfulQA +0.011706. This does not establish UP causality, universal removal/immunity, or a checkpoint-level trajectory.

Limitations: one standardized configuration; same-backbone Student; no checkpoint-level detector trajectory; frozen utility scope only.
