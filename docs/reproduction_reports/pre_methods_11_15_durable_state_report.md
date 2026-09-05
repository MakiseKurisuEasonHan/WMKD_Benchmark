# WMKD_Benchmark Durable State Before Methods 11–15

维护任务完成；未启动任何新 science。当前入口：`../CURRENT_STATE.md`；会话规则：根目录 `AGENTS.md` 与 `../EXPERIMENT_PROTOCOL.md`。

## 当前科学状态

第一批十方法 CLOSED，正式比较 30 个槽位；canonical full-log objects 32，32 unique，0 duplicate / broken path / SHA mismatch（修复后本地及 AutoDL 严格检查）。CTCC 比较使用 Bb2 COMPLETE；原 Bb BLOCKED 保留，fallback 202 > 200，后续 NOT_RUN。Passive Bb/Bb2 BLOCKED；Bb3 COMPLETE，5/5 positive，atomic identity 4635/20000 (23.175%) 限制保留。

归档：24 VERIFIED_ARCHIVED、8 ARCHIVED_STRONGLY_VERIFIED、0 MISSING_ARCHIVE、7 NOT_APPLICABLE、2 PERMANENTLY_UNAVAILABLE；early full-redownload sample count 2。本轮使用已提交归档证据，不声称重新在线验证所有 ModelScope 仓库。PN-FP/SCW original Ba frozen20k 的永久缺失与后来重构件身份仍分开。

## 实际修复

历史 Windows 检查为 32/32，但 AutoDL Git checkout 的 LF 转换使 16 个对象无法匹配索引中的 CRLF SHA。清理脚本在首个删除前拒绝继续。确认 16 个对象仅需恢复 CRLF 即精确匹配原索引后，以 `.gitattributes` 固定全部 32 个对象的原换行格式（16 CRLF / 16 LF），恢复远端规范字节。未改变科学 JSON 内容、旧索引 SHA 或归档 inventory。新增可复用严格检查器 `scripts/validate_durable_state.py`。

README、PROJECT_STATUS、TODO、DECISIONS、EXPERIMENT_LOG、CODEX_LOG 与 EXPERIMENT_PROTOCOL 已增加当前阶段入口；旧待办及旧状态明确标记为历史。新方法不自动套用旧 canonical 3B backbone。正式命名、下载顺序、科研决策权限、最小必要 preflight、日志/归档/Git 闭环与清理门槛已持久化。

## 精确路径清理

完整 dry-run：`../../results/pre_methods_11_15_cleanup_dry_run.json`。
执行记录：`../../results/pre_methods_11_15_cleanup.json`。
只删除 26 个逐文件大小/SHA 匹配已提交 PRIVATE strong-remote 验证证据的 safetensors 文件：CTCC Ba、EverTracer A/Ba、iSeal A6/Ba、SCW A2/Ba，共 7 个模型身份，包含匹配的末步 checkpoint 权重副本。

每个文件记录精确路径、大小、身份、archive repo/evidence SHA、原因、删除时间。所有目录及非权重文件保留，包括优化器状态、manifest、config、tokenizer、日志、数据集、cache、credentials。30 个未在此有限匹配范围证明的权重文件按 UNCERTAIN 保留；不表示其归档失败。没有终止任何进程。

| 磁盘（bytes） | 清理前 | 清理后 |
|---|---:|---:|
| Total | 536870912000 | 536870912000 |
| Used | 422292705280 | 357249638400 |
| Free | 114578206720 | 179621273600 |

删除逻辑字节 65043295200；实际观测 free 增加 65043066880 bytes，约 60.6 GiB。两者差异来自文件系统块/同时期小型维护写入，分别保留，不混淆。清理后约 167.3 GiB free。
`SAFE_TO_BEGIN_METHOD_11_STORAGE = YES`：已有准备空间；具体官方配置确定后仍应检查其空间需求。此 flag 不授权训练。

32 个 full logs、global index、archive inventory、相应归档验证与正式报告均在删除前后核对 SHA 未变（基于已修复的 canonical EOL）。历史本地权重路径继续作为 provenance 保留；再次使用须从 ModelScope 按 manifest 恢复及核验，不能继续当作现存文件。

## 验证、环境与 Git

检查记录：`../../results/pre_methods_11_15_validation.json`。JSON parse、32/32 严格索引、archive evidence paths/counts、冲突标记、常见 secret 模式与 >10 MiB tracked/new 文件检查通过；两个脚本的 Python compile 与 Git diff --check 均通过。

AutoDL：学校 VPN 关闭，`ssh -p 32514 root@connect.westd.seetacloud.com`。RTX PRO 6000 97887 MiB 空闲；driver 580.82.09，driver-supported CUDA 13.0；容器 quota 22 CPU / 110 GiB RAM。未安装依赖、未下载模型/数据，未变更科学运行环境。
实际三端初始 HEAD 均 `be032169ae76b5e193730b130bdad77a94e9638a`，0/0、clean。正常提交推送后 AutoDL ff-only 同步；最终 SHA 通过 Git 实际 HEAD 恢复，避免在提交内容内保存自身 SHA。新会话必须重新 fetch/status/rev-parse/rev-list。

## 给 ChatGPT 的总结

完成 durable state/rules migration、严格索引跨平台换行修复、dry-run 与 26 个已验证归档权重文件清理，释放约 60.6 GiB。科学结果、归档等级、永久缺失历史不变；无新 experiment run ID，此次仅维护任务。新入口和完整证据路径见上文。

新方法顺序：11 EaaW、12 Instructional Fingerprinting、13 UTF、14 Double-I Watermark、15 CodeGenGuard。下一目标 `METHOD_11_EAAW_EXPERIMENT_A`，`NOT_STARTED`。无待处理科学或存储阻塞；具体官方 repo/commit/config/model/data/detector 尚未在本任务核验。

STOP。等待用户独立正式 EaaW Experiment A prompt；本轮未 clone 新方法、下载新模型/数据、预处理、GPU science、训练、detector 或 utility evaluation。后续不能把这次清理授权扩展为任意删除。
