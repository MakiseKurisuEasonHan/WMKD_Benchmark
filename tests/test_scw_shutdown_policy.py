import json
import tempfile
import unittest
from pathlib import Path

from scripts.scw_shutdown_policy import apply_shutdown_policy


class ShutdownDisabledTests(unittest.TestCase):
    def test_all_terminal_states_require_manual_shutdown(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            policy = root / "policy.json"
            policy.write_text(json.dumps({"auto_shutdown_enabled": False}), encoding="utf-8")
            for terminal_state in ("SUCCESS", "FAILED", "BLOCKED"):
                run_root = root / terminal_state
                run_root.mkdir()
                status = {"state": terminal_state, "terminal": True}
                command = apply_shutdown_policy(
                    status,
                    run_root,
                    {"WMKD_AUTO_SHUTDOWN_ENABLED": "true"},
                    policy,
                )
                self.assertIsNone(command)
                self.assertFalse(status["auto_shutdown_enabled"])
                self.assertFalse(status["shutdown_requested"])
                self.assertFalse(status["shutdown_command_issued"])
                self.assertEqual(status["shutdown_method"], "SHUTDOWN_REQUIRED_MANUAL")
                self.assertTrue((run_root / "SHUTDOWN_REQUIRED_MANUAL").is_file())


if __name__ == "__main__":
    unittest.main()
