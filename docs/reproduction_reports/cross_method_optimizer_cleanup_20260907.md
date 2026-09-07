# 七个 optimizer.pt 清理完成（2026-09-07）

用户逐项批准精确七路径，并明确豁免 SCW Ba 原始 frozen dataset 历史缺失。该豁免不改变数据 provenance。

删除前：七项 regular file / 非 symlink / inode-size 身份一致 / Adam state+param_groups+exp_avg+exp_avg_sq 结构确认 / 无活动引用。没有反序列化执行 pickle。
正式模型：五个 Bb/Bb2 本地 final 权重 SHA 通过；CTCC/SCW Ba 正式模型位于 ModelScope，实时 canonical 文件大小/SHA 元数据通过。本轮未宣称这两个模型已恢复至本地。
243 项候选保留证据中，240 项存在；其中 46 项跨平台差异仅 CRLF/LF。另三项是 EverTracer 远端归档添加的 metadata 文件，不位于本地 final_model；其本地正式模型、训练配置、日志/report 已在各自原路径保留。
删除后 344 个受保护文件通过 size/inode/mtime 检查；七项 optimizer 均不存在；其余 checkpoint 文件和模型权重保留。

| Exact path | Logical bytes | Released allocated bytes |
|---|---:|---:|
| `/root/autodl-tmp/WMKD_Benchmark_data/runs/ctcc_ba/ctcc_ba_20260830_025244/checkpoints/student/checkpoint-7500/optimizer.pt` | 12851221159 | 12851224576 |
| `/root/autodl-tmp/WMKD_Benchmark_data/runs/scw/ba/scw_ba_full_20260831_193828_cont1/student/checkpoint-7500/optimizer.pt` | 12851221159 | 12851224576 |
| `/root/autodl-tmp/WMKD_Benchmark_data/runs/evertracer_bb_student/evertracer_bb_student_20260904_033837/student/checkpoint-7500/optimizer.pt` | 12851221159 | 12851224576 |
| `/root/autodl-tmp/WMKD_Benchmark_data/runs/iseal_bb/iseal_bb_20260904_055000/student/checkpoint-7500/optimizer.pt` | 12851221159 | 12851224576 |
| `/root/autodl-tmp/WMKD_Benchmark_data/runs/pnfp_bb/pnfp_bb_20260904_055000/student/checkpoint-7500/optimizer.pt` | 12851221159 | 12851224576 |
| `/root/autodl-tmp/WMKD_Benchmark_data/runs/scw_bb/scw_bb_20260904_055000/student/checkpoint-7500/optimizer.pt` | 12851221159 | 12851224576 |
| `/root/autodl-tmp/WMKD_Benchmark_data/runs/ctcc_bb2/ctcc_bb2_20260905_011104/student/checkpoint-7500/optimizer.pt` | 12851221159 | 12851224576 |

文件分配空间释放 89,958,572,032 bytes = 83.780449 GiB。
df 可用空间净增 89,958,567,936 bytes；与文件空间相差 4096 bytes，为本轮审计回执等文件系统占用差异，未隐藏差额。

```text
Filesystem      Size  Used Avail Use% Mounted on
/dev/md0        500G  329G  172G  66% /root/autodl-tmp
```

实际删除其他路径：0。训练：未启动。EaaW：未处理。GPU：仅只读观察，未 kill/reset。
机器回执 results/cross_method_audit_20260907/optimizer_cleanup_execution.json 同时保存在本地和 AutoDL。
