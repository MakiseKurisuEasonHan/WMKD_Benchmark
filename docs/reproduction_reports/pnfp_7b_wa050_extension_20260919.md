# PN-FP 7B WA=.50 extension — 2026-09-19

WA=.50 extension EXTENSION_COMPLETE_NOT_PREFERRED；fresh-reload 804/1024，best有效更新19；preferred候选=False。训练停止，未启动蒸馏，授权证据闭环后自动关机。

## 冻结配置与恢复

model=meta-llama/Llama-2-7b-chat-hf，revision=f5db02db724555f92da89c216ac04704f23d4590。冻结1024，key16/response1，Perinucleus t=.8/k=3，WA=.50，DM=.25，seed42，BF16全参数6,738,415,616，AdamW8bit0.50.0及activation checkpointing不变。原LR5e-5、WarmupDecayLR horizon40/effective warmup2、seq64、microbatch6+2、accum171、chat template、detector均保留。8-bit moment storage是engineering adaptation，不宣称FP32 Adam数值等价。

旧run未保存optimizer/scheduler状态，因此从canonical初始化重放前14calls（12有效更新），逐点精确比对loss、recall及数据顺序，call14与旧best全部state_dict张量bitwise比较后才延长；没有从权重重置Adam继续。原optimizer moments未保留，不能独立声称原moment逐bit已核验。重放不保存重复模型。恢复门槛：{'status': 'PASS', 'call': 14, 'nonzero_updates': 12, 'all_state_dict_tensors_bitwise_equal': 291, 'optimizer_recovery': 'Recomputed from canonical initialization with identical14-call trajectory; no optimizer reset at extension boundary'}。

## 新增轨迹

| Call | 有效更新 | LR | Loss | live recall | live% | best fresh |
|---:|---:|---:|---:|---:|---:|---:|
|15|13|3.5526316e-05|1.563495|684/1024|66.80%|692/1024|
|16|14|3.4210526e-05|1.508460|703/1024|68.65%|703/1024|
|17|15|3.2894737e-05|1.458358|744/1024|72.66%|741/1024|
|18|16|3.1578947e-05|1.376915|760/1024|74.22%|756/1024|
|19|17|3.0263158e-05|1.318373|754/1024|73.63%|756/1024|
|20|18|2.8947368e-05|1.344744|772/1024|75.39%|774/1024|
|21|19|2.7631579e-05|1.246683|805/1024|78.61%|804/1024|
|22|20|2.6315789e-05|1.278378|789/1024|77.05%|804/1024|
|23|21|2.5e-05|1.270803|776/1024|75.78%|804/1024|
|24|22|2.3684211e-05|1.242229|780/1024|76.17%|804/1024|

停止原因：THREE_CHECKS_WITHOUT_MATERIAL_1PP_GAIN。最多24累计有效更新；3检测无累计11条实质提升或3次持续下降早停。每点live1024，新高保存pending后fresh-reload验证；仅fresh新高替换旧best。fresh结果用于最终checkpoint结论，live和fresh不混用。

## 最终结果与utility

最终fresh detector：804/1024，invalid=0，errors=0。70/80/90%是否达到：[True, False, False]。

| 完整utility | Base | Selected best | Delta pp |
|---|---:|---:|---:|
| ARC-Challenge acc_norm (1172) |0.3660409556313993|0.4206484641638225|+5.4608|
| TruthfulQA-MC2 (817) |0.45754715790333667|0.44199761508116137|-1.5550|

完整utility在fresh recall较上次完整评估提高103条时触发，或达到80%候选门槛时评估；未每checkpoint评估。最终best如已在选中点完整评估，则复用同一checkpoint唯一正式结果，不重复运行；final_utility.json保留对应step与完整分数。Base复用相同canonical固定数据的旧正式全量分数。两项均下降>5pp停止；fresh>=820且两项下降均<=3pp标记preferred候选并停止。未追求1024/1024。

## 资源、证据与运行边界

{
  "gpu_sampled_peak_GiB": 52.6181640625,
  "host_cgroup_peak_GiB": 78.02806854248047,
  "host_RSS_peak_GiB": 29.41781234741211,
  "gpu_allocated_peak_GiB": 51.37268114089966,
  "disk_peak_used_GiB": 64.35958862304688,
  "disk_final_free_GiB": 18.192962646484375,
  "mean_new_update_seconds": 24.996208087354898,
  "training_wall_seconds": 1600.3450848795474,
  "probe_seconds": 793.5120877884328
}

Best保留在 `/root/autodl-tmp/WMKD_Benchmark_data/scale_7b/wa050_extension_v1/best_model`。校验10个模型文件SHA；轻量证据archiveSHA=6ccb7e206e44082f968a7733bb610b2fc59b2bb68dcc12de36fd40db3bb2009b。仅新best验证后轮换删除旧WA50 best，删除路径、字节和理由见checkpoint_retention.jsonl；不删除canonical模型及正式结果。原pilot历史数据不覆盖，原模型位置如被替换则另记supersession。所有配置、provenance、逐点CSV/JSON、detector、utility、runtime、memory、报告同步本地；Git只提交本任务。Git push与关机实况见git_receipt.json、shutdown_receipt.json、automation_state.json。

本轮单seed、有限窗口，达到候选门槛不等同已证明更长训练稳定性。不启动distillation、不改科学参数，不释放实例。用户已明确授权成功/早停/硬失败均保存同步后执行/usr/bin/shutdown；失败缺失字段保留N/A，不虚构结果。

## 关机与最终Git闭环

关机前81个项目文件SHA双端一致、模型10文件SHA验证、最终detector/utility/report存在、GPU无worker且日志落盘。直接exec `/usr/bin/shutdown` 返回ENOEXEC；随后用 `/bin/bash /usr/bin/shutdown` 执行相同官方文本脚本，远端主动关闭连接，之后两次SSH检查均不可达。控制台电源状态未另行查询，不声称拿到平台状态API确认；未释放实例。模型与正式结果保留于数据盘。初次错误和shell重试均保留收据；关闭后的状态补记只存本地。

Git科研闭环commit为ee28d978ffed017ede74f797b1c4cab90bd2d20c；push在非交互模式下因凭据缺失失败，记PUSH_PENDING，未等待用户。后续本地commit保存关机收据及脚本ENOEXEC解释器回退修复。

训练进程总wall（含恢复重放、trajectory和两次完整utility）为1709.475秒；独立最终detector阶段为22.651秒。累计22有效更新中，12个是恢复重放、10个为新增；第19有效更新达到最高fresh804/1024，20–22未创新高，按规则停止。无NaN/Inf。
