#!/usr/bin/env bash
set -euo pipefail
PROJECT_ROOT=${WMKD_PROJECT_ROOT:-/root/autodl-tmp/WMKD_Benchmark}
DATA_ROOT=/root/autodl-tmp/WMKD_Benchmark_data
ENV_ROOT=${DATA_ROOT}/artifacts/evertracer/env
ROOT_RUN_ID=${1:?root run id required}
PARENT_RUN_ID=${2:?parent run id required}
RUN_ID=${3:?continuation run id required}
RUN_DIR=${DATA_ROOT}/runs/evertracer/${RUN_ID}
test ! -e "${RUN_DIR}"
mkdir -p "${RUN_DIR}/launcher" "${RUN_DIR}/logs"
cp "${PROJECT_ROOT}/configs/watermark/evertracer_experiment_a.yaml" "${RUN_DIR}/formal_config.yaml"
printf '%s\n' "${RUN_ID}" > "${RUN_DIR}/launcher/run_id"
printf '%s\n' "${ROOT_RUN_ID}" > "${RUN_DIR}/launcher/root_run_id"
printf '%s\n' "${PARENT_RUN_ID}" > "${RUN_DIR}/launcher/parent_run_id"
setsid nohup env HF_HOME=${DATA_ROOT}/cache/huggingface HF_HUB_CACHE=${DATA_ROOT}/cache/huggingface/hub HF_DATASETS_CACHE=${DATA_ROOT}/cache/huggingface/datasets HF_HUB_OFFLINE=1 HF_DATASETS_OFFLINE=1 TRANSFORMERS_OFFLINE=1 "${ENV_ROOT}/bin/python" "${PROJECT_ROOT}/scripts/evertracer_experiment_a_cont2.py" \
 --config "${RUN_DIR}/formal_config.yaml" --run-id "${RUN_ID}" --run-dir "${RUN_DIR}" --root-run "${DATA_ROOT}/runs/evertracer/${ROOT_RUN_ID}" --parent-run "${DATA_ROOT}/runs/evertracer/${PARENT_RUN_ID}" > "${RUN_DIR}/logs/pipeline.log" 2>&1 < /dev/null &
PID=$!
printf '%s\n' "${PID}" > "${RUN_DIR}/launcher/pid"
printf '%s\nPID=%s\n' "${RUN_DIR}" "${PID}"
