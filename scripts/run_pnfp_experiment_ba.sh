#!/usr/bin/env bash
exec "$(dirname "$0")/run_pnfp_distillation.sh" ba "${1:---dry-run}"
