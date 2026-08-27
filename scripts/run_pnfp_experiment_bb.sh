#!/usr/bin/env bash
exec "$(dirname "$0")/run_pnfp_distillation.sh" bb "${1:---dry-run}"
