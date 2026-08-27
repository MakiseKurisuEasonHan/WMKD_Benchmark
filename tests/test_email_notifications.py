import argparse
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from scripts import notify_experiment
from scripts import retry_pending_notifications
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
        smtp_ssl.return_value = mock.MagicMock()
        with tempfile.TemporaryDirectory() as root, mock.patch.dict(
            os.environ, {"WMKD_GMAIL_APP_PASSWORD": "not-a-real-secret"}, clear=True
        ), mock.patch("scripts.notify_experiment.ssl.create_default_context", return_value=mock.Mock()):
            args = args_for(root)
            self.assertEqual(notify_experiment.notify(args), 0)
            self.assertEqual(notify_experiment.notify(args), 0)
            self.assertEqual(smtp_ssl.return_value.send_message.call_count, 1)

    def test_retry_after_timeout(self):
        message = mock.Mock()
        ssl_sender = mock.Mock(side_effect=[TimeoutError("timed out"), None])
        with mock.patch("scripts.notify_experiment._send_ssl", ssl_sender), \
             mock.patch("scripts.notify_experiment._send_starttls") as fallback:
            transport, failures = notify_experiment.deliver_with_retry(
                message, "sender", "password", 45, sleep=lambda _: None
            )
        self.assertEqual(transport, "ssl465")
        self.assertEqual(len(failures), 1)
        fallback.assert_not_called()

    def test_fallback_after_primary_exhausted(self):
        with mock.patch("scripts.notify_experiment._send_ssl", side_effect=TimeoutError("timeout")) as primary, \
             mock.patch("scripts.notify_experiment._send_starttls", return_value=None) as fallback:
            transport, failures = notify_experiment.deliver_with_retry(
                mock.Mock(), "sender", "password", 45, sleep=lambda _: None
            )
        self.assertEqual(transport, "starttls587")
        self.assertEqual(primary.call_count, 3)
        self.assertEqual(fallback.call_count, 1)
        self.assertEqual(len(failures), 3)

    def test_failed_terminal_send_creates_pending_without_secret(self):
        with tempfile.TemporaryDirectory() as root, mock.patch.dict(
            os.environ, {"WMKD_GMAIL_APP_PASSWORD": "not-a-real-secret"}, clear=True
        ), mock.patch("scripts.notify_experiment.deliver_with_retry", side_effect=TimeoutError("timed out")):
            args = args_for(root, event="COMPLETED")
            self.assertEqual(notify_experiment.notify(args), 0)
            pending = notify_experiment.pending_path_for(args)
            self.assertTrue(pending.exists())
            text = pending.read_text()
            self.assertNotIn("not-a-real-secret", text)
            self.assertIn("COMPLETED", text)

    def test_pending_retry_success_moves_record_and_marks_state(self):
        with tempfile.TemporaryDirectory() as root, mock.patch.dict(
            os.environ, {"WMKD_GMAIL_APP_PASSWORD": "not-a-real-secret"}, clear=True
        ):
            args = args_for(root, event="COMPLETED")
            message = notify_experiment.build_message(args, "sender@example.com", "recipient@example.com")
            notify_experiment.persist_pending(args, message, [{"error": "timeout"}])
            with mock.patch("scripts.notify_experiment.deliver_with_retry", return_value=("ssl465", [])), \
                 mock.patch("sys.argv", ["retry", "--state-root", str(Path(root) / "state"),
                                           "--secret-file", str(Path(root) / "missing.env"), "--run-id", "test_run"]):
                retry_pending_notifications.main()
            state = notify_experiment.read_state(notify_experiment.state_path_for(args))
            self.assertTrue(state["COMPLETED"])
            self.assertFalse(notify_experiment.pending_path_for(args).exists())
            self.assertTrue((Path(root) / "state" / "delivered" / "test_run__COMPLETED.json").exists())

    def test_secret_never_appears_in_failure_output(self):
        with tempfile.TemporaryDirectory() as root, mock.patch.dict(
            os.environ, {"WMKD_GMAIL_APP_PASSWORD": "super-secret-value"}, clear=True
        ), mock.patch("scripts.notify_experiment.deliver_with_retry", side_effect=TimeoutError("timed out")), \
             mock.patch("builtins.print") as printer:
            notify_experiment.notify(args_for(root, event="FAILED"))
            self.assertNotIn("super-secret-value", " ".join(str(call) for call in printer.call_args_list))

    def test_watcher_terminal_classification(self):
        self.assertEqual(watch_experiment_notification.classify({"final_status": "completed"}), "COMPLETED")
        self.assertEqual(watch_experiment_notification.classify({"final_status": "failed"}), "FAILED")


if __name__ == "__main__":
    unittest.main()
