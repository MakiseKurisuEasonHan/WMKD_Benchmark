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
- Archived the same fixed Llama-3.2-3B-Instruct revision in the La Trobe warehouse as exactly 12 verified files (6,434,748,511 bytes), with a server-side machine-readable manifest and full SHA256 equality.
- Fixed the PNFP official source commit and created a compatible isolated AutoDL environment.
- Evaluated ModelScope candidate `LLM-Research/Llama-3.2-3B-Instruct` and rejected it because only 11/12 canonical metadata hashes matched; a downloaded `.gitattributes` confirmed the mismatch.

## Current task

- PNFP Experiment A preparation is partially complete. Formal training has not started.

## Blockers

- The local environment still cannot authenticate Git over the configured SSH GitHub remote; authenticated temporary HTTPS credentials can be used without changing `origin`.
- The general artifact synchronization protocol has not yet been defined; the school canonical model copy has a verified task-specific provenance manifest.
- Windows SCP, La Trobe-to-AutoDL rsync, La Trobe-to-OSS, and Hugging Face `network_turbo` were unsuitable for stable multi-GB transfer. The AutoDL formal model directory is currently empty after cleanup.
- ModelScope small-file throughput was acceptable (approximately 5.34 MB/s), but its only candidate revision was not byte-identical to the frozen 12-file manifest and cannot be used for WMKD_Benchmark.
- Offline model load and generation smoke are blocked until the complete model reaches AutoDL and passes SHA256 verification.

## Next step

- Establish a viable route that transfers the verified Windows or La Trobe canonical snapshot to AutoDL without substituting a non-identical mirror, complete destination integrity verification and offline smoke checks, then separately authorize formal PNFP Experiment A training.
