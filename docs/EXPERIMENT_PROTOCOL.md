# WMKD_Benchmark Formal Experiment Protocol

This is the canonical, durable project protocol. Every new ChatGPT/Codex session must read it together with `PROJECT_STATUS.md`, `TODO.md`, `DECISIONS.md`, `EXPERIMENT_LOG.md`, and the relevant dedicated experiment log before acting. Historical logs preserve what actually happened; this file defines current policy.

## Project identity and decision authority

WMKD_Benchmark benchmarks robustness and stability degradation of LLM model watermarks under knowledge-distillation attacks, with the long-term goal of a top-conference publication such as ICLR. The selected methods are, in benchmark order: PN-FP, CTCC, SCW, EverTracer, iSeal, LLMPrint, and REEF.

The standard workflow is user → ChatGPT research discussion → explicit execution prompt → Codex implementation → copy-ready Codex handoff → ChatGPT discussion. Codex communicates with the user in Chinese and does not independently make major research-design decisions. Changing the backbone or revision, dataset scale/protocol, distillation protocol, watermark core method, long-term paths, Git identity/remotes, model-repository identity, or destructive cleanup policy requires an explicit user/ChatGPT decision unless already fixed here.

At the end of every Codex task, provide a copy-ready `给 ChatGPT 的总结：` covering actions, changed files, run ID, results, blockers, Git state, work not done, and the next allowed step.

## Isolation, machines, and VPN

WMKD_Benchmark is strictly independent of WaterBench, WaterBenchV2, WaterBenchV3, `watermark_benchmark`, and every legacy watermark/distillation project. Do not read, reuse, write, delete, or share their directories, repositories, checkpoints, results, caches, queues, runners, or runtime state unless a specific future instruction authorizes it.

- Local Windows checkout `C:\Users\Eason\Desktop\WMKD_Benchmark`: primary source development, configuration, documentation, project state, and Git.
- GitHub `MakiseKurisuEasonHan/WMKD_Benchmark`: small reproducibility artifacts and recovery.
- AutoDL checkout `/root/autodl-tmp/WMKD_Benchmark`: disposable compute-side code. Before giving manual AutoDL connection instructions state **学校 VPN：关闭**.
- AutoDL data root `/root/autodl-tmp/WMKD_Benchmark_data`: all large compute artifacts and project-owned caches.
- La Trobe lightweight checkout `/data/home/ad/21672330/WMKD_Benchmark` and warehouse `/data/shared/nobackup/21672330/WMKD_Benchmark`: long-term storage. Before giving manual school-server connection instructions state **学校 VPN：开启**.

Current formal AutoDL environment/hardware baseline, as actually observed during EverTracer: Ubuntu 22.04, Python 3.12, PyTorch 2.8.0, CUDA 12.8, one RTX PRO 6000 Blackwell GPU with 97,887 MiB VRAM, Intel Xeon Platinum 8470Q with 208 container-visible vCPUs, approximately 1.0 TiB RAM, a 30 GiB system disk, and an approximately 1 TiB data disk. After EverTracer closure cleanup, the data disk used approximately 35 GiB and had approximately 966 GiB free. These are current point-in-time planning records, not a capacity guarantee or permission to change an environment silently. Older truthful logs may describe an earlier 22-vCPU/110-GB rental instance and must not be rewritten. Models, checkpoints, datasets, caches, and large outputs must stay under the data root and must never fill the system disk.

Cross-border artifacts may use a currently verified accelerator or trusted mirror as command-scoped transport when direct access is materially degraded. Transport is not scientific provenance: pin the official source and exact revision, then verify final size and cryptographic hashes. Never make an untraceable mirror or temporary proxy the provenance authority.

## Experiment names and lifecycle

- **Experiment A:** first formal watermark reproduction.
- **Experiment A2/A3/...:** immutable corrected later reproduction when a previous A's **scientific configuration** produced an unsuitable result and requires a formal correction. Never overwrite or erase the earlier run or its scientific meaning.
- **Experiment Ba:** Direct Distillation.
- **Experiment Bb:** Untargeted Paraphrasing + Distillation (UP + Distillation).

Current default lifecycle is **A → Ba**. Bb is **NOT RUN / deferred** because no acceptable domestic download source is currently available for the required Dipper paraphraser. Do not download Dipper or activate Bb without a new explicit decision.

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

## Scientific fidelity and minimal preflight

