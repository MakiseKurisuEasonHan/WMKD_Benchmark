# Codex 工作日志

## 2026-09-03 — Canonical 10-method audit and passive-Bb decision

Audited the local durable sources and actual Git baseline. Updated current-facing protocol/status/TODO/README records from the obsolete seven-method/5-of-7 state to the completed ten-method A+Ba closure, corrected the global full-log count to 21, froze Bb as UP followed by distillation, and set passive methods 6–10 as the first Bb cohort. Historical dated records were preserved. No external connection, experiment, download, GPU action, archive, or cleanup was performed.

## 2026-09-03 — Passive-5 Shared Bb local pipeline preparation

Added the Qwen-configured, revision-gated Shared Bb pipeline and CPU/static coverage. The implementation validates the canonical Shared Ba source hashes, preserves one-to-one lineage, resumes by explicit sample/attempt state, fails closed on retry exhaustion or source drift, audits paraphrase quality, enforces Ba/Bb Student parity, and wires existing detectors/utility without recalibration. Formal execution remains blocked on Qwen revision resolution and a later explicit run prompt.

Local standard-library test run: 42 tests executed, 39 passed and 3 pre-existing PyYAML-dependent checks skipped; zero failures. The 35 Shared-Bb-specific tests all passed. JSON, syntax, prompt-hash, global-index non-mutation, secret, large-file, and diff checks were also required before Git closure.

## 2026-09-03 — Private ModelScope archive of canonical passive frozen20k

Connected only to no-GPU AutoDL alias 6002, fast-forwarded its clean checkout, verified the canonical source and privacy gates, created an explicitly PRIVATE dataset repository, uploaded the minimal four-file transport package, and independently downloaded it. The downloaded JSONL was byte-identical and passed 20,000/schema/dataset/sample-ID/file SHA gates. Preserved the initial dataset-revision endpoint 404 as infrastructure history and completed verification without re-upload. No source deletion, experiment, Qwen download, paraphrasing, training, detector, GPU, or cache cleanup occurred.

本日志记录 Codex 在 WMKD_Benchmark 项目中的实际工程操作。正式科研实验另行记录在 `EXPERIMENT_LOG.md`。

## 2026-08-27 14:13（Australia/Sydney，UTC+10:00）

### 任务

初始化全新的 WMKD_Benchmark 本地项目与 GitHub 基础设施，建立独立、可复现且不受旧项目污染的项目骨架。

### 完成内容

- 确认唯一项目根目录及初始空目录状态。
- 初始化基础目录、README、项目管理文档和严格的 Git 忽略规则。
- 配置 repository-local Git 作者身份。
- 执行最小 secret、大文件及旧项目引用检查。
- 尝试创建私有 GitHub repository、提交并推送初始化版本。

### 文件变化

- 新增 `README.md`、`LICENSE`、`.gitignore`。
- 新增 `PROJECT_STATUS.md`、`TODO.md`、`DECISIONS.md`、`EXPERIMENT_LOG.md`、`CODEX_LOG.md`。
- 新增基础代码、配置、文档、测试、依赖和结果摘要目录。

### 结果

成功。完成独立项目骨架、私有 GitHub repository、初始化 commit 和 `main` 分支推送，并完成最小安全检查。

### Git

repository-local identity 为 `Yichen Han <EasonHanYichen@gmail.com>`。创建私有仓库 `MakiseKurisuEasonHan/WMKD_Benchmark`，设置 SSH `origin`，使用 commit message `Initialize WMKD benchmark project` 提交。SSH push 因当前环境无可用 public key 失败；保留 SSH remote 不变，并通过 GitHub CLI 已认证的临时 HTTPS credential helper 完成初始化 push。最终 commit hash 与同步状态通过 Git 命令验证。

### 备注

沙箱内初次认证检查因网络权限产生误报；受控联网检查确认 GitHub keyring 中的 `MakiseKurisuEasonHan` 认证有效。未发现 secret、超过 1 MiB 的意外文件或旧项目绝对路径/依赖。初始化已完成；后续常规 SSH push 仍需解决当前环境的 public-key 认证问题，或明确批准改用 HTTPS remote。

## 2026-08-27 14:34（Australia/Sydney，UTC+10:00）

### 任务

初始化 La Trobe University 学校服务器上的 WMKD_Benchmark 轻量项目 mirror 与专属大型 artifact warehouse，并将实际存储信息记录回本地 source of truth。

### 完成内容

- 通过既有 SSH alias `gpu` 确认服务器身份与用户环境。
- 在 `/data/home/ad/21672330/WMKD_Benchmark` clone 私有 GitHub repository，并验证 `main`、HEAD、origin 和 clean 状态。
- 在 `/data/shared/nobackup/21672330/WMKD_Benchmark` 创建模型、checkpoint、数据、结果、generation、artifact、manifest 和日志目录及说明文件。
- 验证 warehouse 不是 Git repository，两套新目录中没有 symlink，并记录对应文件系统空间。
- 新增学校服务器 storage 文档，更新项目状态、任务和基础设施决策。

### 文件变化

- 新增 `docs/storage/school_server.md`。
- 修改 `PROJECT_STATUS.md`、`TODO.md`、`DECISIONS.md`、`CODEX_LOG.md`。
- 学校服务器 warehouse 新增目录结构与 `README.md`；轻量目录新增 GitHub checkout。

### 结果

成功。轻量 mirror 与独立 warehouse 均已按指定路径初始化并验证。

### Git

本轮使用 commit message `Document school storage infrastructure` 提交本地文档，并推送到现有 `origin/main`；最终 commit hash 和同步状态在本轮结束前通过 Git 命令验证。

### 备注

服务器 hostname 为 `aiotcentre-03.latrobe.edu.au`。初始化时 `/data` 文件系统为 33 TB total、20 TB used、13 TB available。未访问旧 WaterBench 项目，未运行 GPU、训练或 evaluation，未下载模型或数据。Artifact 同步与 manifest 协议仍待后续任务定义。

## 2026-08-27 14:40（Australia/Sydney，UTC+10:00）

### 任务

初始化 AutoDL 上的 WMKD_Benchmark 计算端 checkout、独立大型计算数据根目录、cache namespace 和最小路径验证工具，不开始科研实验。

### 完成内容

- 通过既有 SSH 连接 `6000` 确认 AutoDL 主机、系统、磁盘、Python、Git 和 GPU inventory。
- 在 `/root/autodl-tmp/WMKD_Benchmark` clone 私有 GitHub repository。
- 在 `/root/autodl-tmp/WMKD_Benchmark_data` 创建独立的模型、checkpoint、数据、cache、run、generation、artifact、manifest、日志和临时目录。
- 新增 AutoDL 路径配置、target-scoped storage 验证脚本和 compute storage 文档。
- 更新项目状态、任务和基础设施决策。

