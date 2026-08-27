# WMKD_Benchmark Email Notifications

WMKD_Benchmark uses best-effort Gmail SMTP notifications for formal experiment lifecycle events. Notification failure never changes scientific experiment status.

## Configuration

- SMTP: Gmail SMTP over SSL, `smtp.gmail.com:465`
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

The current PN-FP run is not restarted or modified for email support. Its optional watcher must only be launched after the App Password is configured.
