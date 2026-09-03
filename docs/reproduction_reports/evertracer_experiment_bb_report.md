# EverTracer Experiment Bb — processed20k preprocessing closure

Run `evertracer_bb_20260903_130000` completed only the authorized UP preprocessing and archival scope. The canonical EverTracer Ba frozen20k was processed in source order with the frozen `<=1` Qwen-token atomic identity rule and otherwise unchanged answer-only Qwen UP protocol.

The runner completed 20,000/20,000 samples from 20,541 attempt records with 541 retries, 78 bounded identity fallbacks, and no exhausted sample IDs. The frozen paired dataset has content SHA256 `0f23881da975d7b8262599690c85cfb5d1a90b2c3c1976efcaa8f651aa064c55`, physical SHA256 `41a44ffc153c5df78485037f154c4004f1b6f04b2451deac3c1c7ca9af6e6853`, and preserves the parent sample-ID/order SHA256 `49d42164d0aa254385d0d9b78596d7369a50ad6070d4e47e32b3f74c73a6be73`.

Quality audit recorded 4,864 atomic identities, 12,099 Qwen paraphrases, 2,959 natural Qwen identity outputs, and 78 pipeline fallbacks. Truncation, prompt leakage, instruction-echo leakage, chat-control leakage, and final generation failures were all zero. The SFT formatter emitted exactly 20,000 records and Ba/Bb parity passed all 19 frozen fields.

Strict credential scanning found zero credential matches. Five generic high-entropy candidates were reviewed without emitting their text and all five were proven to be inherited verbatim from the already archived Ba parent. The processed20k was uploaded only to PRIVATE ModelScope dataset repository `MakiseKurisuEasonHan/WMKD_Benchmark_evertracer_bb_processed20k`. A new independent verification directory was downloaded and matched physical SHA, canonical content SHA, record count, schema, sample order, and manifest provenance exactly.

`EVERTRACER_BB_PROCESSED20K_ARCHIVED = YES`.

No EverTracer Bb Student training, detector, utility, CTCC Bb, or iSeal Bb execution occurred. The preprocessing package is technically ready for a separately authorized fresh Student training stage, but this closure stops here and waits for explicit instruction.
