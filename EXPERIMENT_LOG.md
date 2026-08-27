# Experiment Log

This is the concise index of formal WMKD_Benchmark experiments. Full scientific history is kept in each dedicated experiment log.

| Experiment | Status | Main run | Concise result | Dedicated log | Report | Blocker |
|---|---|---|---|---|---|---|
| PN-FP Experiment A | Completed successfully | `pnfp_exp_a_20260827_232033` | 30/30 epochs; eval_loss 0.0119302; watermarked 1019/1024 (99.5117%); base 1/1024 (0.0977%); paired difference 99.4141 pp; reload passed. | `docs/experiment_logs/pnfp_experiment_a_log.md` | `docs/reproduction_reports/pnfp_experiment_a_report.md` | None |
| PN-FP Experiment Ba | Formal run failed at teacher QA generation | `pnfp_exp_ba_20260828_012228` | Preflight passed; 64 degenerate-output parse failures and 0 valid candidates; failed safely before freeze/training. STARTED and FAILED emails delivered. | `docs/experiment_logs/pnfp_experiment_ba_log.md` | Template only | Review teacher-generation correction and bounded no-progress guard |
| PN-FP Experiment Bb | Prepared and deferred | Not created | UP/Dipper design only; not running. | `docs/experiment_logs/pnfp_experiment_bb_log.md` | Template only | Explicit future approval |