### 文件变化

- 新增 `env/autodl_paths.sh`。
- 新增 `scripts/verify_autodl_storage.sh`。
- 新增 `docs/storage/autodl_compute.md`。
- 修改 `PROJECT_STATUS.md`、`TODO.md`、`DECISIONS.md`、`CODEX_LOG.md`。
- AutoDL 非 Git 数据根目录新增专属 storage 结构与 `README.md`。

### 结果

成功。AutoDL compute checkout 与独立 compute storage 已初始化；验证脚本在同步最新 Git commit 后执行。

### Git

本轮使用 commit message `Initialize AutoDL compute infrastructure` 提交本地变更并推送到现有 `origin/main`，随后在 AutoDL 执行 fast-forward pull。最终 hash 与同步状态在本轮结束前验证。

### 备注

AutoDL hostname 为 `autodl-container-8sfcmdj9gq-e8387159`。GPU 为 NVIDIA RTX PRO 6000 Blackwell Server Edition（97,887 MiB），检查时无显存占用和运行进程。未连接学校服务器，未访问旧 WaterBench，未下载模型或数据，未运行 GPU workload、训练或 evaluation。正式 ML environment、artifact 同步和 provenance protocol 均待后续批准。

## 2026-08-27 16:47（Australia/Sydney，UTC+10:00）

### 任务

准备 PNFP Experiment A 的固定 Llama-3.2-3B-Instruct 模型、官方源码、独立 AutoDL 环境、离线 smoke 与实验配置框架，但不开始正式训练。

### 完成内容

- 使用现有 Hugging Face gated access 将 `meta-llama/Llama-3.2-3B-Instruct` 固定到 revision `0cb88a4f764b7a12671c53f0838cd831a0843b95`，在 Windows 下载 12 个 Transformers artifact 文件并生成完整 SHA256 manifest；排除重复的 `original/` checkpoint。
- 固定 PNFP 官方仓库 `SewoongLab/scalable-fingerprinting-of-llms` commit `fdceaba14bd3e89340916a6a40e27c945d48460e`，在 AutoDL 建立排除 `generated_data/` 的 clean sparse checkout。
- 在 `/root/autodl-tmp/WMKD_Benchmark_data/artifacts/pnfp/env` 创建全新 Python 3.10.20 独立环境，安装 Blackwell 兼容 PyTorch 2.7.1+cu128 和 PNFP 核心依赖。
- 验证 CUDA 可用、BF16 支持、DeepSpeed 与 PNFP 训练/生成/检测模块可在离线模式 import，且 `pip check` 通过。
- 新增 Experiment A 配置、模型 provenance、方法文档、环境依赖、experiment record 模板、报告模板和离线 smoke 脚本。

### 文件变化

- 新增 `configs/watermark/pnfp_experiment_a.yaml`、`configs/evaluation/experiment_record_template.json`。
- 新增 `docs/models/llama_3_2_3b_instruct.md` 及完整 JSON manifest。
- 新增 `docs/methods/pnfp.md`、`docs/reproduction_reports/pnfp_experiment_report_template.md`。
- 新增 `requirements/pnfp_autodl.txt`、`scripts/smoke_test_local_model.py`。
- 修改 `PROJECT_STATUS.md`、`TODO.md`、`DECISIONS.md`、`CODEX_LOG.md`。

### 结果

部分成功。Windows 模型、provenance、PNFP 官方源码和独立环境已准备完成；Windows 到 AutoDL 的模型传输因链路速度异常未完成，因此完整 SHA 验证、offline model load 和 generation smoke 未执行，正式 Experiment A 不可启动。

### Git

本轮计划使用 commit message `Prepare PNFP 3B reproduction environment` 提交轻量配置、脚本和文档并推送；最终 commit 与同步状态在本轮结束前验证。

### 备注

9,085,657-byte `tokenizer.json` SCP 实测耗时 441.76 秒，约 20 KB/s；按此速度 6.43 GB 模型约需 88 小时。AutoDL 目标目录已创建 `TRANSFER_INCOMPLETE` 标记，禁止误用。未连接学校服务器、未访问旧 WaterBench、未下载其他模型、未开始 fingerprint training、distillation 或 evaluation。

## 2026-08-27 22:00（Australia/Sydney，UTC+10:00）

### 任务

在 La Trobe 学校服务器上直接下载并完整校验固定 revision 的 `Llama-3.2-3B-Instruct`，将其建立为统一 backbone 的长期 canonical archive；不连接 AutoDL、不使用 OSS、不运行模型或训练。

### 完成内容

- 在学校服务器用户专属 venv 中安装 `huggingface_hub 1.8.0`，复用既有 gated Hugging Face 登录状态验证仓库和固定 revision，未记录或输出 token。
- 仅下载 Git manifest 指定的 12 个 Transformers artifact，排除重复 `original/` checkpoint 和 cache 内容。
- 对 staging 中全部 12 个文件逐一验证大小与 SHA256，随后移入 canonical 目录并再次验证文件数量、总大小和摘要一致性。
- 在 warehouse 中写入 server-side machine-readable manifest，并清理 staging 目录。
- 更新模型 provenance、学校存储说明、项目状态和任务清单。

### 文件变化

- 修改 `docs/models/llama_3_2_3b_instruct.md`、`docs/storage/school_server.md`。
- 修改 `PROJECT_STATUS.md`、`TODO.md`、`CODEX_LOG.md`。
- 学校 warehouse 新增 12 文件 canonical 模型目录及 machine-readable manifest；这些大型 artifact 不进入 Git。

### 结果

成功。Canonical 目录包含且仅包含 12 个正式文件，总计 6,434,748,511 bytes，全部文件的大小和 SHA256 均与 Git manifest 相符。下载耗时 27 秒（2026-08-27 21:56:59 至 21:57:26，UTC+10:00）。

### Git

本轮使用 commit message `Archive unified 3B backbone on school storage` 提交轻量文档并推送到 `origin/main`。Windows 本地与 GitHub 已验证同步；学校 SSH 在最终 mirror pull 阶段连续三次连接超时，因此轻量 mirror 的 fast-forward 尚待连接恢复后补做。

### 备注

学校 canonical 路径为 `/data/shared/nobackup/21672330/WMKD_Benchmark/models/base/Llama-3.2-3B-Instruct`，server manifest 为 `/data/shared/nobackup/21672330/WMKD_Benchmark/manifests/models/llama_3_2_3b_instruct_0cb88a4.json`。本轮未连接 AutoDL，未上传 OSS，未调用 GPU，未加载模型，也未运行训练、distillation 或 evaluation。

## 2026-08-27 23:58（Australia/Sydney，UTC+10:00）

### 任务

评估 ModelScope 是否能为 AutoDL 提供与冻结 Hugging Face revision 逐文件完全一致的 Llama-3.2-3B-Instruct，并在不一致时拒绝候选；不运行正式 PNFP 实验。

