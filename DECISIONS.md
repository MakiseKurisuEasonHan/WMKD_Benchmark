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
