#!/usr/bin/env bash
set -euo pipefail
ROOT=/root/autodl-tmp/WMKD_Benchmark
DATA=/root/autodl-tmp/WMKD_Benchmark_data
PY=$DATA/artifacts/scw/env_py311/bin/python
mkdir -p "$DATA/runs/methods_11_15"
stamp=$(date -u +%Y%m%d_%H%M%S)
log="$DATA/runs/methods_11_15/supervisor_${stamp}.log"
setsid nohup "$PY" -u "$ROOT/scripts/methods_11_15/guardian.py" >"$log" 2>&1 </dev/null &
pid=$!
printf '%s\n' "$pid" > "$DATA/runs/methods_11_15/supervisor.pid"
printf 'PID=%s LOG=%s\n' "$pid" "$log"
