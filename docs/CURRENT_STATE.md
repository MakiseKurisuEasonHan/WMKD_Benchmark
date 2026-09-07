最新永久规则（2026-09-07）：每个正式实验最多上传一个最终preferred模型，preferred=false禁止上传；UTF A2 COMPLETED_NOT_PREFERRED，仅证据/Git闭环后STOP。远端已提交对象和本地模型保留待明确删除批准。详见 docs/ARTIFACT_ARCHIVE_POLICY.md；本段覆盖下方历史归档授权。

<!-- UTF_A2_CURRENT_AUTHORITY_20260907 -->
当前最高优先级授权（2026-09-07，UTF A2 新 prompt）：仅执行 Method 13 UTF Experiment A2；STRICT SERIAL INTERACTIVE MODE。Methods 11–15 canonical benchmark 永久统一为 meta-llama/Llama-3.2-3B-Instruct，revision 0cb88a4f764b7a12671c53f0838cd831a0843b95。旧 UTF 7B A 保留 historical / superseded protocol，OLD_UTF_A_CANONICAL_BENCHMARK_ELIGIBLE=NO，不标记 FAILED，不覆盖历史结果。
禁止 orchestrator、guardian/watchdog、自动 continuation、auto-next 和 auto-shutdown。仅允许 UTF 专用实现及单项任务；不得运行 11/12/14/15、Ba/Bb 或其他 watermark。旧远端 supervisor 2051 和本地 sync helper 32236 已停止，模型身份检查时未发现相关旧进程。
当前 UTF A2 已完成科学与轻量证据闭环，模型归档按新规则停止且未验收：30 epochs / 960 updates，PREFERRED_TEACHER=NO；Teacher fingerprint 1/1、非触发负控500/500，Base 0/1、0/500；ARC delta=-0.0708191126，MC2 delta=-0.0014838436。状态 WAITING_FOR_USER_SCIENTIFIC_DECISION；下一科学配置须用户批准。30/3 paper/code discrepancy及选择依据保留。完整结果见 docs/reproduction_reports/utf_a2_final_report_20260907.md。
详见 docs/reproduction_reports/utf_a2_initial_checkpoint_20260907.md 与 results/methods_11_15_pipeline_state.json。以下旧授权与阶段文字仅供历史参考；如冲突，以本段及最新用户决定为准。
<!-- UTF_A2_CURRENT_AUTHORITY_END -->

<!-- WMKD_METHODS_11_15_CURRENT_BEGIN -->
当前授权（2026-09-07）：用户明确解除暂停，仅恢复 Method 13 UTF Experiment A，STRICT SERIAL INTERACTIVE MODE。先修复 DeepSpeed 整数兼容并通过真实单步 preflight，再正式训练、detector、negative control、utility、reload、归档验证及 Git 闭环。不得启动 Method 14/15；auto_advance=false，auto_shutdown=false；UTF 闭环后 STOP。历史暂停证据保留。

EaaW / Instructional Fingerprinting CLOSED；UTF 等待 attempt 4 单步预检；Double-I / CodeGenGuard NOT_STARTED。
<!-- WMKD_METHODS_11_15_CURRENT_END -->

# WMKD_Benchmark 当前状态：方法 11–15 之前

当前授权更新（2026-09-05）：用户已正式批准五方法串行 Experiment A 自动复现、最小工程修复、逐方法归档/Git闭环及全部terminal后的自动关机。前次等待prompt/STOP仅属于已结束的迁移任务。详见 [METHODS_11_15_AUTOMATION.md](METHODS_11_15_AUTOMATION.md) 与 results/methods_11_15_pipeline_state.json；旧科学设计禁改及KEEP/UNCERTAIN保留规则继续有效。


本文件与 `EXPERIMENT_PROTOCOL.md` 定义当前状态和规则；带日期的旧日志仅为历史证据，不构成新执行指令。项目目标是研究 LLM ownership-verification watermarking/fingerprinting 在知识蒸馏和相关模型提取攻击下的稳健性与稳定性，面向 benchmark / analysis 论文，目标 ICLR / 顶级会议。

## 已完成的第一批