### 完成内容

- 在 AutoDL 新建独立轻量环境 `/root/autodl-tmp/WMKD_Benchmark_data/artifacts/modelscope_cli_env`，安装 `modelscope-hub 0.2.0`，未修改 PNFP venv。
- 通过官方 ModelScope API 确认候选 `LLM-Research/Llama-3.2-3B-Instruct`、owner `LLM-Research`、唯一 revision `master` 和 18 项仓库内容。
- 将候选 metadata 与 Git 中冻结的 12 文件 manifest 对照：11/12 size/SHA256 一致，两个权重 shard metadata 均一致，但 `.gitattributes` 不一致。
- 下载 `tokenizer.json` 测速并验证 SHA256；随后下载 `.gitattributes` 复核 mismatch，未启动任何权重下载。
- 清理 ModelScope staging，保持 AutoDL 正式模型目录为空。

### 文件变化

- 修改 `docs/models/llama_3_2_3b_instruct.md`、`docs/storage/autodl_compute.md`。
- 修改 `PROJECT_STATUS.md`、`TODO.md`、`DECISIONS.md`、`CODEX_LOG.md`。
- AutoDL 非 Git 数据区保留独立 ModelScope CLI 环境；测试 staging 已删除。

### 结果

候选被拒绝。9,085,657-byte `tokenizer.json` 在 1.702 秒内下载完成，约 5.34 MB/s，且 SHA256 与 canonical 一致；但候选 `.gitattributes` 为 1,722 bytes、SHA256 `a064aaf95c0e90dfb935d9f5682bdf9912926220c9623b5e7f2a0a0acbce543f`，而 canonical 为 1,519 bytes、SHA256 `11ad7efa24975ee4b0c3c3a38ed18737f0658a5f75a0a96787b576a78a023361`。因此该 ModelScope copy 不是 12/12 byte-identical，不能用于 WMKD_Benchmark。

### Git

本轮计划使用 commit message `Record ModelScope backbone compatibility check` 提交轻量文档并推送；最终 commit 与同步状态在本轮结束前验证。

### 备注

未下载权重、未 promote 模型、未运行 tokenizer/model load、generation smoke、GPU workload、fingerprint generation、training 或 evaluation。正式 PNFP Experiment A 仍未开始。

## 2026-08-28 00:20（Australia/Sydney，UTC+10:00）

### 任务

按后续明确批准的 transport-plus-repair 协议，在 AutoDL 通过 ModelScope 传输固定 Llama-3.2-3B-Instruct 的 12 个指定 artifact，以精确 Hugging Face revision 修复不一致的小文件，并完成 canonical 校验及离线 smoke；不启动正式 PNFP 训练。

### 完成内容

- ModelScope 仅下载 manifest 指定的 12 个根文件，未请求 `original/*` 或 `configuration.json`；exit code 0，总耗时 541 秒，无 retry/resume。
- 验证 ModelScope 的 11 个文件与 canonical 完全一致，包括两个 safetensors shard；唯一 mismatch 为 `.gitattributes`。
- 从 Hugging Face revision `0cb88a4f764b7a12671c53f0838cd831a0843b95` 单独下载 1,519-byte `.gitattributes`，耗时 2 秒，验证 SHA256 后替换 staging 文件。
- 对 repaired staging 和正式目录分别执行完整 12-file SHA256 校验；两次均为 12/12 通过，总字节数 6,434,748,511，且 `original/` 不存在。
- 在既有 PNFP venv 中强制离线加载 tokenizer；GPU preflight 确认 RTX PRO 6000 空闲、0 MiB 占用且无进程；随后 BF16 单 GPU 模型加载、chat template 和极短 generation 全部通过。
- 清理本轮 staging sidecar 与 Hugging Face repair 临时目录；正式目录只保留 12 个 canonical artifact。

### 结果

成功。PNFP Experiment A preparation 已达到可进入正式训练的 readiness gate，但正式 fingerprint generation、training、detection、utility evaluation 和 Experiment A 均未运行，必须等待下一次明确批准。

### Git

本轮计划使用 commit message `Verify canonical 3B backbone on AutoDL` 提交轻量文档并推送，随后在 AutoDL fast-forward；最终 commit 与三端同步状态在本轮结束前验证。

### 备注

正式模型路径为 `/root/autodl-tmp/WMKD_Benchmark_data/models/base/Llama-3.2-3B-Instruct`。ModelScope 仅是传输渠道，科学 provenance 仍由固定 Hugging Face revision 与 Git manifest 定义。未连接学校服务器或 OSS，未输出 token，未修改 PNFP venv，未运行训练。

## 2026-08-28 — Finalize Experiment A records and harden notifications

- Recorded the completed formal run `pnfp_exp_a_20260827_232033`: 30/30 epochs, final eval_loss 0.0119302, watermarked 1019/1024, base 1/1024, paired difference 0.994140625, reload passed, no OOM.
- Added the final Experiment A report and small machine-readable summary; corrected stale Running/Pending project records.
- Diagnosed the missed COMPLETED email as an unclassified top-level SMTP `TimeoutError`; watcher classification and the experiment itself succeeded.
- Added bounded SSL 465 retry, serial STARTTLS 587 fallback, phase-aware failure records, a non-secret pending terminal-event queue, and a CPU-only retry utility. Email failure remains non-fatal.
- PN-FP Ba remains `deployment_blocked`: no run ID and no GPU task. Bb remains prepared/deferred.
## 2026-08-28 — PN-FP Ba formal launch

- Synchronized AutoDL to the authoritative Git history and fixed the launcher to use the verified PN-FP Python environment before creating a run.
- Launched detached formal run `pnfp_exp_ba_20260828_012228` at commit `30b996548f2486e2a072cd2817a36240fe6df360`.
- Stopped the generation child after 64/64 outputs were degenerate parse failures and no valid QA was produced, preventing an unbounded GPU loop. The runner preserved FAILED state and notifications; no training or later stage ran.

## 2026-08-28 — PN-FP final closure

- Closed A with its utility limitation, A2 as preferred WA/DM teacher, and A2-teacher Ba direct distillation.
- Preserved small scientific and transfer metadata, then removed 51,532,878,636 bytes of completed PN-FP AutoDL runs/readback scratch while preserving the canonical base, environment, source, credentials and reusable infrastructure.
- Standardized destination-side SHA256 as the default transfer completion gate; A2 upload remained awaiting destination verification while Ba completed a stronger full remote re-read.

## 2026-08-28 — PN-FP Ba formal closure

