#!/usr/bin/env bash
set -euo pipefail
DATA=/root/autodl-tmp/WMKD_Benchmark_data; PROJECT=/root/autodl-tmp/WMKD_Benchmark; PY=${DATA}/artifacts/ctcc/env/bin/python; set -a; source ${DATA}/credentials/iseal_secret_key.env; set +a
MANIFEST=${DATA}/datasets/iseal/a4/manifest.json; EXPECTED=3e4d0770e744af0ddbbb7d6dc1e6173447d59fbe6076be1f57417992f2b0ff36; ACTUAL=$(sha256sum "${MANIFEST}" | cut -d' ' -f1); test "${ACTUAL}" = "${EXPECTED}"
RUN_ID=iseal_a5_$(date +%Y%m%d_%H%M%S); RUN=${DATA}/runs/iseal/a5/${RUN_ID}; mkdir -p "${RUN}"/{config,logs,status,results,checkpoints,evaluation,reports,manifests}; cp ${PROJECT}/configs/watermark/iseal_experiment_a5.yaml "${RUN}/config/effective_config.yaml"; cp "${MANIFEST}" "${RUN}/manifests/dataset_manifest.json"
export HF_HUB_OFFLINE=1 HF_DATASETS_OFFLINE=1 TRANSFORMERS_OFFLINE=1
setsid nohup "${PY}" ${PROJECT}/scripts/iseal_a2_train.py --config "${RUN}/config/effective_config.yaml" --run-root "${RUN}" --dataset-cache ${DATA}/cache/huggingface/datasets > "${RUN}/logs/training.log" 2>&1 < /dev/null &
echo $! > "${RUN}/status/pid"; printf 'RUN_ID=%s\nRUN_ROOT=%s\nPID=%s\n' "${RUN_ID}" "${RUN}" "$!"
