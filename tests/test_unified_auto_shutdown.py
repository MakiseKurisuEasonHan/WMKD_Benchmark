import unittest
from scripts.unified_auto_shutdown import evaluate


class UnifiedAutoShutdownTests(unittest.TestCase):
    def base(self):
        return dict(state={"status":"READY_FOR_MASTER_CLOSURE","methods":{"scw":{"status":"COMPLETE"},"ctcc_bb2":{"status":"BLOCKED"}}},active_project_pids=[],gpu_processes=[],git={"clean":True,"ahead":0,"behind":0,"local_head":"a","github_head":"a","autodl_head":"a"},full_logs_ok=True,index_ok=True,archives_ok=True,master_report_ok=True,pending_continuation=False)
    def test_terminal_complete_blocked_mix_allowed(self): self.assertTrue(evaluate(**self.base())["eligibility"])
    def test_running_never_shutdown(self):
        x=self.base(); x["state"]["methods"]["ctcc_bb2"]["status"]="RUNNING"; self.assertFalse(evaluate(**x)["eligibility"])
    def test_needs_user_action_never_shutdown(self):
        x=self.base(); x["state"]["methods"]["ctcc_bb2"]["status"]="NEEDS_USER_ACTION"; self.assertFalse(evaluate(**x)["eligibility"])
    def test_gpu_prevents_shutdown(self):
        x=self.base(); x["gpu_processes"]=[{"pid":1}]; self.assertFalse(evaluate(**x)["eligibility"])
    def test_dirty_git_prevents_shutdown(self):
        x=self.base(); x["git"]["clean"]=False; self.assertFalse(evaluate(**x)["eligibility"])
    def test_missing_log_or_report_prevents_shutdown(self):
        for key in ("full_logs_ok","master_report_ok"):
            x=self.base(); x[key]=False; self.assertFalse(evaluate(**x)["eligibility"])


if __name__ == "__main__": unittest.main()
