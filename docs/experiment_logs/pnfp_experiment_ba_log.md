# PN-FP Experiment Ba — Direct Distillation

Status: preparation complete; experiment not run.

Objective: measure PN-FP fingerprint retention and useful knowledge transfer after direct full-parameter distillation from the successful watermarked Experiment A 3B teacher into a fresh unwatermarked canonical 3B student.

Reference: Pan et al., ACL 2025 (`2025.acl-long.648`). Planned configuration: frozen paired 20k QA, 3 epochs, LR `1e-5`, BF16, seed 42, batch 8, full parameter, LoRA off; OOM fallback 8→4→2 only with recorded evidence. Utility scope: ARC Challenge and TruthfulQA MC; MTBench excluded initially.

Resource-bounded deviation: CAN uses about 200k pairs and reports eight H800 GPUs; Ba uses 20k on one RTX PRO 6000. Current state: config, deterministic freeze utility, schema, report template and guarded dry-run runner prepared. No formal QA generation, training or evaluation has started.

## Formal launch preparation — 2026-08-28

- User authorized Ba-only formal execution; Bb and all Dipper work remain deferred.
- AutoDL was briefly reachable: Experiment A teacher/fingerprint artifacts were present, GPU was idle, data disk had 981GB free, and the existing PN-FP environment reported PyTorch 2.7.1+cu128, Transformers 4.44.2, Accelerate 0.32.1, Datasets 2.20.0 and PyYAML 6.0.1.
- Added the formal resumable teacher-QA generator, full-parameter BF16 student trainer, serial Ba pipeline, OOM-only batch fallback and detached launcher.
- Deployment and launch have not occurred because the AutoDL SSH endpoint became unreachable during upload attempts. No GPU process was started.

## Same-size design correction — 2026-08-28

- Cancelled and removed an incomplete, project-owned 1B transport download before any formal run, teacher QA generation, GPU work or Ba STARTED notification.
- Corrected the Ba student to a fresh logical load of the existing canonical unwatermarked `meta-llama/Llama-3.2-3B-Instruct@0cb88a4f764b7a12671c53f0838cd831a0843b95`; the teacher remains the distinct watermarked Experiment A checkpoint.
- CAN ACL 2025 used Llama-3.2-1B as one of its students. WMKD_Benchmark intentionally uses same-size 3B teacher and student to remove model-capacity reduction as a confounder and isolate direct knowledge distillation.
- Stop point retained: Ba has no run ID and has not started.

## Formal run `pnfp_exp_ba_20260828_012228` — failed at dataset generation

- Launched independently with `nohup + setsid` from Git commit `30b996548f2486e2a072cd2817a36240fe6df360`; runner PID `94171`, pipeline PID `94175`, and teacher-generation PID `94421`.
- Minimum preflight passed, including 6/6 AutoDL config/storage tests, separate loadable teacher and canonical student artifacts, the frozen 12-file 3B manifest, the Experiment A 1,024-key detector, idle RTX PRO 6000, data-disk routing, and mode-600 email credentials.
- STARTED notification succeeded through STARTTLS 587. Teacher QA generation then produced degenerate repetitive text from the watermarked Experiment A checkpoint: 64 recorded parse failures, zero valid candidates, and therefore no frozen dataset.
- Because the generator loop was governed by accepted-candidate count, continuing at 0/24,000 would consume GPU indefinitely and could never satisfy the mandatory exactly-20,000 dataset gate. The generation child was terminated deliberately; the immutable runner recorded exit `-15`, final status `failed`, and exit code `1`. FAILED notification succeeded through SSL 465.
- No student training, checkpoint, reload, PN-FP evaluation, ARC, TruthfulQA, Bb, UP, or Dipper work occurred. This run must not be resumed or overwritten. The blocker is teacher ordinary-generation quality and the generator's missing bounded no-progress failure guard; resolving it requires a separately reviewed correction before a new run.

## Bounded teacher diagnostic — 2026-08-28

- Used a fixed 40-call diagnostic with a 900-second internal wall-clock limit and 950-second external timeout: 20 ordinary prompts, 10 CAN Appendix G/Figure 11-style `[[Instruction/Input/Answer]]` calls, and 10 existing WMKD JSON calls. It completed in 211.15 seconds; raw output remains only on the AutoDL data disk under `/root/autodl-tmp/WMKD_Benchmark_data/diagnostics/pnfp_ba_teacher_qa_20260828/results.json`.
- Ordinary generation was broadly degraded: only 1/20 calls ended before the 128-token cap; 19/20 reached it. Many responses began with a correct or relevant answer, then fell into repetitive concatenated tokens or repeated sentences. This is not merely a serialization failure.
- CAN-style generation: 10 calls, 0 calls with a parseable sample, 0 usable QA, 0% acceptance; all 10 reached 768 tokens, with repetitive/degenerate output. The prompt and delimiters follow Appendix G/Figures 11–12; the diagnostic index and chat serialization are documented minimal implementation choices.
- Existing WMKD JSON generation: 10 calls, 0 parse successes, 0 usable QA, 0% acceptance; all 10 reached 768 tokens with the same broad degeneration.
- Root-cause decision: **H1 / Case 3**. Experiment A's PN-FP teacher retains strong fingerprint behavior but its ordinary-generation utility may be severely degraded. H3 is rejected as the primary cause because removing strict JSON did not restore usable generation; H2 alone is insufficient because ordinary prompts also broadly degraded.
- The formal generator now has independent bounds: maximum 12,000 total calls, 64 consecutive zero-acceptance calls, 43,200 seconds wall clock, and a minimum 0.5 accepted records/call after a 200-call warmup. Raw failures remain preserved and each breached guard raises an explicit error. Unit tests cover zero-progress, low-acceptance, and wall-clock failures.
- Per the Case 3 decision rule, the formal format was not changed to CAN-style, the 100–200 candidate smoke was not run, and no new Ba run was created. Teacher and canonical student artifacts remain unchanged; GPU is free.
