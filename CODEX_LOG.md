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
