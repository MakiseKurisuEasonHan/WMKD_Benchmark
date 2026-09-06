# Methods 11–15 Automated Reproduction Pipeline

最新范围（2026-09-06）：当前只执行 Method 13 UTF Experiment A。Method 11/12 已成功闭环，不重跑；execution_scope=utf_only，禁止启动 14/15 或 Ba/Bb/KD/paraphrasing。UTF 闭环后等待用户后续范围授权，本范围结束不关机。以下五方法 unattended 顺序为历史授权，受本段严格范围限制。UTF 工程错误修复当前方法、有界重试，不跳过；RED 科学歧义询问用户。

UTF 传输修复：canonical meta-llama/Llama-2-7b-chat-hf @ f5db02db724555f92da89c216ac04704f23d4590 保持不变；公开 ModelScope shakechen/Llama-2-7b-chat-hf @ 299e68d813ff6f146741f8e8477ed0a57ded4765 仅作为传输映射，按 canonical Git blob/LFS SHA 和大小逐文件核验。禁止把 HF token 发给第三方镜像。旧失败、已有 LICENSE 和新 attempt 分离保存。

2026-09-05 新正式用户授权取代前次迁移任务的 STOP：顺序 EaaW → Instructional Fingerprinting → UTF → Double-I → CodeGenGuard，执行 Experiment A、官方检测、Base/negative control、原生 utility、reload、full logs/report、PRIVATE archive、每方法 Git 闭环，然后继续下一项。没有 Ba/Bb/蒸馏授权。

调度入口 scripts/methods_11_15/run_methods_11_15.py；配置 configs/methods_11_15.json；状态 results/methods_11_15_pipeline_state.json。单GPU，detached，独立stage worker + durable receipt；成功阶段不重复。后续runner未部署不能伪装成 scientific BLOCKED。

允许最小依赖/API/路径/传输/硬件兼容修复，记录差异；同一根因不做无限retry。科学含义、非官方模型/数据、核心算法、trigger、detector/threshold有分歧则该方法 BLOCKED_SCIENTIFIC_PROTOCOL 并继续。旧KEEP/UNCERTAIN不删除。已归档新批次临时文件仅允许精确路径清理。

官方来源已固定五个作者repo commit（见配置）。EaaW原生GPT2/PTB/128bit/20epochs，保留feature-attribution与原生bit/chi-square检测。其他方法仅采用官方明确支持路径；utility优先各自原生metric，CodeGenGuard必须有code-generation utility。

监视进程、GPU、日志mtime/大小、CPU、磁盘及fatal patterns；warnings不是失败，PID消失不等于成功。无receipt保留partial，不报成功。

全部5项terminal后生成master summary和shutdown state。确认所有报告/full logs/index、归档或明确blocker/local保留、无GPU/上传任务、三端Git一致/clean后才能关机。Windows同步助手只在本地干净且ff-only可行时同步并发送精确HEAD确认；远端等待确认，不在单方法结束时关机。

本轮授权来源为用户正式“Methods 11–15 Automated Reproduction Pipeline”请求；不是历史文档推断。

## 后台运行与恢复

2026-09-05 已启动 EaaW 官方 GPT-2/PTB 20 epochs、10000 optimizer steps；不缩短训练。官方 CLI 实际分块为128 tokens。监督器重启测试保留原 worker4582/GPU4585，新的 guardian 成功接管。

Methods12–15 的 SOURCE_PINNED 与 ENV_READY 已通过 CPU 预准备生成独立 receipts；每个 GPU 阶段仍必须按11→15串行进入。`cpu_import_audit.py` 检查官方入口，兼容 patch 记录在各 run root 的 `compatibility.patch`。所有新增依赖仅安装到本批各方法 runtime_overlay。

入口 `scripts/methods_11_15/launch.sh` 启动 guardian；监督器按结果 receipt 恢复，接管存活 worker。`local_sync.ps1` 在本机后台运行，只有本地clean、Local=origin=AutoDL时才写精确HEAD确认。只有五个方法terminal、报告/全日志/索引/归档或归档阻塞证据已保存、无GPU/上传worker、两次最终Git同步确认后才请求AutoDL关机。

任何当前运行状态以 AutoDL 的 `results/methods_11_15_pipeline_state.json` 和 data/runs/methods_11_15/watchdog.json 为准；Git按阶段闭环保存快照。终态报告生成在 docs/reproduction_reports，汇总包含实际 detector、负对照、utility delta、耗时与归档。

## 当前预处理修正与巡检

EaaW run `eaaw_a_20260905_111830_cont1_cont1` 的 PTB 原始行空白未执行官方 builder 的 `line.strip()`，不能作为 canonical A。保留当前训练进度及自然完成的 checkpoint；`training_invalidation.json` 使控制器在训练完成后先保存诊断 full log，再以 `eaaw_a_20260905_111830_cont2` 重跑官方预处理。自动审批拒绝中止旧训练，未得到用户额外明确批准时不得中止；不将等待时间视为批准。

本任务小时级巡检 `wmkd-methods-11-15` 已启用，异常时在授权内修复并继续队列。远端 guardian 独立运行；本机同步助手和 Codex 巡检需要本机及应用保持运行。5/5 尚未 terminal，不得声称完成或提前关机。

## 2026-09-06 STRICT SERIAL INTERACTIVE MODE

用户在线期间执行 strict_serial_interactive；current_focus_method = Instructional Fingerprinting；advance_on_engineering_block = false。优先从 Method 12 TRAINING 新 attempt 恢复，不重建已成功的模型/数据。工程失败先最小修复并有界重试；未解决则等待处理，禁止跳过当前方法。RED 科学分歧停止并报告用户。Method 12 检测、负对照、utility、reload、全日志、报告、私有归档验证和 Git 闭环前，Methods 13–15 不得进入新 expensive stage。保留后续方法的已下载内容、失败回执及当前准备产物。EaaW 已闭环，不重跑。最终关机授权仅在全批真实终态与完整 closure 门槛通过后有效。
