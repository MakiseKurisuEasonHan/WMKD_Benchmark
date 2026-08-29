# Experiment Log

This is the concise index of formal WMKD_Benchmark experiments. Full scientific history is kept in each dedicated experiment log.

| Experiment | Status | Main run | Concise result | Dedicated log | Report | Blocker |
|---|---|---|---|---|---|---|
| PN-FP Experiment A | CLOSED | `pnfp_exp_a_20260827_232033` | 30/30 epochs; eval_loss 0.0119302; watermarked 1019/1024 (99.5117%); base 1/1024 (0.0977%); reload passed; ordinary-generation utility severely degraded. | `docs/experiment_logs/pnfp_experiment_a_log.md` | `docs/reproduction_reports/pnfp_experiment_a_report.md` | None |
| PN-FP Experiment A2 | CLOSED — scientifically complete through immutable continuation | Training: `pnfp_exp_a2_20260828_025240`; evaluation: `pnfp_exp_a2_eval_20260828_105530` | 956/1024 (93.359375%); ARC and TruthfulQA utility gates passed; preferred PN-FP teacher. | `docs/experiment_logs/pnfp_experiment_a2_log.md` | `docs/reproduction_reports/pnfp_experiment_a2_report.md` | None |
| PN-FP Experiment Ba | CLOSED | `pnfp_exp_ba_20260828_111148` | A2 956/1024 → Ba 98/1024; 83.7890625-point drop; 10.251046% retention; utility and reload passed. | `docs/experiment_logs/pnfp_experiment_ba_log.md` | `docs/reproduction_reports/pnfp_experiment_ba_report.md` | None |
| PN-FP Experiment Bb | NOT RUN / deferred | Not created | UP/Dipper design only; no result. | `docs/experiment_logs/pnfp_experiment_bb_log.md` | Template only | Explicit future approval |
| EverTracer Experiment A | COMPLETED through immutable continuation | Root: `evertracer_a_20260828_223155`; cont1: `evertracer_a_20260828_223155_cont1`; cont2: `evertracer_a_20260828_223155_cont2` | Preferred teacher; corrected member-oriented AUC/TPR 1.0/1.0; utility, generation sanity, and reload passed. | `docs/experiment_logs/evertracer_experiment_a_log.md` | AutoDL cont2 report | None |
| EverTracer Experiment Ba | COMPLETED | `evertracer_ba_20260829_124055` | Teacher 1.0/1.0 → student 0.4987/0.06; Base 0.4417/0.05. ARC 0.505119; TruthfulQA MC2 0.493715; generation/reload passed. | AutoDL run report | AutoDL run report | None |

## EverTracer ModelScope archives

- A preferred teacher: private repo `MakiseKurisuEasonHan/WMKD-EverTracer-A-Teacher`; 9 model files, 6,442,815,628 bytes.
- Ba student: private repo `MakiseKurisuEasonHan/WMKD-EverTracer-Ba-Student`; 9 model files, 6,442,815,786 bytes.
- Both states are `uploaded_to_modelscope_awaiting_destination_hash_verification`. No full model download was performed for destination SHA256 verification.

## EverTracer A → Ba closure timeline

1. Fixed official EverTracer commit `70b402f7b7456c6d94e1fae2de554d77dd6cd921`, canonical 3B revision, XSum-only split, target/reference training, and 128-token verification protocol.
2. Root run `evertracer_a_20260828_223155` completed target/reference training and merging, then immutably failed at perturbation due to T5 online/cache resolution.
3. Continuation 1 `evertracer_a_20260828_223155_cont1` generated canonical neighborhoods and verification inference, then immutably failed at utility due to ARC offline-cache resolution.
4. Detector audit preserved `C=suspect PV-reference PV`, corrected member/non-member orientation, and retained the old teacher AUC 0.0 as implementation-error provenance.
5. Continuation 2 `evertracer_a_20260828_223155_cont2` reused target/reference/neighborhoods/scores, corrected aggregation without inference, resolved utility offline, and completed A with teacher AUC/TPR 1.0/1.0.
6. Ba generated EverTracer-specific answers. Raw prefixes 24k/26k/28k/30k were insufficient; 32,003 raw records yielded 20,173 unique valid records and exactly 20,000 were frozen.
7. Ba student completed 7,500 steps and all verification, utility, generation, reload, reporting, and notification stages.
8. Teacher and student uploads plus remote metadata verification completed in their fixed private ModelScope repositories; destination-side full SHA remains deferred.
9. Final local/GitHub archive and protected AutoDL cleanup were authorized as the final closure stage.


## A2 immutable evaluation continuation `pnfp_exp_a2_eval_20260828_105530`

Parent training run `pnfp_exp_a2_20260828_025240` remains operationally FAILED after external dataset acquisition failure. The validated checkpoint and reusable evaluations plus this continuation establish the final result. Watermark gate: **passed**; utility gate: **passed**; judgement: **A2 is the preferred PN-FP teacher for future Ba**.


## A2-teacher formal Ba run `pnfp_exp_ba_20260828_111148`

Teacher A2 provenance: `pnfp_exp_a2_20260828_025240` + `pnfp_exp_a2_eval_20260828_105530`. Base/A2/Ba detection: 1/1024 (0.09765625%) / 956/1024 (93.359375%) / 98/1024 (9.5703125%); teacher→Ba drop 83.7890625 points; retention 10.251046%. ARC Base/A2/Ba: 0.448805461 / 0.443686007 / 0.478668942. TruthfulQA MC2 Base/A2/Ba: 0.505450760 / 0.467427921 / 0.463479842. Utility and reload gates passed. Judgement: **strong watermark degradation with partial retention under the tested setting**. The old A1-based run remains immutable FAILED.
