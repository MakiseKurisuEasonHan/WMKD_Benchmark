# WMKD_Benchmark Formal Experiment Protocol

This is the canonical, durable project protocol. Every new ChatGPT/Codex session must read it together with `PROJECT_STATUS.md`, `TODO.md`, `DECISIONS.md`, `EXPERIMENT_LOG.md`, and the relevant dedicated experiment log before acting. Historical logs preserve what actually happened; this file defines current policy.

## Project identity and decision authority

WMKD_Benchmark benchmarks robustness/stability of LLM ownership-verification methods under knowledge distillation and related model-extraction attacks, with the long-term goal of an ICLR/top-conference paper. The ten selected methods are, in benchmark order: PN-FP, EverTracer, CTCC, iSeal, SCW, LLMPrint, REEF, HuRef, AWM, and ZeroPrint. PN-FP, EverTracer, CTCC, iSeal, and SCW are proactive/embedded ownership signals; LLMPrint, REEF, HuRef, AWM, and ZeroPrint are passive/intrinsic ownership fingerprints. Use “ownership watermarking / fingerprinting methods” or “ownership-verification methods” for the combined benchmark rather than describing all ten as embedded watermarks.

The standard workflow is user → ChatGPT research discussion → explicit execution prompt → Codex implementation → copy-ready Codex handoff → ChatGPT discussion. Codex communicates with the user in Chinese and does not independently make major research-design decisions. Changing the backbone or revision, dataset scale/protocol, distillation protocol, watermark core method, long-term paths, Git identity/remotes, model-repository identity, or destructive cleanup policy requires an explicit user/ChatGPT decision unless already fixed here.

At the end of every Codex task, provide a copy-ready `给 ChatGPT 的总结：` covering actions, changed files, run ID, results, blockers, Git state, work not done, and the next allowed step.

## Canonical closure state before proactive Bb — 2026-09-03

All ten methods have completed their preferred A/A2 (iSeal ultimately A6) reproduction and Ba evaluation. Proactive Ba final results are: PN-FP Teacher/Student `956/1024 → 98/1024`; EverTracer AUC/TPR `1.0/1.0 → 0.4987/0.06`; CTCC trigger `95/95 → 0/95`, Base `0/95`, Student negatives `0/205`; iSeal registered success `179/200 → 0/200`, Teacher/Ba/Base mean BLEU `69.171651/2.589326/2.332514`; SCW Teacher/Base/Ba p-values `0/0.9199569225/0.8440861702`. SCW French exposure `26/20000 = 0.13%` is diagnostic only. These support Teacher-before versus final-Student-after comparisons; no complete checkpoint-detector trajectory exists, so exact disappearance step/epoch is **NOT ESTABLISHED** and must not be inferred from loss, learning rate, or gradient norm. `KD survival ≈ exposure × information preservation × learnability` is a hypothesis, not universal causality.

Passive Shared Ba is COMPLETE, dataset SHA256 `eb90c3e0c95e37d07bf0f099aaeabeedf1779bae7ef8a4aacf25e3fb8bed6ab7`, 5/5 detectors positive, utility ARC `0.4974402730`, TruthfulQA `0.4755413057`. Original Passive Bb is `BLOCKED_AT_PILOT` after pilot/cont1–cont5 because atomic `tech` repeatedly exposed an instruction-echo validation gap. Passive Bb2 is `BLOCKED_AT_PILOT`: even with an exact-source fallback instruction, `tech` still produced transformation meta-commentary. The frozen tokenizer audit uses `add_special_tokens=False`: `<=1` 4,635 (23.175%), `<=2` 7,577 (37.885%), `<=3` 8,698 (43.490%), `<=5` 9,791 (48.955%); all known recurrent failures were one token.

Passive Bb3 is the finalized standardized UP reference: when the frozen Qwen non-special-token count is `<=1`, set `final_answer = source_answer` and `processing_mode = atomic_identity_preserved`; otherwise apply semantic-preserving untargeted paraphrasing with `Qwen/Qwen2.5-3B-Instruct`, prompt SHA256 `7f4284788b5147bca7f444db989eab6f2f9f3a10eb06fddb309fc06748414495`, `do_sample=true`, temperature `0.7`, top-p `0.9`, seed `42`, followed by Ba-style direct behavioral distillation. The protocol is detector-, watermark-, and method-agnostic.

Run `passive5_shared_bb3_20260903_164929` is COMPLETE: 20,000 final records; 4,635 atomic identities; 15,365 Qwen submissions; 13,061 paraphrases; 2,256 natural identities; 48 fallbacks; 279 rejected attempts; zero final leakage, control-token leakage, and truncation; runtime 7,484.502 s; dataset/frozen-file SHA256 `549d38ca634c2c69a646e23d1bfc65ec019887e43070deec031f97459cc7be99` / `60bd4539b5d332b076a92072b86b51f8ddad3749a0a166f594233f5c1730dd88`. Its fresh canonical Student completed 7,500/7,500 steps in 2,022.706 s with final loss `0.962497413953`, fresh reload PASS, and zero non-finite parameters.

Frozen detector Reference/tau/Ba/Bb3 results are: LLMPrint `1/0.7150049776/0.82/0.785`; REEF `1/0.4546738923/0.9542220066/0.967286`; HuRef `99.9999923706/4.1198940277/99.9989852905/99.998734`; AWM `1/0.00179533649/0.9999974136/0.999996`; ZeroPrint `1/0.6793505996/0.8399372697 rescaled/0.917022`. Final: 5/5 detected. Bb3 utility is ARC `0.4906143345`, TruthfulQA `0.4544162042`, English/French sanity PASS. Required wording: **Under the tested same-backbone standardized behavioral-distillation setting, Bb3 preprocessing did not reduce any of the five passive ownership fingerprints below its frozen detector threshold.** Required limitations: same canonical backbone family; no evidence of fingerprint transfer; no universal immunity claim; atomic identity is 4,635/20,000 = 23.175%.

