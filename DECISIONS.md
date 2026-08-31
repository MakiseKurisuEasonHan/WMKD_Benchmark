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

## 2026-08-29 — Consolidate post-EverTracer durable protocol

- **Decision:** Keep `docs/EXPERIMENT_PROTOCOL.md` as the single canonical cross-session rules file and minimally update it after EverTracer rather than creating another rules document.
- **Decision:** A2/A3 designate scientific-configuration corrections; unchanged-science network, cache, infrastructure, pipeline, or downstream recovery uses an immutable continuation lineage where appropriate.
- **Decision:** Every watermark's Ba uses only its own preferred teacher to generate its own exactly-20k frozen QA and always initializes a fresh canonical unwatermarked student. Cross-watermark teacher, QA, frozen dataset, and student reuse are prohibited.
- **Decision:** Preserve the corrected EverTracer detector semantics, immutable continuation lineage, random-AUC interpretation, frozen-neighborhood dependency, archive state, and protected cleanup inventory as durable protocol.
- **Decision:** Current planning uses the latest observed EverTracer AutoDL capacity (208 container-visible vCPUs and approximately 1.0 TiB RAM); older 22-vCPU/110-GB records remain untouched historical observations.
- **Reason:** A new ChatGPT/Codex session must recover current policy and completed-method lessons from the repository without relying on conversation memory, while historical logs continue to describe what actually happened.

## 2026-08-29 — Select CTCC as the third method and stop on pinned-data mismatch

- **Decision:** CTCC is the explicitly authorized third watermark. Experiment A uses `Xuzhenhua55/CTCC@8db93218260bed31b8f18acc9c6ac3e1955d3a42`, canonical Llama-3.2-3B-Instruct, target `IAMALIVE`, LoRA SFT for 12 epochs at `1e-4`, cosine scheduling, cutoff 2048, no packing, rank 8, alpha 16, dropout 0, all compatible targets, BF16, physical batch 8, accumulation 2, and seed 48.
- **Decision:** Record weight decay `0.0` only as the default inherited by the official command in the pinned current Transformers runtime. The CTCC command omits the flag and does not pin LLaMA-Factory, so this remains a reproduction ambiguity rather than a uniquely paper-specified value.
- **Finding:** The pinned official files contain Trigger 461, Suppression 428, Normal 1000, total 1889—not the authorized 500/500/1000 total 2000. The test file contains 95/100/105 positional Trigger/Suppression/Normal records. The pinned repository does not define an automatic `IAMALIVE` detector implementation.
- **Decision:** Fail closed. Do not duplicate, synthesize, borrow, or silently resample records; do not launch Experiment A until the user/ChatGPT explicitly resolves the scientific count discrepancy. Do not start A2, Ba, Bb, another watermark, or ModelScope archival.

## 2026-08-29 — Resolve CTCC A public-artifact and detector ambiguities

- **Decision:** Formally use every record released at the pinned commit: Trigger 461, Suppression 428, Normal 1000, total 1889. Do not duplicate, synthesize, borrow, or modify records to reach the paper-reported 500/500/1000. Preserve the 2000-versus-1889 difference as a paper-vs-public-artifact discrepancy.
- **Decision:** Evaluate all 300 released test records as Trigger 95, Suppression 100, Normal 105. Preserve identity-based seen/unseen audit numbers, but do not call them the paper's official partition because no authoritative split metadata was recovered.
- **Decision:** Use the WMKD operational CTCC detector `generated_answer.strip() == "IAMALIVE"`, case-sensitive, for Base, Teacher, and any future Student. Preserve raw generations. Do not call this the official CTCC detector.
- **Decision:** These are resolved pre-launch reproduction ambiguities inside Experiment A, not a scientific reconfiguration requiring A2.
- **Decision:** Because the released CTCC repository does not pin LLaMA-Factory, use the project-owned Transformers 4.55.2/PEFT 0.17.1 compatibility trainer rather than following a moving LLaMA-Factory head. Preserve assistant-response-only multi-turn loss, PEFT `all-linear` as the operational equivalent of LLaMA-Factory `lora_target=all`, and all authorized hyperparameters; record this implementation adaptation in the report.

