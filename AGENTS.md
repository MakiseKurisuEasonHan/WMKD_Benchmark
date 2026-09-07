用户暂停（2026-09-06 请求，2026-09-07 保存）：PAUSED_BY_USER，暂停到下周；必须收到新的明确恢复指令才可继续。禁止下载、repair continuation、训练、检测、utility、advance 和自动关机。自动任务已 PAUSED；远端 SSH 不通，停止进程/GPU/关机路径尚未核实，不能宣称 SAFE PAUSE 已完成。详见 results/methods_11_15_pause_state_20260906.json。

当前唯一执行范围（2026-09-06 用户新 prompt）：Method 13 UTF Experiment A，STRICT SERIAL INTERACTIVE MODE。EaaW 和 Instructional Fingerprinting 已成功闭环，不重跑。禁止启动 Method 14/15、Ba/Bb、KD 或 paraphrasing attack；UTF 闭环后等待用户下一步范围授权。工程错误最小修复、有界重试当前方法，RED 科学歧义报告用户。UTF canonical 为 meta-llama/Llama-2-7b-chat-hf，revision f5db02db724555f92da89c216ac04704f23d4590；公开镜像只改变传输，必须核验全部 canonical 文件身份，不向第三方镜像发送 HF token。详见 docs/METHODS_11_15_AUTOMATION.md 和 pipeline state 的 execution_scope=utf_only。

# WMKD_Benchmark 会话入口

当前授权更新（2026-09-05）：用户已正式批准五方法串行 Experiment A 自动复现、最小工程修复、逐方法归档/Git闭环及全部terminal后的自动关机。前次等待prompt/STOP仅属于已结束的迁移任务。详见 [docs/METHODS_11_15_AUTOMATION.md](docs/METHODS_11_15_AUTOMATION.md) 与 results/methods_11_15_pipeline_state.json；旧科学设计禁改及KEEP/UNCERTAIN保留规则继续有效。


始终用中文与用户交流。先读 `docs/CURRENT_STATE.md`、`docs/EXPERIMENT_PROTOCOL.md`、`PROJECT_STATUS.md`、`TODO.md`，再读相关实验报告及日志。当前 Git 文件是恢复入口，历史日志不是新执行授权。

第一批十方法已 CLOSED：30 comparison slots、32 canonical full-log objects。下一目标 `METHOD_11_EAAW_EXPERIMENT_A = NOT_STARTED`。必须等用户独立正式 Experiment A prompt；状态迁移/清理任务不授权 science、模型/数据下载或新方法 clone。

用户与 ChatGPT 决定科研设计；按正式 prompt 执行，不擅改科学配置。方法 11–15 优先官方原生最小科学有效设置，不自动沿用旧 3B 骨干。A2/A3 表示科学变化，cont 表示运行延续。每个正式科学对象必须有 full_experiment_log.json 并入全局索引；不编造缺失值。

开始任务重验本地与 AutoDL Git。AutoDL 用 `ssh -p 32514 root@connect.westd.seetacloud.com`，不假设 alias 6000；学校 VPN 关闭（La Trobe 开启）。长 GPU 实验 detached，一次一个大型任务；不得干扰他人进程。

下载优先本地/cache/ModelScope/可信国内镜像；保留官方 identity/revision/SHA。清理须按用户授权的 exact-path dry-run，只有全部归档恢复及无使用等门槛通过的 DELETE 可删；UNCERTAIN=KEEP。不得删除代码、日志、报告、索引、归档验证及唯一证据。不得 force/reset/clean/history rewrite；不得提交大模型/数据/cache/secret。

任务结束给出“给 ChatGPT 的总结”，包括实际动作、文件、运行/结果、环境、归档、Git、阻塞、未做事项和下一步授权边界。详细规则以 docs/EXPERIMENT_PROTOCOL.md 为准。
