#!/usr/bin/env bash
set -euo pipefail
CODE_ROOT="${CODE_ROOT:-/root/autodl-tmp/WMKD_Benchmark}";DATA_ROOT="/root/autodl-tmp/WMKD_Benchmark_data";PY="${DATA_ROOT}/artifacts/ctcc/env/bin/python";CONFIG="${CODE_ROOT}/configs/distillation/ctcc_ba_direct.yaml";GEN="${DATA_ROOT}/runs/ctcc_ba/ctcc_ba_generation_20260829_195943_cont1"
[[ "${1:---dry-run}" == "--approve-formal" ]] || exit 2
if nvidia-smi --query-compute-apps=pid --format=csv,noheader | grep -q .;then echo GPU_BUSY >&2;exit 1;fi
RUN_ID="ctcc_ba_$(date +%Y%m%d_%H%M%S)";RUN="${DATA_ROOT}/runs/ctcc_ba/${RUN_ID}";mkdir -p "${RUN}"/{config,logs,status,metrics,checkpoints};cp "${CONFIG}" "${RUN}/config/formal_config.yaml"
"${PY}" - "${RUN}/status/status.json" "${RUN_ID}" <<'PY'
import datetime,json,sys
json.dump({"run_id":sys.argv[2],"experiment":"CTCC Ba","stage_scope":"student_training_only","status":"PENDING","stage":"LAUNCHING","start_time":datetime.datetime.now().astimezone().isoformat(),"exit_code":None,"completed_stages":[],"evaluation_status":"NOT_STARTED"},open(sys.argv[1],"w"),indent=2)
PY
setsid nohup "${PY}" "${CODE_ROOT}/scripts/ctcc_ba_student_training_pipeline.py" --config "${RUN}/config/formal_config.yaml" --run-dir "${RUN}" --generation-run "${GEN}" --code-root "${CODE_ROOT}" --python "${PY}" > "${RUN}/logs/pipeline.log" 2>&1 < /dev/null &PID=$!
"${PY}" - "${RUN}/status/status.json" "${PID}" <<'PY'
import json,sys
p=sys.argv[1];d=json.load(open(p));d.update({"runner_pid":int(sys.argv[2]),"detached_mode":"setsid_nohup"});json.dump(d,open(p,"w"),indent=2)
PY
sleep 2;kill -0 "${PID}";printf 'RUN_ID=%s\nRUNNER_PID=%s\nRUN_DIR=%s\n' "${RUN_ID}" "${PID}" "${RUN}"