## 2026-08-29 — Accept CTCC Experiment A and preferred teacher

- **Decision:** Accept `ctcc_a_20260829_190251` as the completed CTCC Experiment A. Teacher/Base trigger activation is 95/95 versus 0/95; Teacher combined-negative false activation is 0/205 with zero generation errors.
- **Decision:** Utility remains functional despite bounded declines: ARC 0.446246→0.395051 and TruthfulQA MC2 0.505687→0.476817. Ordinary generation has no observed IAMALIVE leakage, prompt echo, or catastrophic repetition, and fresh reload passes.
- **Decision:** CTCC core reproduction is successful under the pinned-public-artifact setting and the adapter is the preferred CTCC teacher. This does not authorize Ba, Bb, ModelScope upload, another watermark, or destructive cleanup.

## 2026-08-29 — Launch-only monitoring for formal long tasks

- **Decision:** Formal long-running training, generation, evaluation, and preprocessing use an independent detached runner plus one launch health check; Codex must not continuously poll in the foreground. Model archival uploads remain foreground-supervised through command completion and remote repository verification.
- **Reason:** Scientific jobs must survive SSH/Codex disconnection without occupying the interactive task, while archival network transfers require explicit end-to-end verification.

## 2026-08-30 — Continue CTCC Ba generation after resume-cursor defect

- **Decision:** Preserve failed parent `ctcc_ba_generation_20260829_195943` byte-for-byte and create infrastructure-only continuation `cont1`. Recover the next prompt cursor as `max(prompt_index)` over parent/continuation raw and parse-error records plus one, fail on overlap, and keep all Teacher, prompt, sampling, parser, filter, deduplication, and freeze behavior unchanged.
- **Decision:** Raise only the combined-total-raw engineering fail-safe ceiling from 40,000 to 60,000; stop immediately once deterministic unique count reaches 20,000 and freeze exactly 20,000. This is not Ba2 and does not authorize Student training before the frozen manifest passes.
- **Reason:** The parent reached 40,007 raw but only 17,880 unique because the old resume cursor inferred consumed prompts from accepted-record count. Accepted records are not one-to-one with prompt calls, so `existing // records_per_prompt` can revisit consumed seed indices across increments.

## 2026-08-30 — Close CTCC Ba and archive its canonical artifacts

- **Decision:** Accept generation parent `ctcc_ba_generation_20260829_195943` plus infrastructure-only `cont1`, Student `ctcc_ba_20260830_025244`, and evaluation parent `ctcc_ba_eval_20260830_033556` plus infrastructure-only `cont1` as the complete CTCC Ba lineage. Neither continuation changes scientific configuration.
- **Decision:** Interpret Student Trigger 0/95 against Teacher 95/95 and Base 0/95 as loss of detectable CTCC trigger retention to the Base level under this tested same-family, same-size, hard-label direct-distillation setting. Student combined-negative activation is 0/205; ARC 0.483788 and TruthfulQA MC2 0.450614 plus ordinary-generation sanity establish functional tested utility. Do not generalize beyond this setting.
- **Decision:** Archive only the preferred Teacher LoRA adapter and the Student inference-ready `final_model` in their fixed private ModelScope repositories. Exclude checkpoints, optimizer/scheduler state, raw generation, and frozen20k data.
- **Decision:** The user-authorized replacement of ModelScope's automatically initialized README files with formal WMKD_Benchmark model cards is controlled metadata replacement, not a scientific deviation. Preserve `.gitattributes` and `configuration.json`.
- **Decision:** Both archives remain `uploaded_to_modelscope_awaiting_destination_hash_verification` with `destination_verified=false` after source and remote metadata verification. Only a future download on an independent destination followed by full SHA256 comparison may upgrade this state.

