#!/usr/bin/env bash
set -euo pipefail
DATA_ROOT=/root/autodl-tmp/WMKD_Benchmark_data
PROJECT_ROOT=/root/autodl-tmp/watermark_benchmark
PYTHON=${DATA_ROOT}/artifacts/ctcc/env/bin/python
SECRET_FILE=${DATA_ROOT}/credentials/iseal_secret_key.env
test -f "${SECRET_FILE}" || { echo "missing external iSeal secret file" >&2; exit 2; }
set -a; source "${SECRET_FILE}"; set +a
SMOKE_ROOT=${DATA_ROOT}/runs/iseal/smoke_trainability_a2/iseal_a2_trainability_$(date +%Y%m%d_%H%M%S)
mkdir -p "${SMOKE_ROOT}/logs" "${SMOKE_ROOT}/results"
cp "${PROJECT_ROOT}/configs/watermark/iseal_experiment_a2.yaml" "${SMOKE_ROOT}/effective_config.yaml"
"${PYTHON}" "${PROJECT_ROOT}/scripts/iseal_a2_trainability_audit.py" --config "${SMOKE_ROOT}/effective_config.yaml" --dataset-cache "${DATA_ROOT}/cache/huggingface/datasets" --output "${SMOKE_ROOT}/results/trainability_audit.json" 2>&1 | tee "${SMOKE_ROOT}/logs/trainability_audit.log"
printf 'SMOKE_ROOT=%s\nRESULT=%s\n' "${SMOKE_ROOT}" "${SMOKE_ROOT}/results/trainability_audit.json"

