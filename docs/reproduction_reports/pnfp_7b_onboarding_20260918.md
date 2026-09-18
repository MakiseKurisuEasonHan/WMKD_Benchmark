# PN-FP 7B 补实验：恢复记录（2026-09-18）

状态：准备中，AutoDL SSH 认证阻塞；没有下载模型、测速或正式训练，没有科学结果。

## 最新授权

本轮仅新增 PN-FP 7B Teacher → same-lineage Ba → Bb → Bc。Teacher 成功后才进入蒸馏。复用既有科学定义，真实短测速先于正式 Teacher，四个最终模型及证据保留。用户完整请求保存在 `results/pnfp/scale_7b/user_authorization_20260918.txt`。历史其他方法、旧实例关机授权不用于本轮。

## Git / 环境实测

- 原 remote：`https://github.com/MakiseKurisuEasonHan/WMKD_Benchmark.git`。
- 当前 branch：main；本地 HEAD、缓存 origin/main、GitHub 连接器读取的实时 main 均为 `d840b76637afaf6c699598832eee7d9c8c8d0d8d`。提交无分叉。
- 原工作区有 11 个 tracked 文件修改及多项 untracked 历史证据、论文文件，均未覆盖、清理或提交。
- 本地捆绑 Git 缺少 remote-https helper，CLI ls-remote 失败；实时提交身份改用 GitHub 只读连接器核实。push 通道尚未修复。
- 新 endpoint：`root@connect.westd.seetacloud.com:47990`。获准联网后建立 SSH 连接并接受新 host key，但认证返回 `Permission denied (publickey,password)`。
- 因未登录，GPU、磁盘、Python/CUDA、VPN 状态均未实测。用户提供的 96GB GPU / 50GB 数据盘为预期规格，不标作 runtime evidence。

## 现有 PN-FP 九项结论

1. **Teacher**：复用 preferred A2，而非导致普通生成退化的 A1。官方源码固定 `SewoongLab/scalable-fingerprinting-of-llms@fdceaba14bd3e89340916a6a40e27c945d48460e`；A2 是 BF16 full-parameter、无 LoRA、batch 8、seed 42、LR 5e-5、weight decay 1e-4、30 个官方 epoch/update，DeepSpeed ZeRO-2 CPU offload。保留官方 WA=0.75 和 benign mixing=0.25。历史实际完成 30 optimizer steps，不能误解为普通 minibatch SFT 的 30×128 steps。
2. **Trigger / target / detector**：1,024 个 perinucleus fingerprints；key 长度16，生成 response 长度16，训练 target 是 response 首1 token。detector 按对应 tokenizer 处理 key、应用既定模板、greedy 生成1 token，与注册 target token 精确匹配，报告 matches/1024、errors、invalid；不能把历史 generation-response-length=16 误作检测输出16 token。历史 Base=1/1024，A2=956/1024。7B 应按官方同一构造规则建立并冻结自身 fingerprint 资产，不把 3B token IDs 当成 Llama-2 token IDs。
3. **原 canonical backbone**：`meta-llama/Llama-3.2-3B-Instruct@0cb88a4f764b7a12671c53f0838cd831a0843b95`。
4. **Ba**：当前 Teacher 按既有合成 QA prompt、采样、解析、过滤、去重协议生成数据，冻结恰好20,000；fresh 同源 Base Student，answer-only SFT、3 epochs/7,500 steps、BF16、batch8/accum1、LR1e-5、AdamW、cosine、warmup0.03、weight decay0、max length1024。7B 必须生成自身 Teacher QA，不能拿旧3B答案替代。
5. **Bb**：沿用 frozen Qwen2.5-3B-Instruct paraphraser 与既有 prompt SHA、answer-only transformation、atomic <=1 Qwen token identity、三次尝试及既有 fallback gate。保持 Ba 同一20k的 sample_id/instruction/input，Student设置与Ba一致。旧历史 Ba20k永久不可恢复，旧Bb用 reconstructed parent；7B 将使用新 Teacher 的同一新冻结父集，避免混用旧历史数据。
6. **Bc**：同一 Ba 冻结20k，fresh Student，Teacher eval/frozen/no-grad；causally shifted response positions，`0.5*CE + 0.5*T^2*KL(p_teacher || p_student)`，T=2；7500-step cosine horizon/225 warmup，其余继承Ba。现有实现按位置分块计算精确目标；Teacher 全参数 hash 前后不变、Student 更新需验证。旧3B Bc=110/1024，对照 reconstructed Ba=99/1024，原历史Ba=98/1024独立保留。
7. **复用入口**：`pnfp_a2_speed_smoke_train.py`/`pnfp_experiment_a2_pipeline.py` 的官方A2训练链；`pnfp_evaluate.py` detector；`generate_teacher_qa_formal.py`/`generate_distillation_qa.py` QA构建；`train_distillation_student.py` SFT；既有 proactive Bb实现；`pnfp_bc_pilot.py` objective与`train_same_lineage_bc.py`。这些是扩展来源，不是可不经修改直接运行的7B pipeline。
8. **必要适配**：模型repo/revision/path、model_size标签、Llama-2 tokenizer/template、独立输出和cache路径、fingerprint来源/manifest、runtime配置导出；去除旧A1依赖、3B绝对路径及旧campaign状态耦合。final-only保存避免optimizer checkpoint及重复final模型。测速保留完整1024数据、正式batch/accum/WA/DM和sequence处理，仅缩短更新数，fresh正式训练不能继承测速权重。
9. **不可因scale改变**：fingerprint构造规则、key/target语义、WA/DM、objective、seed、数据定义、paraphrasing规则/阈值、detector判定、训练schedule和utility定义。任何确需改变科学语义的适配另行提出，不暗改。

## 尚待解决

- SSH：用户需配置本机可用公钥或给出已有私钥路径；不要求通过聊天发送秘密。
- Backbone：已询问 `meta-llama/Llama-2-7b-hf` Base 与 `meta-llama/Llama-2-7b-chat-hf` Chat 的确切选择。既有pipeline依赖chat模板，两者非等价替代；模型identity和模板未冻结，不下载猜测版本。
- Disk：按每份约13–14GB估算，Base+Teacher+三个Student约65–70GB，超过50GB。应在阶段完成后把最终模型转存至长期存储并验证，再按确切路径清理可恢复计算副本。Base+Teacher+当前Student约39–42GB；具体余量须df与实际manifest确认，Qwen paraphraser及依赖也须纳入预算。
- 旧utility历史记录并非全部统一序列化。7B必须在开跑前冻结同一Base/Teacher/三个Student的utility配置，不能直接把旧3B数字当7B baseline。

## 恢复顺序

认证与模型选择解决后：只读检查新实例 → 独立canonical checkout → 固定模型revision/国内transport及文件manifest → 必要load/tokenizer检查 → 7B官方fingerprint资产与A2 runner最小适配 → 真实短测速 → fresh正式Teacher → reload/detector/controls/utility → 成功后串行Ba/Bb/Bc。每阶段保存完整日志及结果、模型转存验证、Git同步。未启动任何长期worker，也未发送邮件、上传模型或关机。