## 2026-08-30 — Consolidate canonical protocol after CTCC closure

- **Decision:** Continue using `docs/EXPERIMENT_PROTOCOL.md` as the single canonical cross-session rules file; do not create a parallel rule set.
- **Decision:** Persist method-specific detector semantics, fresh-reload evaluation, standardized utility, infrastructure-failure continuation, consumed-work resume cursors, Teacher-neutral oversampling, isolated speed tests, detached compute with launch-only monitoring, foreground-supervised ModelScope upload, controlled private-repository creation, and independent-destination SHA verification as durable defaults.
- **Decision:** Bb remains NOT RUN/deferred while all seven methods' A and Ba are completed first. A future UP implementation is not inherently limited to Dipper and still requires explicit scientific approval.
- **Decision:** PN-FP, EverTracer, and CTCC remain FULLY CLOSED (3/7). SCW is the fourth method to discuss, but this documentation audit does not authorize downloading or starting it.

## 2026-08-30 — Stop iSeal A at the pinned-code trainability gate

- **Decision:** Pin official `IntelliSys-Lab/iSeal@7e382321eef4355002acd93120d888dc9b45a8bd` and preserve its public zero-initialized delta/A/B plus full-`lm_head` trainable semantics for the mandatory audit; do not silently repair them.
- **Finding:** In two real optimizer steps on canonical Llama-3.2-3B-Instruct and 10 seed-42 AG News plaintexts, delta/A/B each had zero gradients and zero updates. The tied 394,002,432-parameter embedding/`lm_head` matrix had nonzero gradients and delta norm `6.019554`.
- **Decision:** Mark iSeal Experiment A `BLOCKED_BEFORE_FORMAL_RUN`, `preferred_teacher=NO`, and `ready_for_ba=NO`. This is an implementation/trainability blocker, not a completed scientific failure of iSeal.
- **Decision:** Any nonzero adapter initialization, removal of one zero factor, change in trainable blocks, untied/frozen head treatment, or optimizer-semantic change is a scientific configuration modification requiring explicit user/ChatGPT discussion before a formal A/A2 run.

## 2026-08-30 — Complete iSeal A5 and reserve the Teacher decision

- **Decision:** Accept `iseal_a5_20260830_063925` as completed A5 after sanity gate `iseal_a5_trainability_20260830_063618` passed. Relative to A4, the sole scientific change is adapter `inner_dim` 16→128; all data identities, key provenance, optimizer, initialization, freezing, detector, and utility semantics remain fixed.
- **Finding:** The released alternative `embed_adapter/Embed.py` at pinned commit `7e382321eef4355002acd93120d888dc9b45a8bd` uses inner dimension 128. This is code provenance, not a paper mandate.
- **Finding:** A5 improved registered-100 mean BLEU from A4's 34.865706 to 56.048270 and success from 15/100 to 66/100. Held-out remained 0/100 (mean 5.944563). ARC 0.401877, TruthfulQA MC2 0.518636, ordinary generation 10/10, and fresh reload passed.
- **Decision:** Set `preferred_teacher=REQUIRES_DECISION` and `ready_for_ba=NO` because registered ownership signal is substantially stronger but partial, while unseen-plaintext generalization is not established. Do not start A6 or Ba without explicit approval.

## 2026-08-30 — Select iSeal A6 as the preferred Teacher

- **Decision:** Accept gate `iseal_a6_trainability_20260830_131945` and formal run `iseal_a6_20260830_132300` as completed A6. Its sole A5 change is registered training count 100→200 at fixed inner dimension 128 and otherwise unchanged adapter-only protocol.
- **Finding:** The immutable A6 manifest preserves A5's original 100 and the fixed held-out 100 exactly, adds 100 unique records, and has digest `a68fff13eb0add1f64634e50235a232c3f00fcdcf5d543db942e40a5f3b7bbe9` with zero index/hash overlap.
- **Finding:** A6 achieved 179/200 full registered successes and improved the paired historical A5-100 subset from A5's 66/100 to 86/100. Ordinary generation remained 10/10 and fresh reload passed; held-out remained 0/100. ARC/TruthfulQA were 0.389932/0.477828.
- **Decision:** Select A6 as the final preferred iSeal Teacher and set `ready_for_ba=YES`. Held-out plaintext generalization is not established. Do not create A7 or start Ba without explicit authorization.

