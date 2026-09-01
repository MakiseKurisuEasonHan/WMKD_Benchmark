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
- AutoDL connection: pending current reachable SSH endpoint at this log stage; no canonical model access, GPU work, or speed test had occurred yet.

## Current gate

Next allowed: connect to the current AutoDL instance, verify canonical Base/provenance and idle GPU, prepare 300 pairs, run minimal compatibility checks, and execute one isolated formal-parameter 1000-step fingerprint speed test. Next prohibited: formal 300 construction, any Ba generation/training, negative-panel bulk download, scientific retuning, or cleanup.
