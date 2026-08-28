# Experiment Log

This is the concise index of formal WMKD_Benchmark experiments. Full scientific history is kept in each dedicated experiment log.

| Experiment | Status | Main run | Concise result | Dedicated log | Report | Blocker |
|---|---|---|---|---|---|---|
| PN-FP Experiment A | Completed successfully | `pnfp_exp_a_20260827_232033` | 30/30 epochs; eval_loss 0.0119302; watermarked 1019/1024 (99.5117%); base 1/1024 (0.0977%); paired difference 99.4141 pp; reload passed. | `docs/experiment_logs/pnfp_experiment_a_log.md` | `docs/reproduction_reports/pnfp_experiment_a_report.md` | None |
| PN-FP Experiment A2 | Completed scientifically through immutable continuation | Training: `pnfp_exp_a2_20260828_025240`; evaluation: `pnfp_exp_a2_eval_20260828_105530` | 30/30 optimizer steps; final eval_loss 0.3678587; A2 956/1024 (93.359375%); base 1/1024; ARC delta -0.005119453924914696; TruthfulQA MC2 delta -0.03802283891367614; both gates passed; preferred Ba teacher. | `docs/experiment_logs/pnfp_experiment_a2_log.md` | `docs/reproduction_reports/pnfp_experiment_a2_report.md` | None; parent training run remains operationally FAILED only at downstream ARC acquisition |
| PN-FP Experiment Ba | A2-based formal run active | `pnfp_exp_ba_20260828_111148` | Active at `teacher_qa_generation` using A2 teacher and fresh canonical 3B student; 2,344/24,000 candidates at the last read-only observation; no final result. Old A1-based run `pnfp_exp_ba_20260828_012228` remains immutable FAILED. | `docs/experiment_logs/pnfp_experiment_ba_log.md` | Pending active run | Await active run completion; no runtime blocker observed |
| PN-FP Experiment Bb | Prepared and deferred | Not created | UP/Dipper design only; not running. | `docs/experiment_logs/pnfp_experiment_bb_log.md` | Template only | Explicit future approval |


## A2 immutable evaluation continuation `pnfp_exp_a2_eval_20260828_105530`

Parent training run `pnfp_exp_a2_20260828_025240` remains operationally FAILED after external dataset acquisition failure. The validated checkpoint and reusable evaluations plus this continuation establish the final result. Watermark gate: **passed**; utility gate: **passed**; judgement: **A2 is the preferred PN-FP teacher for future Ba**.
