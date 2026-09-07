# PN-FP Ba checkpoint trajectory follow-up 完整报告

Run ID: `pnfp_ba_trajectory_followup_20260907_reconstructed_parent`。状态COMPLETE，11/11测量点及独立完整性验证PASS。

本轮是 reconstructed-parent mechanistic follow-up，不是历史 Ba exact replay。原始Ba frozen dataset永久缺失；现有protocol-faithful parent 20k不声称byte-identical或sample-identical。

## 实测轨迹

| Step | Detected / 1024 | Rate | 最近train loss | 累计训练回调耗时(s) | Wall(s) |
|---:|---:|---:|---:|---:|---:|
| 0 | 1/1024 | 0.0977% | N/A | 0.000 | 27.050 |
| 25 | 1/1024 | 0.0977% | 1.6851 | 6.155 | 108.763 |
| 50 | 3/1024 | 0.2930% | 1.3432 | 11.150 | 187.597 |
| 100 | 58/1024 | 5.6641% | 0.6902 | 21.495 | 271.441 |
| 250 | 79/1024 | 7.7148% | 0.6295 | 52.048 | 385.334 |
| 500 | 86/1024 | 8.3984% | 0.5212 | 103.334 | 527.188 |
| 1000 | 85/1024 | 8.3008% | 0.5102 | 207.303 | 735.182 |
| 2000 | 94/1024 | 9.1797% | 0.4791 | 414.938 | 1078.856 |
| 4000 | 99/1024 | 9.6680% | 0.3148 | 829.156 | 1688.716 |
| 6000 | 99/1024 | 9.6680% | 0.3396 | 1244.106 | 2299.440 |
| 7500 | 99/1024 | 9.6680% | 0.2766 | 1552.474 | 2773.714 |

训练耗时为on_step_begin到on_step_end回调计时之和，排除checkpoint、检测、数据读取与回调外开销，不等同端到端时长。step25的loss来自最近step20日志，其余目标点有同step日志。
完整run wall=2803.819s（46.73分钟），Trainer平均train_loss=0.398821849569。

历史Teacher=956/1024（93.3594%），历史Ba=98/1024（9.5703%），本轮实测Base step0=1/1024（0.0977%），final Student=99/1024（9.6680%）。Teacher不是step0。99接近98不能证明exact replay，也不是训练/调参目标。

## 解释与限制

实测事实：早期1→1→3→58→79→86；step1000小幅回落至85，2000达到94，4000/6000/7500均为99。11点invalid=0、errors=0；最终fresh reload的1024条prediction/target/decision与step7500逐条一致。各点key-level获得/丢失/保留数量见transition_analysis.json，计数平台不自动等于匹配key身份完全不变。

解释：最合适描述为早期获得较低匹配率信号，随后大体上升并趋于平台，伴有局部非单调变化；没有观察到已采样点上的强峰值后遗忘或collapse。“较低”是相对Teacher93.36%的描述性比较，不是新detector阈值。

不支持的因果：单seed单run不提供跨run稳定性/显著性；不能排除采样点之间短暂峰值，不能仅凭轨迹证明水印信息转移的独立机制。尚无当前paired Bb结果，不推断paraphrasing效果。

联合exposure audit：docs/reproduction_reports/cross_method_dataset_exposure_audit_20260907.md。完整注册key在20k问题中exact overlap=0，完整response在答案/labels中exact overlap=0；这不代表partial-token、semantic或indirect信息为零。本detector是one-token exact match，完整response零重叠尤其不能排除首token层面的重叠。联合事实是完整串直接重叠为零、训练中per-key match数上升；因果机制未建立。

## 科学配置与连续性

Fresh Base meta-llama/Llama-3.2-3B-Instruct，revision 0cb88a4f764b7a12671c53f0838cd831a0843b95。BF16 full FT，无LoRA；seed42、batch8、accum1、3epochs/7500updates、LR1e-5、AdamW torch、cosine、warmup_ratio0.03、weight_decay0、max_length1024。历史SFTDataset/Collator与frozen detector逻辑未改，仅增加checkpoint/evidence回调。

同一PID4676、同一Trainer连续完成7500steps。每点保存完整model/optimizer/scheduler/RNG/Trainer state，新进程加载检测；父optimizer/scheduler对象保持，Python/NumPy/CPU/CUDA RNG摘要前后相同。sampler fetch共60000，每epoch20000行各一次，未拆成11次独立重训。原生template及序列化日期见tokenizer_template_identity.json。

环境PyTorch2.8.0+cu128，RTX PRO6000 Blackwell Server Edition 97887MiB；结束GPU0%/0MiB，无worker，disk available154GiB。Generation sanity两例分别输出Paris与连贯光合作用解释，只是小规模sanity，不是utility。Utility=NOT_RUN_NOT_IN_FROZEN_FOLLOWUP_PROTOCOL。

## 永久证据、SHA与保留

永久目录results/pnfp/experiment_ba_trajectory_followup/。每点detector_raw/result、metadata、checkpoint SHA清单、evidence SHA清单、stdout均保存；另有完整训练日志、采样顺序、full log、config、provenance、dataset/detector manifest。
最终可恢复checkpoint保留：`/root/autodl-tmp/WMKD_Benchmark_data/runs/pnfp_ba_trajectory/pnfp_ba_trajectory_followup_20260907_reconstructed_parent/training/checkpoint-7500`；最终模型和optimizer未删除、未上传。旧临时checkpoint仅在新可恢复checkpoint及证据通过后删除，详见checkpoint_inventory.json。

| 文件 | SHA256 |
|---|---|
| trajectory.json | `3533b780be160b0ae21599b906f7f51adb6f6747dfaf818cb34a521b670aae9f` |
| trajectory.csv | `1d962a5f17a5e2cfc3d2e37665df0d6f3779dc5f51d1a7f6cc260f2186cd97e6` |
| plotting_ready.csv | `1d962a5f17a5e2cfc3d2e37665df0d6f3779dc5f51d1a7f6cc260f2186cd97e6` |

完整清单closure_sha_manifest.json；各点checkpoints/step_*/evidence_sha_manifest.json。worker原始完成时full log/state/summary/清单保留于worker_closure_snapshot/。

## Git与范围

提交版全局索引43个唯一full-log路径/0重复/0broken/0SHA mismatch。部分passive对象共享run_id，不能把共享run_id误判为重复scientific object。工作区44条视图仍保留此前未提交的Bb计划和EaaW索引改动；这些不混入本次提交。当前Ba条目按run_id迁移到新永久路径，旧planned对象原地保留，不覆盖历史Ba/Bb。

仅本轮轻量证据、脚本、报告及必要状态/索引提交和push；最终commit身份见Git记录与交付消息。完成后STOP，等待用户下一步，不启动Bb、其他方法、模型上传或关机。
