# PN-FP Experiment A — Final Reproduction Report

## Identity and objective

- Method: PN-FP (perinucleus fingerprinting)
- Formal run: `pnfp_exp_a_20260827_232033`
- Objective: embed 1,024 behavioral fingerprints into the benchmark Llama-3.2-3B-Instruct backbone and compare the reloaded checkpoint with the unchanged base control.

## Provenance and environment

- Backbone: `meta-llama/Llama-3.2-3B-Instruct@0cb88a4f764b7a12671c53f0838cd831a0843b95`
- Official implementation: `SewoongLab/scalable-fingerprinting-of-llms@fdceaba14bd3e89340916a6a40e27c945d48460e`
- Compute: one NVIDIA RTX PRO 6000 Blackwell Server Edition, BF16
- Compatibility deviation: PyTorch 2.7.1+cu128 replaced the official older PyTorch pin to support Blackwell. The PN-FP method was not changed.

## Planned and actual configuration

The run used 1,024 fingerprints, key/generation/training-response lengths 16/16/1, 30 epochs, learning rate `5e-5`, weight decay `1e-4`, per-device batch 8, seed 42, full-parameter training, LoRA off, DeepSpeed ZeRO-2 CPU offload, Llama chat serialization, nucleus threshold 0.8, nucleus k 3 and model-averaging strength 0.0. All 3,212,749,824 parameters were trainable. Training completed 30/30 epochs with no OOM; final `eval_loss` was 0.0119302.

## Preserved engineering attempts

Three immutable attempts failed before optimization and are not scientific trials:

1. `pnfp_exp_a_20260827_231202`: official `generated_data/word_list.txt` was missing from the sparse checkout.
2. `pnfp_exp_a_20260827_231325`: only 1,012 valid fingerprints remained after the official whitespace filter. Candidate generation was increased to 1,100 while the formal set remained exactly 1,024.
3. `pnfp_exp_a_20260827_231639`: detached PATH did not expose the installed `ninja` executable required by CPUAdam.

The corrected run generated 1,087 valid candidates and fixed the first 1,024 for both training and evaluation.

## Results

| Model | Detected | Total | Rate | Invalid | Errors |
|---|---:|---:|---:|---:|---:|
| Reloaded PN-FP checkpoint | 1019 | 1024 | 99.5117% | 0 | 0 |
| Unchanged base control | 1 | 1024 | 0.0977% | 0 | 0 |

Paired absolute difference: `0.994140625`, or 99.4141 percentage points. Checkpoint reload validation passed.

## Artifacts

- Run root: `/root/autodl-tmp/WMKD_Benchmark_data/runs/pnfp/pnfp_exp_a_20260827_232033`
- Final checkpoint: `/root/autodl-tmp/WMKD_Benchmark_data/runs/pnfp/pnfp_exp_a_20260827_232033/checkpoints/official/saved_models/a0a21e74c9f8f189aee68a315cb668b4/final_model`
- Raw configuration, logs, fingerprint keys, checkpoint manifest, evaluations and summary remain beneath the immutable run root.

## Scope, limitations and conclusion

This is a resource-bounded core reproduction on Llama-3.2-3B-Instruct with 1,024 fingerprints, not a reproduction of every scale, backbone, utility or persistence experiment in the PN-FP paper. Under the declared configuration, the watermarked checkpoint exhibits near-complete target behavior while the unchanged base has negligible accidental detection. The reload and base controls support the bounded judgement: **PN-FP core reproduction successful**.

The COMPLETED watcher notification initially failed with an SMTP timeout. This was an operational notification failure only and did not affect any scientific artifact or result.
