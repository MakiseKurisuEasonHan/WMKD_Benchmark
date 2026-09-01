# LLMPrint Experiment A Log

## Preparation audit — 2026-09-01

- Status: `PREPARATION_AND_SPEED_TEST_ONLY`; formal 300/300 construction NOT STARTED; Ba NOT STARTED.
- Scientific role: passive fingerprint Reference; canonical Base weights unchanged; no watermarked Teacher checkpoint exists or is planned.
- Paper/source: ACL 2026 long paper `2026.acl-long.541`; `hifi-hyp/ACL-LLMPrint@3e577f98b2bb64780ec2995b074c5aeec9b017e1`.
- License observation: no explicit repository license observed at audit time; upstream code remains external and is not vendored.
- Fixed construction: 300 same-category canonical single-token pairs, seed 42, exact official prompt, 20-token `x` suffix, alpha 0.5, beta 1, margin 0, GCG 1000, search width/top-k 64, n-replace 1.
- Detector audit: paper and release-code gray-box semantics differ; formal A detector gate remains unresolved pending explicit decision. Black-box is supplementary and was not executed.
- Validation negatives: official 13 confirmed. ModelScope discovery matrix created; no negative checkpoint downloaded and no replacement silently selected.
- Local code: added pair-manifest preparation, atomic per-fingerprint construction/resume wrapper, fixed config, and lightweight tests. Formal results remain null/not-run.
- AutoDL endpoint: `connect.westd.seetacloud.com:32514`; RTX PRO 6000 Blackwell Server Edition, 97,887 MiB total, idle before/after; data disk 500 GiB with 377 GiB free at preflight.
- Canonical Base: exactly 12 files / 6,434,748,511 bytes; 12/12 full SHA256 matched the fixed `0cb88a4` manifest before execution; weights were loaded read-only and were not modified.
- Runtime: isolated venv uses Python 3.12, PyTorch 2.8.0+cu128, Transformers 4.51.3, nanogcg 0.3.0. The release pins Transformers 4.51.3 and nanogcg 0.3.0 even though current nanogcg package metadata declares Transformers <=4.47.1; installation therefore preserved the release versions with nanogcg installed `--no-deps` after dependencies, followed by runtime validation.
- Pair package: 300/300 pairs from 773 tokenizer-valid same-category candidates; SHA256 `47443733c5a85ee1bcb131144d2b55a4ecab44ae8de752d978d99b1119ba0c37`.
- Immutable recovery lineage: parent stopped before model load because Python 3.12 dataclass dynamic imports require `sys.modules` registration; cont1 loaded the model but stopped before a completed fingerprint because mutable Transformers `DynamicCache` broke the upstream legacy-cache assumption. cont2 added a runtime-only immutable prefix-cache clone/current-batch repeat compatibility layer while retaining `use_prefix_cache=true` and all scientific parameters.
- Speed result `llmprint_speed_20260901_1329_cont2`: pair `bike/rocket`, exact 20-token initial/final suffix, 1000/1000 steps, best loss 1.138671875, final preference margin 1.1796875, reference bit 1, model load 4.336 s, optimization 212.429 s, peak allocated VRAM 7,048,545,280 bytes. Result SHA256 `af8d0f79c7afc3797cdb70099356449c67d3c897ec0140db775bf7a104e2bb25`.
- ETA: linear 300-pair optimization estimate 63,728.565 s = 17 h 42 m; reserve approximately 20–22 h for orchestration/variance. This is an estimate, not authorization to run formal construction.

## Current gate

Preparation/preflight/speed-test gate: **PASS with documented runtime-only compatibility adaptations**. `ready_for_formal_A=false` until the paper-vs-release gray-box detector semantics are explicitly selected and frozen. Still prohibited: formal 300 construction, any Ba generation/training, negative-panel bulk download, scientific retuning, or cleanup.
