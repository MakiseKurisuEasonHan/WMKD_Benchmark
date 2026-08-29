#!/usr/bin/env bash
set -euo pipefail
CODE_ROOT="${CODE_ROOT:-/root/autodl-tmp/WMKD_Benchmark}"
DATA_ROOT="/root/autodl-tmp/WMKD_Benchmark_data"
PY="${DATA_ROOT}/artifacts/evertracer/env/bin/python"
CONFIG="${CODE_ROOT}/configs/distillation/evertracer_ba_direct.yaml"
MODE="${1:---dry-run}"
export HF_HOME="${DATA_ROOT}/cache/huggingface" HF_HUB_CACHE="${DATA_ROOT}/cache/huggingface/hub" HF_DATASETS_CACHE="${DATA_ROOT}/cache/huggingface/datasets" TRANSFORMERS_OFFLINE=1 HF_HUB_OFFLINE=1 HF_DATASETS_OFFLINE=1 TMPDIR="${DATA_ROOT}/tmp" WANDB_MODE=disabled TOKENIZERS_PARALLELISM=false
"${PY}" "${CODE_ROOT}/scripts/evertracer_ba_preflight.py" --config "${CONFIG}"
[[ "${MODE}" == "--dry-run" ]] && { echo DRY_RUN_OK; exit 0; }
[[ "${MODE}" == "--approve-formal" ]] || { echo "use --approve-formal" >&2; exit 2; }
[[ -z "$(nvidia-smi --query-compute-apps=pid --format=csv,noheader)" ]] || { echo "GPU busy" >&2; exit 1; }
RUN_ID="evertracer_ba_$(date +%Y%m%d_%H%M%S)";RUN="${DATA_ROOT}/runs/evertracer_ba/${RUN_ID}";mkdir -p "${RUN}"/{config,logs,status,dataset,checkpoints,metrics,reports}
cp "${CONFIG}" "${RUN}/config/formal_config.yaml"
"${PY}" - "${RUN}/config/runtime.json" <<PY
import json,sys
json.dump({"git_commit":"$(git -C "${CODE_ROOT}" rev-parse HEAD)","code_root":"${CODE_ROOT}","teacher":"${DATA_ROOT}/runs/evertracer/evertracer_a_20260828_223155/checkpoints/target_merged","reference":"${DATA_ROOT}/runs/evertracer/evertracer_a_20260828_223155/checkpoints/reference_merged","base":"${DATA_ROOT}/models/base/Llama-3.2-3B-Instruct","neighborhoods":"${DATA_ROOT}/runs/evertracer/evertracer_a_20260828_223155_cont1/artifacts/frozen_neighborhoods.jsonl","prior_a_summary":"${DATA_ROOT}/runs/evertracer/evertracer_a_20260828_223155_cont2/reports/summary.json"},open(sys.argv[1],"w"),indent=2)
PY
"${PY}" - "${RUN}/status/status.json" <<PY
import json,sys,datetime
json.dump({"run_id":"${RUN_ID}","status":"PENDING","stage":"LAUNCHING","start_time":datetime.datetime.now().astimezone().isoformat(),"exit_code":None,"completed_stages":[]},open(sys.argv[1],"w"),indent=2)
PY
setsid nohup "${PY}" "${CODE_ROOT}/scripts/evertracer_ba_pipeline.py" --config "${RUN}/config/formal_config.yaml" --run-dir "${RUN}" --code-root "${CODE_ROOT}" --python "${PY}" > "${RUN}/logs/pipeline.log" 2>&1 < /dev/null & PID=$!
"${PY}" - "${RUN}/status/status.json" "${PID}" <<'PY'
import json,sys
p=sys.argv[1];d=json.load(open(p));d["runner_pid"]=int(sys.argv[2]);d["detached_mode"]="setsid_nohup";json.dump(d,open(p,"w"),indent=2)
PY
sleep 2;kill -0 "${PID}";printf 'RUN_ID=%s\nRUNNER_PID=%s\nRUN_DIR=%s\n' "${RUN_ID}" "${PID}" "${RUN}"
