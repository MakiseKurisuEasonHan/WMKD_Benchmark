# WMKD_Benchmark Formal Experiment Protocol

This document is the durable execution policy for all formal WMKD_Benchmark experiments. A new working session must first read this file together with `PROJECT_STATUS.md`, `TODO.md`, `DECISIONS.md`, `EXPERIMENT_LOG.md`, and the relevant dedicated experiment log.

## Isolation and machine roles

WMKD_Benchmark is independent of WaterBench, WaterBenchV2, WaterBenchV3, `watermark_benchmark`, and all legacy watermark or distillation runs. Formal experiments must not read or reuse their checkpoints, results, caches, configuration, queues, or runtime state.

- The local computer owns source development, configuration, documentation, and Git.
- AutoDL owns training, evaluation, temporary checkpoints, and compute artifacts. School VPN must be **off**.
- The La Trobe server owns long-term large-artifact archives. School VPN must be **on**.
- GitHub stores small reproducibility files, never model weights, optimizer states, caches, large logs, raw tensors, credentials, or secrets.

## Default backbone standardization

Unless a watermark method has a documented technical limitation and the user separately approves a deviation, every formal method uses the same pinned canonical backbone: `meta-llama/Llama-3.2-3B-Instruct@0cb88a4f764b7a12671c53f0838cd831a0843b95`.

- Experiment A embeds the watermark into the canonical unwatermarked 3B backbone.
- Experiment Ba uses the successful watermarked Experiment A 3B checkpoint as teacher and a fresh load of the canonical unwatermarked 3B as student initialization.
- Experiment Bb uses that watermarked 3B teacher, UP-modified distillation targets, and another fresh load of the canonical unwatermarked 3B as student initialization.

This same-family, same-size, same-revision policy supports horizontal comparisons between watermark methods and vertical A → Ba/Bb retention comparisons. It reduces confounding from compression, parameter count, architecture, tokenizer/template, and capacity reduction so the benchmark isolates watermark-method and distillation-attack effects. Matching architecture and revision never permits initializing the student from watermarked teacher weights.

If a method cannot run on this 3B backbone, is officially incompatible, or is infeasible under available resources, do not substitute another model automatically. Record the blocker, propose a deviation, wait for explicit user approval, and label any approved result as a non-standard backbone deviation in its configuration, log, summary, and report.

## Formal experiment lifecycle

Each formal experiment has an independent immutable run namespace, dedicated output directory, raw logs, checkpoints, evaluation outputs, machine-readable summary, report, and dedicated Markdown log. Run IDs use `<method>_<experiment>_YYYYMMDD_HHMMSS`; failed runs are retained and never silently overwritten or resumed.

The normal pipeline is:

```text
minimum preflight
→ training
→ checkpoint validation and reload
→ formal evaluation
→ base/control evaluation where applicable
→ paired metrics
→ machine-readable result and report
→ project status and Git synchronization
```

A mandatory-stage failure must preserve evidence, mark the run failed, and stop downstream stages. Engineering completion and scientific success are separate judgements. Scientific claims must be bounded by the metrics and controls actually run.

## Independent runners and persistent state

Long GPU jobs run through a project-owned detached `tmux` session or an equivalent robust launcher. Only one large GPU task may run at a time. CPU-side work may continue during training.

Each run persists at least its run ID, timestamps, Git commit, exact runtime configuration, current stage, PID, detached-session identifier, stdout/stderr logs, exit code, checkpoint and evaluation paths, final status, and failure reason. The runtime must demonstrate that key declared values—model/revision, seed, tokenizer/template, batch size, learning rate, training mode, and output path—are actually consumed.

Formal runners support best-effort email lifecycle notifications: `STARTED` after a real formal start, `COMPLETED` only after every mandatory pipeline stage succeeds, `FAILED` after a fatal pipeline error, and `INTERRUPTED` when a read-only watcher can establish abnormal process disappearance. Gmail SSL 465 uses bounded retries before a serial STARTTLS 587 fallback. Exhausted terminal notifications enter a non-secret data-disk pending queue for later CPU-only retry. Only confirmed success updates at-most-once `run_id + event` state. SMTP failure is recorded separately and must never fail or alter an experiment. Credentials live only in a mode-600 secret file outside Git. See `docs/EMAIL_NOTIFICATIONS.md`.

Preflight is intentionally minimal: verify isolation, required inputs and provenance, active runtime configuration, output uniqueness, trainability, precision, GPU availability, and storage. Diagnose concrete failures instead of building speculative infrastructure.

## Logs, reports, and artifacts

`EXPERIMENT_LOG.md` is a concise project index. Each experiment's dedicated log is its scientific history and records planned and actual settings, paper differences, runs, failures and fixes, deviations, milestones, artifacts, results, limitations, judgement, Git state, and next action. Raw stdout remains in the run directory.

Every completed formal experiment produces a report with identity, environment, actual configuration, paper comparison, formal and control results, engineering observations, limitations, and bounded conclusion. It also produces a small JSON summary suitable for aggregation.

Large successful artifacts are archived on the La Trobe server with provenance, revision, source/destination paths, and hashes where practical. They are never committed to Git.

## GitHub synchronization

At stable milestones and completion, inspect status, unstaged and staged diffs, and remotes; verify the remote is the private WMKD_Benchmark repository; scan for secrets and large artifacts; then commit and push appropriate small files. Never push to a legacy repository.

## How to resume WMKD_Benchmark on a new device

1. Clone the correct WMKD_Benchmark GitHub repository.
2. Read this protocol, `PROJECT_STATUS.md`, `TODO.md`, `DECISIONS.md`, `EXPERIMENT_LOG.md`, and the active experiment log.
3. Determine the latest immutable run and its file-recorded stage/status; do not infer state from an old shell or conversation.
4. Locate or restore large artifacts using recorded storage manifests, provenance, revisions, and archive paths.
5. Establish project-owned compute storage and cache paths on the new server.
6. Verify the exact model revision and active runtime configuration.
7. Continue from the next explicit TODO without reusing unrelated failed state.
