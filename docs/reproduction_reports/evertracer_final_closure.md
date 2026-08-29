# EverTracer Final Closure

EverTracer Experiment A reproduced the method's core natural-language fingerprint behavior on the canonical Llama-3.2-3B-Instruct adaptation. Its immutable root and continuation 1 failures were infrastructure/implementation corrections, not target/reference training failures. Continuation 2 completed with corrected teacher/base member-oriented AUC 1.0000/0.4417 and TPR@FPR≤5% 1.00/0.05. The A checkpoint is the preferred teacher.

EverTracer Ba run `evertracer_ba_20260829_124055` generated EverTracer-specific answers, froze exactly 20,000 samples with canonical SHA256 `ca1aa9c991ae58e1d5bbf32275f1738786db15c337bc4bb80fdc0813aa447142`, and trained a fresh canonical same-size student. Student member-oriented AUC/TPR was 0.4987/0.06. Under this tested standardized condition, the strong teacher fingerprint was reduced to approximately base/random-level detectability while tested utility remained functional. This is not a universal claim.

Teacher and student are private at `MakiseKurisuEasonHan/WMKD-EverTracer-A-Teacher` and `MakiseKurisuEasonHan/WMKD-EverTracer-Ba-Student`. Source hashes and remote filename/count/size/blob metadata were verified. Both remain `uploaded_to_modelscope_awaiting_destination_hash_verification`; no full model download established `destination_verified`.

Protected cleanup removed only explicitly named EverTracer smoke outputs and the redundant Ba `checkpoint-7500`. It released 83,707,244,544 bytes (77.958 GiB). Canonical base, Teacher, Student, Reference, adapters, frozen neighborhoods, final20k, raw32k candidates, shared infrastructure/cache, reports, manifests, and credentials remain intact. Experiments A and Ba are FULLY CLOSED; Bb is NOT RUN/deferred.