- Closed authoritative A2-teacher run `pnfp_exp_ba_20260828_111148`: 7,500/7,500 steps, reload passed, Ba 98/1024 versus A2 956/1024 and Base 1/1024.
- Recorded 83.7890625-point degradation, 10.251046% retention, passed utility gate, bounded scientific judgement, and required limitations.
- Synchronized the final dedicated log, scientific report, JSON summary, project status, experiment index, TODO, and decisions. COMPLETED email succeeded; no GPU task remained active.
- No model, checkpoint, dataset, raw log, or secret was added to Git. Bb, UP, and Dipper were not started.

## 2026-08-28 — Durable project protocol audit

- Audited the canonical experiment protocol, root project state/logs, storage and notification documentation, PN-FP closure records, and machine-readable upload summaries without connecting to AutoDL or La Trobe.
- Consolidated durable project identity, seven-method scope, A/A2/Ba/Bb naming, fixed 3B backbone, fresh-student Ba invariant, minimal preflight, detached formal-runner, foreground ModelScope-upload, reporting, Git safety, decision authority, and Chinese ChatGPT handoff rules into `docs/EXPERIMENT_PROTOCOL.md`.
- Corrected stale current-facing statements that Ba had not started, clarified initialization versus current AutoDL environment, and normalized Ba's same-source remote re-read to `uploaded_to_modelscope_awaiting_destination_hash_verification` rather than implying distinct-destination verification.
- Preserved immutable historical experiment logs and all PN-FP scientific metrics. No experiment, remote connection, GPU work, model download, artifact deletion, or scientific-result change occurred.

## 2026-08-28 — Begin EverTracer Experiment A

- Fixed official provenance to `Xuzhenhua55/EverTracer@70b402f7b7456c6d94e1fae2de554d77dd6cd921` and confirmed that the pinned repository has no license file; official code is not vendored.
- Recorded the paper/README reference-epoch discrepancy and selected the paper's 4 epochs as explicitly authorized.
- Added the canonical XSum/3B Experiment A configuration and project-owned components for immutable splitting, LoRA training, CPU merge, frozen T5 neighborhoods, calibrated probability-variation verification, standardized utility, ordinary-generation/reload sanity, reporting, preflight, and detached orchestration.
- This entry records local preparation only. No AutoDL connection, training, formal run, Experiment Ba, or ModelScope upload had occurred at the time of this entry.

## 2026-08-29 — Launch EverTracer Experiment A

- Preserved the dirty primary AutoDL checkout and deployed EverTracer through isolated, commit-addressed clones under the project data root.
- Installed the isolated environment, pinned official source/data/T5 revisions, froze disjoint XSum Dtr/Dref/Dunseen manifests, passed server tests and 16/16 preflight checks, and completed representative target/reference/T5/verification/utility/reload speed smoke.
- Diagnosed the T5 fill failure as a mismatch between a provisional 512-token window and the official 128-token packed XSum protocol. After explicit user approval, commit `507183234afc231c8a821e77f4b48f4590cc8e06` fixed the official 128-token window; T5 smoke then passed with zero retries.
- Launched detached formal run `evertracer_a_20260828_223155`, PID 185252. It entered `RUNNING_TARGET` and delivered STARTED email via SSL465. No Experiment Ba, automatic retuning/A2, ModelScope upload, or destructive cleanup was performed.

## 2026-08-29 — Post-EverTracer durable protocol audit

- Audited the canonical protocol, current status/TODO/decisions/logs, storage and notification documentation, method reports, machine-readable results, and current-facing contradiction patterns using only the local WMKD_Benchmark checkout.
- Kept `docs/EXPERIMENT_PROTOCOL.md` as the single canonical cross-session rules file. Added the A2-versus-continuation distinction, per-watermark Ba teacher/QA isolation, fresh canonical student invariant, fixed Ba training reference, full EverTracer lineage/detector lessons/results, protected cleanup gate, and explicit 2/7 current state.
- Updated the current AutoDL planning baseline from the older rental's 22 vCPU/110 GB to the latest observed EverTracer environment: 208 container-visible vCPUs, approximately 1.0 TiB RAM, 97,887 MiB GPU VRAM, and approximately 35 GiB used/966 GiB free after cleanup. Historical observations were not rewritten.
- Preserved all PN-FP and EverTracer scientific metrics, immutable historical logs, ModelScope `uploaded_to_modelscope_awaiting_destination_hash_verification` states, and the intentionally untracked `artifacts/` directory.
- No AutoDL or La Trobe connection, GPU/model operation, download, new watermark selection, experiment launch, artifact deletion, or scientific-result modification occurred.

## 2026-08-29 — CTCC Experiment A static preparation and fail-closed audit

- Confirmed CTCC as the explicitly selected third method and pinned official provenance to `Xuzhenhua55/CTCC@8db93218260bed31b8f18acc9c6ac3e1955d3a42` without accessing any legacy WaterBench project.
- GitHub direct transfer on AutoDL was unusably slow; obtained the exact commit locally, produced a 949,470-byte sparse official archive for README, the four Experiment A datasets, and official scripts, SHA256 `13ff182cc87ce67070603cba9c7b4d2f2d52e43163475851e01281cfde73eb1c`, and verified the same archive SHA on AutoDL. Failed/incomplete transfer evidence was retained rather than deleted.
- Audited the official README configuration and prepared a canonical Llama-3/LoRA config, byte-preserving dataset freezer, role-preserving multi-turn serialization audit, fail-closed preflight, tests, and method note. Local CTCC plus EverTracer preservation tests passed 7/7; `git diff --check` passed.
- Found official pinned counts Trigger 461, Suppression 428, Normal 1000, total 1889, conflicting with the fixed 500/500/1000 total 2000. Official test positional counts are 95/100/105. Final freezer audit established exact full-record identity as 45/50, 49/51, and 1/104; the preliminary Normal 4/101 figure used a wider prompt/history match. No official automatic IAMALIVE detector semantics are present.
- Confirmed the official command omits weight decay; current Transformers 4.55.2 reports inherited default 0.0. Recorded this as a reproduction ambiguity. AutoDL GPU was idle at 0 MiB/0%, but no run was launched.
- Deployment of the new local config/scripts to AutoDL was blocked by transfer safety review pending explicit user approval. No inline-SSH workaround was attempted. No CTCC training, run ID/PID, Ba, utility evaluation, ModelScope upload, or scientific result exists.

## 2026-08-29 — Complete CTCC Experiment A