## 2026-08-30 — Close iSeal Ba and archive canonical artifacts

- **Decision:** Accept generation `iseal_ba_generation_20260830_134058`, frozen20k SHA256 `d51c22b9d33d4aa79b5cd733dd6bcb910ecd6378f1ffe2a40328e64cb085aacf`, Student `iseal_ba_20260830_165442`, and fresh-process evaluation as the complete Ba lineage.
- **Finding:** Primary registered success fell A6 179/200 → Student 0/200, equal to Base 0/200: an 89.5-point drop and 0% thresholded retention. Student ARC/TruthfulQA was 0.481229/0.449818; ordinary generation 10/10 and fresh reload passed.
- **Decision:** Interpret this only as reduction of registered-secret detectability to Base level under the tested standardized same-family, same-size direct-distillation setting.
- **Decision:** Archive only the inference-ready A6 Teacher and Ba Student privately. Exclude Student `training_args.bin`, checkpoints, optimizer state, generated QA, and raw key material.
- **Decision:** Both archives remain `uploaded_to_modelscope_awaiting_destination_hash_verification`, `destination_verified=false`; only future independent download plus full SHA256 may upgrade the state. iSeal is FULLY CLOSED; do not start Bb/A7.

## 2026-08-30 — Final iSeal closure and conservative cleanup outcome

- **Decision:** Repair only current-facing stale records in README/TODO/method documentation and add complete Ba generation accounting. Preserve all immutable A/A2-A5 blocked, failed, running, and non-preferred historical states.
- **Finding:** Ba generation accounting is 32,006 raw, 1,849 generation errors, 367 empty records, 10,464 duplicate tasks, 10,831 deterministic rejections, and 21,175 unique; exactly 20,000 were frozen. Canonical dataset SHA256 and physical-file SHA256 have different semantics.
- **Decision:** Keep canonical base, code deployment, A6 Teacher, Ba final Student, frozen20k, ModelScope manifests, shared infrastructure/cache, other-watermark artifacts, small provenance, and raw generation. A2-A5 non-preferred Teacher checkpoints and Ba checkpoint-7500 were identified as deletion candidates, but destructive review rejected deletion before execution. No workaround was attempted; actual deletion and bytes freed are zero.
- **Decision:** iSeal remains FULLY CLOSED with no scientific blocker. Selecting the fifth watermark is the next scientific task and is not authorized by this closure.

## 2026-08-31 — Consolidate fixed protocol after iSeal closure

- **Decision:** Keep `docs/EXPERIMENT_PROTOCOL.md` as the single canonical cross-session rule source. Add the complete iSeal A→A6→Ba lineage, cross-method metric semantics, trainability/tied-weight lessons, final authorized cleanup outcome, current environment/billing state, and explicit SCW-next boundary without creating a parallel rules file.
- **Decision:** Record the later authorized cleanup outcome alongside the earlier rejected attempt: after exact realpath and safety checks, delete only A2-A5 non-preferred Teachers and Ba `checkpoint-7500`, then verify all protected artifacts. Logical deletion was 47,429,470,039 bytes; filesystem used-space reduction was 47,429,681,152 bytes.
- **Decision:** Current AutoDL is the 22-vCPU/110-GB/approximately-500-GB pay-as-you-go instance. Older 208-vCPU/approximately-1-TiB capacity remains truthful historical provenance, not current planning state.
- **Decision:** PN-FP, EverTracer, CTCC, and iSeal remain FULLY CLOSED (4/7). SCW is the fixed fifth watermark and next discussion target, but this audit does not authorize clone, download, configuration, or Experiment A execution.

