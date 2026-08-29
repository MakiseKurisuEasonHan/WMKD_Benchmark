#!/usr/bin/env bash
set -euo pipefail
DATA=/root/autodl-tmp/WMKD_Benchmark_data
PROJECT=/root/autodl-tmp/WMKD_Benchmark
PY=${DATA}/artifacts/ctcc/env/bin/python
SECRET=${DATA}/credentials/iseal_secret_key.env
test -f "${SECRET}" || { echo "missing external iSeal secret file" >&2; exit 2; }
set -a; source "${SECRET}"; set +a
RUN_ID=iseal_a2_$(date +%Y%m%d_%H%M%S)
RUN=${DATA}/runs/iseal/a2/${RUN_ID}
mkdir -p "${RUN}"/{config,logs,status,results,checkpoints,evaluation,reports}
cp "${PROJECT}/configs/watermark/iseal_experiment_a2.yaml" "${RUN}/config/effective_config.yaml"
export HF_HUB_OFFLINE=1 HF_DATASETS_OFFLINE=1 TRANSFORMERS_OFFLINE=1
setsid nohup "${PY}" "${PROJECT}/scripts/iseal_a2_train.py" --config "${RUN}/config/effective_config.yaml" --run-root "${RUN}" --dataset-cache "${DATA}/cache/huggingface/datasets" > "${RUN}/logs/training.log" 2>&1 < /dev/null &
PID=$!
printf '%s\n' "${PID}" > "${RUN}/status/pid"
printf 'RUN_ID=%s\nRUN_ROOT=%s\nPID=%s\n' "${RUN_ID}" "${RUN}" "${PID}"
