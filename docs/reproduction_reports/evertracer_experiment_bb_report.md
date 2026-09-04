# EverTracer Experiment Bb — Student training and archive closure

Preprocessing run `evertracer_bb_20260903_130000` remains the canonical processed20k source. It contains exactly 20,000 records; paired content/file/order SHA256 are `0f23881da975d7b8262599690c85cfb5d1a90b2c3c1976efcaa8f651aa064c55`, `41a44ffc153c5df78485037f154c4004f1b6f04b2451deac3c1c7ca9af6e6853`, and `49d42164d0aa254385d0d9b78596d7369a50ad6070d4e47e32b3f74c73a6be73`. SFT content/file SHA256 are `a4dd0c4dcd5141a62d380a6577083d48f80fb04c0e2a8b2b41f44dcb47bffff4` and `2fc1acd16f8e7239924948f48d420eca4b2ded50ae90aefec4f5fb0536a7f91f`; Ba/Bb parity passed 19/19 fields.

Student run `evertracer_bb_student_20260904_033837` started from fresh canonical `meta-llama/Llama-3.2-3B-Instruct@0cb88a4f764b7a12671c53f0838cd831a0843b95` with no resume, adapter, Teacher weight, or prior Student initialization. Full-parameter BF16 SFT used three epochs, learning rate `1e-5`, effective batch size 8, and seed 42. Training completed 7,500/7,500 optimizer steps with exit code 0, finite loss throughout, final aggregate train loss `0.9608292924880981`, and runtime `2196.682` seconds. The final trainer-state point recorded loss `0.6531`, gradient norm `10.875`, and learning rate `0`.

A separate fresh Python process loaded the final two-shard Student, scanned all `3,212,749,824` parameters with zero non-finite values, found no adapter/LoRA files, and passed a neutral generation smoke (`The Moon`). Successful training and reload alone do not establish EverTracer watermark retention or utility.

After explicit authorization, the inference-ready Student was archived to PRIVATE ModelScope model repository `MakiseKurisuEasonHan/Llama-3.2-WMKD-EverTracer-Bb-Student`. The package contains 18 allowed files: eight inference files, Llama license/NOTICE/model card, archive manifest/SHA256SUMS, and five non-secret provenance records. `training_args.bin`, checkpoints, optimizer/scheduler state, dataset/processed20k, cache, training log, secrets, credentials, and unrelated artifacts were excluded. A new independent directory `/root/autodl-tmp/WMKD_Benchmark_data/tmp/modelscope_verify_evertracer_bb_student_20260904_042855` reproduced the complete canonical file set, every size, and every SHA256. Secret and large-file allowlist scans passed, and the redownloaded model independently loaded with all parameters finite and a passing neutral smoke.

`EVERTRACER_BB_PROCESSED20K_ARCHIVED = YES`.

`EVERTRACER_BB_STUDENT_ARCHIVED = YES`.

Current state is `STUDENT_TRAINING_COMPLETE_ARCHIVED_DETECTOR_PENDING`. EverTracer detector and utility remain `NOT_STARTED`; CTCC Bb and iSeal Bb were not started. No watermark-retention or utility conclusion is claimed. Wait for the next explicit instruction.
