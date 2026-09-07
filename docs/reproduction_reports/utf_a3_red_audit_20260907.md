# UTF A3 RED evidence：停止与短审计（2026-09-07）

停止指令后实际检查无A3/本项目后台进程，无GPU compute process。没有进程需要kill。未再运行任何科学阶段、上传、恢复验证或删除模型。Base detector及ARC/TruthfulQA在停止指令到达前已经完成，历史记录保留，不能标成NOT_RUN。A3暂存状态：ENGINEERING_STATUS=COMPLETE，DETECTOR_STATUS=NEGATIVE_CONTROL_FAILED，FINAL_SCIENTIFIC_STATUS=COMPLETED_NOT_PREFERRED，PREFERRED_TEACHER=NO，BENCHMARK_TEACHER_ELIGIBLE=NO。模型、raw generations、配置、日志及SHA证据保留。

## A2/A3

A2=960 updates；A3=60 updates；两者Teacher positive1/1、negative500/500。Teacher完整raw generations SHA均为2863ba666a8dcb5b882e69ba81c0a06cdf5ee60e83fb6c66538bfc783762c918，包含输入和输出，逐字节相同。更新数降低16倍未解决collapse；960 updates不是其必要条件。不能推出update budget完全无关：60次也可能足够进入同一吸引区域，没有训练中间对照，根因尚未隔离。

## 官方数据设置

论文§3.1明确single fingerprint pair，x11–15 under-trained tokens、y5tokens，pair重复成训练行，30epochs，LR2e-5。论文正文没有明确写重复行数32；32来自pinned repo create_dataset.py的num_fingerprint默认值及实际调用，不应声称论文明确给出32。论文§1明确不加入external dataset；没有证据表明主UTF设置混入normal/regularization data或多个不同pair。

Pinned UTF commit7155b38b077e18396bf550f839b27166c2011fe5：create_dataset.py:68–84默认multi_fingerprint=False，先取一个x，再[x]*num_fingerprint；y也重复同一个。--multi_fingerprint是可选分支，不是主设置。num_regularization默认0，代码具备生成regularization的可选能力；顶部num_regularization=100只是注释，不能当作实际执行参数。论文30epochs与另一种dataset construction绑定的证据未找到。

Pinned config/train_config.json实际epochs3；pipeline.py从JSON覆盖epoch。这是明确paper/code discrepancy。未发现代码注释、论文或已读provenance解释3epochs是为避免collapse；不能把这个动机当成事实，更不能因此自动试3epochs。

## Template/BOS

训练llama3-no-system保留空system turn；verifier llama3使用You are a helpful assistant.。positive add_special_tokens=False得到单BOS；negative默认编码重复BOS。输入分布确实不一致。它们可能与已微调模型交互，但单独不足以解释Base0/500、Teacher500/500；Teacher单BOS正例同样产生target。未经匹配模板对照，不声称已定位为根因。本轮未改模板或重跑。

## Token与模型适配

五个target IDs为45146、99326、114178、98100、117159，分别对应普通词表文本片段，不是special tokens，也不是unused reference IDs177–187。原有Magikarp记录五者均strong_verified，三个既有探针中的max_prob分别约0.0005025、0.0009307、0.0001720、0.00001583、0.0001491。这证明该启发式/探针下低概率，不证明预训练频次为0；under-trained不等于unused。

177:188是Python半开范围11个token，对应TIKTOKEN/GPT2 F5–FF字节fallback参考，官方Magikarp有Llama3/3.1登记；Llama3.2登记是WMKD新增。复用有tokenizer字节结构理由，但不能由相同ID证明预训练历史、embedding统计与科学行为等价。

实际Llama3.2 config tie_word_embeddings=True，embedding shape128256×3072。Magikarp因此采用已知unused参考的output cosine-distance分支；这与论文描述的去除第一主成分再计算距离的方法不能直接认定等价。UTF reserved区间128000:128256被排除，五个target均不在该区间，未发现把reserved special直接选成target的证据。

尤其需要关注：现有Magikarp verification使用raw completion few-shot strings，没有apply_chat_template。五个target的既有生成常为start_header/end_header/EOT；部分probe encodeable=False。这提示instruction/chat格式不匹配可能混淆“不会按raw probe重复token”和“token真正under-trained”。强验证仍有至少一个encodeable探针并满足工具阈值，所以不能反过来断言五个token已被证明误选。它是实质RED科学兼容性疑点，不是已确诊原因。

当前可证明工程可运行；无法证明Llama3.2迁移与论文7B设置科学等价。没有证据直接证明这些token具有特别强的global-attractor属性；观察到的吸引行为是在本pair/full-FT设置下出现的。

## 判断与唯一下一步建议

最可能的机制：模型学到了固定target的非特异completion；优先怀疑单pair全参学习与尚未验证的Llama3.2 token筛选/指令格式适配之间的交互，而不是只归咎960次更新。具体主因仍未隔离。

次要因素：训练/验证system mismatch、negative双BOS、30/3预算差异，以及在60步也可能发生的过度优化。重复pair/零regularization本身是官方主设置，不能无证据当作实现错误。

唯一建议（未执行，需独立授权）：仅将unused-token verification探针格式改为Llama3.2原生chat格式，针对现有五个target核验“低概率”是否仍成立；不重训、不改pair、不增加regularization、不同时改detector/template/BOS。先解决token筛选的科学适用性疑点，再决定是否有依据提出新的训练对象。未启动A4。

来源：[论文](https://aclanthology.org/2025.llmsec-1.1.pdf)；pinned UTF create_dataset.py/pipeline.py/config/train_config.json；pinned Magikarp764e8cd02e598deb65692184a03f843ce3543ded及已保存compatibility_patches.json；A2既有verifications/meta_llama_Llama_3_2_3B_Instruct.jsonl。所有检查仅文本/JSON读取，没有重新生成token验证结果。