方法 1–10：PN-FP、EverTracer、CTCC、iSeal、SCW、LLMPrint、REEF、HuRef、AWM、ZeroPrint。
正式比较矩阵已 CLOSED：10 reproduction + 10 Ba + 10 Bb comparison = 30 个比较实验槽位；共享被动攻击不是五次独立训练。
PN-FP、EverTracer、iSeal、SCW Bb COMPLETE；CTCC 使用独立 Bb2 COMPLETE 填入比较槽位。
原 CTCC Bb 永久保留为 `BLOCKED_AT_PREPROCESSING_ACCEPTANCE_GATE`：fallback 202 > gate 200，后续 Student/detector/utility `NOT_RUN`。

| 方法 / 原生指标 | Teacher | Base | Ba | Bb comparison |
|---|---|---|---|---|
| PN-FP / matches | 956/1024 | 1/1024 | 98/1024 | 72/1024 |
| EverTracer / AUC, TPR | 1, 1 | .4417, .05 | .4987, .06 | .4757, .08 |
| CTCC / trigger | 95/95 | 0/95 | 0/95 | Bb2: 0/95; negatives 0/205 |
| iSeal / registered; BLEU | 179/200; 69.171651 | 0/200; 2.332514 | 0/200; 2.589326 | 0/200; 2.3018129521270327 |
| SCW / p-value | 0 | .9199569225 | .8440861702 | .9529914855957031 |

以上指标不可统一为伪造的 retention %。仅支持已测设置下的结论，不能推导普遍移除、普遍免疫或精确消失步骤。
来源：`reproduction_reports/proactive_bb_final_closure_integrity.md`、各方法 canonical summary/full log。

Passive Shared Ba COMPLETE；原 Bb 与 Bb2 均 `BLOCKED_AT_PILOT`；Bb3 COMPLETE，5/5 frozen detectors positive。
Bb3 含 4,635/20,000 = 23.175% atomic identity，必须披露；同骨干结果不证明指纹转移或普遍 KD 免疫。

## 冻结的历史 UP 参考

`VALIDATED_UP_REFERENCE = PASSIVE_SHARED_BB3`。
若 Qwen non-special-token count <= 1，保留 source answer；否则使用冻结的 Qwen2.5-3B-Instruct semantic-preserving paraphrase。
Prompt SHA256 `7f4284788b5147bca7f444db989eab6f2f9f3a10eb06fddb309fc06748414495`；do_sample=true、temperature=.7、top_p=.9、seed=42。
这不是方法 11–15 已获授权的新攻击配置，不得回写历史协议。

## 证据、归档与恢复

Canonical index：`../results/experiment_full_logs_index.json`：32 objects / 32 unique composite IDs，严格路径及 SHA 检查见 `../results/pre_methods_11_15_validation.json`。
30 比较槽位与 32 canonical scientific objects 不是同一计数口径。此次维护不新增 scientific object。

Canonical archive：`../results/project_archive_inventory.json`，41 artifacts：24 VERIFIED_ARCHIVED、8 ARCHIVED_STRONGLY_VERIFIED、0 MISSING_ARCHIVE、7 NOT_APPLICABLE、2 PERMANENTLY_UNAVAILABLE。
早期模型 full independent redownload 样本为 2；另外 8 个 strong-remote 不得称为 full-redownload。
报告：`reproduction_reports/project_modelscope_archive_final_report.md`。

归档闭环 flags：ALL_RECOVERABLE_CRITICAL_ARTIFACTS_ARCHIVED、ALL_RECOVERABLE_CRITICAL_MODELS_ARCHIVED、ALL_RECOVERABLE_CRITICAL_DATASETS_ARCHIVED、ALL_CRITICAL_DETECTOR_DEPENDENCIES_ARCHIVED、ALL_COMPLETED_BB_ARTIFACTS_VERIFIED_ARCHIVED、EARLY_A_BA_ARCHIVES_STRONGLY_VERIFIED、STRICT_FULL_LOG_INDEX_32_32_PASS 均 YES。
`EARLY_A_BA_FULL_REDOWNLOAD_SAMPLE_COUNT = 2`。
`SERVER_CAN_BE_DELETED_WITHOUT_NEW_RECOVERABLE_SCIENTIFIC_DATA_LOSS = YES` 是恢复能力结论，不是任意删除授权。

