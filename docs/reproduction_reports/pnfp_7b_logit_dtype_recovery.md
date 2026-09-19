# PN-FP7B Logit serialization compatibility recovery

Scope: only unfinished Bc. Accepted Teacher804, Direct53, Paraphrase71 and their utility remain unchanged; no prior scientific stage is repeated.

## Confirmed cause

Actual environment: torch2.8.0+cu128, Transformers4.44.2, DeepSpeed0.16.9 installed but no DeepSpeed engine active. Cache inference runs without autocast. All model parameters and lm_head input/weight/output are BF16. Installed LlamaForCausalLM.forward explicitly executes `logits = logits.float()` after lm_head, returning FP32. The previous assertion confused the public output dtype with the canonical target-storage dtype.

Canonical3B `scripts/train_same_lineage_bc.py` and `scripts/pnfp_bc_pilot.py` explicitly select shifted assistant positions and then `.to(torch.bfloat16)` before the CE/KL consumer. The historical implementation is online, so it has no historical offline serialization step. It does not require FP32 teacher targets. Student/teacher full-vocab alignment, masking, T2, .5CE+.5T²KL and full-parameter training are unchanged.

## Necessary real smoke

All Teacher/Base/Direct/Paraphrase model files match saved SHA manifests. Frozen20k dataset and complete canonical sequence construction hash match the previous run. Real two-sample forward covers23 supervised positions and32000 vocabulary entries. Casting selected FP32 logits back to BF16 preserves shape, order, finite values and every top1. Maximum logits difference0, softmax difference0, KL difference0 at T2. This is expected because the forward had merely widened BF16 lm_head values. A1,472,000-byte BF16 shard reloads bitwise; actual existing OfflineTrainer loss consumer matches canonical ResponseObjective exactly and backward gradients are finite. This spot-check is evidence for this path, not a general claim that arbitrary FP32→BF16 casts are lossless.

## Fix and continuation

Writer first asserts returned logits are FP32 or BF16, selects exactly the original supervised positions, explicitly casts toBF16, and retains the BF16/shape/finite assertions. Record as **serialization dtype compatibility fix**, not a scientific protocol change. No top-k, temperature/weight/tokenizer/dataset/mask/seed changes.

Formal cache:527,563 supervised tokens ×32000×2=33,764,032,000 bytes (~31.45GiB),157 shards. All shard counts/SHAs/bytes/dtype/positions/token order verified before independent clean7B training. Student retains3epochs/7500steps/effectivebatch8/LR1e-5/cosine225warmup/seed42/fullFT/BF16/checkpointing/AdamW8bit0.50.0. Only Logit detector and utility run after final save.

Recovery evidence: results/pnfp/scale_7b/logit_recovery_6004/. New artifacts: /root/autodl-tmp/WMKD_Benchmark_data/scale_7b/logit_recovery_6004/. Old failed cache and complete Direct/Paraphrase artifacts remain untouched.

ControllerPID1701 and local guardianPID68964. On successful Logit completion, merge prior immutable results into final report, verify final model/evidence, sync locally, update index/status/TODO/logs and local Git, then official shutdown via its required bash interpreter. An arbitrary engineering exception no longer automatically triggers shutdown or a scientific-failure classification.
