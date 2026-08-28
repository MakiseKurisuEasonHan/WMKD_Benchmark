# PN-FP Experiment Ba — Direct Distillation

## Identity and research question

- Method: PN-FP
- Experiment: Ba — Direct Distillation
- Formal run: `pnfp_exp_ba_20260828_111148`
- Question: how much PN-FP watermark signal persists after direct knowledge distillation when teacher and student use the same 3B architecture and revision?

## Provenance

The teacher is the utility-preserving A2 checkpoint from training run `pnfp_exp_a2_20260828_025240`, completed scientifically through evaluation continuation `pnfp_exp_a2_eval_20260828_105530`. A2 passed both watermark and utility gates and detected 956/1024 fingerprints (93.359375%).

The student was initialized from fresh canonical unwatermarked `meta-llama/Llama-3.2-3B-Instruct` revision `0cb88a4f764b7a12671c53f0838cd831a0843b95`, not from A2 weights.

## Verified environment

- GPU: NVIDIA RTX PRO 6000 Blackwell Server Edition, 97,887 MiB reported VRAM
- CPU: 2 × Intel Xeon Platinum 8470Q, 52 cores/socket, 208 logical CPUs
- RAM: 1.0 TiB
- OS: Ubuntu 22.04.5 LTS
- Python: 3.10.20
- PyTorch: 2.7.1+cu128; CUDA runtime reported by PyTorch: 12.8
- Transformers: 4.44.2
- DeepSpeed: 0.14.5

## Distillation design

This is a same-size 3B→3B experiment using teacher-generated CAN-style QA. The immutable dataset contains exactly 20,000 samples. Training used 3 epochs, learning rate `1e-5`, BF16, full-parameter optimization, LoRA off, seed 42, and batch size 8. No OOM fallback occurred.

CAN uses roughly 200,000 teacher-generated QA pairs and includes additional student/settings. WMKD_Benchmark deliberately uses a resource-bounded 20,000-pair, single-GPU setting and standardizes teacher and student to the same 3B backbone. Results therefore apply to this WMKD setting and are not a full reproduction of every CAN configuration.

## Dataset generation

- Raw accepted candidates: 32,002
- Generation/parse failures: 1,198
- Deduplication rejections: 11,789
- Unique QA after deduplication: 20,213
- Frozen QA: 20,000
- Dataset manifest SHA256: `6ad11ff25826c32d71641c7433993070a8865e9e64e99841856e09b61d861a72`

## Training and reload

Training completed 7,500/7,500 optimizer steps over 3 epochs. Aggregate train loss was `0.3961066076`; the last logged batch loss was `0.2683`. Training eval loss was not recorded. The final checkpoint was saved at `checkpoints/student_batch_8/final_model`; reload validation passed with `RELOAD_OK`.

## Watermark results

| Model | Detected | Total | Rate |
|---|---:|---:|---:|
| Canonical Base 3B | 1 | 1024 | 0.09765625% |
| A2 Teacher | 956 | 1024 | 93.359375% |
| Ba Student | 98 | 1024 | 9.5703125% |

Teacher→Ba absolute drop was 83.7890625 percentage points. Ba remained 9.47265625 percentage points above Base, and retained 10.251046% of the teacher detection rate. Ba evaluation had zero invalid samples and zero evaluation errors.

## Utility results

| Metric | Base | A2 Teacher | Ba Student | Ba vs A2 | Ba vs Base |
|---|---:|---:|---:|---:|---:|
| ARC Challenge `acc_norm` | 0.448805461 | 0.443686007 | 0.478668942 | +0.034982935 | +0.029863481 |
| TruthfulQA MC2 | 0.505450760 | 0.467427921 | 0.463479842 | -0.003948080 | -0.041970918 |

The utility gate passed. A Ba-specific ordinary-generation/repetition diagnostic was not run, so that metric is not established.

## Interpretation

Engineering completion is distinct from scientific interpretation. Under the tested same-size 3B direct-distillation setting, PN-FP is highly vulnerable to knowledge distillation: detection decreased from 93.36% in the A2 teacher to 9.57% in the Ba student while benchmark utility remained largely preserved. A residual signal remains well above the unwatermarked Base, so the result is strong degradation with partial retention, not complete watermark removal.

## Limitations

- One formal Ba run and one seed.
- One teacher/student architecture and a same-size 3B→3B setting.
- The 20,000-pair resource-bounded dataset is smaller than CAN's roughly 200,000-pair setting.
- No Ba ordinary-generation/repetition diagnostic was run.
- Training eval loss was not recorded.
- Ba detection remains 9.57%, above the Base rate.
- The result establishes vulnerability only for this tested setting; it does not establish universal vulnerability, complete removal, or multi-seed robustness.

## Bounded conclusion

**PN-FP is vulnerable under the tested direct-distillation setting, with strong watermark degradation and partial retention while utility remains largely preserved.**