The canonical inventory `results/passive5_modelscope_inventory.json` records four verified PRIVATE artifacts: Shared Ba frozen20k and Student, plus Shared Bb3 processed20k and Student. Do not duplicate-upload them. The global `results/experiment_full_logs_index.json` contains 26/26 unique formal objects with no broken paths. Every future formal scientific object requires `full_experiment_log.json`; unavailable data stays null/unavailable/not-recorded rather than invented.

`PROACTIVE_BB_PROTOCOL_FROZEN = YES` for PN-FP, EverTracer, CTCC, iSeal, and SCW. Each formal Experiment Bb uses its own canonical Ba frozen20k, exact validated Passive Bb3 scientific preprocessing, its own processed20k, an independent fresh-canonical Student, Ba-identical training, the exact method-specific frozen detector, and Ba-matched utility. Passive methods could share one dataset/Student because they share one Reference; proactive Teachers differ, so Teacher answers, frozen20k, processed20k, and Students must never be shared across these five methods. Framework, Qwen model/tokenizer, frozen prompt, UP implementation, retry/validation, SFT/utility infrastructure, and logging may be shared. Formal Bb execution remains `NOT_STARTED` until separately authorized.

## Isolation, machines, and VPN

WMKD_Benchmark is strictly independent of WaterBench, WaterBenchV2, WaterBenchV3, `watermark_benchmark`, and every legacy watermark/distillation project. Do not read, reuse, write, delete, or share their directories, repositories, checkpoints, results, caches, queues, runners, or runtime state unless a specific future instruction authorizes it.

- Local Windows checkout `C:\Users\Eason\Desktop\WMKD_Benchmark`: primary source development, configuration, documentation, project state, and Git.
- GitHub `MakiseKurisuEasonHan/WMKD_Benchmark`: small reproducibility artifacts and recovery.
- AutoDL checkout `/root/autodl-tmp/WMKD_Benchmark`: disposable compute-side code. Before giving manual AutoDL connection instructions state **学校 VPN：关闭**.
- AutoDL data root `/root/autodl-tmp/WMKD_Benchmark_data`: all large compute artifacts and project-owned caches.
- La Trobe lightweight checkout `/data/home/ad/21672330/WMKD_Benchmark` and warehouse `/data/shared/nobackup/21672330/WMKD_Benchmark`: long-term storage. Before giving manual school-server connection instructions state **学校 VPN：开启**.

Current formal AutoDL environment/hardware baseline: Ubuntu 22.04, Python 3.12, PyTorch 2.8.0, CUDA 12.8, one RTX PRO 6000 96 GB GPU, Intel Xeon Platinum 8470Q with 22 vCPUs, 110 GB RAM, a 30 GB system disk, and approximately 500 GB data capacity composed of 50 GB free storage plus 450 GB paid storage. These are current point-in-time operational records, not a scientific protocol or a capacity guarantee. Historical logs truthfully recording an older 208-container-vCPU, approximately 1 TiB RAM, approximately 1 TiB data-disk instance must not be rewritten.

The current AutoDL instance is pay-as-you-go rather than on a weekly package. When no scientific workload is active, shutdown may save GPU charges, but shutdown releases the GPU allocation and later inventory may be unavailable; paid storage may continue charging while powered off. Billing considerations must never reduce scientific completeness or authorize cleanup. Models, checkpoints, datasets, caches, and large outputs must stay under the data root and must never fill the system disk.

For every model, tokenizer, dataset, repository, dependency, evaluation resource, auxiliary pretrained model, checkpoint, or large binary, first check the current local/AutoDL project paths and project/shared cache. If absent, the default transport priority is: local existing resource → project/shared cache → ModelScope → trusted domestic mirror → Hugging Face mirror → PyPI mirror → trusted GitHub proxy → official overseas source. Multi-GB overseas downloads must not be allowed to stall for long before a trustworthy domestic transport is considered.

A mirror is transport acceleration only, never scientific provenance. Record `canonical_upstream`, exact model/dataset identity, revision/version/commit, `transport_source`, file list, sizes, and integrity verification. Never substitute a model, version, dataset, checkpoint, or scientific content for download convenience. If equivalence to the canonical upstream cannot be established, stop and report the blocker.

## Experiment names and lifecycle

- **Experiment A:** first formal watermark reproduction.
- **Experiment A2/A3/...:** immutable corrected later reproduction when a previous A's **scientific configuration** produced an unsuitable result and requires a formal correction. Never overwrite or erase the earlier run or its scientific meaning.
- **Experiment Ba:** Direct Distillation, formally defined as offline hard-label sequence-level behavioral distillation.
- **Experiment Bb:** answer-only Untargeted Paraphrasing followed by Distillation (UP + Distillation).

Passive Shared Bb and Bb2 are immutable `BLOCKED_AT_PILOT` histories; Passive Shared Bb3 is COMPLETE and is the current validated UP reference. The next proactive attack remains named **Experiment Bb**, not Bb3, unless a future explicit scientific decision changes it. Reusing the finalized Passive Bb3 implementation does not rename the proactive experiment or authorize execution.

Each formal experiment has an immutable run namespace. Run IDs use `<method>_<experiment>_YYYYMMDD_HHMMSS`; a corrected or continued run receives a new ID. If the scientific configuration is unchanged and the failure is only network, cache, infrastructure, pipeline implementation, or a downstream stage, use an immutable continuation lineage where appropriate rather than automatically renaming the experiment A2. Never overwrite or silently resume failed, limited, or completed history.

## Canonical backbone