## 2026-08-31 — Prepare SCW Experiment A locally without execution

- **Decision:** Select SCW as the fifth method and pin official `eth-sri/robust-llm-fingerprints@15bc1929569357130f2dbc0b09f91bbf4f4bd947`, licensed under Responsible AI SOURCE CODE License 1.1. Do not vendor/copy official source or use legacy project implementations.
- **Decision:** Fix Experiment A to canonical Llama-3.2-3B-Instruct, French semantic condition, KGW gamma 0.25/delta 4/k 1/`simple_1`, LucieFr/AlpacaGPT4/OpenWebText at 0.6/0.2/0.2, lambdas 1/1/1, full-parameter batch 4 × accumulation 16, LR 2e-5, 2500 steps, Adafactor, cosine, warmup 0.1, sequence 512, and gradient checkpointing false initially.
- **Decision:** Preserve official aggregate detector semantics: tokenize with padding, concatenate/flatten completions and masks, one KGW p-value, `p<1e-3` positive. Fix and record permutation seed 42 for reproducibility; supplementary 10/25/50/100/250/500/1000 points use prefixes of the same fixed generations/order and never replace the primary 1000-query result.
- **Decision:** Treat `caching_models=true`, `PYTHONHASHSEED=42`, immutable run-directory control, and explicit runtime dtype/trainable-parameter assertions as wrapper-layer reproducibility/safety adaptations. They do not change data, loss, optimizer, batch semantics, steps, or watermark mechanism. Official source remains unedited.
- **Decision:** This task authorizes local source audit, config/code/tests/docs only. AutoDL/La Trobe/GPU, model/dataset downloads, training, formal generation/evaluation, A2, Ba, ModelScope, and cleanup remain prohibited.
## 2026-08-31 — SCW runtime preflight and speed-test boundary

- AutoDL received the exact local source state at `de4880db573a2c43aa27efe2f18a61f815166a43`; the pre-existing dirty AutoDL checkout was preserved intact in a data-disk deployment backup rather than overwritten or deleted.
- Official SCW source is fixed at `eth-sri/robust-llm-fingerprints@15bc1929569357130f2dbc0b09f91bbf4f4bd947` under Responsible AI SOURCE CODE License 1.1, with zero official-source modifications.
- Runtime provenance is fixed to canonical Llama revision `0cb88a4f764b7a12671c53f0838cd831a0843b95` and immutable LucieFr/AlpacaGPT4/OpenWebText/FrenchEvaluation dataset revisions recorded in the SCW manifest.
- The HF mirror host rewrite, dataset revision injection, speed-only model-save suppression, telemetry, and numeric-string LR guard are infrastructure adaptations only. The LR guard converts a group LR only when its parsed value exactly equals the configured `2e-5`; all other cases fail closed.
- Runtime preflight is READY, but the bounded recommendation after speed test is `RUNTIME_ADAPTATION_NEEDED`: 4/4 steps completed and metrics are usable, yet Python aborted during PyArrow/GIL interpreter finalization after `train_end`. Formal A remains NOT RUN pending an explicit next decision.

## 2026-08-31 — SCW terminal-cleanup investigation remains blocked

- **Finding:** `scw_speed_terminalfix_20260831_01`, `_02`, and `_03` each completed 4/4 optimizer steps and `train_end`, then died with the same SIGABRT during CPython finalization. `_03` also emitted both Trainer-level teardown and late atexit-GC telemetry before aborting.
- **Decision:** Exact official pins (`pyarrow 21.0.0`, `aiohttp 3.12.15` and its pinned stack), releasing the streaming source chain, stopping/resetting fsspec, and late GC are insufficient. Revert these unproven code changes; never mask the abort with `os._exit(0)` or reinterpret FAILED as success.
- **Boundary:** Formal A and Ba remain NOT RUN. No fourth GPU retry is authorized by this investigation. The next bounded candidate is a clean Python 3.11 environment or an upstream-confirmed native-extension fix, followed by one identical 4-step clean-exit gate.

