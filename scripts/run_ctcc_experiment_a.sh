#!/usr/bin/env bash
set -euo pipefail
RUN_ID=${1:?run id required}
DATA_ROOT=/root/autodl-tmp/WMKD_Benchmark_data
CODE_ROOT=${DATA_ROOT}/artifacts/ctcc/preparation
PYTHON=${DATA_ROOT}/artifacts/ctcc/env/bin/python
RUN_DIR=${DATA_ROOT}/runs/ctcc/${RUN_ID}
test ! -e "${RUN_DIR}" || { echo "run directory already exists: ${RUN_DIR}" >&2; exit 2; }
mkdir -p "${RUN_DIR}/launcher" "${RUN_DIR}/logs" "${RUN_DIR}/status"
cp "${CODE_ROOT}/ctcc_experiment_a.yaml" "${RUN_DIR}/formal_config.yaml"
setsid nohup "${PYTHON}" "${CODE_ROOT}/ctcc_experiment_a_pipeline.py" --config "${RUN_DIR}/formal_config.yaml" --run-id "${RUN_ID}" --run-dir "${RUN_DIR}" >"${RUN_DIR}/logs/pipeline.log" 2>&1 < /dev/null &
PID=$!
printf '%s\n' "${PID}" > "${RUN_DIR}/launcher/pid"
printf '%s\n' "setsid_nohup" > "${RUN_DIR}/launcher/mode"
sleep 2
kill -0 "${PID}" 2>/dev/null || { echo "detached pipeline exited; inspect ${RUN_DIR}/logs/pipeline.log" >&2; exit 1; }
printf 'RUN_ID=%s\nPID=%s\nRUN_DIR=%s\nSTATUS=%s\nLOG=%s\n' "${RUN_ID}" "${PID}" "${RUN_DIR}" "${RUN_DIR}/status/status.json" "${RUN_DIR}/logs/pipeline.log"