Unless an explicitly approved and documented method-specific exception exists, all A and Ba experiments use `meta-llama/Llama-3.2-3B-Instruct` revision `0cb88a4f764b7a12671c53f0838cd831a0843b95`. The canonical AutoDL copy is `/root/autodl-tmp/WMKD_Benchmark_data/models/base/Llama-3.2-3B-Instruct`; it must never be deleted, overwritten, or silently modified. Its preserved verification is 12 canonical files, 6,434,748,511 bytes, 12/12 SHA256 passed.

This fixed family, size, revision, tokenizer, and template maximize horizontal comparison across watermark methods and vertical comparison before/after distillation. Incompatibility is a blocker, not permission to substitute a model. Record it, discuss it, obtain explicit approval, and label any approved exception in configuration, log, summary, and report.

## Standard Ba protocol

Ba follows the general behavioral/direct-distillation idea of ACL 2025, “Can LLM Watermarks Robustly Prevent Unauthorized Knowledge Distillation?”:

```text
CURRENT watermark's own preferred watermarked 3B teacher
→ teacher-generated synthetic QA
→ filtering, parsing, deduplication, and a frozen dataset
→ fresh canonical unwatermarked 3B student
→ supervised fine-tuning
→ watermark and utility evaluation
```

The student **must** initialize from a fresh canonical unwatermarked Llama-3.2-3B-Instruct. Never initialize the student from teacher weights. Each watermark **must generate its own Ba answers from its own preferred teacher**. Never reuse another watermark's teacher, teacher-generated QA, frozen 20k dataset, or student checkpoint. The standardized prompt source/distribution, generation infrastructure, parsing/filtering/deduplication code, exactly-20k freeze framework, training configuration, utility framework, runner, logging, reporting, and email infrastructure may be reused.

The canonical Ba reference protocol is exactly 20,000 frozen instruction/input/answer QA samples, full-parameter SFT, 3 epochs, learning rate `1e-5`, BF16, and batch size 8, with remaining fields taken from the existing method-specific canonical Ba configuration. Any method-specific exception requires explicit prior discussion and documentation; do not silently change the protocol.

Teacher-dependent duplicate rates may differ. Use the same standardized prompts, sampling, parser, filters, and deterministic deduplication for every method, and increase raw generation only through the fixed oversampling policy until exactly 20,000 unique records can be frozen. Never copy or hand-fill samples, loosen filtering or deduplication, or change the prompt protocol post hoc for one Teacher. Raw-to-unique efficiency is engineering provenance, not watermark robustness.

Resume position must come from the identity of work actually consumed, never an output-count estimate such as `existing_candidates // records_per_prompt`. Standardized QA generation reconstructs consumed `prompt_index` values from both raw-candidate and generation-error records and resumes at `max(consumed prompt_index) + 1`. Paraphrase processing uses a durable per-`sample_id` journal with `attempt_count`. Every continuation must fail closed unless the cursor is monotonic, deterministic, and non-overlapping.

## Detector and evaluation principles

WMKD_Benchmark does not impose one detector across watermark methods. Each method uses its method-specific detector and preserves exactly the same detector semantics between A and Ba. The benchmark standardizes backbone, distillation attack, Student protocol, utility panel, and Teacher/Base/Student comparison; it does not force incomparable detectors into one metric. Detector provenance, formula, sign, labels, threshold direction, ROC semantics, and any benchmark operational adaptation must be explicit.

Raw detector units are not interchangeable across methods: PN-FP reports match rate, EverTracer reports AUC/TPR, CTCC reports trigger activation, iSeal reports BLEU plus registered-secret thresholded success, and SCW reports an aggregate KGW statistical p-value. Never label every `Student score / Teacher score` ratio as a common “watermark retention” metric. In particular, AUC near 0.5 is random discrimination, not approximately 50% watermark retention; an SCW p-value is not a linear watermark-strength scale and must never be divided Teacher-to-Student. Cross-method comparison preserves each native detector and reports whether the Teacher is detectable, whether the Student is detectable, whether Base/random is the relevant regime, absolute degradation where mathematically valid, utility, and a bounded outcome.

Final scientific evaluation for both A and Ba must fresh-reload the saved artifact; evaluation of only the in-memory training model is insufficient. The standardized utility panel is ARC Challenge, TruthfulQA MC2, and ordinary-generation sanity. A method-specific paper utility measure may be added but cannot replace this panel.

## Scientific fidelity and minimal preflight

Protect both watermark strength and model utility so the teacher remains scientifically usable for later distillation. Do not remove important original-paper regularization or utility-preserving mechanisms merely to save time. Speed/resource adaptations are allowed only when scientific meaning remains intact; record the paper setting, benchmark setting, reason, and consequence.

Before a formal run, minimally confirm isolation, model/revision, tokenizer/template, seed, dataset/provenance, key method/training configuration, runner/output path, storage, GPU availability, and that declared settings are actually consumed at runtime. Then run. Do not add speculative audit layers merely to pursue perfect certainty; diagnose concrete failures specifically.

If a large stage has unknown runtime, a small representative speed test is allowed before the formal run. It must use an isolated namespace, cannot become formal data or a training continuation, and records only engineering estimates such as samples/s, tokens/s, seconds/step, and ETA. A speed test never authorizes a scientific-configuration change.

## Formal execution and notifications

GPU-heavy training, generation, and evaluation must use a project-owned independent detached runner (`nohup` + `setsid`, `tmux`, or an equivalent robust launcher) so closing Codex or SSH cannot terminate the run. Run one large GPU task at a time unless explicitly approved; never kill or interfere with unrelated processes.

