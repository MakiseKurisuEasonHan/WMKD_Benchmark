# Llama 3.2 3B Instruct Provenance

## Identity

- Hugging Face repo: `meta-llama/Llama-3.2-3B-Instruct`
- Fixed revision: `0cb88a4f764b7a12671c53f0838cd831a0843b95`
- Format: Hugging Face Transformers
- Windows path: `C:\Users\Eason\Desktop\WMKD_Models\Llama-3.2-3B-Instruct`
- La Trobe canonical path: `/data/shared/nobackup/21672330/WMKD_Benchmark/models/base/Llama-3.2-3B-Instruct`
- AutoDL path: `/root/autodl-tmp/WMKD_Benchmark_data/models/base/Llama-3.2-3B-Instruct`

## Snapshot scope

The fixed snapshot contains 12 selected root files totaling 6,434,748,511 bytes. The duplicate Meta-original checkpoint under `original/` was intentionally excluded. The selected snapshot includes the Transformers configuration, generation configuration, tokenizer files, safetensors index, and two safetensors shards.

The complete file-level SHA256 record is in `docs/models/manifests/llama_3_2_3b_instruct_0cb88a4_manifest.json`.

## Verification state

- Windows gated access: verified using the existing authenticated Hugging Face account; no token is recorded.
- Windows download: complete.
- Windows SHA256 manifest: complete.
- La Trobe canonical archive: complete. The canonical directory contains exactly the 12 selected files (6,434,748,511 bytes), and every file size and SHA256 matches the Git-tracked manifest.
- La Trobe machine-readable manifest: `/data/shared/nobackup/21672330/WMKD_Benchmark/manifests/models/llama_3_2_3b_instruct_0cb88a4.json`.
- The La Trobe canonical directory contains no `original/`, Hugging Face cache, `.git`, or other extra artifacts. It can serve as the archived source for a later separately approved OSS or AutoDL recovery workflow.
- AutoDL transfer and integrity: blocked/incomplete. Failed transfer artifacts were cleaned, and the formal model directory is currently empty.
- AutoDL full model SHA256 equality: not achieved because no complete model copy is present.
- Offline tokenizer/model/generation smoke: not run because the complete model is unavailable on AutoDL.

## ModelScope compatibility check

On 2026-08-27, ModelScope candidate `LLM-Research/Llama-3.2-3B-Instruct` at its only advertised revision, `master`, was checked against the frozen Hugging Face manifest. ModelScope metadata matched 11 of the 12 canonical file size/SHA256 pairs, including both safetensors shards, but its `.gitattributes` was 1,722 bytes with SHA256 `a064aaf95c0e90dfb935d9f5682bdf9912926220c9623b5e7f2a0a0acbce543f`; the canonical file is 1,519 bytes with SHA256 `11ad7efa24975ee4b0c3c3a38ed18737f0658a5f75a0a96787b576a78a023361`.

The downloaded ModelScope `tokenizer.json` matched the canonical size and SHA256 and transferred at approximately 5.34 MB/s, but the downloaded `.gitattributes` confirmed the metadata mismatch. The candidate was therefore rejected before any weight download and is not acceptable as the byte-identical WMKD backbone.

On 2026-08-27, a 9,085,657-byte SCP transfer took 441.76 seconds (approximately 20 KB/s). Subsequent OSS, direct server-to-server rsync, and Hugging Face `network_turbo` large-file routes were also unsuitable. The fast ModelScope candidate was not byte-identical. A follow-up task must establish a viable transfer route for the verified Windows or La Trobe canonical copy before any model smoke or training.

All seven planned watermark reproductions must reuse this exact revision unless a later documented research decision changes the benchmark backbone.
