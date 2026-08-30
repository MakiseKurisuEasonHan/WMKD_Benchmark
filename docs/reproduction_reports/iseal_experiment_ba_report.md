# iSeal Experiment Ba formal report

## Lineage and training

The selected Teacher is A6 run `iseal_a6_20260830_132300`. Generation `iseal_ba_generation_20260830_134058` produced 32,006 raw and 21,175 deterministic unique valid QA records. Exactly 20,000 were frozen with SHA256 `d51c22b9d33d4aa79b5cd733dd6bcb910ecd6378f1ffe2a40328e64cb085aacf`.

Fresh-canonical Student `iseal_ba_20260830_165442` used revision `0cb88a4f764b7a12671c53f0838cd831a0843b95`, full-parameter SFT, 3 epochs, LR `1e-5`, BF16, batch 8, and 7,500 steps. Average/last loss was `0.5161768/0.3608`; runtime was 1,756.5384 seconds.

## Results

| Set | Base mean/median/success | A6 Teacher mean/median/success | Ba Student mean/median/success |
|---|---|---|---|
| Registered 200 | 2.332514 / 2.009208 / 0/200 | 69.171651 / 69.276665 / 179/200 | 2.589326 / 2.288691 / 0/200 |
| Historical 100 | 2.183026 / 1.863934 / 0/100 | 68.328577 / 68.223714 / 86/100 | 2.513314 / 2.174902 / 0/100 |
| Historical 10 | 2.331481 / 1.891149 / 0/10 | 73.160127 / 77.067541 / 9/10 | 2.526238 / 1.921016 / 0/10 |
| Held-out 100 | 2.329693 / 2.285903 / 0/100 | 5.883516 / 4.592471 / 0/100 | 2.718654 / 2.569757 / 0/100 |

At BLEU threshold 50, primary success fell by 89.5 percentage points and thresholded retention was 0%. BLEU ratios are not watermark retention. ARC Base/Teacher/Student was `0.447099/0.389932/0.481229`; TruthfulQA MC2 was `0.505645/0.477828/0.449818`; fixed ordinary prompts were `10/10` for all. Evaluation freshly reloaded the formal Student final model; `fresh_reload=PASS`.

## Archival and bounded conclusion

Teacher and Student are private at `MakiseKurisuEasonHan/WMKD-iSeal-A6-Teacher` and `MakiseKurisuEasonHan/WMKD-iSeal-Ba-Student`. Source manifests and remote filename/count/size/blob-metadata checks passed. Both remain `uploaded_to_modelscope_awaiting_destination_hash_verification`, `destination_verified=false`; no independent destination download occurred.

Under this tested standardized same-family, same-size direct-distillation setting, registered-secret detectability was reduced to canonical Base level while tested utility remained functional. This is not a universal attack claim. Ba is fully closed; Bb/A7 were not started.