Protect both watermark strength and model utility so the teacher remains scientifically usable for later distillation. Do not remove important original-paper regularization or utility-preserving mechanisms merely to save time. Speed/resource adaptations are allowed only when scientific meaning remains intact; record the paper setting, benchmark setting, reason, and consequence.

Before a formal run, minimally confirm isolation, model/revision, tokenizer/template, seed, dataset/provenance, key method/training configuration, runner/output path, storage, GPU availability, and that declared settings are actually consumed at runtime. Then run. Do not add speculative audit layers merely to pursue perfect certainty; diagnose concrete failures specifically.

## Formal execution and notifications

GPU-heavy training, generation, and evaluation must use a project-owned independent detached runner (`nohup` + `setsid`, `tmux`, or an equivalent robust launcher) so closing Codex or SSH cannot terminate the run. Run one large GPU task at a time unless explicitly approved; never kill or interfere with unrelated processes.

Every formal run exposes and durably records run ID, PID, detached-session/launcher identity, status JSON, logs, result JSON or equivalent, timestamps, exit code, terminal state, failure reason, configuration, source revision, and artifact paths. A mandatory-stage failure preserves evidence, marks the run failed, and stops downstream stages. Engineering completion and scientific success remain separate judgments.

Formal lifecycle email notifications are best-effort: `STARTED`, `COMPLETED`, and `FAILED` or another meaningful premature termination. Credentials remain in a mode-600 file outside Git and must never appear in source, logs, output, or conversation. Notification failure is operational and never automatically makes a scientific run fail. See `docs/EMAIL_NOTIFICATIONS.md`.

## Durable logging and reports

Every Codex task updates the appropriate existing project state/log records. Every formal experiment writes durable machine-readable data rather than relying on terminal output, including environment, actual configuration, source/model revision, dataset provenance, seed, run ID, timing, metrics, checkpoint/reload state, failures, and artifact paths.

`EXPERIMENT_LOG.md` is the concise index. Each completed formal A/Ba experiment automatically produces all three of:

1. a dedicated immutable experiment log under `docs/experiment_logs/`;
2. a formal report under `docs/reproduction_reports/`;
3. a small machine-readable summary under the method's canonical `results/` namespace (legacy PN-FP summaries remain under `results/summaries/`).

The formal report includes objective, environment table, configuration table, original-paper versus benchmark comparison, training results, watermark results, utility results, checkpoint/reload validation, deviations, limitations, and a bounded scientific conclusion. The user does not need to request these separately.

## Artifact retention and ModelScope transfer

After successful A/A2 and Ba, normally preserve the preferred canonical watermarked teacher and canonical distilled student in private ModelScope for future fine-tuning, extraction, pruning, quantization, merging, and other attacks. Do not delete a canonical final model on AutoDL until its archive gate is satisfied.

Formal experiments use detached runners, but ModelScope uploads normally remain **foreground and supervised by the current Codex task** until upload and efficient verification finish. Do not detach an upload unless explicitly approved.

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

## Protected cleanup policy

Never clean AutoDL before reports and summaries are archived, local/Git state is checked, `origin/main` is synchronized, ModelScope transfer state is recorded, and an exact KEEP/DELETE dry-run has been reviewed. The canonical base is never deleted. Default to KEEP when uncertain, especially for small or future detector-dependent artifacts.

EverTracer closure kept the canonical base, preferred Teacher and Ba Student AutoDL copies, Reference merged model, Target/Reference adapters, frozen neighborhoods, final20k, raw32k, formal reports/summaries/status/logs/manifests, and shared T5/cache/environment. It removed only explicitly disposable smoke/intermediate content and redundant `checkpoint-7500`, reclaiming 83,707,244,544 bytes (77.958 GiB).

## Current state

PN-FP and EverTracer are FULLY CLOSED with no blockers: 2 of 7 selected methods are complete. The canonical Llama is preserved. EverTracer closure commit is `c14a176faebb483198736beb8a82bb526403f76d`. CTCC is now the explicitly selected third method, but Experiment A remains in preparation and has not launched because its pinned official files contain 461/428/1000 training records rather than the fixed 500/500/1000 design. Do not augment data or launch until an explicit user/ChatGPT decision resolves this scientific discrepancy.

## Resuming in a new session

1. Read this file and the five root project state/log files named at the top.
2. Read the active method's dedicated log, report, summary, storage protocol, and notification documentation.
3. Recover current state from immutable file records, not an old shell or conversation.
4. Confirm Git repository/remotes and the next explicit TODO.
5. Locate large artifacts through manifests; never infer or substitute provenance.
6. Apply the minimum preflight and continue only the explicitly authorized action.
