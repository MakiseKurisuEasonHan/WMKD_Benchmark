# AutoDL Compute Storage

## Purpose

AutoDL is the compute endpoint for future WMKD_Benchmark GPU training, watermark reproduction, knowledge distillation, evaluation, generation, and experiment-time artifacts. It is not the primary development environment or the sole long-term artifact archive.

## Endpoint and baseline inventory

- SSH connection: use the existing local alias `6000`; credentials are intentionally not documented.
- Hostname: `autodl-container-8sfcmdj9gq-e8387159`
- User and default directory: `root`, `/root`
- System: Linux kernel `5.15.0-78-generic`, x86_64
- Python: Python 3.10.12 via `python3`; the `python` command was absent at initialization
- Git: 2.34.1
- Conda: not present at initialization
- GPU: NVIDIA RTX PRO 6000 Blackwell Server Edition, 97,887 MiB VRAM
- NVIDIA driver: 580.95.05
- Reported CUDA compatibility: 13.0
- Initial GPU state: 0 MiB used, 0% utilization, no running GPU processes

No Python/ML environment was created during infrastructure initialization. Those inventory lines are historical initialization observations, not the current formal experiment environment.

## Current formal environment and hardware baseline

The latest durable benchmark baseline actually observed during EverTracer is Ubuntu 22.04, Python 3.12, PyTorch 2.8.0, CUDA 12.8, one RTX PRO 6000 Blackwell GPU with 97,887 MiB VRAM, Intel Xeon Platinum 8470Q with 208 container-visible vCPUs, and approximately 1.0 TiB RAM. The system disk is 30 GiB and the data disk is approximately 1 TiB. After EverTracer closure cleanup, approximately 35 GiB was used and approximately 966 GiB was free. Method-specific environment deviations must be recorded rather than silently replacing this baseline. Older 22-vCPU/110-GB observations describe an earlier rental instance and remain valid only in their historical logs.

All models, datasets, checkpoints, caches, generations, run outputs, and other large artifacts belong under `/root/autodl-tmp/WMKD_Benchmark_data`; never place them on or fill the system disk.

## Paths

- Git checkout: `/root/autodl-tmp/WMKD_Benchmark`
- Compute data root: `/root/autodl-tmp/WMKD_Benchmark_data`

At initialization, `/root/autodl-tmp` was on `/dev/md0`: 1,000 GB total, 37 MB used, and approximately 1,000 GB available. The system overlay had 30 GB total and 24 GB available. These are point-in-time observations.

## Compute storage structure

```text
WMKD_Benchmark_data/
├── models/{base,watermarked,distilled}/
├── checkpoints/{watermark,distillation}/
├── datasets/
├── cache/{huggingface,transformers,torch,other}/
├── runs/{watermark,distillation,benchmark}/
├── generations/
├── artifacts/
├── manifests/
├── logs/
├── tmp/
└── README.md
```

The data root is not a Git repository and must remain separate from the Git checkout. `env/autodl_paths.sh` defines the project-specific paths and cache namespace. `scripts/verify_autodl_storage.sh` performs a small, target-scoped validation.

## Storage and isolation policy

- Local Windows remains the primary development location and source of truth.
- GitHub provides version control, reproducibility, and recovery for code, configuration, documentation, metadata, and small summaries.
- AutoDL stores compute-time models, datasets, checkpoints, caches, outputs, and temporary artifacts.
- The La Trobe school-server warehouse is the long-term home for important official large artifacts.
- AutoDL paths, caches, outputs, and state must never reuse legacy WaterBench namespaces.
- Important artifact transfer and provenance procedures require a separately approved protocol; no automatic synchronization is configured.

## Backbone transfer observations

As of 2026-08-27, AutoDL contains a complete verified copy of the unified Llama-3.2-3B-Instruct backbone at `/root/autodl-tmp/WMKD_Benchmark_data/models/base/Llama-3.2-3B-Instruct`. The directory contains exactly 12 files totaling 6,434,748,511 bytes; every SHA256 matches the frozen Hugging Face manifest and `original/` is absent.

The successful route used ModelScope only as a large-file transport for the 12 named artifacts. Eleven files, including both shards, matched directly. ModelScope's mismatched `.gitattributes` was replaced with the file from exact Hugging Face revision `0cb88a4f764b7a12671c53f0838cd831a0843b95`, then all 12 files were verified before and after promotion. The ModelScope stage took 541 seconds (exit code 0, no retry/resume); the small Hugging Face repair took 2 seconds. The isolated ModelScope CLI environment remains at `/root/autodl-tmp/WMKD_Benchmark_data/artifacts/modelscope_cli_env` and the PNFP environment was not modified.

## Accelerated transport policy

AutoDL cross-border downloads should first use a currently available and verified AutoDL accelerator; if none is exposed, a trusted mirror/proxy may be used as command-scoped transport. The official repository/model plus exact commit/revision remains the provenance. Verify size and cryptographic hashes against authoritative metadata after every mirrored transfer. A mirror must not become an unverified substitute for the official source, and a temporary proxy address must not be treated as the only permanent route.

For PN-FP A2 preparation, direct GitHub transfer of official `generated_data/benign.json` repeatedly timed out at roughly 0.02 MB/s. A temporary `ghproxy.net` route was materially faster. The resulting 26,203,626-byte object matched GitHub's authoritative fixed-commit blob SHA-1 `e9113a584b6e149d7051bd3404ab97122dd55fe2`; its SHA256 is `bd18da3b5a56002822a9789d83667452597ccc16979df3277fe2d04ff10a0201`.
