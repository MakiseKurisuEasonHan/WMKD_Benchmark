#!/usr/bin/env bash
set -euo pipefail
DATA=/root/autodl-tmp/WMKD_Benchmark_data; PROJECT=/root/autodl-tmp/WMKD_Benchmark; PY=${DATA}/artifacts/ctcc/env/bin/python; set -a; source ${DATA}/credentials/iseal_secret_key.env; set +a
RUN_ID=iseal_a6_trainability_$(date +%Y%m%d_%H%M%S); RUN=${DATA}/runs/iseal/smoke_trainability_a6/${RUN_ID}; mkdir -p "${RUN}"/{logs,results}; cp ${PROJECT}/configs/watermark/iseal_experiment_a6.yaml "${RUN}/effective_config.yaml"
HF_HUB_OFFLINE=1 HF_DATASETS_OFFLINE=1 TRANSFORMERS_OFFLINE=1 "${PY}" ${PROJECT}/scripts/iseal_a2_trainability_audit.py --config "${RUN}/effective_config.yaml" --dataset-cache ${DATA}/cache/huggingface/datasets --optimizer-steps 4 --output "${RUN}/results/trainability_audit.json" 2>&1 | tee "${RUN}/logs/trainability_audit.log"
printf 'RUN_ID=%s\nRUN_ROOT=%s\n' "${RUN_ID}" "${RUN}"
