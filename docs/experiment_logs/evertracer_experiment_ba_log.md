# EverTracer Experiment Ba Log

## Timeline

- Design fixed EverTracer A preferred teacher as the sole response generator; PN-FP teacher, QA, student, and checkpoints were explicitly excluded.
- Formal run `evertracer_ba_20260829_124055` started on 2026-08-29.
- Teacher generation tested immutable raw prefixes. Freeze attempts at 24k, 26k, 28k, and 30k were insufficient; 32,003 raw records produced 20,173 unique valid records.
- Exactly 20,000 records were frozen with canonical SHA256 `ca1aa9c991ae58e1d5bbf32275f1738786db15c337bc4bb80fdc0813aa447142`.
- A fresh canonical 3B student completed 7,500 steps, 3 epochs, full-parameter BF16 SFT, batch 8, LR 1e-5.
- Verification completed with teacher/student/base member AUC 1.0000/0.4987/0.4417 and TPR@FPR≤5% 1.00/0.06/0.05.
- Utility completed: ARC base/teacher/student 0.446246/0.421502/0.505119; TruthfulQA MC2 0.505687/0.514798/0.493715.
- Ordinary-generation sanity and fresh-process reload passed; final report and summary were generated; COMPLETED email was delivered.
- Preferred teacher and Ba student were uploaded to their fixed private ModelScope repositories. Both remain `uploaded_to_modelscope_awaiting_destination_hash_verification`.

## Result

The engineering pipeline completed without a scientific blocker. Under this tested direct-distillation condition, the student detector result is approximately base/random-level while tested utility remains functional. Bb is NOT RUN and deferred.
