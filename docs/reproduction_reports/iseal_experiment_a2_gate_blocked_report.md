# iSeal Experiment A2 — Trainability Gate Blocked Report

Experiment A formal training was not started because the pinned public-code gate failed before launch. Experiment A2 applied only the approved initialization correction: `delta ~ Normal(0, 0.02)`, PyTorch default-equivalent Kaiming-uniform `A`, and exact-zero `B`; official `lm_head` and optimizer semantics were retained.

The canonical runtime key was replaced before any A2 scientific execution. Git records only SHA256 `8399db2b1e89eb03da1a1a6a4f9cd66d541f36c3695bd899e06613e06d75ffcf`; raw key material remained external to Git and logs.

## Gate outcome

Run `iseal_a2_trainability_20260830_053009` completed the mandatory two-step audit and failed the declared progression condition. `B` received a nonzero gradient at step 1, but the retained linear warmup made the first optimizer step's effective learning rate zero. Consequently, the step-2 backward pass still observed zero `A` and `delta` gradients. Their tiny final parameter deltas are attributable to AdamW weight decay acting on nonzero initial values, not task-gradient progression.

| Block | Step 1 grad norm | Step 2 grad norm | Final delta norm | Interpretation |
|---|---:|---:|---:|---|
| Base transformer | 0 | 0 | 0 | Frozen as required |
| Tied embedding / `lm_head` | 178.5911335110173 | 370.6112771489826 | 5.466963121858134 | Updated under retained official semantics |
| iSeal `delta` | 0 | 0 | 0.00018254498307234286 | No task gradient; weight-decay-only movement |
| iSeal `A` | 0 | 0 | 0.000023089552422913337 | No task gradient; weight-decay-only movement |
| iSeal `B` | 7.611014375590119 | 16.49304792580233 | 0.148625862921559 | Gradient path started, but too late for downstream step-2 progression |

Checks: `B_started_step1=true`, `A_or_delta_progression_by_step2=false`, `base_transformer_frozen=true`. Therefore `gate_passed=false` and formal Experiment A2 was not started. No further initialization, scheduler, optimizer, audit-length, or trainable-block modification was attempted.

Scientific status: A2 is blocked at its mandatory pre-formal trainability gate; no A2 Teacher exists, `preferred_teacher=NO`, and `ready_for_ba=NO`.

