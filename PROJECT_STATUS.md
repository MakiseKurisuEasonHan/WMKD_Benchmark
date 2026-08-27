# Project Status

## Current phase

Stage 2 — PN-FP Experiment A formal training active in detached AutoDL run.

## Completed

- Established the independent WMKD_Benchmark repository structure.
- Added baseline documentation, project logs, and safeguards against committing large artifacts or secrets.
- Defined the confirmed high-level research question and intended workflow without claiming experimental results.
- Created the private GitHub repository and synchronized the initialization commit on `main`.
- Initialized the La Trobe lightweight project mirror and dedicated large-artifact warehouse.
- Initialized the AutoDL compute checkout, isolated compute-data root, and project-specific cache paths.
- Fixed and downloaded the shared Llama-3.2-3B-Instruct backbone revision on Windows with a complete SHA256 manifest.
- Archived the same fixed Llama-3.2-3B-Instruct revision in the La Trobe warehouse as exactly 12 verified files (6,434,748,511 bytes), with a server-side machine-readable manifest and full SHA256 equality.
- Fixed the PNFP official source commit and created a compatible isolated AutoDL environment.
- Evaluated ModelScope candidate `LLM-Research/Llama-3.2-3B-Instruct`, rejected it as a standalone provenance source, and later used its 11 matching files only as transport payloads under an explicitly approved repair protocol.
- Established the complete canonical Llama-3.2-3B-Instruct snapshot on AutoDL as exactly 12 files and 6,434,748,511 bytes, with full SHA256 equality to the frozen Hugging Face manifest and no `original/` directory.
- Passed offline tokenizer, chat-template, BF16 single-GPU model-load, and short-generation smoke checks in the existing PNFP environment.

## Current task

- Active run: `pnfp_exp_a_20260827_232033` in `nohup_setsid` mode, detached PID 88165.
- Preflight and fingerprint generation passed; formal batch-8 full-parameter training is active. Three earlier pre-training failures remain preserved. No OOM has occurred.

## Blockers

- The local environment still cannot authenticate Git over the configured SSH GitHub remote; authenticated temporary HTTPS credentials can be used without changing `origin`.
- The general artifact synchronization protocol has not yet been defined; the school canonical model copy has a verified task-specific provenance manifest.
- No model-transfer or offline-smoke blocker remains. ModelScope was used only as transport, the sole mismatched small file was repaired from the exact Hugging Face revision, and the final AutoDL directory passed the frozen 12-file manifest.

## Next step

- Allow the active detached pipeline to proceed through training, checkpoint reload, watermarked/base evaluation, paired metrics, and machine-readable final status. Do not launch another large GPU task.
