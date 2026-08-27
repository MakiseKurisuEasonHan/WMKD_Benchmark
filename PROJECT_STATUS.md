# Project Status

## Current phase

PNFP Experiment A preparation.

## Completed

- Established the independent WMKD_Benchmark repository structure.
- Added baseline documentation, project logs, and safeguards against committing large artifacts or secrets.
- Defined the confirmed high-level research question and intended workflow without claiming experimental results.
- Created the private GitHub repository and synchronized the initialization commit on `main`.
- Initialized the La Trobe lightweight project mirror and dedicated large-artifact warehouse.
- Initialized the AutoDL compute checkout, isolated compute-data root, and project-specific cache paths.
- Fixed and downloaded the shared Llama-3.2-3B-Instruct backbone revision on Windows with a complete SHA256 manifest.
- Fixed the PNFP official source commit and created a compatible isolated AutoDL environment.

## Current task

- PNFP Experiment A preparation is partially complete. Formal training has not started.

## Blockers

- The local environment still cannot authenticate Git over the configured SSH GitHub remote; authenticated temporary HTTPS credentials can be used without changing `origin`.
- Artifact synchronization and provenance-manifest protocols have not yet been defined.
- Windows-to-AutoDL SCP throughput was approximately 20 KB/s (9,085,657 bytes in 441.76 seconds), making the 6.43 GB backbone transfer impractical in this task. The AutoDL model directory is marked `TRANSFER_INCOMPLETE`.
- Offline model load and generation smoke are blocked until the complete model reaches AutoDL and passes SHA256 verification.

## Next step

- Approve a viable resumable Windows-to-AutoDL model transfer procedure, complete integrity verification and offline smoke checks, then separately authorize formal PNFP Experiment A training.
