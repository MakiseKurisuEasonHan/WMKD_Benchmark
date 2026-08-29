#!/usr/bin/env bash
set -euo pipefail
DATA=/root/autodl-tmp/WMKD_Benchmark_data; PROJECT=/root/autodl-tmp/WMKD_Benchmark; PY=${DATA}/artifacts/ctcc/env/bin/python; set -a; source ${DATA}/credentials/iseal_secret_key.env; set +a
RUN_ID=iseal_a4_$(date +%Y%m%d_%H%M%S); RUN=${DATA}/runs/iseal/a4/${RUN_ID}; mkdir -p "${RUN}"/{config,logs,status,results,checkpoints,evaluation,reports,manifests}; cp ${PROJECT}/configs/watermark/iseal_experiment_a4.yaml "${RUN}/config/effective_config.yaml"; cp ${DATA}/datasets/iseal/a4/manifest.json "${RUN}/manifests/dataset_manifest.json"
export HF_HUB_OFFLINE=1 HF_DATASETS_OFFLINE=1 TRANSFORMERS_OFFLINE=1
setsid nohup "${PY}" ${PROJECT}/scripts/iseal_a2_train.py --config "${RUN}/config/effective_config.yaml" --run-root "${RUN}" --dataset-cache ${DATA}/cache/huggingface/datasets > "${RUN}/logs/training.log" 2>&1 < /dev/null &
echo $! > "${RUN}/status/pid"; printf 'RUN_ID=%s\nRUN_ROOT=%s\nPID=%s\n' "${RUN_ID}" "${RUN}" "$!"
