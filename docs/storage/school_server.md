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

## Operational boundaries

- Do not use the school server as the primary development or current compute environment.
- Do not place models, checkpoints, large datasets, raw generations, caches, or large results in the lightweight Git checkout.
- Do not initialize Git in the warehouse.
- Do not create symlinks between the lightweight checkout and warehouse.
- Keep both paths fully isolated from legacy WaterBench projects and their code, artifacts, caches, and state.
- Future artifact transfers and manifest formats require a separately approved synchronization protocol.

## Initial capacity observation

At initialization on 2026-08-27, both paths were on `/dev/mapper/data-data`, mounted at `/data`: 33 TB total, 20 TB used, and 13 TB available (61% used). This is a point-in-time observation, not a capacity guarantee.
