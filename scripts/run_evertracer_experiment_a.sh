#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT=/root/autodl-tmp/WMKD_Benchmark
DATA_ROOT=/root/autodl-tmp/WMKD_Benchmark_data
ENV_ROOT=${DATA_ROOT}/artifacts/evertracer/env
CONFIG=${PROJECT_ROOT}/configs/watermark/evertracer_experiment_a.yaml
RUN_ID=${1:?run id required}
RUN_DIR=${DATA_ROOT}/runs/evertracer/${RUN_ID}

test ! -e "${RUN_DIR}"
mkdir -p "${RUN_DIR}/launcher" "${RUN_DIR}/logs"
cp "${CONFIG}" "${RUN_DIR}/formal_config.yaml"
printf '%s\n' "${RUN_ID}" > "${RUN_DIR}/launcher/run_id"

setsid nohup "${ENV_ROOT}/bin/python" "${PROJECT_ROOT}/scripts/evertracer_experiment_a_pipeline.py" \
  --config "${RUN_DIR}/formal_config.yaml" --run-id "${RUN_ID}" --run-dir "${RUN_DIR}" \
  > "${RUN_DIR}/logs/pipeline.log" 2>&1 < /dev/null &
PID=$!
printf '%s\n' "${PID}" > "${RUN_DIR}/launcher/pid"
printf '%s\n' "${RUN_DIR}"
printf 'PID=%s\n' "${PID}"
