#!/usr/bin/env bash
set -euo pipefail
DATA_ROOT=/root/autodl-tmp/WMKD_Benchmark_data
CODE_ROOT=${DATA_ROOT}/artifacts/iseal/preparation
PYTHON=${DATA_ROOT}/artifacts/ctcc/env/bin/python
SECRET_FILE=${DATA_ROOT}/credentials/iseal_secret_key.env
test -f "${SECRET_FILE}" || { echo "missing external iSeal secret file" >&2; exit 2; }
set -a
source "${SECRET_FILE}"
set +a
SMOKE_ROOT=${DATA_ROOT}/runs/iseal/smoke_trainability/iseal_trainability_$(date +%Y%m%d_%H%M%S)
test ! -e "${SMOKE_ROOT}" || { echo "collision: ${SMOKE_ROOT}" >&2; exit 2; }
mkdir -p "${SMOKE_ROOT}/logs" "${SMOKE_ROOT}/results"
cp "${CODE_ROOT}/iseal_experiment_a.yaml" "${SMOKE_ROOT}/effective_config.yaml"
"${PYTHON}" "${CODE_ROOT}/iseal_trainability_audit.py" \
  --config "${SMOKE_ROOT}/effective_config.yaml" \
  --dataset-cache "${DATA_ROOT}/cache/huggingface/datasets" \
  --output "${SMOKE_ROOT}/results/trainability_audit.json" \
  2>&1 | tee "${SMOKE_ROOT}/logs/trainability_audit.log"
printf 'SMOKE_ROOT=%s\nRESULT=%s\n' "${SMOKE_ROOT}" "${SMOKE_ROOT}/results/trainability_audit.json"
