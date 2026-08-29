# Decisions

This log records consequential project decisions. It does not record routine engineering operations.

## 2026-08-27 — Establish WMKD_Benchmark as an independent project

- **Decision:** WMKD_Benchmark uses a new local project root and a dedicated GitHub repository.
- **Reason:** The benchmark requires clean provenance, reproducibility, and recovery without contamination from earlier WaterBench or watermark benchmark projects.

## 2026-08-27 — Keep legacy projects isolated

- **Decision:** Do not import, link, copy, cache-share, or otherwise depend on legacy WaterBench projects unless a future task explicitly authorizes a specific reference.
- **Reason:** Isolation prevents stale code, configuration, artifacts, Git history, and experimental state from affecting research conclusions.

## 2026-08-27 — Use one Codex workflow

- **Decision:** A single Codex instance performs project implementation work based on prompts produced through the user's ChatGPT research-planning workflow.
- **Reason:** This preserves a clear chain of instruction and accountability and avoids conflicting autonomous project decisions.

## 2026-08-27 — Separate development, compute, and long-term storage roles

- **Decision:** Local development will be used for code and documentation; AutoDL is intended for future compute; the La Trobe server is intended for future long-term large-file storage. Their setup is deferred to dedicated future tasks.
- **Reason:** Separating these roles supports reproducibility, cost control, and durable artifact management while keeping large files out of Git.

## 2026-08-27 — Do not commit large artifacts or secrets

- **Decision:** Git tracks source, configuration, documentation, metadata, and small summaries, but not model weights, checkpoints, large datasets, raw outputs, caches, or secrets. Git LFS is not enabled.
- **Reason:** GitHub is for reproducibility and project-state backup, not large-artifact storage.

## 2026-08-27 — Defer selection of an open-source license

- **Decision:** Retain all rights until the project owner explicitly selects a release license.
- **Reason:** Choosing distribution and reuse terms is a consequential publication decision and is not yet specified.

## 2026-08-27 — Assign infrastructure roles

- **Decision:** The local Windows project is the primary development location; GitHub versions and backs up code, configurations, documentation, metadata, and small summaries; AutoDL is reserved for future compute; and the La Trobe school server is the long-term large-artifact warehouse.
- **Reason:** Explicit role separation prevents large artifacts from entering Git, avoids treating archival storage as a development or compute environment, and provides a clear recovery model.

## 2026-08-27 — Keep the school-server warehouse physically separate

- **Decision:** Maintain a lightweight Git checkout at `/data/home/ad/21672330/WMKD_Benchmark` and a non-Git warehouse at `/data/shared/nobackup/21672330/WMKD_Benchmark`, without symlinks between them or to legacy projects.
- **Reason:** Physical and logical separation reduces accidental Git ingestion, cross-project contamination, and ambiguous artifact provenance. A future task will define explicit synchronization configuration and manifests.

## 2026-08-27 — Separate AutoDL code and compute data

- **Decision:** Use `/root/autodl-tmp/WMKD_Benchmark` as a disposable compute-side Git checkout and `/root/autodl-tmp/WMKD_Benchmark_data` as a non-Git, project-specific compute-data root. All model, checkpoint, dataset, cache, run, and temporary paths use the new namespace.
- **Reason:** Keeping code and large compute artifacts separate protects Git reproducibility and prevents accidental reuse of legacy paths, caches, and state.

## 2026-08-27 — Defer the AutoDL ML environment

- **Decision:** Record existing system, Python, and GPU inventory without installing dependencies or creating an ML environment until the first watermark method is approved.
- **Reason:** Environment requirements should follow a selected reproduction target rather than prematurely committing the benchmark to a framework or dependency set.

## 2026-08-27 — Standardize the 3B benchmark backbone

- **Decision:** Use `meta-llama/Llama-3.2-3B-Instruct` at revision `0cb88a4f764b7a12671c53f0838cd831a0843b95` as the shared 3B backbone for watermark reproductions and later clean-student initialization unless a future explicit decision changes it.
- **Reason:** A fixed shared model revision supports fair cross-method comparisons and reproducible model provenance.

## 2026-08-28 — Make same-size 3B the default A/Ba/Bb benchmark rule

- **Decision:** Unless the user separately approves a documented method-specific deviation, Experiment A, Ba, and Bb all use `meta-llama/Llama-3.2-3B-Instruct@0cb88a4f764b7a12671c53f0838cd831a0843b95`. A starts from canonical unwatermarked weights; Ba/Bb use the successful watermarked A checkpoint only as teacher and initialize each student through a fresh load of the canonical unwatermarked weights.
- **Reason:** Same family, size, revision, tokenizer, and template enable horizontal cross-method comparison and vertical A → Ba/Bb retention comparison without mixing distillation with model compression or capacity reduction.
- **Exception policy:** Incompatibility or resource infeasibility is a blocker, not permission to swap models. Record it, propose the deviation, obtain explicit user approval, and label the result as a non-standard backbone deviation without rewriting historical runs.

