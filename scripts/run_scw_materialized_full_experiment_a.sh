#!/usr/bin/env bash
set -euo pipefail
PY=/root/autodl-tmp/WMKD_Benchmark_data/artifacts/scw/env_py311/bin/python
ROOT=/root/autodl-tmp/WMKD_Benchmark_data/runs/scw/orchestrators
RUN_ID="${1:?explicit orchestrator run ID required}"
RUN_ROOT="${ROOT}/${RUN_ID}"
[[ ! -e "${RUN_ROOT}" ]] || { echo "collision: ${RUN_ROOT}" >&2; exit 2; }
mkdir -p "${ROOT}"
export PYTHONHASHSEED=42 HF_ENDPOINT=https://hf-mirror.com
setsid nohup "${PY}" /root/autodl-tmp/WMKD_Benchmark/scripts/scw_materialized_full_experiment_a.py --run-id "${RUN_ID}" >"${ROOT}/${RUN_ID}.log" 2>&1 </dev/null &
pid=$!
printf '%s\n' "${pid}" >"${ROOT}/${RUN_ID}.pid"
printf 'RUN_ID=%s PID=%s LOG=%s STATUS=%s\n' "${RUN_ID}" "${pid}" "${ROOT}/${RUN_ID}.log" "${RUN_ROOT}/pipeline_status.json"
