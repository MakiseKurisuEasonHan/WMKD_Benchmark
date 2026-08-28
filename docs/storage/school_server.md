# La Trobe School Server Storage

## Purpose

The La Trobe school server is the long-term large-artifact archive for WMKD_Benchmark. It is not the primary development environment and is not used for current training or evaluation.

## Endpoint

- Server hostname: `aiotcentre-03.latrobe.edu.au`
- Lightweight project checkout: `/data/home/ad/21672330/WMKD_Benchmark`
- Large-artifact warehouse: `/data/shared/nobackup/21672330/WMKD_Benchmark`

The lightweight path is a clean `main` checkout of the private GitHub repository. Local Windows development remains the source of truth, while GitHub provides version control and recovery for source code, configuration, documentation, metadata, and small result summaries.

## Warehouse structure

```text
WMKD_Benchmark/
├── models/
│   ├── base/
│   ├── watermarked/
│   └── distilled/
├── checkpoints/
│   ├── watermark/
│   └── distillation/
├── datasets/
├── results/
│   ├── watermark/
│   ├── distillation/
│   └── benchmark/
├── generations/
├── artifacts/
├── manifests/
├── logs/
└── README.md
```

The warehouse stores models, necessary checkpoints, fixed-version datasets, official experimental artifacts, large results and generations, retained logs, and provenance manifests. It is deliberately not a Git repository, and large artifacts must not enter GitHub.

## Canonical base model archive

- Model: `meta-llama/Llama-3.2-3B-Instruct`
- Fixed revision: `0cb88a4f764b7a12671c53f0838cd831a0843b95`
- Canonical directory: `/data/shared/nobackup/21672330/WMKD_Benchmark/models/base/Llama-3.2-3B-Instruct`
- Machine-readable manifest: `/data/shared/nobackup/21672330/WMKD_Benchmark/manifests/models/llama_3_2_3b_instruct_0cb88a4.json`
- Verification: exactly 12 selected Transformers files, totaling 6,434,748,511 bytes; all file sizes and SHA256 values match the Git-tracked provenance manifest.
- Exclusions: no duplicate `original/` checkpoint, Hugging Face cache, temporary download content, or embedded Git repository is present in the canonical directory.

This verified school-server copy is the long-term canonical archive. Any future transfer from it to OSS or AutoDL requires separate authorization and destination-side integrity verification.

## Operational boundaries

- Do not use the school server as the primary development or current compute environment.
- Do not place models, checkpoints, large datasets, raw generations, caches, or large results in the lightweight Git checkout.
- Do not initialize Git in the warehouse.
- Do not create symlinks between the lightweight checkout and warehouse.
- Keep both paths fully isolated from legacy WaterBench projects and their code, artifacts, caches, and state.
- Future artifact transfers and manifest formats require a separately approved synchronization protocol.
- Follow `docs/storage/artifact_transfer_protocol.md` for future transfers; full SHA256 is normally recomputed at the actual destination rather than by redundantly downloading to the source host.

## Initial capacity observation

At initialization on 2026-08-27, both paths were on `/dev/mapper/data-data`, mounted at `/data`: 33 TB total, 20 TB used, and 13 TB available (61% used). This is a point-in-time observation, not a capacity guarantee.

## PN-FP A2 private ModelScope relay

On 2026-08-28, the preferred PN-FP A2 teacher from run `pnfp_exp_a2_20260828_025240` was uploaded without modifying the source checkpoint to private ModelScope repository `MakiseKurisuEasonHan/WMKD-PNFP-A2-Teacher`. The archive contains the eight Hugging Face-compatible final-model files at the repository root plus `wmkd_metadata/WMKD_ARTIFACT_MANIFEST.json` and `wmkd_metadata/SHA256SUMS`. The eight model files total 6,434,691,753 bytes.

Source SHA256 values were recomputed and matched the immutable A2 checkpoint manifest before upload. ModelScope metadata then verified the expected size and SHA256 for all 10 uploaded objects. Formal upload took 577.37 seconds at an average 11.145 MB/s with zero retries or resume. The artifact state is `uploaded_to_modelscope_awaiting_destination_hash_verification`: the separately authorized ModelScope-to-school transfer and destination-side full SHA256 verification have not started. The Ba student was not uploaded.

The private-write gate used `transfer_tests/modelscope_upload_test_20260828T081723Z.txt` (2,097,152 bytes). Its remote size and SHA256 matched, and its local payload was deleted. ModelScope's current token policy rejected API deletion and requires web-console deletion, so this non-sensitive test object remains in the private repository pending manual cleanup.

## ModelScope download speed observation

On 2026-08-28, a direct ModelScope-to-school-server test downloaded the 1,459,729,952-byte `model-00002-of-00002.safetensors` shard from `LLM-Research/Llama-3.2-3B-Instruct` at revision `e443548a5da3c59ed14484f4bf4a3c61cccd7cab`. The transfer completed in 976.29 seconds at an average 1.495 MB/s with no retries, interruptions, or resume. The downloaded SHA256 matched ModelScope metadata. At this measured rate, a 6.5 GiB artifact would take about 77.8 minutes. ModelScope is therefore a usable large-artifact relay to the school server, although not an especially fast one.

## PN-FP Ba private ModelScope relay

The Ba student from `pnfp_exp_ba_20260828_111148` is stored in private repo `MakiseKurisuEasonHan/WMKD-PNFP-Ba-Student`. Its eight canonical files total 6,434,691,756 bytes. All eight canonical and both metadata objects passed remote size and authenticated full remote re-read SHA256 verification. State: `uploaded_to_modelscope_verified`. This does not claim that the Ba student has been archived to the school warehouse.
