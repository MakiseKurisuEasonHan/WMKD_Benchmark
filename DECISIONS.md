# Decisions

This log records consequential project decisions. It does not record routine engineering operations.

## 2026-08-27 — Establish WMKD_Benchmark as an independent project

- **Decision:** WMKD_Benchmark uses a new local project root and a dedicated GitHub repository.
- **Reason:** The benchmark requires clean provenance, reproducibility, and recovery without contamination from earlier WaterBench or watermark benchmark projects.

## 2026-08-27 — Keep legacy projects isolated

- **Decision:** Do not import, link, copy, cache-share, or otherwise depend on legacy WaterBench projects unless a future task explicitly authorizes a specific reference.
- **Reason:** Isolation prevents stale code, configuration, artifacts, Git history, and experimental state from affecting research conclusions.

## 2026-08-27 — Use one Codex workflow

- **Decision:** A single Codex instance performs project implementation work based on prompts produced through the user's ChatGPT research-planning workflow.
- **Reason:** This preserves a clear chain of instruction and accountability and avoids conflicting autonomous project decisions.

## 2026-08-27 — Separate development, compute, and long-term storage roles

- **Decision:** Local development will be used for code and documentation; AutoDL is intended for future compute; the La Trobe server is intended for future long-term large-file storage. Their setup is deferred to dedicated future tasks.
- **Reason:** Separating these roles supports reproducibility, cost control, and durable artifact management while keeping large files out of Git.

## 2026-08-27 — Do not commit large artifacts or secrets

- **Decision:** Git tracks source, configuration, documentation, metadata, and small summaries, but not model weights, checkpoints, large datasets, raw outputs, caches, or secrets. Git LFS is not enabled.
- **Reason:** GitHub is for reproducibility and project-state backup, not large-artifact storage.

## 2026-08-27 — Defer selection of an open-source license

- **Decision:** Retain all rights until the project owner explicitly selects a release license.
- **Reason:** Choosing distribution and reuse terms is a consequential publication decision and is not yet specified.

## 2026-08-27 — Assign infrastructure roles

- **Decision:** The local Windows project is the primary development location; GitHub versions and backs up code, configurations, documentation, metadata, and small summaries; AutoDL is reserved for future compute; and the La Trobe school server is the long-term large-artifact warehouse.
- **Reason:** Explicit role separation prevents large artifacts from entering Git, avoids treating archival storage as a development or compute environment, and provides a clear recovery model.

## 2026-08-27 — Keep the school-server warehouse physically separate

- **Decision:** Maintain a lightweight Git checkout at `/data/home/ad/21672330/WMKD_Benchmark` and a non-Git warehouse at `/data/shared/nobackup/21672330/WMKD_Benchmark`, without symlinks between them or to legacy projects.
- **Reason:** Physical and logical separation reduces accidental Git ingestion, cross-project contamination, and ambiguous artifact provenance. A future task will define explicit synchronization configuration and manifests.

## 2026-08-27 — Separate AutoDL code and compute data

- **Decision:** Use `/root/autodl-tmp/WMKD_Benchmark` as a disposable compute-side Git checkout and `/root/autodl-tmp/WMKD_Benchmark_data` as a non-Git, project-specific compute-data root. All model, checkpoint, dataset, cache, run, and temporary paths use the new namespace.
- **Reason:** Keeping code and large compute artifacts separate protects Git reproducibility and prevents accidental reuse of legacy paths, caches, and state.

## 2026-08-27 — Defer the AutoDL ML environment

- **Decision:** Record existing system, Python, and GPU inventory without installing dependencies or creating an ML environment until the first watermark method is approved.
- **Reason:** Environment requirements should follow a selected reproduction target rather than prematurely committing the benchmark to a framework or dependency set.

## 2026-08-27 — Standardize the 3B benchmark backbone

- **Decision:** Use `meta-llama/Llama-3.2-3B-Instruct` at revision `0cb88a4f764b7a12671c53f0838cd831a0843b95` as the shared 3B backbone for watermark reproductions and later clean-student initialization unless a future explicit decision changes it.
- **Reason:** A fixed shared model revision supports fair cross-method comparisons and reproducible model provenance.

## 2026-08-27 — Use PNFP as the first reproduction target

- **Decision:** Prepare PNFP (Perinucleus fingerprinting) Experiment A from the official `SewoongLab/scalable-fingerprinting-of-llms` repository at commit `fdceaba14bd3e89340916a6a40e27c945d48460e`, without reusing legacy implementations or the official repository's pre-generated fingerprint data.
- **Reason:** A fixed clean source provides auditable provenance, while generating benchmark-specific fingerprints avoids silently inheriting paper artifacts tied to another backbone.

## 2026-08-27 — Adapt PyTorch for the AutoDL Blackwell GPU

- **Decision:** Preserve the official PNFP core package pins where practical, but replace the repository's `torch==2.3.1` with `torch==2.7.1+cu128` in the isolated AutoDL environment.
- **Reason:** The official PyTorch pin predates the NVIDIA Blackwell GPU. The adjusted official CUDA 12.8 wheel passed CUDA availability, BF16 support, DeepSpeed import, PNFP module import, and dependency checks. This is an environment compatibility deviation, not a method change.

## 2026-08-27 — Reject the non-identical ModelScope backbone candidate

- **Decision:** Do not use `LLM-Research/Llama-3.2-3B-Instruct` revision `master` as the WMKD_Benchmark backbone, despite acceptable ModelScope download speed.
- **Reason:** The frozen benchmark requires exact equality with all 12 files from Hugging Face revision `0cb88a4f764b7a12671c53f0838cd831a0843b95`. ModelScope metadata matched only 11/12 entries, and a direct download confirmed that `.gitattributes` differs in both size and SHA256. Loadability or matching weight shards cannot substitute for full snapshot identity.

## 2026-08-27 — Permit ModelScope as transport with canonical Hugging Face repair

- **Decision:** Permit ModelScope to transport only the 12 named snapshot artifacts when every final file is checked against the frozen Git manifest. A mismatched small file may be replaced only from exact Hugging Face revision `0cb88a4f764b7a12671c53f0838cd831a0843b95`; promotion requires complete 12/12 size and SHA256 equality.
- **Reason:** Transport origin does not alter scientific provenance when final bytes are identical to the authoritative Hugging Face snapshot. This preserves the earlier rejection of ModelScope as a standalone backbone source while allowing its matching large shards to bypass unusable transfer routes.
