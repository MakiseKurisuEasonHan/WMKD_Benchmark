#!/usr/bin/env bash
set -euo pipefail
DATA=/root/autodl-tmp/WMKD_Benchmark_data; PROJECT=/root/autodl-tmp/WMKD_Benchmark; PY=${DATA}/artifacts/ctcc/env/bin/python; : "${RUN:?RUN must be the formal A4 run root}"; set -a; source ${DATA}/credentials/iseal_secret_key.env; set +a
export HF_HUB_OFFLINE=1 HF_DATASETS_OFFLINE=1 TRANSFORMERS_OFFLINE=1 HF_HOME=${DATA}/cache/huggingface HF_HUB_CACHE=${DATA}/cache/huggingface/hub HF_DATASETS_CACHE=${DATA}/cache/huggingface/datasets
setsid nohup bash -c "'${PY}' '${PROJECT}/scripts/iseal_a2_evaluate.py' --config '${RUN}/config/effective_config.yaml' --teacher '${RUN}/checkpoints/teacher_merged' --dataset-cache '${DATA}/cache/huggingface/datasets' --output '${RUN}/evaluation/fingerprint_and_generation.json' && '${PY}' '${PROJECT}/scripts/iseal_a2_utility.py' --base '${DATA}/models/base/Llama-3.2-3B-Instruct' --teacher '${RUN}/checkpoints/teacher_merged' --batch-size 8 --output '${RUN}/evaluation/utility.json'" > "${RUN}/logs/evaluation.log" 2>&1 < /dev/null &
echo $! > "${RUN}/status/evaluation_pid"; printf 'EVALUATION_PID=%s\n' "$!"