- After explicit decisions, used every pinned public-artifact record (461 Trigger, 428 Suppression, 1000 Normal) without augmentation and all 300 released test records. Recorded the paper/public-artifact 2000/1889 training and 295/300 test discrepancies.
- Deployed the isolated project-owned Transformers 4.55.2/PEFT 0.17.1 compatibility implementation. Real canonical-tokenizer serialization preserved `user→assistant→user→assistant`; 11/11 preflight checks passed; 1889/1889 records retained assistant supervision under cutoff 2048.
- Launched detached run `ctcc_a_20260829_190251`, PID 299376. STARTED and COMPLETED notifications succeeded. Training completed 1428/1428 steps, 12 epochs, loss 0.693911, in 1439.685 seconds; final LoRA adapter and trainer state were saved.
- WMKD operational exact-match detector (`strip()=="IAMALIVE"`) on the frozen 300 records produced Teacher/Base Trigger 95/95 versus 0/95, Teacher Suppression 0/100, Normal 0/105, combined negatives 0/205, and zero generation errors. Raw generations remain on AutoDL.
- ARC Base/Teacher was 0.446246/0.395051; TruthfulQA MC2 was 0.505687/0.476817. Ordinary generation passed without IAMALIVE leakage, prompt echo, or catastrophic repetition; fresh reload passed.
- All gates passed; CTCC core reproduction is successful under the pinned-public-artifact setting and `preferred_teacher=YES`. No Ba, Bb, ModelScope upload, other watermark, or cleanup was performed.

## 2026-08-29 — Formal long-task monitoring rule

- Recorded the durable rule that formal training, generation, evaluation, and long preprocessing use detached runners with one launch-only health check and no continuous Codex polling.
- Preserved ModelScope model archival as the exception: uploads remain foreground-supervised until exit status and remote filename/count/size/blob-consistency verification are complete.

## 2026-08-29 — CTCC Ba generation launch

- Speed-tested CTCC Teacher generation in isolated namespace `ctcc_ba_speedtest_20260829_220000`: 35 candidates in 30.695 seconds, 138.459 tokens/s, mean 265.625 generated tokens, with no IAMALIVE leakage, repetition, or prompt echo. A fresh-canonical full-parameter 5-step benchmark had 0.192-second steady median step time, finite loss, and 32.163 GB peak allocated VRAM.
- Preflight was READY for CTCC A teacher `ctcc_a_20260829_190251`, adapter weight SHA256 `36957869183ee2581c7377ba973de0aef4d162c7caa3a2353684cf931ae429cd`, fixed 24k/+2k/40k oversampling, exactly 20k freeze, standardized training, and the frozen A multi-turn detector.
- Launched detached generation run `ctcc_ba_generation_20260829_195943`, runner PID 307205. The one launch health check found RUNNING/TEACHER_QA_GENERATION, growing candidate logs, active GPU child PID 307228, STARTED email exit code 0, and no immediate traceback/OOM. Continuous foreground monitoring stopped by protocol; Student training and evaluation did not start.

## 2026-08-30 — CTCC Ba generation failure and approved infrastructure continuation

- Parent `ctcc_ba_generation_20260829_195943` failed closed at 2026-08-30 01:22:44+08:00 after 40,007 intact raw candidates yielded 17,880 deterministic unique records. Parent raw SHA256 is `2cd9406971f79df45c5350e5d364f03daa462c32f09204bb51b5259154884d16`; Teacher/config provenance remained unchanged.
- Root cause included a resumable cursor defect: deriving prompt index from accepted-record count can overlap already consumed prompt indices because a prompt may yield fewer than four accepted records. The approved `cont1` recovers consumed indices from both raw and parse-error records, starts at their maximum plus one, and rejects overlap.
- The combined raw ceiling is an engineering guard raised to 60,000. Teacher, sampling, eight-category prompt distribution, parser, filter, deterministic deduplication, and exactly-20k freeze remain unchanged. Student remains blocked until freeze verification succeeds.
- Cursor recovery regression tests passed 3/3. Parent consumed maximum prompt index is 10,156 and continuation starts at 10,157 with `no_overlap=true`; parent raw/config/Teacher hashes passed unchanged.
- Launched detached `ctcc_ba_generation_20260829_195943_cont1`, runner PID 340630 and generation child PID 340790. The one launch health check found RUNNING, STARTED email exit code 0, model-load log growth, 7.65 GB GPU use, and no immediate traceback/OOM/overlap. Continuous monitoring stopped; completion counts and frozen SHA remain pending.

## 2026-08-30 — CTCC Ba Student training launch

- Continuation completed with 6,002 added raw, 46,009 combined raw, 20,160 pre-freeze unique, and exactly 20,000 deterministic frozen QA. Canonical dataset SHA256 is `621c9aedcf3a4a1db86a4848bbf93fa893d18022f15b913e8aeeb28739412484`.
- Student preflight bound the frozen dataset to fresh canonical `Llama-3.2-3B-Instruct@0cb88a4f764b7a12671c53f0838cd831a0843b95` and the standardized full-parameter 3-epoch BF16, LR `1e-5`, effective-batch-8 protocol (7,500 steps).
- Launched training-only detached run `ctcc_ba_20260830_025244`, runner PID 347107 and training child PID 347115. The one launch check found RUNNING at approximately 58/7500 steps, 92% GPU utilization, 45.27 GB VRAM, STARTED email exit code 0, and no immediate traceback/OOM. Evaluation remains NOT_STARTED and continuous monitoring stopped.

## 2026-08-30 — CTCC Ba completion, evaluation continuation, and ModelScope archival

- Under the user's one-run monitoring exception, Student training completed 7,500/7,500 steps with exit code 0 from 02:52:44 to 03:25:29+08:00. The final model and trainer state passed terminal checks; the long-term detached/no-continuous-monitoring default remains unchanged.
- Preserved failed evaluation parent `ctcc_ba_eval_20260830_033556`, which stopped before model loading on `ModuleNotFoundError: No module named 'ctcc_serialization_audit'`. Added deployment/import preflight and completed unchanged-science continuation `ctcc_ba_eval_20260830_033556_cont1` with exit code 0.
- Fresh-reload Student evaluation produced Trigger 0/95, Suppression 0/100, Normal 0/105, zero generation errors, ARC 0.48378839590443684, TruthfulQA MC2 0.4506136480297226, and a passing ordinary-generation sanity result. No OOM, traceback, NaN/Inf, or terminal GPU process remained.
- Audited and uploaded the CTCC A preferred Teacher LoRA adapter to private `MakiseKurisuEasonHan/WMKD-CTCC-A-Teacher`, then the Ba inference-ready Student `final_model` to private `MakiseKurisuEasonHan/WMKD-CTCC-Ba-Student`, serially and under foreground supervision. Upload commands exited 0 with no retries.
- Replaced only each repository's automatic initialization README with the formal WMKD_Benchmark model card under explicit user authorization. Preserved `.gitattributes` and `configuration.json`; excluded Student `training_args.bin`, all checkpoints, optimizer/scheduler state, raw generation, and frozen20k.
- Teacher remote metadata verification passed 9/9 expected blob hashes and Student passed 12/12; filename/count/size checks passed with no missing or unexpected files. Teacher manifest SHA256 is `789fbb9c28300c1c199baac348ee62585005f6c57616aeab79e80e7e78865b1f`; Student manifest SHA256 is `969f41a186cd37a116d58a472c3e24cea1ee35acefbaa3c2dc0b183b8d1473bc`.
- Both archives remain `uploaded_to_modelscope_awaiting_destination_hash_verification`, `destination_verified=false`, pending a future independent destination download and full SHA256 comparison. GPU terminal state was idle at 0% utilization and 0 MiB used. No cleanup or Bb was performed.

