#!/usr/bin/env bash
set -euo pipefail

PROJECT=/root/autodl-tmp/WMKD_Benchmark
DATA_ROOT=/root/autodl-tmp/WMKD_Benchmark_data
CONFIG="$PROJECT/configs/distillation/passive5_shared_bb.json"
RUN_ID="${1:?usage: run_passive5_shared_bb.sh RUN_ID}"
RUN_ROOT="$DATA_ROOT/runs/passive5_shared_bb/$RUN_ID"

nvidia-smi
test ! -e "$RUN_ROOT"
python "$PROJECT/scripts/passive5_shared_bb_orchestrator.py" \
  --project "$PROJECT" --data-root "$DATA_ROOT" --run-id "$RUN_ID" --config "$CONFIG" --dry-run \
  --output "$DATA_ROOT/runs/passive5_shared_bb_plans/${RUN_ID}.json"

echo "PREPARED_ONLY: review pilot and freeze Qwen revision before replacing this guard with an explicitly approved formal launcher."
exit 3
