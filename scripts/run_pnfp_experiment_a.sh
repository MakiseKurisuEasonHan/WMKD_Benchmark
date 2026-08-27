#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="/root/autodl-tmp/WMKD_Benchmark"
DATA_ROOT="/root/autodl-tmp/WMKD_Benchmark_data"
ENV_ROOT="${DATA_ROOT}/artifacts/pnfp/env"
SOURCE_ROOT="${DATA_ROOT}/artifacts/pnfp/source"
MODEL_ROOT="${DATA_ROOT}/models/base/Llama-3.2-3B-Instruct"
RUN_ROOT="${DATA_ROOT}/runs/pnfp"

if [[ "${PWD}" != "${PROJECT_ROOT}" ]]; then
  cd "${PROJECT_ROOT}"
fi
if nvidia-smi --query-compute-apps=pid --format=csv,noheader | grep -Eq '[0-9]'; then
  echo "Refusing launch: another GPU compute process is active." >&2
  exit 1
fi

RUN_ID="pnfp_exp_a_$(date +%Y%m%d_%H%M%S)"
RUN_DIR="${RUN_ROOT}/${RUN_ID}"
SESSION="${RUN_ID}"
if [[ -e "${RUN_DIR}" ]] || { command -v tmux >/dev/null && tmux has-session -t "${SESSION}" 2>/dev/null; }; then
  echo "Run collision: ${RUN_ID}" >&2
  exit 1
fi
mkdir -p "${RUN_DIR}"/{config,logs,status,checkpoints,evaluation,results}

export HF_HOME="${DATA_ROOT}/cache/huggingface"
export HF_HUB_CACHE="${DATA_ROOT}/cache/huggingface/hub"
export TRANSFORMERS_CACHE="${DATA_ROOT}/cache/huggingface/transformers"
export HF_DATASETS_CACHE="${DATA_ROOT}/cache/datasets"
export TORCH_EXTENSIONS_DIR="${DATA_ROOT}/cache/torch_extensions"
export TMPDIR="${DATA_ROOT}/tmp"
export WANDB_MODE="disabled"
export TOKENIZERS_PARALLELISM="false"
mkdir -p "$HF_HOME" "$HF_HUB_CACHE" "$TRANSFORMERS_CACHE" "$HF_DATASETS_CACHE" "$TORCH_EXTENSIONS_DIR" "$TMPDIR"

GIT_COMMIT="$(git rev-parse HEAD)"
START="$(date --iso-8601=seconds)"
RUNTIME_CONFIG="${RUN_DIR}/config/runtime_config.json"
python - "${RUNTIME_CONFIG}" <<PY
import json, sys
config = {
  "run_id": "${RUN_ID}", "git_commit": "${GIT_COMMIT}",
  "source_commit": "fdceaba14bd3e89340916a6a40e27c945d48460e",
  "model_id": "meta-llama/Llama-3.2-3B-Instruct",
  "revision": "0cb88a4f764b7a12671c53f0838cd831a0843b95",
  "formal_config": {"fingerprints": 1024, "key_length": 16, "generation_response_length": 16,
    "training_response_length": 1, "epochs": 30, "learning_rate": 5e-5, "weight_decay": 1e-4,
    "batch_size": 8, "gradient_accumulation_steps": 128, "precision": "bf16", "seed": 42,
    "full_parameter": True, "lora": False, "forgetting_regularizer_strength": 0.0,
    "deepspeed_stage": 2, "nucleus_threshold": 0.8, "nucleus_k": 3,
    "use_chat_template": True, "gpu_count": 1},
  "paths": {"project_root": "${PROJECT_ROOT}", "data_root": "${DATA_ROOT}", "model": "${MODEL_ROOT}",
    "official_source": "${SOURCE_ROOT}", "python": "${ENV_ROOT}/bin/python", "run_dir": "${RUN_DIR}"}
}
open(sys.argv[1], "w").write(json.dumps(config, indent=2) + "\n")
PY
python - "${RUN_DIR}/status/status.json" <<PY
import json, os, sys
status = {"run_id": "${RUN_ID}", "detached_mode": None, "tmux_session": None, "launcher_pid": os.getppid(),
          "pid": None, "start_timestamp": "${START}", "active_stage": "launching",
          "stage_status": "pending", "final_status": "running", "exit_code": None,
          "checkpoint_path": None, "evaluation_status": "pending", "failure_reason": None}
open(sys.argv[1], "w").write(json.dumps(status, indent=2) + "\n")
PY
nvidia-smi > "${RUN_DIR}/logs/nvidia_smi_at_launch.txt"
env > "${RUN_DIR}/config/environment.txt"

COMMAND="source '${ENV_ROOT}/bin/activate'; export PATH='${ENV_ROOT}/bin':\$PATH HF_HOME='${HF_HOME}' HF_HUB_CACHE='${HF_HUB_CACHE}' TRANSFORMERS_CACHE='${TRANSFORMERS_CACHE}' HF_DATASETS_CACHE='${HF_DATASETS_CACHE}' TORCH_EXTENSIONS_DIR='${TORCH_EXTENSIONS_DIR}' TMPDIR='${TMPDIR}' WANDB_MODE=disabled TOKENIZERS_PARALLELISM=false; '${ENV_ROOT}/bin/python' '${PROJECT_ROOT}/scripts/pnfp_experiment_a_pipeline.py' --runtime-config '${RUNTIME_CONFIG}' >> '${RUN_DIR}/logs/pipeline.log' 2>&1"
if command -v tmux >/dev/null; then
  tmux new-session -d -s "${SESSION}" "bash -lc \"${COMMAND}\""
  DETACHED_MODE="tmux"
  DETACHED_PID=""
else
  nohup setsid bash -lc "${COMMAND}" >/dev/null 2>&1 < /dev/null &
  DETACHED_PID="$!"
  DETACHED_MODE="nohup_setsid"
fi
python - "${RUN_DIR}/status/status.json" "${DETACHED_MODE}" "${DETACHED_PID}" "${SESSION}" <<'PY'
import json, sys
path, mode, pid, session = sys.argv[1:]
status = json.load(open(path))
status["detached_mode"] = mode
status["detached_pid"] = int(pid) if pid else None
status["tmux_session"] = session if mode == "tmux" else None
open(path, "w").write(json.dumps(status, indent=2) + "\n")
PY
sleep 2
if [[ "${DETACHED_MODE}" == "tmux" ]]; then
  tmux has-session -t "${SESSION}" 2>/dev/null || { echo "Detached tmux session exited; inspect ${RUN_DIR}/logs/pipeline.log" >&2; exit 1; }
else
  kill -0 "${DETACHED_PID}" 2>/dev/null || { echo "Detached process exited; inspect ${RUN_DIR}/logs/pipeline.log" >&2; exit 1; }
fi
printf 'RUN_ID=%s\nDETACHED_MODE=%s\nSESSION=%s\nPID=%s\nRUN_DIR=%s\nSTATUS=%s\nLOG=%s\n' "$RUN_ID" "$DETACHED_MODE" "${SESSION:-}" "${DETACHED_PID:-}" "$RUN_DIR" "${RUN_DIR}/status/status.json" "${RUN_DIR}/logs/pipeline.log"
