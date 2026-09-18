# PN-FP 7B controlled recall trajectory diagnostic

Status: RUNNING. This is one user-authorized fresh controlled rerun, not a new optimizer/regularization search. Same canonical Llama-2-7b-chat revision, frozen1024/key16/response1/Perinucleus0.8,k3, WA0.75,DM0.25, seed42, BF16 full parameters, AdamW8bit0.50.0, checkpointing and existing chat detector. No distillation.

Original40-call LR horizon is retained to observe rise and any subsequent collapse. The loss<0.005 threshold is recorded, not the sole stopping criterion; resource, numeric or detector-integrity failure still stops. Full1024 detector runs after every epoch WA, including the two LR0 baseline calls. Detector and best-saving actions restore Python/NumPy/Torch RNG and model training mode. Exact ordered input hashes are logged; prior formal run lacks batch hashes, so direct cross-run hash proof is unavailable. Actual LR is asserted identical and loss is compared at every call.

Best is selected only by strictly improved recall; earliest wins ties. Writes use a temporary checkpoint and SHA manifest, then replace the best and remove only the superseded checkpoint in this new run. Old formal failed model stays untouched. Save final at end; no optimizer states or epoch checkpoints. A best-model fresh reload detector and one complete paired utility suite follow training. All40 per-call detector files and scalar trajectory records are retained. Evaluation and checkpoint-save seconds are separately timed.

Remote output: /root/autodl-tmp/WMKD_Benchmark_data/scale_7b/trajectory_adamw8bit_v1. Supervisor16674, training16683. Prelaunch GPU idle, about43.34GiB free. Local config: configs/watermark/pnfp_7b_trajectory.json. Source wrappers are assertion-checked against the exact previous formal executed training source, and both source hashes are recorded.

Optimizer-state storage remains an engineering adaptation; no equivalence with canonical FP32 Adam is claimed. Final measurements, best selection and utility assessment pending.