## 2026-08-27 — Use PNFP as the first reproduction target

- **Decision:** Prepare PNFP (Perinucleus fingerprinting) Experiment A from the official `SewoongLab/scalable-fingerprinting-of-llms` repository at commit `fdceaba14bd3e89340916a6a40e27c945d48460e`, without reusing legacy implementations or the official repository's pre-generated fingerprint data.
- **Reason:** A fixed clean source provides auditable provenance, while generating benchmark-specific fingerprints avoids silently inheriting paper artifacts tied to another backbone.

## 2026-08-27 — Adapt PyTorch for the AutoDL Blackwell GPU

- **Decision:** Preserve the official PNFP core package pins where practical, but replace the repository's `torch==2.3.1` with `torch==2.7.1+cu128` in the isolated AutoDL environment.
- **Reason:** The official PyTorch pin predates the NVIDIA Blackwell GPU. The adjusted official CUDA 12.8 wheel passed CUDA availability, BF16 support, DeepSpeed import, PNFP module import, and dependency checks. This is an environment compatibility deviation, not a method change.

## 2026-08-27 — Reject the non-identical ModelScope backbone candidate

- **Decision:** Do not use `LLM-Research/Llama-3.2-3B-Instruct` revision `master` as the WMKD_Benchmark backbone, despite acceptable ModelScope download speed.
- **Reason:** The frozen benchmark requires exact equality with all 12 files from Hugging Face revision `0cb88a4f764b7a12671c53f0838cd831a0843b95`. ModelScope metadata matched only 11/12 entries, and a direct download confirmed that `.gitattributes` differs in both size and SHA256. Loadability or matching weight shards cannot substitute for full snapshot identity.

## 2026-08-27 — Permit ModelScope as transport with canonical Hugging Face repair

- **Decision:** Permit ModelScope to transport only the 12 named snapshot artifacts when every final file is checked against the frozen Git manifest. A mismatched small file may be replaced only from exact Hugging Face revision `0cb88a4f764b7a12671c53f0838cd831a0843b95`; promotion requires complete 12/12 size and SHA256 equality.
- **Reason:** Transport origin does not alter scientific provenance when final bytes are identical to the authoritative Hugging Face snapshot. This preserves the earlier rejection of ModelScope as a standalone backbone source while allowing its matching large shards to bypass unusable transfer routes.

## 2026-08-28 — Make formal experiments file-recoverable and independently runnable

- **Decision:** Every formal experiment uses an immutable run namespace, dedicated scientific log, structured status/configuration files, and a project-owned detached runner. `docs/EXPERIMENT_PROTOCOL.md` is the durable cross-experiment policy.
- **Reason:** Training and project continuity must not depend on a particular Codex conversation, shell, computer, or AutoDL instance.

## 2026-08-28 — Use consistent Llama chat serialization for PN-FP Experiment A

- **Decision:** Generate perinucleus responses, train, and evaluate with the canonical Llama-3.2-Instruct chat template. Explicitly use PN-FP nucleus threshold 0.8, k=3, and model-averaging strength 0.0 from the official documented configuration.
- **Reason:** Training and detection must serialize the same fingerprint keys, and all method-relevant values must be explicit rather than inherited from inconsistent CLI defaults.

## 2026-08-28 — Treat experiment email as best-effort external operations

- **Decision:** Future formal runners emit duplicate-safe lifecycle email through Gmail SMTP over SSL, while credentials remain in a mode-600 file outside Git. Notification errors are recorded independently and never change scientific pipeline status.
- **Reason:** Long detached experiments need useful operational visibility without making external email availability part of scientific correctness or exposing credentials in project history.

## 2026-08-28 — Define resource-bounded PN-FP Ba/Bb distillation

- **Decision:** Ba is Direct Distillation and Bb is answer-only Untargeted Paraphrasing plus Distillation. Both share exactly 20,000 frozen task IDs, start from fresh unwatermarked canonical `meta-llama/Llama-3.2-3B-Instruct@0cb88a4f764b7a12671c53f0838cd831a0843b95`, and use full-parameter BF16 SFT for 3 epochs at `1e-5` with seed 42 and initial batch 8. The teacher is the separate watermarked Experiment A 3B checkpoint.
- **Reason:** Same-size teacher and student remove model-capacity reduction as a confounding variable, isolating the effect of behavioral knowledge distillation on watermark persistence. CAN ACL 2025's use of Llama-3.2-1B as one student remains a paper fact; the 3B-to-3B setup is an intentional WMKD_Benchmark adaptation.
- **Reason:** The paired design isolates response paraphrasing, while 20k is a deliberate single-GPU adaptation of CAN's roughly 200k/eight-H800 setting.

