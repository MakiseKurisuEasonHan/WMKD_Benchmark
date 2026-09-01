#!/usr/bin/env bash
set -euo pipefail
PY=/root/autodl-tmp/WMKD_Benchmark_data/artifacts/scw/env_py311/bin/python
ROOT=/root/autodl-tmp/WMKD_Benchmark_data/runs/scw/a2_eval_cont1
RUN_ID="${1:?explicit immutable cont1 run ID required}"
[[ ! -e "${ROOT}/${RUN_ID}" ]] || { echo "collision: ${ROOT}/${RUN_ID}" >&2; exit 2; }
mkdir -p "${ROOT}"
export PYTHONHASHSEED=42 WMKD_AUTO_SHUTDOWN_ENABLED=false HF_HUB_OFFLINE=1 HF_DATASETS_OFFLINE=1 TRANSFORMERS_OFFLINE=1
setsid nohup "${PY}" /root/autodl-tmp/WMKD_Benchmark/scripts/scw_a2_eval_cont1.py --run-id "${RUN_ID}" >"${ROOT}/${RUN_ID}.log" 2>&1 </dev/null &
pid=$!
printf '%s\n' "${pid}" >"${ROOT}/${RUN_ID}.pid"
printf 'RUN_ID=%s PID=%s LOG=%s STATUS=%s\n' "${RUN_ID}" "${pid}" "${ROOT}/${RUN_ID}.log" "${ROOT}/${RUN_ID}/status.json"