For every formal long-running training, generation, evaluation, or preprocessing job, Codex performs only one launch health check (detached PID/status, growing log, GPU activity, immediate traceback/OOM, and STARTED notification) and then returns control. Continuous foreground polling or SSH wait loops are prohibited by default; later status checks occur only when the user explicitly requests one. Temporary continuous monitoring is a per-run exception only when the user explicitly says “这次监控”; it does not change the canonical default. This does not stop or pause the detached runner.

Every formal run exposes and durably records run ID, PID, detached-session/launcher identity, status JSON, logs, result JSON or equivalent, timestamps, exit code, terminal state, failure reason, configuration, source revision, and artifact paths. A mandatory-stage failure preserves evidence, marks the run failed, and stops downstream stages. Engineering completion and scientific success remain separate judgments.

Infrastructure failure is not scientific failure. A network, cache, import, deployment, model-loading, post-processing, or evaluation failure does not invalidate an already valid training artifact. If scientific configuration is unchanged, preserve the failed parent, reuse valid artifacts, and recover through an immutable continuation rather than retraining by default or renaming the experiment A2/Ba2.

Formal lifecycle email notifications are best-effort: `STARTED`, `COMPLETED`, and `FAILED` or another meaningful premature termination. Credentials remain in a mode-600 file outside Git and must never appear in source, logs, output, or conversation. Notification failure is operational and never automatically makes a scientific run fail. See `docs/EMAIL_NOTIFICATIONS.md`.

## Durable logging and reports

Every Codex task updates the appropriate existing project state/log records. Every formal experiment writes durable machine-readable data rather than relying on terminal output, including environment, actual configuration, source/model revision, dataset provenance, seed, run ID, timing, metrics, checkpoint/reload state, failures, and artifact paths.

`EXPERIMENT_LOG.md` is the concise index. Each completed formal A/Ba experiment automatically produces all three of:

1. a dedicated immutable experiment log under `docs/experiment_logs/`;
2. a formal report under `docs/reproduction_reports/`;
3. a small machine-readable summary under the method's canonical `results/` namespace (legacy PN-FP summaries remain under `results/summaries/`).

The formal report includes objective, environment table, configuration table, original-paper versus benchmark comparison, training results, watermark results, utility results, checkpoint/reload validation, deviations, limitations, artifact/archive state, and a bounded scientific conclusion. The user does not need to request these separately.

Every formal A/Ba/Bb scientific object requires a canonical `full_experiment_log.json`; a summary, terminal log, or Markdown report alone is insufficient. It must cover identity, provenance, environment, scientific configuration, training telemetry, stage timeline, generation, detector semantics/results, utility, artifact lineage, failure/continuation history, ModelScope state, watermark-loss-analysis support, and bounded conclusion. Historical facts that were not recorded remain `null`, `unavailable`, or `not-recorded`; never invent them. The global index is `results/experiment_full_logs_index.json`, schema `wmkd.full-experiment-log-index.v1`. The current 2026-09-03 closure has 26/26 unique indexed formal objects with valid paths and SHA256; every future object must be added with the same checks. The older 10-object and 21-object audits remain historical records.

Watermark-disappearance claims require detector evidence. Teacher-before versus final-Student-after is supported for all five completed Ba experiments, but exact intermediate disappearance localization is supported for 0/5: none retained the complete combination of intermediate Student checkpoint, generation, and method-specific detector evaluation. Loss, gradient norm, learning rate, timing, or telemetry may describe training dynamics but cannot establish “the watermark disappeared at step X.” Future methods must inventory retained intermediate checkpoints, but adding checkpoint-level detector evaluation is a separate scientific/analysis-protocol decision requiring user/ChatGPT approval.

## Artifact retention and ModelScope transfer

After successful A/A2 and Ba, normally preserve the preferred canonical watermarked teacher and canonical distilled student in private ModelScope for future fine-tuning, extraction, pruning, quantization, merging, and other attacks. Do not delete a canonical final model on AutoDL until its archive gate is satisfied.

Formal experiments use detached runners, but ModelScope uploads normally remain **foreground and supervised by the current Codex task** until upload and efficient verification finish. Do not detach an upload unless explicitly approved.

An approved private ModelScope repository may be created either manually by the user or through a controlled SDK workflow; manual web creation is not mandatory. A newly initialized repository may already contain `README.md`, `.gitattributes`, or `configuration.json`. Never silently overwrite conflicting remote metadata; obtain explicit authorization for controlled replacement.

Default transfer protocol:

1. Freeze the canonical source file list, byte counts, per-file SHA256 values, and immutable manifest.
2. Upload to the approved private ModelScope repository.
3. Verify remote filenames, file count, individual sizes, and ModelScope blob/content consistency where available.
4. Record `uploaded_to_modelscope_awaiting_destination_hash_verification`.
5. Do **not** normally download the whole model back to the same source AutoDL host solely for verification.
6. At a real future destination, download, recompute every SHA256, compare the immutable source manifest, then mark `destination_verified`.

PN-FP A2 did not perform a full 6.43 GB remote re-download and remains awaiting destination verification. PN-FP Ba performed a valid stronger authenticated same-source remote re-read (8/8 canonical and 2/2 metadata passed), but it added approximately 37.6 minutes and does not replace future destination verification. See `docs/storage/artifact_transfer_protocol.md`.

## Git safety and closure

Git tracks only code, scripts, configs, docs, small JSON, summaries, manifests, and reports. Never commit model weights, checkpoints, optimizer states, raw large datasets, caches, tokens, `.env` secrets, Gmail App Passwords, or SSH private keys. Inspect status/diffs/remotes, scan for secrets and large artifacts, run appropriate lightweight checks, and never force-push or rewrite history without explicit approval.

At a meaningful closure point require `HEAD == origin/main`, ahead/behind `0/0`, and a clean working tree. No task may push to a legacy repository.

