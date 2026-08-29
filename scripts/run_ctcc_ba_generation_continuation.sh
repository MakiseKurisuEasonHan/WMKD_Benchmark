#!/usr/bin/env bash
set -euo pipefail
CODE_ROOT="${CODE_ROOT:-/root/autodl-tmp/WMKD_Benchmark}"; DATA_ROOT="/root/autodl-tmp/WMKD_Benchmark_data"; PY="${DATA_ROOT}/artifacts/ctcc/env/bin/python"; CONFIG="${CODE_ROOT}/configs/distillation/ctcc_ba_direct.yaml"; PARENT_ID="ctcc_ba_generation_20260829_195943"; PARENT="${DATA_ROOT}/runs/ctcc_ba/${PARENT_ID}"; RUN_ID="${PARENT_ID}_cont1"; RUN="${DATA_ROOT}/runs/ctcc_ba/${RUN_ID}"
[[ "${1:---dry-run}" == "--approve-formal" ]] || exit 2
[[ ! -e "${RUN}" ]] || { echo RUN_PATH_COLLISION >&2; exit 1; }
[[ -z "$(nvidia-smi --query-compute-apps=pid --format=csv,noheader)" ]] || { echo GPU_BUSY >&2; exit 1; }
mkdir -p "${RUN}"/{config,logs,status,dataset,metrics}; cp "${CONFIG}" "${RUN}/config/formal_config.yaml"
"${PY}" - "${RUN}/status/status.json" "${RUN_ID}" "${PARENT_ID}" <<'PY'
import datetime,json,sys
json.dump({"run_id":sys.argv[2],"parent_run_id":sys.argv[3],"continuation_type":"infrastructure_only","status":"PENDING","stage":"LAUNCHING","start_time":datetime.datetime.now().astimezone().isoformat(),"exit_code":None,"completed_stages":[],"student_run_id":None},open(sys.argv[1],"w"),indent=2)
PY
setsid nohup "${PY}" "${CODE_ROOT}/scripts/ctcc_ba_generation_continuation.py" --config "${RUN}/config/formal_config.yaml" --run-dir "${RUN}" --parent-run "${PARENT}" --code-root "${CODE_ROOT}" --python "${PY}" > "${RUN}/logs/pipeline.log" 2>&1 < /dev/null & PID=$!
"${PY}" - "${RUN}/status/status.json" "${PID}" <<'PY'
import json,sys
p=sys.argv[1];d=json.load(open(p));d.update({"runner_pid":int(sys.argv[2]),"detached_mode":"setsid_nohup"});json.dump(d,open(p,"w"),indent=2)
PY
sleep 2; kill -0 "${PID}"; printf 'RUN_ID=%s\nRUNNER_PID=%s\nRUN_DIR=%s\n' "${RUN_ID}" "${PID}" "${RUN}"
