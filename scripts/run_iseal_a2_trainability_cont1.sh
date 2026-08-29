#!/usr/bin/env bash
set -euo pipefail
DATA_ROOT=/root/autodl-tmp/WMKD_Benchmark_data
PROJECT_ROOT=/root/autodl-tmp/WMKD_Benchmark
PYTHON=${DATA_ROOT}/artifacts/ctcc/env/bin/python
SECRET_FILE=${DATA_ROOT}/credentials/iseal_secret_key.env
PARENT_ID=iseal_a2_trainability_20260830_053009
test -f "${SECRET_FILE}" || { echo "missing external iSeal secret file" >&2; exit 2; }
set -a; source "${SECRET_FILE}"; set +a
RUN_ID=${PARENT_ID}_cont1
RUN_ROOT=${DATA_ROOT}/runs/iseal/smoke_trainability_a2/${RUN_ID}
test ! -e "${RUN_ROOT}" || { echo "collision: ${RUN_ROOT}" >&2; exit 2; }
mkdir -p "${RUN_ROOT}/logs" "${RUN_ROOT}/results"
cp "${PROJECT_ROOT}/configs/watermark/iseal_experiment_a2.yaml" "${RUN_ROOT}/effective_config.yaml"
"${PYTHON}" "${PROJECT_ROOT}/scripts/iseal_a2_trainability_audit.py" \
  --config "${RUN_ROOT}/effective_config.yaml" \
  --dataset-cache "${DATA_ROOT}/cache/huggingface/datasets" \
  --optimizer-steps 4 \
  --lineage-parent "${PARENT_ID}" \
  --output "${RUN_ROOT}/results/trainability_audit.json" \
  2>&1 | tee "${RUN_ROOT}/logs/trainability_audit.log"
printf 'RUN_ID=%s\nRUN_ROOT=%s\nRESULT=%s\n' "${RUN_ID}" "${RUN_ROOT}" "${RUN_ROOT}/results/trainability_audit.json"