## PN-FP preserved lesson and closed state

PN-FP Experiment A achieved 1019/1024 versus base 1/1024, but ordinary generation was severely degraded because the initial speed-oriented adaptation omitted important utility-preserving original-method regularization, especially WA/DM. This history must remain visible.

Experiment A2 corrected the design with WA `0.75` and DM `0.25`, achieved 956/1024 = 93.359375%, and passed utility and reload gates. Experiment Ba initialized a fresh canonical unwatermarked student and achieved 98/1024 = 9.5703125%, an 83.7890625 percentage-point drop and approximately 10.251046% retention; utility and reload passed. The bounded conclusion is substantial watermark degradation with residual signal above the base level under the tested standardized same-size 3B direct-distillation condition.

PN-FP A, A2, and Ba are CLOSED. Bb is NOT RUN/deferred. There is no PN-FP scientific blocker. Large PN-FP AutoDL training/readback artifacts were cleaned with approximately 48 GiB reclaimed while the canonical base was preserved. Preferred artifacts are private at `MakiseKurisuEasonHan/WMKD-PNFP-A2-Teacher` and `MakiseKurisuEasonHan/WMKD-PNFP-Ba-Student`.

## EverTracer preserved lessons and closed state

EverTracer Experiment A used the canonical backbone and XSum. Target settings were `Dtr=100`, 20 epochs, batch 4, learning rate `1e-4`, LoRA rank 8, and block size 128. Reference settings were `Dref=1000`, 4 epochs, and block size 128. The paper specifies 4 reference epochs while its README example uses 10; the benchmark follows the formal paper setting. Verification used `K=5`, perturb fraction `0.3`, T5-Base, block size 128, and reference-calibrated probability variation.

The immutable A lineage is part of the scientific record:

- Root `evertracer_a_20260828_223155`: Target/Reference training and merge succeeded; a later perturb stage failed because T5 loading attempted online resolution while AutoDL networking was unavailable.
- Continuation `evertracer_a_20260828_223155_cont1`: offline T5 loading was fixed and perturb plus Teacher/Base inference succeeded; a later utility stage failed because ARC could not resolve offline. Audit also found detector-direction semantics were wrong. Neither failure required Target/Reference retraining or neighborhood regeneration.
- Continuation `evertracer_a_20260828_223155_cont2`: completed with corrected aggregation semantics.

The official calibrated score is `C = suspect PV - reference PV`, with `member=0`, `non-member=1`, and higher `C` indicating non-member. The equivalent member-oriented benchmark representation is `member=1`, `score=-C`. The calibrated score numbers were correct; the historical bug was the ROC positive-class and threshold direction. Detector audits must check probability/loss transformation, formula, subtraction order, sign, labels, threshold direction, and ROC semantics. An extreme AUC such as exactly 0.0 triggers an implementation-direction audit before scientific interpretation. Infrastructure failure is not automatically scientific failure, and unchanged-science engineering recovery may remain Experiment A through continuation.

The completed A result was Teacher member-oriented AUC `1.0000` and TPR@FPR<=5% `1.00`, versus Base AUC `0.4417` and TPR `0.05`. ARC Base/Teacher was `0.446246/0.421502`; TruthfulQA Base/Teacher was `0.505687/0.514798`; ordinary-generation sanity and reload passed. EverTracer core reproduction therefore succeeded and A is the preferred teacher.

EverTracer Ba used only the EverTracer A teacher. Oversampling produced 15,562/16,752/17,904/19,051 unique records from the 24k/26k/28k/30k prefixes; 32k produced 20,173 unique records. Exactly 20,000 were frozen with SHA256 `ca1aa9c991ae58e1d5bbf32275f1738786db15c337bc4bb80fdc0813aa447142`. A fresh canonical student completed full-parameter training for 3 epochs at `1e-5`, BF16, batch 8, and 7500/7500 steps.

Ba detection was Teacher AUC/TPR `1.0000/1.00`, Student `0.4987/0.06`, and Base `0.4417/0.05`. ROC AUC has a random baseline of 0.5, so raw “49.87% AUC retention” is misleading and must not be the primary interpretation: the Student AUC is approximately random and its TPR is only 0.01 above Base. ARC Base/Teacher/Student was `0.446246/0.421502/0.505119`; TruthfulQA was `0.505687/0.514798/0.493715`; sanity and reload passed. Under the tested standardized same-size 3B direct-distillation condition, EverTracer's strong teacher-side fingerprint signal was reduced to approximately base/random-level detectability while overall model utility remained functional.

The frozen canonical neighborhoods SHA256 is `7834e3d77704951ea06501c2166e960fef2b147ced3d751a8e55f07ec7b3672b`; reuse these frozen detector inputs across Teacher/Base/Student and future attacks. EverTracer A and Ba are FULLY CLOSED with no blocker; Bb is NOT RUN/deferred. Teacher and Student are private at `MakiseKurisuEasonHan/WMKD-EverTracer-A-Teacher` and `MakiseKurisuEasonHan/WMKD-EverTracer-Ba-Student`, both still `uploaded_to_modelscope_awaiting_destination_hash_verification`.

## CTCC preserved lessons and closed state

CTCC uses official source `Xuzhenhua55/CTCC@8db93218260bed31b8f18acc9c6ac3e1955d3a42` and target `IAMALIVE`. Experiment A run `ctcc_a_20260829_190251` used the canonical 3B backbone with LoRA, 12 epochs, learning rate `1e-4`, cosine scheduling, cutoff 2048, packing false, rank 8, alpha 16, dropout 0, all-linear targets, BF16, batch 8, accumulation 2, seed 48, and `adamw_torch`. Weight decay `0.0` is only a runtime-inherited reproduction value because the official command omits it and does not pin LLaMA-Factory; it is not paper-specified.