## 2026-08-30 — CTCC closure local/GitHub integrity audit

- Independently fetched private `origin/main` and verified the pre-audit local/GitHub commit and tree matched at `f8402879e5e770801d6e2d3f78ad8ed917e8a2ee`, ahead/behind 0/0. The only untracked path was the intentionally untracked `artifacts/`, which was not inspected for scientific content, deleted, staged, or modified.
- Found current-state drift in root `README.md` and `docs/EXPERIMENT_PROTOCOL.md`: both still described 2/7 complete and CTCC Ba as unstarted. Historical RUNNING/NOT_STARTED statements in `CODEX_LOG.md` and the Experiment A-era boundary in the A log/report were retained as truthful historical provenance.
- Completed the small-record closure by adding full Ba generation cursor/accounting fields, explicit evaluation pre-model-load import failure provenance, a compact archival summary, and regression assertions. No scientific result, historical failure, model/data artifact, external storage, or experiment was modified.

## 2026-08-30 — Post-CTCC canonical protocol and project-status audit

- Read the canonical protocol, root status/decision/log files, relevant method records, configs, scripts, tests, and machine-readable CTCC closure summaries locally. No remote service, GPU, model download, cleanup, or fourth-watermark work was used.
- Kept `docs/EXPERIMENT_PROTOCOL.md` as the single canonical rules file. Added the formal Ba definition; method-specific detector and A/Ba semantic consistency; true-consumed-work resume cursor; standardized oversampling; infrastructure-failure continuation; isolated speed-test; detached launch-only monitoring with explicit per-run exception; fresh reload; standardized utility; ModelScope foreground supervision, controlled private-repository creation, and destination verification boundary.
- Added the durable CTCC A/Ba history, including paper/public-artifact discrepancies, operational detector limitation, runtime-inherited weight decay ambiguity, generation parent/continuation cursor evidence, Student/evaluation lineage, bounded conclusion, and archive manifests.
- Updated current-facing README/status/TODO/decisions to keep Bb deferred without treating Dipper as the only possible paraphraser and to identify SCW only as the next discussion target. No SCW download or experiment was authorized or started. Historical logs were not rewritten.

## 2026-08-30 — iSeal Experiment A stopped at mandatory trainability gate

- Verified actual baseline `aeaaeb7ebb92ae392708fa4e9841b4d3192a4a89`, synchronized with `origin/main` at task start. Pinned official `IntelliSys-Lab/iSeal@7e382321eef4355002acd93120d888dc9b45a8bd` and recorded paper/public-code discrepancies.
- Direct AutoDL GitHub clone timed out. Preserved the later incomplete SCP source as explicitly named failure evidence and deployed a deterministic local verified Git archive (92,160 bytes, SHA256 `8cfb522a215751d4a58d8774fb29387c066e2f59efcafa770299c0fcd5baea77`). This was transport only; official GitHub remained provenance.
- Added the authorized canonical iSeal configuration and a fail-closed two-step audit that preserved official exact-zero delta/A/B and full-`lm_head` trainability. Canonical model/source/dependency/config preflight passed 10/10.
- First smoke `iseal_trainability_20260830_045232` failed before model load/optimizer steps because AutoDL could not reach `huggingface.co`. A new immutable smoke used `hf-mirror.com` transport to resolve the same upstream AG News dataset (120,000 train, 7,600 test).
- Completed `iseal_trainability_20260830_045431`: adapter delta/A/B gradients and updates were all zero across two steps. The full tied 394,002,432-parameter original-embedding/`lm_head` matrix had gradients `195.003445/381.784871` and delta norm `6.019554`.
- Enforced the predeclared stop gate: formal iSeal A, fingerprint metrics, utility, fresh reload, Teacher creation, Ba, ModelScope, and cleanup did not start. Recorded `preferred_teacher=NO`, `ready_for_ba=NO`, and the required explicit scientific decision before any initialization/trainable/tied-weight modification.

## 2026-08-31 — Fixed-rule audit after iSeal closure

- Audited only the local WMKD_Benchmark checkout: canonical protocol, root status/decision/TODO/log files, method records, storage/archive rules, configs, scripts, tests, reports, and machine-readable iSeal closure records. No AutoDL, La Trobe, ModelScope, GPU, download, SCW source, or artifact cleanup was accessed.
- Retained `docs/EXPERIMENT_PROTOCOL.md` as the single canonical rules source and added the complete iSeal A→A6→Ba lineage, registered-versus-held-out semantics, canonical-versus-physical dataset hashes, archive manifests, trainability/tied-weight lessons, cross-method detector-unit rule, and the final authorized exact-path cleanup outcome.
- Corrected current-facing AutoDL state to the 22-vCPU/110-GB/approximately-500-GB pay-as-you-go instance while preserving older 208-vCPU/approximately-1-TiB statements only as historical provenance.
- Corrected SCW from an old “fourth watermark” label to the fixed fifth watermark and next discussion target. No clone, download, configuration, or Experiment A was authorized or started.
- Updated the current experiment index so A5's resolved historical Teacher decision and A6's completed Ba successor no longer appear as live blockers. Preserved every scientific metric and immutable historical failure/continuation record.

## 2026-08-31 — SCW Experiment A local static preparation

- Verified official `eth-sri/robust-llm-fingerprints`, fixed commit `15bc1929569357130f2dbc0b09f91bbf4f4bd947`, and Responsible AI SOURCE CODE License 1.1 from a temporary shallow source checkout. Inspected official README, French embedding/evaluation configs, training/dataset/loss pipeline, KGW implementation, and decision script; no source was vendored or copied.
- Prepared canonical Llama-3.2-3B-Instruct SCW A protocol and official-compatible runtime config, pure-CPU static contracts, deterministic manifest/order helpers, official-detector adapter, fail-closed preflight, result schema, pending summary, report/log records, and future detached/speed-test runners.
- Preserved official French/KGW scientific settings. Recorded wrapper-level deviations: fixed `PYTHONHASHSEED=42`; fixed detector permutation seed/index; `caching_models=true` to prevent official post-training output removal; immutable run namespace; future runtime-effective dtype/trainable/data/loss assertions.
- No AutoDL or La Trobe connection, GPU use, model/dataset download, training, generation, formal evaluation, A2, Ba, ModelScope operation, cleanup, or push occurred. SCW formal A remains NOT RUN.
## 2026-08-31 — SCW AutoDL preflight and speed-test-only execution