## 2026-08-31 — SCW finite materialized-stream adaptation

- **Finding:** Python 3.11 reproduced Python 3.12's post-4/4, post-`train_end` `PyGILState_Release` SIGABRT, so Python-version and dependency sweeps are no longer justified. Official code tokenizes/packs each streaming source, assigns label IDs, shuffles with Python-hash-derived seeds, and probabilistically interleaves 0.6/0.2/0.2 with `all_exhausted`.
- **Decision:** Do not substitute `streaming=False` or reconstruct an approximate mixture. A scientifically acceptable wrapper must enumerate and freeze the actual official post-preprocess/post-shuffle/post-interleave prefix, preserving every token, mask, label, occurrence, and order.
- **Decision:** The fixed single-GPU contract consumes exactly 2,500 × 16 × 4 = 160,000 examples. Preserve stochastic observed source proportions; never rebalance to exact 60/20/20 or deduplicate.
- **Decision:** The prepared wrapper/materializer/manifest/local sequential iterable is conditionally `RUNTIME_DATA_ACCESS_ADAPTATION`, not A2, because scientific data/loss/order remain fixed and only transport changes. Official source remains unmodified.
- **Boundary:** Local synthetic tests are necessary but not sufficient. Formal A remains blocked until a separately authorized AutoDL materialization passes immutable audit and one four-step local-materialized gate exits cleanly. Failure of exact audit changes the verdict to `MATERIALIZATION_NOT_SCIENTIFICALLY_SAFE`.

## 2026-08-31 — SCW resumable pinned-Parquet cache

- **Finding:** HF/datasets retried the pinned LucieFr shard from byte 0 after `IncompleteRead`; the inferred 289,899,066-byte response was not authoritative. Pinned mirror metadata identifies an 824,184,452-byte Xet object with SHA256/x-linked-etag `a78e663cfddc361d3f54e634793b9cb3b0f028e10a8d40ad523324e6bd350228`.
- **Decision:** Use a wrapper-only, on-demand `.part` cache with `curl --continue-at -`; verify authoritative size, SHA256, Parquet footer/schema and row groups before serving the exact bytes. Cached Range reads receive local HTTP 206 semantics; uncached bounded Range probes stay bounded, while only an official full GET triggers full resumable prefetch.
- **Boundary:** Dataset repositories, revisions, official preprocessing/interleave/loss semantics, scientific configs, and official source are unchanged. Classification is `NETWORK/CACHE INFRASTRUCTURE FIX`, not A2.
# 2026-08-31 — SCW deterministic finite-stream sampling adaptation

- SCW remains Experiment A because Formal A and the 4-step gate never started in prior infrastructure attempts.
- Adopt `DETERMINISTIC_FINITE_STREAM_SAMPLING_ADAPTATION`: NumPy `Generator(PCG64(42))` draws a fixed 160,000-label schedule with probabilities 0.6/0.2/0.2; each pinned source is extracted in repository-path/shard order through unmodified official preprocessing, then assembled according to that schedule.
- This changes only the finite sampling realization. It is explicitly not byte-identical to the official online streaming/shuffle realization. Dataset/model revisions, labels/losses, model, optimizer, LR, batch/accumulation, sequence length, and 2500-step contract remain unchanged.
- Historical streaming/network/cache failures and partial/verified caches remain immutable evidence. No A2 and no Ba are authorized.

## SCW materialized orchestrator `scw_deterministic_full_20260831_213700` — 2026-08-31T12:31:33.423144+00:00

- State `FAILED`; stage `DETERMINISTIC_FINITE_STREAM_BUILD`; Formal A started `False`; Ba `False`.
- Materialization `/root/autodl-tmp/WMKD_Benchmark_data/runs/scw/materialized_stream/scw_materialized_20260831_203129`; status `/root/autodl-tmp/WMKD_Benchmark_data/runs/scw/orchestrators/scw_deterministic_full_20260831_213700/pipeline_status.json`.