The paper describes 500 Trigger, 500 Suppression, and 1000 Normal training records (2000), while the pinned public artifact contains 461/428/1000 (1889). WMKD used all 1889 without augmentation. The released test contains 95/100/105 (300), while the paper describes 295; the official seen/unseen partition cannot be authoritatively reconstructed. WMKD's operational detector is `generated_answer.strip() == "IAMALIVE"`, case-sensitive, for Base/Teacher/Student. It is not claimed as the official CTCC detector.

A achieved Base Trigger 0/95, Teacher Trigger 95/95, and Teacher negatives 0/205. ARC Base/Teacher was `0.446246/0.395051`; TruthfulQA Base/Teacher was `0.505687/0.476817`; ordinary-generation sanity and fresh reload passed, so A is the preferred Teacher.

CTCC Ba generation parent `ctcc_ba_generation_20260829_195943` stopped fail-closed at 40,007 raw and 17,880 unique. The old output-count cursor formula was corrected without changing scientific configuration. Continuation `ctcc_ba_generation_20260829_195943_cont1` resumed after parent maximum prompt index 10,156 at 10,157, ended at 12,108 with zero overlap, added 6,002 raw and 3,460 continuation-unique records, and produced a net 2,280 new unique records (37.99% marginal yield). Combined generation was 46,009 raw and 20,160 deterministic unique; exactly 20,000 were frozen with SHA256 `621c9aedcf3a4a1db86a4848bbf93fa893d18022f15b913e8aeeb28739412484`. The low corrected-cursor yield is Teacher generation provenance, not a watermark metric.

Fresh-canonical Student `ctcc_ba_20260830_025244` completed 7,500/7,500 steps: full-parameter, 3 epochs, `1e-5`, BF16, batch 8. Evaluation parent `ctcc_ba_eval_20260830_033556` failed before model loading with `ModuleNotFoundError: ctcc_serialization_audit`, an import/deployment failure. Unchanged-science continuation `ctcc_ba_eval_20260830_033556_cont1` completed with Student Trigger 0/95, Suppression 0/100, Normal 0/105, combined negatives 0/205, zero errors, ARC `0.483788`, TruthfulQA MC2 `0.450614`, ordinary-generation sanity passed, and fresh reload passed.

Under the tested standardized same-size 3B hard-label direct-distillation condition, CTCC's perfect teacher-side trigger behavior was not retained in the distilled student, matching the canonical Base trigger level while negative false activation remained zero and utility remained functional. CTCC A and Ba are FULLY CLOSED.

The private Teacher LoRA adapter archive is `MakiseKurisuEasonHan/WMKD-CTCC-A-Teacher`, source-manifest SHA256 `789fbb9c28300c1c199baac348ee62585005f6c57616aeab79e80e7e78865b1f`. The private standalone inference-ready Student archive is `MakiseKurisuEasonHan/WMKD-CTCC-Ba-Student`, source-manifest SHA256 `969f41a186cd37a116d58a472c3e24cea1ee35acefbaa3c2dc0b183b8d1473bc`. Remote verification passed; both remain `uploaded_to_modelscope_awaiting_destination_hash_verification` with `destination_verified=false`.

## Protected cleanup policy

Destructive cleanup is allowed only after: (1) scientific closure; (2) reports, summaries, canonical full JSON logs, and manifests are complete; (3) GitHub closure is complete; (4) required ModelScope archive state is recorded; (5) an exact dry-run inventory; (6) KEEP/DELETE/UNCERTAIN classification; (7) explicit user authorization; (8) exact realpath and non-symlink validation; (9) exact-path deletion; (10) post-delete verification of every protected artifact; and (11) a cleanup audit plus Git record. `UNCERTAIN` always means KEEP. Wildcard removal, broad `find`-delete, or whole runs/models/cache cleanup is prohibited. The canonical base is never deleted. Shared prompts/caches, tokenizers, ARC, TruthfulQA, ModelScope/runtime environments, and common dependencies that LLMPrint or REEF may reuse are protected by default.

EverTracer closure kept the canonical base, preferred Teacher and Ba Student AutoDL copies, Reference merged model, Target/Reference adapters, frozen neighborhoods, final20k, raw32k, formal reports/summaries/status/logs/manifests, and shared T5/cache/environment. It removed only explicitly disposable smoke/intermediate content and redundant `checkpoint-7500`, reclaiming 83,707,244,544 bytes (77.958 GiB).

iSeal cleanup first stopped before deletion when destructive safety review rejected the proposed action. After separate explicit user authorization, exactly five audited realpaths were deleted: A2, A3, A4, and A5 non-preferred `teacher_merged` artifacts and Ba `checkpoint-7500`. Logical deletion was 47,429,470,039 bytes and filesystem used space decreased by 47,429,681,152 bytes (approximately 47.43 GB). The A6 Teacher, Ba final Student, frozen20k, canonical base, source manifests, shared infrastructure/cache, raw generation, and every other-watermark artifact were verified protected. The final cleanup record is `results/iseal/cleanup_summary.json`; closure commit is `92fd6ac425d5ae28e0869ceb6e0006ef192fd272`.

## iSeal preserved A to Ba lineage and lessons

Official provenance is `IntelliSys-Lab/iSeal@7e382321eef4355002acd93120d888dc9b45a8bd`. Formal A training was **not started** because its mandatory public-code trainability gate found released `delta=0`, `A=0`, `B=0` in the path `B(A(delta))`: delta/A/B had zero task gradients and zero updates, while the tied embedding/`lm_head` updated. The bounded finding is that the pinned public implementation's advertised adapter path is gradient-inactive under simultaneous exact-zero initialization; it is not evidence that the iSeal method is universally untrainable.

