#!/usr/bin/env bash
set -euo pipefail
DATA=/root/autodl-tmp/WMKD_Benchmark_data; PROJECT=/root/autodl-tmp/WMKD_Benchmark; PY=${DATA}/artifacts/ctcc/env/bin/python; set -a; source ${DATA}/credentials/iseal_secret_key.env; set +a
MANIFEST=${DATA}/datasets/iseal/a6/manifest.json; EXPECTED=a68fff13eb0add1f64634e50235a232c3f00fcdcf5d543db942e40a5f3b7bbe9; ACTUAL=$("${PY}" -c 'import json,sys; print(json.load(open(sys.argv[1], encoding="utf-8"))["manifest_sha256"])' "${MANIFEST}"); test "${ACTUAL}" = "${EXPECTED}"
RUN_ID=iseal_a6_$(date +%Y%m%d_%H%M%S); RUN=${DATA}/runs/iseal/a6/${RUN_ID}; mkdir -p "${RUN}"/{config,logs,status,results,checkpoints,evaluation,reports,manifests}; cp ${PROJECT}/configs/watermark/iseal_experiment_a6.yaml "${RUN}/config/effective_config.yaml"; cp "${MANIFEST}" "${RUN}/manifests/dataset_manifest.json"
export HF_HUB_OFFLINE=1 HF_DATASETS_OFFLINE=1 TRANSFORMERS_OFFLINE=1
setsid nohup "${PY}" ${PROJECT}/scripts/iseal_a2_train.py --config "${RUN}/config/effective_config.yaml" --run-root "${RUN}" --dataset-cache ${DATA}/cache/huggingface/datasets > "${RUN}/logs/training.log" 2>&1 < /dev/null &
echo $! > "${RUN}/status/pid"; printf 'RUN_ID=%s\nRUN_ROOT=%s\nPID=%s\n' "${RUN_ID}" "${RUN}" "$!"
