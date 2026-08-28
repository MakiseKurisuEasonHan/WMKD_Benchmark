# Experiment Log

This is the concise index of formal WMKD_Benchmark experiments. Full scientific history is kept in each dedicated experiment log.

| Experiment | Status | Main run | Concise result | Dedicated log | Report | Blocker |
|---|---|---|---|---|---|---|
| PN-FP Experiment A | Completed successfully | `pnfp_exp_a_20260827_232033` | 30/30 epochs; eval_loss 0.0119302; watermarked 1019/1024 (99.5117%); base 1/1024 (0.0977%); paired difference 99.4141 pp; reload passed. | `docs/experiment_logs/pnfp_experiment_a_log.md` | `docs/reproduction_reports/pnfp_experiment_a_report.md` | None |
| PN-FP Experiment A2 | Completed scientifically through immutable continuation | Training: `pnfp_exp_a2_20260828_025240`; evaluation: `pnfp_exp_a2_eval_20260828_105530` | 30/30 optimizer steps; final eval_loss 0.3678587; A2 956/1024 (93.359375%); base 1/1024; ARC delta -0.005119453924914696; TruthfulQA MC2 delta -0.03802283891367614; both gates passed; preferred Ba teacher. | `docs/experiment_logs/pnfp_experiment_a2_log.md` | `docs/reproduction_reports/pnfp_experiment_a2_report.md` | None; parent training run remains operationally FAILED only at downstream ARC acquisition |
| PN-FP Experiment Ba | Completed | `pnfp_exp_ba_20260828_111148` | A2 956/1024 (93.36%) → Ba 98/1024 (9.57%); 83.7891-point drop; 10.251% retention; utility gate passed; strong degradation with partial retention. | `docs/experiment_logs/pnfp_experiment_ba_log.md` | `docs/reproduction_reports/pnfp_experiment_ba_report.md` | None |
| PN-FP Experiment Bb | Prepared and deferred | Not created | UP/Dipper design only; not running. | `docs/experiment_logs/pnfp_experiment_bb_log.md` | Template only | Explicit future approval |


## A2 immutable evaluation continuation `pnfp_exp_a2_eval_20260828_105530`

Parent training run `pnfp_exp_a2_20260828_025240` remains operationally FAILED after external dataset acquisition failure. The validated checkpoint and reusable evaluations plus this continuation establish the final result. Watermark gate: **passed**; utility gate: **passed**; judgement: **A2 is the preferred PN-FP teacher for future Ba**.


## A2-teacher formal Ba run `pnfp_exp_ba_20260828_111148`

Teacher A2 provenance: `pnfp_exp_a2_20260828_025240` + `pnfp_exp_a2_eval_20260828_105530`. Base/A2/Ba detection: 1/1024 (0.09765625%) / 956/1024 (93.359375%) / 98/1024 (9.5703125%); teacher→Ba drop 83.7890625 points; retention 10.251046%. ARC Base/A2/Ba: 0.448805461 / 0.443686007 / 0.478668942. TruthfulQA MC2 Base/A2/Ba: 0.505450760 / 0.467427921 / 0.463479842. Utility and reload gates passed. Judgement: **strong watermark degradation with partial retention under the tested setting**. The old A1-based run remains immutable FAILED.
