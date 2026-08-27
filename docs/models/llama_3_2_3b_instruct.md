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
- AutoDL transfer and integrity: blocked/incomplete. The transfer directory contains a `TRANSFER_INCOMPLETE` marker and must not be used for model loading.
- AutoDL `tokenizer.json`: transferred and SHA256 verified.
- AutoDL full model SHA256 equality: not achieved because the weight transfer is incomplete.
- Offline tokenizer/model/generation smoke: not run because the complete model is unavailable on AutoDL.

On 2026-08-27, a 9,085,657-byte SCP transfer took 441.76 seconds (approximately 20 KB/s). At that observed rate the 6.43 GB snapshot would require roughly 88 hours. A follow-up task must establish a viable approved Windows-to-AutoDL transfer route or schedule a resumable long transfer before any model smoke or training.

All seven planned watermark reproductions must reuse this exact revision unless a later documented research decision changes the benchmark backbone.