- Connected with school VPN off; deployed exact local HEAD while preserving the old dirty AutoDL checkout in a recoverable data-disk backup.
- Pinned official SCW source, canonical model, independent environment, and all dataset manifests; runtime preflight passed full-trainability and BF16 gates.
- Completed only the authorized 4-step non-scientific speed test. Recovered representative 9.617 s/step and approximately 6.68-hour 2500-step training ETA from complete telemetry after a post-`train_end` PyArrow/GIL SIGABRT.
- Ended with no SCW GPU process. Formal A, Ba, ModelScope, and cleanup remained unstarted. Next status: `RUNTIME_ADAPTATION_NEEDED`.

## 2026-08-31 — SCW terminal-cleanup diagnosis and bounded validations

- Reproduced the post-`train_end` SIGABRT in three immutable 4-step runs while preserving every FAILED status. Ruled out OOM, numerical failure, CUDA/training corruption, local-only datasets streaming, dependency-version drift, ordinary Python dataset references, and a live fsspec Python thread as sufficient causes.
- Restored the official pyarrow/aiohttp pins. Tested source-chain release, fsspec teardown, and late atexit GC without modifying the official SCW source or scientific configuration. The strongest cleanup attempt emitted its atexit telemetry and still aborted during CPython finalization, so it was reverted locally and on AutoDL.
- Full AutoDL tests passed 69/69 before the final bounded validation. Formal A and Ba remained NOT RUN; no ModelScope or cleanup action occurred; GPU ended idle. Status is `BLOCKED_RUNTIME_FINALIZATION`, with a clean Python 3.11 environment/upstream native fix as the next candidate rather than another blind GPU retry.

## 2026-08-31 — SCW materialized-stream runtime adaptation (local only)

- Confirmed from pinned official code that each source is transformed/tokenized before hash-seeded shuffle, label assignment, and stochastic `interleave_datasets(..., probabilities=[0.6,0.2,0.2], stopping_strategy="all_exhausted")`. `PYTHONHASHSEED=42` affects every source-shuffle seed and the interleave seed.
- Designed exact-prefix materialization at the official post-interleave tokenized layer. Added immutable record/manifest hashing, exact source/loss provenance, a PyTorch-only sequential iterable, a wrapper-only official training entry point, and an audit tool without modifying official source.
- Verified 17 targeted CPU tests (5 new materialization tests plus 12 SCW preparation tests). No AutoDL/La Trobe connection, GPU, model/real-data download, Formal A, Ba, large artifact, or push occurred.
# 2026-08-31 — SCW post-mortem and shutdown safety

Persisted evidence proved the prior deterministic run failed at LucieFr repository-path discovery with zero records and then invoked the configured AutoDL shutdown finalizer. Added a default-off, reversible shutdown policy that emits `SHUTDOWN_REQUIRED_MANUAL`. No experiment, download, materializer, gate, GPU training, Formal A, or Ba was started.

## 2026-09-01 SCW A2 post-mortem

Recovered persisted state after reboot. Training completed and Teacher saved; Base French generation failed because the pinned Hugging Face dataset was unavailable under offline mode. The pipeline finalizer then issued `/usr/bin/shutdown`. Added a project-level fail-closed shutdown policy and tests; no training or evaluation was restarted.

## SCW A2 evaluation cont2 `scw_a2_eval_cont2_20260901_021640`

Training remained immutable and complete. Cont1 failed at Base detector because the runtime tokenizer lacked a pad token. cont2 reused both immutable 1000-record generation files and applied runtime-only EOS-as-PAD with left padding; Base/Teacher p-values `0.9199569225311279` / `0.0`; preferred Teacher `True`. Ba was not started. Auto-shutdown remained disabled.

## SCW A2 final closure — report/summary cont3

<!-- SCW_A2_FINAL_CLOSURE_CONT3_20260901 -->
Strict A remains a pre-formal infrastructure attempt: Formal training never started and no scientific result was established. A2 run `scw_a2_20260831_214339` completed 2500/2500 and produced the immutable Teacher. Cont1 preserved Base/Teacher 1000-record generations but failed at detector padding infrastructure. Cont2 applied runtime-only left EOS-as-PAD and completed evaluation: Base/Teacher primary p-values `0.9199569225311279 / 0.0`, ARC `0.4505119454 / 0.4488054608`, TruthfulQA MC2 `0.5051617516 / 0.5032315125`, ordinary/French sanity PASS/PASS, and preferred Teacher **YES**. The bounded conclusion is successful SCW core method/idea reproduction under the adapted domestic-data, 80k-pool, deterministic two-pass A2 setting—not exact or full-paper reproduction. Ba remains NOT STARTED. Next step: separately archive the final Teacher to ModelScope, verify the archive, then discuss Ba without starting it automatically.

## SCW A2 preferred Teacher ModelScope archive

<!-- SCW_A2_MODELSCOPE_ARCHIVE_20260901 -->
The immutable SCW A2 preferred Teacher was archived to private repo `MakiseKurisuEasonHan/WMKD-SCW-A2-Teacher`. Upload completed with 9 files / 6,442,815,654 bytes and zero retries. Remote filename, size, and metadata identity verification passed for 9/9 files and all bytes. Source archive manifest SHA256: `0e2bd96ef266fc791e182e793507bfc0db7fe994f1d37ce440adaef923b5dbe1`; Teacher manifest SHA256: `27f68ea443ca1dbc9f02036ac560a12db5cb063ceec589a0144be5586da97b7b`. Status: `uploaded_to_modelscope_awaiting_destination_hash_verification` with `destination_verified=false` because a full destination redownload was intentionally not performed. Preferred Teacher remains YES; Ba remains NOT STARTED. Exact next step: design and explicitly authorize SCW Ba; do not start it automatically.

## SCW Ba `scw_ba_full_20260831_193828_cont1`

Completed standardized Direct Distillation with exactly 20,000 frozen Teacher QA, fresh-canonical 3B Student and Base/Teacher/Student SCW evaluation. Dataset SHA `a8c93d4fc55521abe6abab48aa67cc06a6251ce769caa913bd24adfebb87b05c`; primary p-values `0.9199569225311279` / `0.0` / `0.8440861701965332`; bounded result `lost_or_moved_to_base_regime`. Auto-shutdown remained disabled; Student archive not run.

## SCW Ba Student ModelScope archive

<!-- SCW_BA_STUDENT_MODELSCOPE_ARCHIVE_20260901 -->
The immutable SCW Ba Student from `scw_ba_full_20260831_193828_cont1` was archived to private repo `MakiseKurisuEasonHan/WMKD-SCW-Ba-Student`. Upload and remote filename/size/metadata verification passed for 9 files and 6442815786 bytes. Source manifest SHA256 `f8554fc57258f28b945835dcab759ae4891633cc835918cf63156b14a9f41ef1`; status `uploaded_to_modelscope_awaiting_destination_hash_verification`; `destination_verified=false`. The bounded scientific result remains loss of detectable SCW watermark under the tested standardized Ba condition with the Student in a Base-like negative detector regime. Next step: SCW final closure / commit review; no cleanup was performed.

