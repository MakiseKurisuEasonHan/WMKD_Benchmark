#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
EXPECTED_PROJECT_ROOT="/root/autodl-tmp/WMKD_Benchmark"
EXPECTED_DATA_ROOT="/root/autodl-tmp/WMKD_Benchmark_data"

# shellcheck source=../env/autodl_paths.sh
source "${SCRIPT_DIR}/../env/autodl_paths.sh"

fail() {
  printf 'ERROR: %s\n' "$1" >&2
  exit 1
}

[[ "${WMKD_PROJECT_ROOT}" == "${EXPECTED_PROJECT_ROOT}" ]] || fail "unexpected project root"
[[ "${WMKD_DATA_ROOT}" == "${EXPECTED_DATA_ROOT}" ]] || fail "unexpected data root"
[[ -d "${WMKD_PROJECT_ROOT}/.git" ]] || fail "project root is not a Git checkout"
[[ -d "${WMKD_DATA_ROOT}" ]] || fail "data root does not exist"
[[ ! -e "${WMKD_DATA_ROOT}/.git" ]] || fail "data root must not be a Git repository"
[[ ! -L "${WMKD_PROJECT_ROOT}" ]] || fail "project root must not be a symlink"
[[ ! -L "${WMKD_DATA_ROOT}" ]] || fail "data root must not be a symlink"

required_directories=(
  models/base models/watermarked models/distilled
  checkpoints/watermark checkpoints/distillation
  datasets
  cache/huggingface cache/transformers cache/torch cache/other
  runs/watermark runs/distillation runs/benchmark
  generations artifacts manifests logs tmp
)

for relative_path in "${required_directories[@]}"; do
  [[ -d "${WMKD_DATA_ROOT}/${relative_path}" ]] || fail "missing ${relative_path}"
done

for cache_path in "${HF_HOME}" "${HF_HUB_CACHE}" "${TORCH_HOME}"; do
  case "${cache_path}" in
    "${WMKD_DATA_ROOT}"/*) ;;
    *) fail "cache path is outside the WMKD_Benchmark namespace: ${cache_path}" ;;
  esac
done

printf 'AutoDL storage verification passed.\n'
