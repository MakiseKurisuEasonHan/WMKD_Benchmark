# PN-FP Final Closure

Experiment A reproduced core fingerprint behavior at 1019/1024 versus base 1/1024, but its initial no-WA/no-DM ordinary-generation utility was severely degraded.

Experiment A2 (`pnfp_exp_a2_20260828_025240`; evaluation `pnfp_exp_a2_eval_20260828_105530`) used WA 0.75 and DM 0.25, achieved 956/1024 detections, ARC `0.44368600682593856`, TruthfulQA MC2 `0.4674279212401518`, and passed reload and utility gates. A2 is the preferred PN-FP teacher.

Experiment Ba (`pnfp_exp_ba_20260828_111148`) distilled 20,000 frozen QA pairs into a fresh canonical same-size 3B student. It achieved 98/1024 detections, an 83.7890625 percentage-point drop and retention ratio `0.10251046025104603`, while utility and reload passed.

Under the tested standardized same-size 3B direct-distillation condition, PN-FP robustness was substantially degraded while residual watermark signal remained above the base-model level. This does not establish complete removal, universal vulnerability, or behavior under every distillation attack. A, A2 and Ba are CLOSED. Bb was not run and remains deferred.