## 2026-09-01 — Full-project closure/integrity/logging audit

Merged the detached AutoDL SCW A2/Ba history into local `main` without rewriting history. Built and validated ten evidence-preserving canonical full JSON logs plus a global index and formal audit. Historical gaps remain explicit; no values were invented and no scientific work was rerun. The next controlled operations are GitHub synchronization and high-confidence AutoDL cleanup while retaining shared LLMPrint/REEF resources and all unique final/checkpoint evidence.

## 2026-09-01 — Post-SCW fixed-rule and 5/7 status audit

Audited the local repository only. Updated the existing canonical protocol and current-facing README/status/TODO/SCW method records to 5/7 closure, LLMPrint-next-but-not-authorized, domestic mirror transport priority, SCW A/A2/Ba lineage, native cross-method metric semantics, 10/10 full JSON logging, disappearance-evidence limits, and protected cleanup. Historical decision/experiment records were not rewritten; completed scientific metrics were not changed.

Validation: all 123 workspace JSON files parsed; global full-log index schema/object count/path existence and SHA256 passed; `git diff --check` passed. `pytest` was unavailable in the bundled local Python, so no dependency was installed and pytest was not run. No AutoDL, La Trobe, ModelScope, GPU, download, clone, cleanup, or LLMPrint operation occurred.

## 2026-09-01 — LLMPrint preparation started

Under explicit authorization, audited the ACL 2026 LLMPrint paper and official repository, pinned source commit `3e577f98b2bb64780ec2995b074c5aeec9b017e1`, and recorded that no explicit repository license was observed. Added the canonical Llama-compatible configuration, pair-preparation and atomic fingerprint-construction wrappers, local tests, source audit, method documentation, experiment-preparation log, and a non-substitutive ModelScope availability matrix for all 13 official validation negatives. Local compilation, atomic-output test, JSON parsing, and diff checks passed.

The paper and released code disagree on the gray-box final decision rule; this is an unresolved scientific decision before formal Experiment A. No negative model was downloaded or substituted. Formal fingerprint construction remains 0/300; Ba and Student training remain NOT STARTED. AutoDL preflight and the isolated full-parameter speed test are pending because the restarted instance's saved SSH endpoint is stale and the browser session has no AutoDL login state.

## 2026-09-01 — LLMPrint AutoDL preflight and speed test

Connected through the restarted endpoint, synchronized the repository to `ea7c6e8`, verified an idle RTX PRO 6000 and the canonical Base at 12/12 SHA256, deployed pinned external source, and created an isolated release-version environment from the domestic PyPI mirror. Prepared exactly 300 deterministic tokenizer-valid pairs from 773 candidates. The parent and cont1 speed attempts stopped without completed fingerprints on two engineering compatibility faults; preserved both logs and fixed only Python 3.12 dynamic import registration plus mutable DynamicCache handling. cont2 retained the complete formal construction parameters and finished one fingerprint at 1000/1000 steps in 212.429 seconds with 7,048,545,280 peak allocated VRAM bytes. Linear 300-pair ETA is 17 h 42 m; reserve 20–22 h.

No formal 300 construction was launched (formal progress remains 0/300), no validation-negative model was downloaded, no Ba/Student work began, and no cleanup occurred. Preparation passes, but `ready_for_formal_A=false` until the paper-vs-release gray-box detector discrepancy is resolved.

## 2026-09-03 — Passive Bb3 closure state recovered into durable entry points

Performed a local/GitHub-only durable-state audit before proactive Bb. Updated the existing canonical protocol and current-facing README/status/TODO rather than creating a parallel rules system; appended decision and experiment audit records. The repository now leads with the ten-method taxonomy, completed A/A2/A6 and Ba state, Passive Bb/Bb2 `BLOCKED_AT_PILOT` histories, completed Bb3 atomic-identity plus Qwen UP protocol, exact detector/utility results and limitations, 4/4 verified PRIVATE ModelScope inventory, and actual 26/26 global full-log state.

No scientific run or external artifact operation was performed. In particular: no `ssh 6000`, GPU, download, Qwen generation, Student training, detector/utility run, ModelScope write, cleanup, or proactive Bb start. Proactive methods 1–5 Experiment Bb remains `PENDING_EXPLICIT_FREEZE`; Passive Bb3 is only the current validated UP reference and leading candidate.

Local audit classification: A canonical = tracked source/docs/configs/tests/small results plus the two canonical JSON inventories; B expected ignored = project `artifacts/`, local bundles, runtime logs, caches, and `__pycache__`; C stale harmless = `.scw_ba_final_summary.tmp.json` and retained transfer bundles; D suspicious/requires decision = NONE. Nothing was deleted. All 288 JSON files parsed; the 26-object index had 26 unique identities with existing SHA-matching paths; four inventory artifacts were PRIVATE; local Markdown links, Python compilation, `git diff --check`, tracked secret scan, and tracked >10 MiB scan passed. Pytest was unavailable and was not installed. Standard-library unittest discovered 87 tests: 76 passed, 4 skipped, and 7 modules could not import because the lightweight Windows runtime lacks pytest/PyYAML/Torch/PyArrow or POSIX `resource`; this is an environment limitation, not a failing scientific assertion.

## 2026-09-03 — Proactive Bb readiness blocked during 6000 bring-up

Recorded the explicit proactive Bb protocol freeze and began the authorized SSH 6000 readiness audit. The initial connection captured host/GPU/disk state and exposed an outdated detached, bundle-origin checkout. Connection loss then prevented safe repository bring-up and actual five-dataset/Qwen/detector/utility inventory. Preserved unknowns as unavailable and marked all methods NOT_READY. No scientific or destructive action was taken.

Direct endpoint `connect.westd.seetacloud.com:48835` recovered access. Verified the old checkout was clean, protected its HEAD on `historical/scw-deployment-45d6f77`, and switched active code to canonical GitHub main without touching the data root. Completed actual parent/Student/detector/utility/Qwen/storage inventory. Implemented only the minimum shared proactive Bb identity/namespace parameterization and regression tests. Missing PN-FP/SCW parents and exact Qwen snapshot remain blockers; three surviving parents require archive. Formal work remains unstarted.

Restored and fully verified frozen Qwen, added proactive full-log/archive infrastructure, and ran remote targeted tests plus an 18-record Qwen/SFT compatibility smoke. External parent uploads were rejected before execution pending explicit approval. GPU returned idle; no prohibited scientific work occurred.
