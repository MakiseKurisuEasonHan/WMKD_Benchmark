#!/bin/bash
# Independent of the campaign. Restart only this CPU safety supervisor on crash.
cd /root/autodl-tmp/WMKD_Benchmark || exit 1
while true; do
  /root/miniconda3/bin/python scripts/awm_7b_night_watchdog.py >> results/awm/scale_7b/night_watchdog.log 2>&1
  rc=$?
  if [ "$rc" = 0 ]; then exit 0; fi
  sleep 30
done