## 2026-08-28 — Attribute Bb UP as a project-owned integration

- **Decision:** Use `kalpeshk2011/dipper-paraphraser-xxl@c1fbf7a958a2aab022e9e6f81f7a3139f9e6ee3c` with a pinned T5 tokenizer. Label the method “paper-defined UP + project-owned Dipper integration”; never call it official CAN author code.
- **Reason:** The official CAN repository implements WN and explicitly delegates UP/TP paraphrasing to users.

## 2026-08-28 — Persist exhausted terminal email notifications

- **Decision:** Gmail SSL 465 uses three bounded attempts with 45-second timeouts before up to two serial STARTTLS 587 attempts. Exhausted COMPLETED, FAILED, and INTERRUPTED events enter a non-secret data-disk pending queue and may be retried later without touching experiment state. Only confirmed SMTP success marks `run_id + event` delivered.
- **Reason:** Experiment A showed that a temporary SMTP timeout can otherwise permanently lose a valid terminal notification even though watcher classification and scientific execution succeeded.

## 2026-08-28 — Close PN-FP and standardize destination verification

- **Decision:** Close PN-FP Experiments A, A2, and Ba; retain Bb as not run/deferred. A2 is the preferred utility-preserving teacher. Ba establishes substantial but incomplete degradation under the tested same-size 3B direct-distillation condition.
- **Decision:** Future transfers establish immutable source hashes and verify ModelScope filenames/count/sizes/blob consistency, then defer full SHA256 to the real destination download. A same-source full remote re-read, as performed for Ba, is stronger but optional.
- **Reason:** A2 correctly remained awaiting destination verification. Ba's redundant same-host readback added about 37.6 minutes without replacing the need for destination-side verification.

## 2026-08-28 — Use PN-FP A2 as the preferred Ba teacher

- **Decision:** Replace A1 with A2 as the preferred and sole formal teacher for the new Ba run while retaining the same canonical 3B backbone standard. A2 is the watermarked teacher; every Ba student still initializes from a fresh load of canonical unwatermarked `meta-llama/Llama-3.2-3B-Instruct@0cb88a4f764b7a12671c53f0838cd831a0843b95`.
- **Reason:** A1 has stronger PN-FP detection at 1019/1024 but exhibits severe ordinary-generation degradation. A2 retains strong detection at 956/1024 (93.359375%), avoids the observed A1-like collapse in the bounded diagnostic, and passed both ARC/TruthfulQA utility and watermark gates. The change selects a usable teacher without changing model family, size, revision, tokenizer, or the fresh-student initialization rule.

## 2026-08-28 — Interpret the completed Ba result as strong degradation with partial retention

- **Decision:** Under run `pnfp_exp_ba_20260828_111148`, describe PN-FP as vulnerable under the tested same-size 3B direct-distillation setting. Detection fell from 956/1024 (93.359375%) in A2 to 98/1024 (9.5703125%) in Ba while the utility gate passed. Because Ba remains 9.47265625 percentage points above the canonical Base and retains 10.251046% of the teacher rate, do not claim complete removal or universal vulnerability.
- **Reason:** The paired watermark and utility results support a bounded attack-success interpretation, while the residual signal, single run/seed, 20k resource-bounded dataset, and missing Ba ordinary-generation diagnostic prohibit broader claims.
- **Decision:** Keep Bb, UP, and Dipper deferred until explicit user approval.

## 2026-08-28 — Define EverTracer Experiment A on the canonical 3B backbone

- **Decision:** Use the official `Xuzhenhua55/EverTracer` repository at commit `70b402f7b7456c6d94e1fae2de554d77dd6cd921` as primary implementation provenance. Because that commit has no license file, do not vendor its code; use project-owned compatibility wrappers that preserve the published algorithm.
- **Decision:** Freeze mutually disjoint XSum Dtr=100, Dref=1000 and Dunseen=100 subsets with seed 48. Train the target for 20 epochs and independent fresh-base reference for 4 epochs using LoRA rank 8, batch 4, LR 1e-4, packed block size 128 and BF16.
- **Decision:** Follow the paper's 4 reference epochs instead of the pinned README example's 10 epochs. Record this official-material discrepancy in the method log and final report.
- **Decision:** Verify with frozen T5-Base K=5 symmetric perturbation pairs at 30% token fraction, calibrated probability variation, AUC, and FSR defined as the maximum attainable TPR at empirical FPR <=5%. Reuse identical neighborhoods for teacher and canonical-base control.
- **Reason:** These settings preserve EverTracer's core natural-language memorization and reference-calibration design while adapting only backbone, precision, environment, utility suite, provenance manifests, and reload/control requirements to WMKD_Benchmark.
- **Boundary:** Experiment Ba, AG News, robustness attacks, automatic retuning/A2, destructive cleanup, and ModelScope upload are not authorized in this task.

