# WMKD_Benchmark Email Notifications

WMKD_Benchmark uses best-effort Gmail SMTP notifications for formal experiment lifecycle events. Notification failure never changes scientific experiment status.

## Configuration

- Primary SMTP: Gmail SMTP over SSL, `smtp.gmail.com:465`, three attempts
- Fallback SMTP: `smtp.gmail.com:587` with STARTTLS, up to two attempts after all 465 attempts fail
- Per-attempt timeout: 45 seconds; bounded backoff is 5 and 15 seconds for 465, then 5 seconds for 587
- Sender: `EasonHanYichen@gmail.com`
- Recipient: `21672330@students.latrobe.edu.au`
- Secret file: `/root/autodl-tmp/WMKD_Benchmark_data/secrets/email.env`

Google App Passwords require an eligible Google account with two-step verification. Do not paste the App Password into Git, source, configuration, documentation, logs, or a Codex conversation.

On AutoDL, configure the credential interactively with hidden input:

```bash
cd /root/autodl-tmp/WMKD_Benchmark
/root/autodl-tmp/WMKD_Benchmark_data/artifacts/pnfp/env/bin/python scripts/setup_email_notifications.py
```

The helper writes the file outside the Git checkout with mode `600` and prints no secret. To rotate it, rerun the helper. To disable and delete the credential, remove only the exact project-owned file:

```bash
rm /root/autodl-tmp/WMKD_Benchmark_data/secrets/email.env
```

## Test and use

After configuration, send exactly one independent test:

```bash
/root/autodl-tmp/WMKD_Benchmark_data/artifacts/pnfp/env/bin/python scripts/notify_experiment.py \
  --event STARTED \
  --experiment "Email notification test" \
  --run-id "email_test_$(date +%Y%m%d_%H%M%S)" \
  --stage test \
  --subject "[WMKD] Email notification test" \
  --message "WMKD email notification test"
```

Future runners call `notify_experiment.py` for `STARTED`, `COMPLETED`, and `FAILED`. A read-only watcher can additionally classify an unexpectedly disappeared detached process as `INTERRUPTED`. Notification state is stored outside Git under `/root/autodl-tmp/WMKD_Benchmark_data/notifications/<run_id>/notification_state.json`; each `run_id + event` is sent at most once.

Only confirmed SMTP success marks an event delivered. If every immediate attempt for `COMPLETED`, `FAILED`, or `INTERRUPTED` fails, a non-secret record is retained under `/root/autodl-tmp/WMKD_Benchmark_data/notifications/pending/<run_id>__<event>.json`. Retry queued events without touching experiment state:

```bash
/root/autodl-tmp/WMKD_Benchmark_data/artifacts/pnfp/env/bin/python \
  scripts/retry_pending_notifications.py \
  --run-id pnfp_exp_a_20260827_232033
```

Successful retries move the pending record to `notifications/delivered/`. Failure JSON and pending records contain transport, attempt and phase information but never credentials. SMTP delivery remains best-effort and cannot change scientific experiment status.

The current PN-FP run is not restarted or modified for email support. Its optional watcher must only be launched after the App Password is configured.

## Current standalone deployment

For PN-FP run `pnfp_exp_a_20260827_232033`, the original utilities were deployed independently under `/root/autodl-tmp/WMKD_Benchmark_data/notification_tools/`. This did not modify the running process. The standalone setup command is:

```bash
python3 /root/autodl-tmp/WMKD_Benchmark_data/notification_tools/setup_email_notifications.py
```

The credential was configured in the external mode-600 secret file and independent test `email_test_20260827_233957` succeeded. Read-only watcher PID 89850 detected the terminal COMPLETED state, but its single original SMTP_SSL attempt ended in `TimeoutError: timed out`. The experiment was unaffected. The hardened notifier queues the legitimate missed COMPLETED event for bounded retry; no retrospective STARTED event is generated.

If its success state is still false after AutoDL access returns, deploy the hardened scripts and retry the one legitimate historical event with:

```bash
cd /root/autodl-tmp/WMKD_Benchmark
/root/autodl-tmp/WMKD_Benchmark_data/artifacts/pnfp/env/bin/python scripts/notify_experiment.py \
  --event COMPLETED \
  --experiment "PN-FP Experiment A" \
  --run-id pnfp_exp_a_20260827_232033 \
  --stage completed \
  --status completed \
  --exit-code 0 \
  --status-file /root/autodl-tmp/WMKD_Benchmark_data/runs/pnfp/pnfp_exp_a_20260827_232033/status/status.json \
  --log-path /root/autodl-tmp/WMKD_Benchmark_data/runs/pnfp/pnfp_exp_a_20260827_232033/logs \
  --message $'Watermarked detection: 1019 / 1024 = 99.5117%\nBase detection: 1 / 1024 = 0.0977%\nPaired difference: 99.4141 percentage points\nReload validation: passed\nScientific judgement: PN-FP core reproduction successful'
```

If delivery still fails, this command creates the pending record automatically. Running `retry_pending_notifications.py --run-id pnfp_exp_a_20260827_232033` later is safe and duplicate-aware.
