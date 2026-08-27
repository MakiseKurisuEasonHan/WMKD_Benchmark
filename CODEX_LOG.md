# Codex 工作日志

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