## 2026-08-29 — Use the official 128-token EverTracer verification window

- **Decision:** Canonicalize each verification record with the fixed Llama tokenizer to the official packed `block_size=128` before applying the 30% T5 mask. Reuse that same 128-token window for suspect/reference probability calculations.
- **Reason:** The official XSum pipeline packs verification data into 128-token records. A provisional 512-token window produced 29 masks and deterministically exceeded the official T5 150-token fill budget; the approved 128-token alignment passed the representative T5 smoke with zero retries.

## 2026-08-29 — Continue EverTracer A from the infrastructure failure

- **Decision:** Preserve `evertracer_a_20260828_223155` as immutable FAILED and create continuation `evertracer_a_20260828_223155_cont1`. Reuse its target/reference merged artifacts without retraining or re-merging, and run only perturbation and downstream evaluation stages.
- **Decision:** Resolve `google-t5/t5-base@a9723ea7f1b39c1eae772870f3b547bf6ef7e6c1` through the pinned local snapshot with `local_files_only=True` and offline environment flags. Retain model ID, revision, local resolved path, and model SHA-256 in provenance.
- **Reason:** The parent completed all scientific training stages and failed only because the perturb loader attempted online Hub resolution while AutoDL networking was unavailable. This is an engineering continuation with no scientific configuration change.

## 2026-08-29 — Correct EverTracer detector direction through immutable continuation 2

- **Decision:** Preserve the official calibrated score `C = suspect PV - reference PV`, official labels `member=0/non-member=1`, and official high-score non-member threshold direction. For benchmark-readable fingerprint detection, report the mathematically equivalent `member=1, member_score=-C` AUC and member TPR at member FPR <=5%.
- **Decision:** Derive corrected metrics from continuation 1's saved per-sample scores without rerunning inference. Reuse the canonical neighborhoods SHA256 `7834e3d77704951ea06501c2166e960fef2b147ced3d751a8e55f07ec7b3672b` unchanged.
- **Decision:** Resolve the already prepared pinned ARC and TruthfulQA datasets through explicit project data-disk cache paths under forced offline mode; do not change the utility tasks or gates.
- **Reason:** Continuation 1 proved that inference outputs are complete but exposed a ROC label/threshold implementation error and a cache-environment propagation failure. Neither requires scientific retraining, perturbation regeneration, or verification inference.

## 2026-08-29 — Close the EverTracer A/Ba scientific design

- **Decision:** Treat the canonical Llama-3.2-3B-Instruct adaptation as the formal EverTracer reproduction, limited to XSum. Use the paper's four reference epochs, the approved 128-token verification window, and the corrected official/member-equivalent detector orientations.
- **Decision:** Accept root `evertracer_a_20260828_223155`, continuation 1 `evertracer_a_20260828_223155_cont1`, and continuation 2 `evertracer_a_20260828_223155_cont2` as one Experiment A lineage. The first two immutable failures were infrastructure/implementation corrections; target/reference scientific training configuration did not change and their valid artifacts were reused.
- **Decision:** Standardize EverTracer Ba as exactly 20,000 teacher-specific synthetic QA followed by fresh-canonical, same-size 3B, three-epoch full-parameter direct distillation. Prompt protocol may match PN-FP Ba, but all answers must be regenerated by the EverTracer A preferred teacher; PN-FP teacher/QA artifacts are prohibited.
- **Decision:** Interpret Ba student AUC 0.4987 and TPR 0.06 against the 0.5 random AUC baseline and Base TPR 0.05. Raw AUC retention is not the primary interpretation. The bounded result is approximately base/random-level detectability with functional tested utility, not a universal robustness claim.
- **Decision:** Keep EverTracer Bb NOT RUN/deferred. Do not infer authorization for paraphrasing, additional attacks, or a new experiment from closure.
- **Decision:** ModelScope source/archive verification and destination verification are distinct. The A teacher and Ba student remain `uploaded_to_modelscope_awaiting_destination_hash_verification` after source SHA and remote filename/count/size/blob-metadata checks. Only a future real download on another machine may establish `destination_verified`.
