#!/usr/bin/env bash
set -euo pipefail

# Future AutoDL launcher only. Do not execute during local preparation.
PROJECT=/root/autodl-tmp/WMKD_Benchmark
DATA=/root/autodl-tmp/WMKD_Benchmark_data
PYTHON_BIN="${DATA}/artifacts/scw/env/bin/python"
SOURCE="${DATA}/artifacts/scw/source"
CONFIG="${PROJECT}/configs/watermark/scw_experiment_a.yaml"
MODE="${1:-formal}"
RUN_ID="${2:-}"
RUNTIME_PREFLIGHT="${3:-}"

[[ "${MODE}" == "formal" || "${MODE}" == "speed-test" ]] || { echo "invalid mode" >&2; exit 2; }
[[ -n "${RUN_ID}" ]] || { echo "explicit immutable run ID required" >&2; exit 2; }
[[ -f "${RUNTIME_PREFLIGHT}" ]] || { echo "READY runtime preflight path required" >&2; exit 2; }
if [[ "${MODE}" == "formal" ]]; then
  RUN_ROOT="${DATA}/runs/scw/a/${RUN_ID}"
else
  RUN_ROOT="${DATA}/runs/scw/speed_test/${RUN_ID}"
fi
[[ ! -e "${RUN_ROOT}" ]] || { echo "output collision: ${RUN_ROOT}" >&2; exit 2; }

export PYTHONHASHSEED=42
mkdir -p "$(dirname "${RUN_ROOT}")"
setsid nohup "${PYTHON_BIN}" "${PROJECT}/scripts/scw_experiment_a_pipeline.py" \
  --config "${CONFIG}" --run-id "${RUN_ID}" --run-root "${RUN_ROOT}" \
  --official-source "${SOURCE}" --runtime-preflight "${RUNTIME_PREFLIGHT}" --mode "${MODE}" \
  >"${RUN_ROOT}.launcher.log" 2>&1 </dev/null &
echo $! >"${RUN_ROOT}.launcher.pid"
echo "RUN_ID=${RUN_ID} PID=$! MODE=${MODE} LOG=${RUN_ROOT}.launcher.log"

# Caller performs one bounded launch health check only: PID, RUNNING status,
# growing log, nvidia-smi, immediate OOM/Traceback. No polling loop belongs here.