- A2 repaired initialization with small-random delta/A and zero B while retaining the official trainable `lm_head`. The adapter passed through continuation, but canonical Llama ties input embedding and `lm_head`, so the approximately 394-million-parameter tied matrix also trained. Registered was 10/10, held-out 0/100, ordinary generation 8/10, and ARC degraded materially; A2 was not preferred.
- A3 froze the tied embedding/head and trained only the adapter with 10 fingerprints and `inner_dim=16`. Utility recovered and ordinary generation was 10/10, but thresholded registered success was 0/10.
- A4 changed only fingerprints 10→100 at `inner_dim=16`; registered success was 15/100 and utility remained healthy.
- A5 changed only `inner_dim` 16→128, an alternative released `embed_adapter` implementation provenance rather than a paper mandate; registered success was 66/100 and utility remained healthy.
- A6 changed only fingerprints 100→200 at `inner_dim=128`. Run `iseal_a6_20260830_132300` became the preferred Teacher: Base 0/200, Teacher 179/200 (89.5%), mean BLEU 69.171651; historical subsets were 86/100 and 9/10; held-out was 0/100; ARC 0.389932, TruthfulQA MC2 0.477828, ordinary generation 10/10, and fresh reload passed. No A7 was created.

Ba generation `iseal_ba_generation_20260830_134058` produced 32,006 raw records and 1,849 generation errors. Deterministic accounting recorded 367 empty records, 10,464 duplicate tasks, 10,831 total deterministic rejections, and 21,175 unique valid records; exactly 20,000 were frozen. The content-canonical dataset digest is `d51c22b9d33d4aa79b5cd733dd6bcb910ecd6378f1ffe2a40328e64cb085aacf`; physical `frozen_qa.jsonl` byte SHA256 is `04b02863bbec70b731bbb79471e5be9364ddd89d3b9b51fe5c5c3bb441ec40cc`. They have different semantics and are never interchangeable.

Fresh-canonical full-parameter Student `iseal_ba_20260830_165442` completed 7,500/7,500 steps, 3 epochs, LR `1e-5`, BF16, batch 8, average loss 0.5161768, and fresh reload PASS. Registered-200 Base/Teacher/Student was 0/179/0 successes with mean BLEU 2.332514/69.171651/2.589326: an 89.5-point absolute success-rate drop and 0% **fixed registered-secret BLEU@50 thresholded-success retention only**, not 0% of all watermark information. Historical-100 Teacher/Student was 86/0; historical-10 was 9/0; held-out Teacher/Student was 0/0. ARC Base/Teacher/Student was 0.447099/0.389932/0.481229; TruthfulQA MC2 was 0.505645/0.477828/0.449818; ordinary generation was 10/10 for all. The bounded conclusion is reduction of registered-secret detectability to Base level under the tested standardized same-size 3B hard-label direct-distillation condition.

Private archives are `MakiseKurisuEasonHan/WMKD-iSeal-A6-Teacher` (source-manifest SHA256 `86287873ef8d86f7b056bd907b65a0e05e1dddd8a2047b66f114a04e3c3b51bb`, remote expected 18/18 verified) and `MakiseKurisuEasonHan/WMKD-iSeal-Ba-Student` (source-manifest SHA256 `33176fd47347b42b7bf65330febd977c2d9b47e3bd171623d5628c616db8966a`, remote expected 12/12 verified). Both are private, `uploaded_to_modelscope_awaiting_destination_hash_verification`, and `destination_verified=false`.

Durable trainability lessons: official code is not proof of a runtime-valid mechanism; `requires_grad=True` is not proof of task gradient; simultaneous zero-factor chains may be gradient-dead; distinguish task-gradient movement from weight-decay-only movement; tied weights can defeat intended freeze semantics; count unique `Parameter` objects rather than aliases twice; trainability repair is a scientific modification; a strong watermark with broken utility is not a preferred Teacher; registered-secret and held-out-generalization semantics must remain separate; and stop unlimited tuning once a sufficient usable Teacher is obtained.

## SCW preserved A/A2/Ba lineage and closed state

SCW official provenance is `eth-sri/robust-llm-fingerprints@15bc1929569357130f2dbc0b09f91bbf4f4bd947`; the paper is *LLM Fingerprinting via Semantically Conditioned Watermarks* (ICLR 2026 conference paper/poster). Strict A's official-data/streaming attempt never reached formal training because of PyArrow/GIL finalization instability and overseas official-data access; this is a pre-formal infrastructure/runtime/data-access blocker, not a scientific failure.

The explicitly approved A2 adaptation used domestically accessible Aya French, `wyj123456/instruct`, and `mapjack/openwebtextSample` with a frozen 80k unique pool (role counts 47,773/16,291/15,936) and deterministic two-pass replay. It retained French conditioning, KGW gamma 0.25/delta 4/k 1/`simple_1`, 0.6/0.2/0.2 roles, lambdas 1/1/1, full-parameter training, batch 4, accumulation 16, LR `2e-5`, 2500 steps, Adafactor, cosine, warmup 0.1, and sequence length 512. Run `scw_a2_20260831_214339` completed 2500/2500; Base/Teacher primary p-values were 0.9199569225/0 at alpha 0.001, utility and fresh reload were healthy, and A2 is the preferred Teacher. This is a successful core-method reproduction under an adapted setting, not exact/full-paper reproduction.

