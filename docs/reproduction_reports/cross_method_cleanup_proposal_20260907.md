# 五方法审计：清理候选（尚未删除）

仅以下七个 optimizer.pt；不包含模型权重、其他 checkpoint 文件、数据、日志、manifest 或代码。
这些优化器状态尚未核验归档恢复；当前分类 UNCERTAIN，按规则保留。批准弃置后无法从这些状态精确恢复优化器训练。

| Exact path | GiB |
|---|---:|
| `/root/autodl-tmp/WMKD_Benchmark_data/runs/ctcc_ba/ctcc_ba_20260830_025244/checkpoints/student/checkpoint-7500/optimizer.pt` | 11.969 |
| `/root/autodl-tmp/WMKD_Benchmark_data/runs/scw/ba/scw_ba_full_20260831_193828_cont1/student/checkpoint-7500/optimizer.pt` | 11.969 |
| `/root/autodl-tmp/WMKD_Benchmark_data/runs/evertracer_bb_student/evertracer_bb_student_20260904_033837/student/checkpoint-7500/optimizer.pt` | 11.969 |
| `/root/autodl-tmp/WMKD_Benchmark_data/runs/iseal_bb/iseal_bb_20260904_055000/student/checkpoint-7500/optimizer.pt` | 11.969 |
| `/root/autodl-tmp/WMKD_Benchmark_data/runs/pnfp_bb/pnfp_bb_20260904_055000/student/checkpoint-7500/optimizer.pt` | 11.969 |
| `/root/autodl-tmp/WMKD_Benchmark_data/runs/scw_bb/scw_bb_20260904_055000/student/checkpoint-7500/optimizer.pt` | 11.969 |
| `/root/autodl-tmp/WMKD_Benchmark_data/runs/ctcc_bb2/ctcc_bb2_20260905_011104/student/checkpoint-7500/optimizer.pt` | 11.969 |

合计 83.780 GiB；实际释放 0。
