import json, unittest
from pathlib import Path
from scripts.generate_teacher_qa_formal import consumed_prompt_indices, recover_next_prompt_index

class TestSCWBaProtocol(unittest.TestCase):
    def test_fixed_config(self):
        c=json.loads(Path("configs/distillation/scw_ba_direct.yaml").read_text())
        self.assertEqual(c["dataset"]["final_samples"],20000)
        self.assertEqual(c["training"],{"epochs":3,"learning_rate":1e-5,"precision":"bf16","full_parameter":True,"lora":False,"batch_size":8,"gradient_accumulation_steps":1,"max_length":1024,"optimizer":"adamw_torch","scheduler":"cosine","warmup_ratio":0.03,"weight_decay":0.0,"expected_steps":7500})
        self.assertFalse(c["runtime"]["auto_shutdown_enabled"])
        self.assertFalse(c["runtime"]["modelscope_upload"])
    def test_cursor_uses_raw_and_errors(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            raw=Path(d)/"raw"; err=Path(d)/"err"
            raw.write_text('{"prompt_index": 3}\n'); err.write_text('{"prompt_index": 8}\n')
            self.assertEqual(consumed_prompt_indices([raw,err]),{3,8})
            self.assertEqual(recover_next_prompt_index([raw,err]),9)
if __name__=="__main__": unittest.main()
