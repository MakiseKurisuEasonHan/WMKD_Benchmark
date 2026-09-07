# UTF A2 — 完成记录，非 Preferred Teacher

Run ID: `utf_a2_20260907_30ep`
PREFERRED_TEACHER = NO
FINAL_SCIENTIFIC_STATUS = COMPLETED_NOT_PREFERRED
ENGINEERING_STATUS = COMPLETE
DETECTOR_STATUS = NEGATIVE_CONTROL_FAILED
BENCHMARK_TEACHER_ELIGIBLE = NO
NEXT_ACTION = WAITING_FOR_USER_SCIENTIFIC_DECISION

采用 canonical meta-llama/Llama-3.2-3B-Instruct，revision 0cb88a4f764b7a12671c53f0838cd831a0843b95。旧 UTF 7B A 保留为 historical / superseded，eligible=NO，未改成 FAILED。

PAPER_EPOCHS=30；PINNED_RUNTIME_JSON_EPOCHS=3；WMKD_A2_SELECTED_EPOCHS=30；SELECTION_BASIS=PAPER_PROTOCOL_PLUS_WARMUP_COHERENCE。论文明确30 epochs，代码JSON实际3；3 epochs至多96次更新，不足以越过100-step warmup。用户明确选30 epochs；差异未隐藏。完整七点依据在 training_config.json 和 utf_a2_30epoch_protocol_20260907.md。

配置：32 records，1 unique fingerprint pair；micro=1，accumulation=1，effective batch=1；30 epochs，960 exposures，960 optimizer calls，958 nonzero-LR updates，warmup=100，post-warmup=860。首个非零LR更新为3，首个最大LR更新为101。Full FT，BF16计算，FP32 GPU master weights/Adam moments，无CPUAdam或offload。LR=2e-5，官方WarmupLR log后恒定；未切换为JSON中被覆盖的cosine。无tail accumulation。

可训练参数 3,212,749,824。唯一preflight PASS，3次optimizer调用后验证参数确实改变；未复用preflight权重。训练最终loss=2.54702172242105e-05，训练循环耗时=240.170s。显存allocated峰值=50.832 GiB，reserved峰值=52.842 GiB，主机RAM峰值=14.568 GiB。最终BF16权重相对Base的数值变化另经CPU safetensors检查。最终模型已fresh-process加载。

| Detector | Fingerprint | Non-trigger target emission |
|---|---:|---:|
| Teacher | 1/1 | 500/500 |
| Base | 0/1 | 0/500 |

使用未修改的pinned fp_test函数，greedy max_new_tokens=100，目标字符串包含规则及500次官方随机负控。Teacher虽然通过官方positive布尔判定，但负控全部命中，区分性门槛失败；不能认定有效Preferred Teacher。无未解决的detector执行错误。

| Primary utility | Base | Teacher | Delta |
|---|---:|---:|---:|
| ARC-Challenge acc_norm | 0.45051194539249145 | 0.3796928327645051 | -0.07081911262798635 |
| TruthfulQA MC2 acc | 0.5054615624501503 | 0.5039777188370608 | -0.0014838436130895083 |

UTILITY_STATUS=MATERIAL_DEGRADATION_ARC：ARC下降约7.08个百分点，MC2下降约0.15个百分点。不事后创造宽松阈值。复用WMKD现有evaluator及其冻结依赖/数据版本。旧Base的动态Today Date无法与本次实际prompt确认一致，按用户授权仅补跑一次Base并冻结；Base/Teacher同日prompt和token IDs核对一致。未使用.408703或.4951作为基线。

工程修复：detector attempt1因cwd无法解析既有canonical alias，在任何probe前退出；GREEN修复为进入既有work目录，attempt2恢复。旧日志保留；无重训、无新科学配置。

PRIVATE archive: `MakiseKurisuEasonHan/WMKD-UTF-A2-utf-a2-20260907-30ep`。在用户新规则生效前已提交94文件；恢复验证按用户要求停止，未验收为VERIFIED_ARCHIVED。远端PRIVATE独立仓库明确标为not preferred，保留待删除审批；本地模型6,434,691,656 bytes及恢复partial保留。禁止追加上传。本轮删除0。

Full log: results/methods_11_15/utf/experiment_a2/full_experiment_log.json。原始detector generations、训练日志、数据与完整环境证据在run目录及PRIVATE归档；Git仅保存轻量结果/manifest与代码。

限制：Single canonical backbone, one fingerprint pair, one frozen primary configuration; no generalization to other UTF settings. Paper 30 epochs and pinned runtime JSON 3 epochs discrepancy remains explicit; user selected paper protocol plus warmup coherence. Single-GPU accumulation=1 is an explicitly approved update-budget adaptation, not original effective-batch equivalence. BF16 compute uses GPU FP32 master parameters/Adam states; not a bitwise reproduction of native ZeRO3 offload numerics. Pinned verifier default system template is retained even though official UTF training uses the empty-system template. Teacher target emission is non-specific (500/500 non-trigger guesses); positive probe recovery is not valid ownership evidence by itself. ARC material decline is descriptive; no new acceptance threshold or significance test is claimed. Native SciQ/LAMBADA supplemental utility was not run; no retuning or second scientific configuration was attempted.

UTF A2已结束；任何下一科学配置须用户决定。未启动其他方法、orchestrator、guardian、watchdog、自动继续或自动关机。

永久归档规则：见 docs/ARTIFACT_ARCHIVE_POLICY.md。远端只读清单确认94文件均存在且大小一致（payload 6,495,952,613 bytes）；不声称完成独立恢复验证。当前无本项目后台进程，GPU 0 MiB / 0%，数据盘可用107,533,938,688 bytes。所有删除均未执行。
