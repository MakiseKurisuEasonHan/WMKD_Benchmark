# UTF 恢复结果与科学预算决策（2026-09-07）

本文件为诊断报告，不是新的执行授权。Run ID：`utf_a_20260905_111830`。

## 当前结论

`RED_SCIENTIFIC_BUDGET_DECISION_REQUIRED`。Attempt 8 完成 forward/backward，但 Trainer 显示 step=1 时 CPUAdam 实际调用为 0；真实 optimizer-step 断言正确拒绝预检成功。正式训练、detector、utility、fresh trained-model reload 与新模型归档均未启动。不能把该结果认定为 UTF 科学失败，也不能把方法标成已闭环。

实际 pipeline 仍为 `WAITING_FOR_REPAIR`，监督器 PID 2051 仍存在、处于等待状态；GPU 已核实 0/97887 MiB、0%且无计算进程，数据盘约112 GiB可用。auto_advance=false、auto_shutdown=false；11/12 CLOSED，14/15 未启动。

## 工程修复及证据

1. 先保存 attempt 3 原始日志、配置、dirty runtime、diff 和 SHA；scoped stash + fast-forward 保留暂停提交与远端最新失败历史。原件十项 SHA 核验一致，字节换行已固定。
2. Transformers 4.44 `integrations/deepspeed.py:244` 用 `0.9*hidden_size*hidden_size` 生成 15099494.4。配置生成层以 `int()` 得到 15099494；相邻 reduce_bucket=16777216、persistence_threshold=40960本已为整数。隔离、幂等回归通过。
3. Attempt 4 越过整数检查，CPUAdam 初始化发现已安装 Ninja 未在 PATH；仅补 overlay/bin 与原 Python/bin，无重复下载。
4. Attempts 5/6/7 在初始化阶段 SIGKILL。6/7 采样到106.44/107.66 GiB主机内存，上限110 GiB；oom_kill计数0且内核日志不可读，因此“主机内存压力”是证据支持的诊断，不声称已拿到内核 OOM 事件。
5. 原生 hybrid optimizer offload先尝试CPU比例0.5，再改0.25并关闭optimizer pin_memory以避免大块缓冲复制。ZeRO3、参数CPU offload保留；CPUAdam/GPU AdamW后端使用相同AdamW超参数。另限制不必要的Inductor编译池为1线程。该资源适配不能描述为原始offload设置完全未变。
6. Attempt 8 成功进入训练循环；loss=4.71935510635376，Trainer runtime=335.7027秒，显示epoch=1、step=1、LR=0；CPUAdam调用0，断言失败。GPU采样峰值55124688896 bytes（51.34 GiB），主机93411860480 bytes（约87 GiB）。这些不是PyTorch精确分配峰值；完整真实optimizer step资源容量仍未验证。

原始预检日志、资源采样、配置及不可变回执位于 `results/methods_11_15/utf/engineering_resume_20260907/`；诊断数字见 `results/utf_scientific_decision_required_20260907.json`。

## 为什么需要科学决策

冻结设置为32条数据、micro-batch1、accumulation64、3epochs、seed42、LR2e-5、warmup100。实际 scheduler 是 DeepSpeed `WarmupLR`，不能把 Trainer 的 cosine字段误报为实际scheduler。

已安装源码证据：

- `transformers/trainer.py:2307–2320,2362`：epoch不足accumulation时仍增加Trainer global_step。
- `accelerate/utils/deepspeed.py:164–175`：backward内调用engine.step；外层optimizer/scheduler为兼容空操作。
- `deepspeed/runtime/engine.py:2339–2345`：更新边界为 `(micro_steps+1)%64==0`；`:2429–2436` 在optimizer之后调用scheduler。
- `deepspeed/runtime/lr_schedules.py:655–687`：WarmupLR默认min_lr=0，构造时设为0；`:709–715`为warmup公式。

由此推断正式3epochs共96micro-step，仅跨过一次完整64-step更新边界，而且其初始LR为0；预计没有非零LR参数更新。**这是源码推断，不是已经运行正式训练得到的结果。** 单纯将诊断max_steps加到2或删除CPUAdam断言，不能解决正式科学预算问题。

用户需明确预期实际optimizer-step预算、warmup/scheduler与尾批累积规则。没有据此擅改epochs、有效batch、数据或调度，也未为了获得正指纹结果调参。

## 持久化范围与审批限制

自动审批拒绝了“SIGTERM远端监督器并批量修改AGENTS、协议、状态和日志”，认为具体副作用缺乏明确授权；整项操作未执行。安全替代只读取/复制证据并新增本报告，不修改生效控制文件，不停止进程。若要停止等待中的PID2051并将生效状态改为WAITING_FOR_USER_SCIENTIFIC_DECISION，需要用户确认。

轻量诊断Git提交不等于UTF完整科学闭环。没有新正式模型可归档；canonical full-log index没有新增科学对象。下一步先解决科学预算，不进入Method14/15，不关机。
