import argparse
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from scripts import notify_experiment
from scripts import watch_experiment_notification


def args_for(root, event="STARTED"):
    return argparse.Namespace(
        event=event, experiment="PN-FP Experiment A", run_id="test_run", stage="training",
        message="test", pid=None, exit_code=None, status="running", log_path="/tmp/log",
        status_file="/tmp/status", error_summary=None, time="2026-08-28T00:00:00+10:00",
        host="test-host", subject=None, secret_file=str(Path(root) / "missing.env"),
        state_root=str(Path(root) / "state"), state_file=None, failure_record=None,
        timeout=1.0, dry_run=False,
    )


class NotificationTests(unittest.TestCase):
    def test_missing_password_is_nonfatal(self):
        with tempfile.TemporaryDirectory() as root, mock.patch.dict(os.environ, {}, clear=True):
            self.assertEqual(notify_experiment.notify(args_for(root)), 0)

    def test_message_contains_operational_fields_not_password(self):
        args = args_for("/tmp")
        message = notify_experiment.build_message(args, "sender@example.com", "recipient@example.com")
        body = message.get_content()
        self.assertIn("PN-FP Experiment A", body)
        self.assertIn("training", body)
        self.assertNotIn("WMKD_GMAIL_APP_PASSWORD", body)

    @mock.patch("scripts.notify_experiment.smtplib.SMTP_SSL")
    def test_duplicate_event_sent_once(self, smtp_ssl):
        smtp_ssl.return_value.__enter__.return_value = mock.Mock()
        with tempfile.TemporaryDirectory() as root, mock.patch.dict(
            os.environ, {"WMKD_GMAIL_APP_PASSWORD": "not-a-real-secret"}, clear=True
        ), mock.patch("scripts.notify_experiment.ssl.create_default_context", return_value=mock.Mock()):
            args = args_for(root)
            self.assertEqual(notify_experiment.notify(args), 0)
            self.assertEqual(notify_experiment.notify(args), 0)
            self.assertEqual(smtp_ssl.return_value.__enter__.return_value.send_message.call_count, 1)

    def test_watcher_terminal_classification(self):
        self.assertEqual(watch_experiment_notification.classify({"final_status": "completed"}), "COMPLETED")
        self.assertEqual(watch_experiment_notification.classify({"final_status": "failed"}), "FAILED")


if __name__ == "__main__":
    unittest.main()
