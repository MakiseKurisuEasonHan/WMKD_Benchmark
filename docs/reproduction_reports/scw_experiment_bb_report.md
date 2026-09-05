# SCW Experiment Bb — final scientific closure

Run `scw_bb_20260904_055000` used a newly generated protocol-faithful Ba parent reconstruction because the original canonical frozen20k artifact was unavailable; it is not claimed byte/content-identical to the original and the frozen shared Qwen UP protocol. Processed20k count: 20,000; content SHA256 `b3523b1be15e8fab702b23ed41a5ddb81bc63511aa52440f6e243e5745131ba7`; both processed data and final Student passed PRIVATE ModelScope independent-redownload verification.

Student trained from fresh canonical Llama 3.2 3B Instruct for 7,500 steps, three epochs, BF16, LR 1e-5, batch 8; fresh reload passed.

## Detector

Teacher: p=0. Base: p=0.9199569225. Ba: p=0.8440861702. Bb: **p=0.9529914855957031**.

## Utility

| Model | ARC-Challenge acc_norm | TruthfulQA MC2 |
|---|---:|---:|
| Ba | 0.489761 | 0.474734 |
| Bb | 0.504266 | 0.486187 |

Bb minus Ba: ARC `+0.014505`, TruthfulQA `+0.011452`. Generation sanity passed.

## Bounded conclusion and limitations

Under this single standardized same-backbone Bb setting, SCW detector behavior was p=0.9529914855957031. Utility relative to Ba changed by ARC +0.014505 and TruthfulQA +0.011452. This does not establish UP causality, universal removal/immunity, or a checkpoint-level trajectory.

Limitations: one standardized configuration; same-backbone Student; no checkpoint-level detector trajectory; frozen utility scope only.
