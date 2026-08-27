#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="/root/autodl-tmp/WMKD_Benchmark"
DATA_ROOT="/root/autodl-tmp/WMKD_Benchmark_data"
EXPERIMENT="${1:?usage: run_pnfp_distillation.sh ba [--dry-run|--approve-formal]}"
MODE="${2:---dry-run}"
case "${EXPERIMENT}" in ba) CONFIG="configs/distillation/pnfp_ba_direct.yaml";; *) echo "Only Ba is authorized; Bb remains prepared/deferred" >&2; exit 2;; esac

export HF_HOME="${DATA_ROOT}/cache/huggingface"
export HF_HUB_CACHE="${DATA_ROOT}/cache/huggingface/hub"
export HF_DATASETS_CACHE="${DATA_ROOT}/cache/datasets"
export TRANSFORMERS_CACHE="${DATA_ROOT}/cache/huggingface/transformers"
export TORCH_EXTENSIONS_DIR="${DATA_ROOT}/cache/torch_extensions"
export TMPDIR="${DATA_ROOT}/tmp"
mkdir -p "${HF_HOME}" "${HF_HUB_CACHE}" "${HF_DATASETS_CACHE}" "${TRANSFORMERS_CACHE}" "${TORCH_EXTENSIONS_DIR}" "${TMPDIR}"
cd "${PROJECT_ROOT}"

python scripts/pnfp_distillation_preflight.py --config "${CONFIG}" --dry-run
if [[ "${MODE}" == "--dry-run" ]]; then
  echo "DRY_RUN_OK: no GPU process or formal artifact was created"
  exit 0
fi
if [[ "${MODE}" != "--approve-formal" ]]; then echo "formal launch requires --approve-formal" >&2; exit 2; fi
if nvidia-smi --query-compute-apps=pid --format=csv,noheader | grep -Eq '[0-9]'; then echo "Refusing launch: another GPU task is active" >&2; exit 1; fi
RUN_ID="pnfp_exp_ba_$(date +%Y%m%d_%H%M%S)"; RUN_DIR="${DATA_ROOT}/runs/pnfp_ba/${RUN_ID}"
mkdir -p "${RUN_DIR}"/{config,logs,status,dataset,checkpoints,evaluation,results}
TEACHER="${DATA_ROOT}/runs/pnfp/pnfp_exp_a_20260827_232033/checkpoints/official/saved_models/a0a21e74c9f8f189aee68a315cb668b4/final_model"
STUDENT="${DATA_ROOT}/models/base/Llama-3.2-1B-Instruct"
FINGERPRINTS="$(find "${DATA_ROOT}/runs/pnfp/pnfp_exp_a_20260827_232033/evaluation" -maxdepth 1 -name 'fingerprint_keys-perinucleus-*.json' -print -quit)"
PYTHON="${DATA_ROOT}/artifacts/pnfp/env/bin/python"; START="$(date --iso-8601=seconds)"
"${PYTHON}" - "${RUN_DIR}/config/runtime_config.json" <<PY
import json,sys
json.dump({"run_id":"${RUN_ID}","git_commit":"$(git rev-parse HEAD)","formal_config":{"samples":20000,"epochs":3,"learning_rate":1e-5,"precision":"bf16","full_parameter":True,"lora":False,"seed":42,"batch_size":8},"paths":{"project_root":"${PROJECT_ROOT}","data_root":"${DATA_ROOT}","teacher":"${TEACHER}","student":"${STUDENT}","fingerprints":"${FINGERPRINTS}","python":"${PYTHON}","run_dir":"${RUN_DIR}"}},open(sys.argv[1],"w"),indent=2)
PY
"${PYTHON}" - "${RUN_DIR}/status/status.json" <<PY
import json,os,sys
json.dump({"run_id":"${RUN_ID}","start_timestamp":"${START}","active_stage":"launching","stage_status":"pending","final_status":"running","pid":None,"runner_pid":None,"exit_code":None,"checkpoint_path":None,"evaluation_status":"pending"},open(sys.argv[1],"w"),indent=2)
PY
COMMAND="export HF_HOME='${HF_HOME}' HF_HUB_CACHE='${HF_HUB_CACHE}' HF_DATASETS_CACHE='${HF_DATASETS_CACHE}' TRANSFORMERS_CACHE='${TRANSFORMERS_CACHE}' TORCH_EXTENSIONS_DIR='${TORCH_EXTENSIONS_DIR}' TMPDIR='${TMPDIR}' WANDB_MODE=disabled TOKENIZERS_PARALLELISM=false; '${PYTHON}' '${PROJECT_ROOT}/scripts/pnfp_ba_pipeline.py' --runtime-config '${RUN_DIR}/config/runtime_config.json' >> '${RUN_DIR}/logs/pipeline.log' 2>&1"
nohup setsid bash -lc "${COMMAND}" >/dev/null 2>&1 < /dev/null & RUNNER_PID="$!"
"${PYTHON}" - "${RUN_DIR}/status/status.json" "${RUNNER_PID}" <<'PY'
import json,sys
p=sys.argv[1]; d=json.load(open(p)); d["detached_mode"]="nohup_setsid"; d["runner_pid"]=int(sys.argv[2]); json.dump(d,open(p,"w"),indent=2)
PY
sleep 2; kill -0 "${RUNNER_PID}" 2>/dev/null || { echo "Detached Ba runner exited; inspect ${RUN_DIR}/logs/pipeline.log" >&2; exit 1; }
printf 'RUN_ID=%s\nRUNNER_PID=%s\nRUN_DIR=%s\nSTATUS=%s\nLOG=%s\n' "${RUN_ID}" "${RUNNER_PID}" "${RUN_DIR}" "${RUN_DIR}/status/status.json" "${RUN_DIR}/logs/pipeline.log"
