#!/usr/bin/env bash
set -euo pipefail
PROJECT=/root/autodl-tmp/WMKD_Benchmark
DATA=/root/autodl-tmp/WMKD_Benchmark_data
ENV=$DATA/artifacts/pnfp/env
SOURCE=$DATA/artifacts/pnfp/source
MODEL=$DATA/models/base/Llama-3.2-3B-Instruct
A1=$DATA/runs/pnfp/pnfp_exp_a_20260827_232033
FP=$(find "$A1/evaluation" -maxdepth 1 -name 'fingerprint_keys-perinucleus-*.json' | head -1)
A1_CHECKPOINT=$(dirname "$(find "$A1/checkpoints" -name config.json | head -1)")
BENIGN=$DATA/artifacts/pnfp/a2/official_data/benign.json
[[ -z "$(nvidia-smi --query-compute-apps=pid --format=csv,noheader)" ]] || { echo 'GPU busy' >&2; exit 1; }
RUN_ID=pnfp_exp_a2_$(date +%Y%m%d_%H%M%S)
RUN=$DATA/runs/pnfp/$RUN_ID
[[ ! -e "$RUN" ]] || { echo 'run collision' >&2; exit 1; }
mkdir -p "$RUN"/{config,logs,status,checkpoints,evaluation,results}
START=$(date --iso-8601=seconds)
python3 - "$RUN/config/runtime_config.json" <<PY
import json,sys
c={"run_id":"$RUN_ID","source_commit":"fdceaba14bd3e89340916a6a40e27c945d48460e","model_revision":"0cb88a4f764b7a12671c53f0838cd831a0843b95","benign_sha256":"bd18da3b5a56002822a9789d83667452597ccc16979df3277fe2d04ff10a0201","fingerprints_sha256":"922d3aec3b6bbac62dcdcf617b41e08a1384e7875db77aa6c4f9a278e03a8612","formal_config":{"fingerprints":1024,"key_length":16,"generation_response_length":16,"training_response_length":1,"epochs":30,"learning_rate":5e-5,"weight_decay":1e-4,"batch_size":8,"precision":"bf16","seed":42,"full_parameter":True,"lora":False,"lambda_wa":0.75,"beta_dm":0.25,"deepspeed_stage":2},"paths":{"project_root":"$PROJECT","data_root":"$DATA","run_dir":"$RUN","python":"$ENV/bin/python","official_source":"$SOURCE","model":"$MODEL","fingerprints":"$FP","benign_data":"$BENIGN","a1_checkpoint":"$A1_CHECKPOINT","a1_summary":"$A1/results/summary.json"}}
open(sys.argv[1],'w').write(json.dumps(c,indent=2)+'\n')
PY
python3 - "$RUN/status/status.json" <<PY
import json,sys
s={"run_id":"$RUN_ID","detached_mode":"nohup_setsid","detached_pid":None,"pid":None,"start_timestamp":"$START","active_stage":"launching","stage_status":"pending","final_status":"running","exit_code":None,"checkpoint_path":None,"evaluation_status":"pending","failure_reason":None,"email_started_status":"pending"}
open(sys.argv[1],'w').write(json.dumps(s,indent=2)+'\n')
PY
export PATH="$ENV/bin:$PATH" HF_HOME=$DATA/cache/huggingface TRANSFORMERS_CACHE=$DATA/cache/huggingface/transformers HF_DATASETS_CACHE=$DATA/cache/datasets TORCH_EXTENSIONS_DIR=$DATA/cache/torch_extensions TMPDIR=$DATA/tmp WANDB_MODE=disabled TOKENIZERS_PARALLELISM=false
nohup setsid bash -lc "export PATH='$ENV/bin':\$PATH HF_HOME='$HF_HOME' TRANSFORMERS_CACHE='$TRANSFORMERS_CACHE' HF_DATASETS_CACHE='$HF_DATASETS_CACHE' TORCH_EXTENSIONS_DIR='$TORCH_EXTENSIONS_DIR' TMPDIR='$TMPDIR' WANDB_MODE=disabled TOKENIZERS_PARALLELISM=false; '$ENV/bin/python' '$PROJECT/scripts/pnfp_experiment_a2_pipeline.py' --runtime-config '$RUN/config/runtime_config.json' >> '$RUN/logs/pipeline.log' 2>&1" >/dev/null 2>&1 < /dev/null &
DETACHED=$!
python3 - "$RUN/status/status.json" "$DETACHED" <<'PY'
import json,sys
p=sys.argv[1]; s=json.load(open(p)); s['detached_pid']=int(sys.argv[2]); open(p,'w').write(json.dumps(s,indent=2)+'\n')
PY
sleep 3
kill -0 "$DETACHED" 2>/dev/null || { echo "launcher exited; see $RUN/logs/pipeline.log" >&2; exit 1; }
echo "RUN_ID=$RUN_ID"
echo "DETACHED_PID=$DETACHED"
echo "RUN_DIR=$RUN"
