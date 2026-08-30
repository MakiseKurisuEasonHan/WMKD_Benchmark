#!/usr/bin/env bash
set -euo pipefail
CODE=/root/autodl-tmp/WMKD_Benchmark;DATA=/root/autodl-tmp/WMKD_Benchmark_data;PY=${DATA}/artifacts/ctcc/env/bin/python;CONFIG=${CODE}/configs/distillation/iseal_ba_direct.yaml;: "${GEN:?GEN must be completed iSeal Ba generation run}"
[[ "${1:---dry-run}" == "--approve-formal" ]] || exit 2; [[ -z "$(nvidia-smi --query-compute-apps=pid --format=csv,noheader)" ]] || { echo GPU_BUSY >&2; exit 1; }
RUN_ID=iseal_ba_$(date +%Y%m%d_%H%M%S);RUN=${DATA}/runs/iseal_ba/${RUN_ID};mkdir -p "${RUN}"/{config,logs,status,metrics,checkpoints,evaluation,reports};cp "${CONFIG}" "${RUN}/config/formal_config.yaml"
"${PY}" -c 'import datetime,json,sys;json.dump({"run_id":sys.argv[2],"experiment":"iSeal Ba","status":"PENDING","stage":"LAUNCHING","start_time":datetime.datetime.now().astimezone().isoformat(),"exit_code":None,"completed_stages":[],"evaluation_status":"NOT_STARTED"},open(sys.argv[1],"w"),indent=2)' "${RUN}/status/status.json" "${RUN_ID}"
setsid nohup "${PY}" "${CODE}/scripts/iseal_ba_student_training_pipeline.py" --config "${RUN}/config/formal_config.yaml" --run-dir "${RUN}" --generation-run "${GEN}" --code-root "${CODE}" --python "${PY}" > "${RUN}/logs/pipeline.log" 2>&1 < /dev/null &PID=$!;echo "${PID}" > "${RUN}/status/pid";sleep 2;kill -0 "${PID}";printf 'RUN_ID=%s\nPID=%s\nRUN=%s\n' "${RUN_ID}" "${PID}" "${RUN}"
