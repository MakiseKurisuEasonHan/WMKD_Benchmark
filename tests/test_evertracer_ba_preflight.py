import copy,tempfile,unittest
from pathlib import Path
from scripts.evertracer_ba_preflight import validate

BASE={"distillation_experiment":"Ba","teacher":{"run_id":"evertracer_a_20260828_223155","final_continuation_id":"evertracer_a_20260828_223155_cont2","checkpoint":"/root/autodl-tmp/WMKD_Benchmark_data/runs/evertracer/evertracer_a_20260828_223155/checkpoints/target_merged"},"student":{"model_id":"meta-llama/Llama-3.2-3B-Instruct","revision":"0cb88a4f764b7a12671c53f0838cd831a0843b95","path":"/root/autodl-tmp/WMKD_Benchmark_data/models/base/Llama-3.2-3B-Instruct"},"dataset":{"final_samples":20000,"answer_source":"evertracer_a_preferred_teacher","output_root":"/root/autodl-tmp/WMKD_Benchmark_data/runs/evertracer_ba"},"training":{"epochs":3,"learning_rate":1e-5,"precision":"bf16","full_parameter":True,"lora":False,"batch_size":8,"gradient_accumulation_steps":1,"max_length":1024}}
class T(unittest.TestCase):
 def test_valid_protocol(self):self.assertEqual(validate(copy.deepcopy(BASE))["batch_size"],8)
 def test_rejects_pnfp_teacher(self):
  c=copy.deepcopy(BASE);c["teacher"]["checkpoint"]="/data/runs/pnfp/a2/final_model"
  with self.assertRaisesRegex(ValueError,"PN-FP"):validate(c)
 def test_rejects_stale_teacher(self):
  c=copy.deepcopy(BASE);c["teacher"]["final_continuation_id"]="evertracer_a_old"
  with self.assertRaisesRegex(ValueError,"lineage"):validate(c)
 def test_rejects_adapter_only_teacher(self):
  c=copy.deepcopy(BASE);c["teacher"]["checkpoint"]="/root/autodl-tmp/WMKD_Benchmark_data/runs/evertracer/evertracer_a_20260828_223155/checkpoints/target/adapter"
  with self.assertRaisesRegex(ValueError,"adapter-only"):validate(c)
 def test_rejects_nonfresh_student(self):
  c=copy.deepcopy(BASE);c["student"]["path"]=c["teacher"]["checkpoint"]
  with self.assertRaisesRegex(ValueError,"initialize from teacher"):validate(c)
 def test_rejects_pnfp_dataset(self):
  c=copy.deepcopy(BASE);c["dataset"]["output_root"]="/data/pnfp_distillation_20k"
  with self.assertRaisesRegex(ValueError,"PN-FP"):validate(c)
 def test_config_effective_is_fixed(self):
  c=copy.deepcopy(BASE);c["training"]["batch_size"]=4
  with self.assertRaisesRegex(ValueError,"training config"):validate(c)
if __name__=="__main__":unittest.main()
