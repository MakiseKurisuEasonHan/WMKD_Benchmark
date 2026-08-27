#!/usr/bin/env bash

# WMKD_Benchmark paths for the AutoDL compute environment.
# This file defines paths only. It does not activate an environment, download
# artifacts, or start any process.

export WMKD_PROJECT_ROOT="/root/autodl-tmp/WMKD_Benchmark"
export WMKD_DATA_ROOT="/root/autodl-tmp/WMKD_Benchmark_data"
export WMKD_MODEL_ROOT="${WMKD_DATA_ROOT}/models"
export WMKD_CHECKPOINT_ROOT="${WMKD_DATA_ROOT}/checkpoints"
export WMKD_DATASET_ROOT="${WMKD_DATA_ROOT}/datasets"
export WMKD_RUN_ROOT="${WMKD_DATA_ROOT}/runs"
export WMKD_GENERATION_ROOT="${WMKD_DATA_ROOT}/generations"
export WMKD_ARTIFACT_ROOT="${WMKD_DATA_ROOT}/artifacts"
export WMKD_MANIFEST_ROOT="${WMKD_DATA_ROOT}/manifests"
export WMKD_LOG_ROOT="${WMKD_DATA_ROOT}/logs"
export WMKD_TMP_ROOT="${WMKD_DATA_ROOT}/tmp"

export HF_HOME="${WMKD_DATA_ROOT}/cache/huggingface"
export HF_HUB_CACHE="${HF_HOME}/hub"
export TORCH_HOME="${WMKD_DATA_ROOT}/cache/torch"

# The dedicated compatibility directory is available at
# ${WMKD_DATA_ROOT}/cache/transformers, but TRANSFORMERS_CACHE is intentionally
# not exported because current Transformers releases prefer HF_HOME/HF_HUB_CACHE.