Ba continuation `scw_ba_full_20260831_193828_cont1` preserved its telemetry-directory parent failure, froze exactly 20,000 of 20,194 unique Teacher QA from 32,003 raw records (329 errors), SHA256 `a8c93d4fc55521abe6abab48aa67cc06a6251ce769caa913bd24adfebb87b05c`, and trained a fresh-canonical full-parameter Student for 7500/7500. Base/Teacher/Student p-values were 0.9199569225/0/0.8440861702; Teacher was fingerprinted and Base/Student negative across the 10→1000 curve. ARC was 0.450512/0.448805/0.489761 and TruthfulQA MC2 was 0.505162/0.503232/0.474734; fresh reload and ordinary/French sanity passed. Detectability was not retained; Student moved into the Base-like negative regime under tested standardized Ba. French exposure 26/20,000 (0.13%) is diagnostic only, not causal proof.

Teacher and Student are private at `MakiseKurisuEasonHan/WMKD-SCW-A2-Teacher` and `MakiseKurisuEasonHan/WMKD-SCW-Ba-Student`; remote metadata verification passed and `destination_verified=false`. The 5/7 bounded cleanup reclaimed approximately 51.69 GB while preserving canonical Base, SCW preferred Teacher/Ba Student/frozen20k/checkpoints, CTCC checkpoint 7500, shared resources, formal evidence, and ambiguous artifacts.

## Passive fingerprint methods and closed A/Ba state

The passive methods preserve different intrinsic signals and native detector units: LLMPrint uses a probability/bit behavioral-response fingerprint; REEF uses hidden-representation geometry; HuRef uses weight-invariant relationships; AWM uses attention Wq/Wk structural geometry; ZeroPrint uses functional Jacobian/input-output response similarity.

Preferred reproduction results are closed: LLMPrint A2 Reference `1.0`, threshold `0.7150049776126003`, false positives `0/13`; REEF A Reference `1.0`, threshold `0.4546738923165847`, false positives `0/3`; HuRef A2 Reference ICS `99.99999237060547`, threshold `4.119894027709961`, false positives `0/3`; AWM A Reference `1.0`, threshold `0.0017953364917795106`, false positives `0/3`; ZeroPrint A2 Reference `1.0`, threshold `0.6793505996465683`, false positives `0/3`.

Passive Ba is one scientifically shared attack, not five independent Students. Parent `passive5_shared_ba_20260902_114500_cont1` and evaluation continuation `passive5_shared_ba_eval_cont2_20260902_164200` used 40,003 raw / 39,850 valid / 20,896 unique records, exactly 20,000 selected records (SHA256 `eb90c3e0c95e37d07bf0f099aaeabeedf1779bae7ef8a4aacf25e3fb8bed6ab7`), and a fresh canonical Student trained for 7,500/7,500 steps, 3 epochs, BF16, LR `1e-5`, effective batch 8. Fresh reload passed. Utility was ARC acc_norm `0.4974402730` and TruthfulQA MC2 `0.4755413057`.

All five remained detectable: LLMPrint `0.82`; REEF `0.9542220066`; HuRef `99.9989852905`; AWM `0.9999974136`; ZeroPrint raw Pearson `0.6798745394`, rescaled `0.8399372697`. Because Reference and Student use the same canonical pretrained backbone/initialization family, this does not establish general KD immunity or newly transferred fingerprints. The bounded conclusion is only that all five remained detectable under the tested same-backbone direct-distillation setting; cross-backbone/different-initialization distillation is a possible future control, not an authorized task.

## Current state

All ten methods have a completed preferred A/A2/A6 reproduction object and completed Ba evaluation. Proactive Ba reduced PN-FP strongly with a partial residual and moved EverTracer, CTCC, iSeal, and SCW to random/Base-like negative regimes under their native detectors. Passive Shared Ba retained detectability for all five frozen passive detectors in the tested same-backbone direct-distillation setting; this establishes neither general KD immunity nor newly transferred fingerprints because the Student shares the canonical pretrained backbone/initialization family with the References.

`NEXT_STAGE = PROACTIVE_1_TO_5_BB_EXECUTION_READINESS`. `VALIDATED_UP_REFERENCE = PASSIVE_SHARED_BB3`. `PROACTIVE_BB_PROTOCOL_FROZEN = YES`. Passive Shared Ba and Bb3 are COMPLETE; original Passive Bb and Bb2 are `BLOCKED_AT_PILOT`. Proactive Bb has not started. Every new task must fetch and re-check local HEAD, `origin/main`, ahead/behind, and worktree state.

The completed Passive Bb3 pipeline reused canonical Shared Ba frozen20k while preserving each `sample_id`/instruction/input, applied atomic identity or Qwen UP only to the Teacher answer, froze exactly 20,000 paired records, trained one fresh canonical Student with Ba-parity settings, and evaluated it with five frozen detectors. Original Bb/Bb2 preparation and failure evidence remains in `configs/distillation/passive5_shared_bb.json`, `docs/experiment_logs/passive5_shared_bb_log.md`, and their immutable result records.

## Resuming in a new session

1. Read this file and the five root project state/log files named at the top.
2. Read the active method's dedicated log, report, summary, storage protocol, and notification documentation.
3. Recover current state from immutable file records, not an old shell or conversation.
4. Confirm Git repository/remotes and the next explicit TODO.
5. Locate large artifacts through manifests; never infer or substitute provenance.
6. Apply the minimum preflight and continue only the explicitly authorized action.
## CTCC Bb2 distinct follow-up protocol

CTCC Bb2 reuses the frozen standardized Bb per-sample UP transformation and downstream distillation protocol. Its sole primary scientific difference is removal of the experiment-level global identity-fallback-count acceptance gate. It does not weaken the semantic validator, alter retries, suppress fallback records, or change any model, prompt, tokenizer, generation, training, detector, or utility configuration. The original CTCC Bb remains formally blocked at `202 > 200` and is never overwritten. Bb2 must use a new run namespace, verify and reuse the original Bb journal results restart-safely, disclose the final fallback count and rate, and satisfy exactly-20,000/schema/pairing/leakage/control-token/truncation gates before downstream execution.