永久历史缺失：PN-FP original canonical Ba frozen20k 与 SCW original canonical Ba frozen20k；后来的 reconstructed parents 是不同身份，已归档验证，不代表原件恢复。
清理仅按 `../results/pre_methods_11_15_cleanup.json` 的 exact DELETE paths 执行；保留历史路径，未来使用前按 archive manifest 恢复并校验 SHA，不能把清理后的本地路径误认为仍存在。

## New proactive ownership-verification methods

| 编号 | 方法 | 当前状态 |
|---|---|---|
| 11 | EaaW | NOT_STARTED |
| 12 | Instructional Fingerprinting | NOT_STARTED |
| 13 | UTF | NOT_STARTED |
| 14 | Double-I Watermark | NOT_STARTED |
| 15 | CodeGenGuard | NOT_STARTED |

这是当前计划顺序，不是不可变的科研设计。均按主动嵌入式语言模型所有权验证方法入选；Instructional Fingerprinting / UTF 使用 fingerprint 术语；CodeGenGuard 面向代码语言模型。正式执行前仍须核实官方实现。
选择优先级：官方代码、稳定实现、小下载、轻量模型、快训练、低工程复杂度。
`NEXT_STAGE = METHOD_11_EAAW_EXPERIMENT_A`，`STATUS = NOT_STARTED`。
等待独立正式 Experiment A prompt；本次任务结束后 STOP。不得下载 EaaW 模型/数据、clone 新方法源码、训练、预处理、detector 或 utility science。

## 新会话恢复入口

1. 读取本文件、`EXPERIMENT_PROTOCOL.md`、根目录 README / PROJECT_STATUS / TODO / DECISIONS / EXPERIMENT_LOG / CODEX_LOG。
2. 本地与 AutoDL 分别 git fetch、status、rev-parse HEAD origin/main、rev-list --left-right --count HEAD...origin/main。历史 HEAD 仅为基线；最终提交用 Git 实际值确认，避免自引用提交 SHA。
3. 本地：`C:\Users\Eason\Desktop\WMKD_Benchmark`；GitHub：`MakiseKurisuEasonHan/WMKD_Benchmark`。
4. AutoDL：`ssh -p 32514 root@connect.westd.seetacloud.com`；代码 `/root/autodl-tmp/WMKD_Benchmark`；数据 `/root/autodl-tmp/WMKD_Benchmark_data`。不能假设旧 alias 6000。AutoDL 学校 VPN 关闭；La Trobe 学校 VPN 开启。
5. 本轮硬件：RTX PRO 6000 97887 MiB，driver 580.82.09 / driver-supported CUDA 13.0；cgroup CPU quota 22 核、memory.max 118111600640 bytes (110 GiB)。宿主 free/nproc 展示的 1 TiB / 208 并非容器配额。CUDA toolkit、Python/PyTorch 实验环境须在正式任务重新核实。
6. 清理前后磁盘、删除列表、保留对象见 cleanup JSON；严格验证见 validation JSON。只继续用户明确授权的下一步。

## 本轮实际发现与修复

在归档权重删除前发现：历史索引在 Windows 为 32/32 PASS，但 AutoDL 有 16 个 full logs 因 Git LF/CRLF 转换而字节 SHA 不符。转换回 CRLF 后全部精确匹配原索引哈希，JSON 科学内容未改变。`.gitattributes` 现逐个固定 32 个对象的原有换行格式（16 CRLF、16 LF），保留原索引及历史哈希。`scripts/validate_durable_state.py` 默认只读；显式 `--restore-indexed-eol` 只允许转换后精确等于既有索引 SHA 的修复，不能容忍或掩盖内容差异。今后新增 full log 时必须固定稳定的换行字节并验证 Windows/Linux 两端。

清理范围有意限定为已匹配 strong-remote evidence 的历史 A/Ba 权重；未额外请求 ModelScope 网络重验证，亦未将 strong-remote 升格为 full-redownload。其它已归档 Bb 模型在本轮未建立逐文件清理匹配，按 UNCERTAIN 保留；这不表示其归档缺失。优化器及其它非权重证据也保留。
