#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="/root/autodl-tmp/WMKD_Benchmark"
DATA_ROOT="/root/autodl-tmp/WMKD_Benchmark_data"
EXPERIMENT="${1:?usage: run_pnfp_distillation.sh ba|bb [--dry-run|--approve-formal]}"
MODE="${2:---dry-run}"
case "${EXPERIMENT}" in ba) CONFIG="configs/distillation/pnfp_ba_direct.yaml";; bb) CONFIG="configs/distillation/pnfp_bb_up.yaml";; *) echo "experiment must be ba or bb" >&2; exit 2;; esac

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
echo "Formal orchestration is intentionally locked until the preparation commit is deployed and separately approved." >&2
exit 3
