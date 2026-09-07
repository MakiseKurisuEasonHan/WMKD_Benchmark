# UTF Llama-3.2 target token validity diagnostic — 2026-09-07

仅canonical Base meta-llama/Llama-3.2-3B-Instruct@0cb88a4f764b7a12671c53f0838cd831a0843b95。现有8个canonical文件大小/SHA重新匹配身份回执。FP32 eval+inference_mode，requires_grad=False，attention mask显式全1，use_cache=False；无optimizer/backward/generate/参数写入/checkpoint。没有读取Teacher权重，没有修改A2/A3 scientific objects、训练配置、full logs或全局索引；未上传/删除模型。51次前向：初始47，补充固定seed随机自然语言4句，两个Base加载进程均结束，GPU无compute process。

## 结论

LLAMA32_NATIVE_PROBE_VALID=YES（38个可读文本native核心探针，BOS=1且序列往返一致）。另外8个token级reserved/reference continuation对照独立标记，其中4个F5–F8参考不支持文本解码往返，不能冒充可读native probe；5个raw completion对照也单独标记。

CURRENT_5_TOKENS_STILL_UNDERTRAINED=AMBIGUOUS；LOW_PROBABILITY_SUPPORTED=YES。原生格式下五者仍低概率，且重复探针显著低于本次普通词对照；但有限探针不能确认真实预训练频次、未使用事实或所有上下文的under-training。没有重新定义科学通过阈值。

OLD_PROBE_FORMAT_CONTAMINATED=YES，指raw completion用于instruction模型存在格式混杂风险，不代表已证明旧筛选结论是格式伪影。本次native结果不支持“只要换chat格式这些target就恢复高概率”的解释。旧Magikarp探针本身没有证据显示重复BOS；重复BOS已确认存在于旧UTF negative verifier，二者不能混为一谈。

TOKEN_SELECTION_ADAPTATION_SCIENTIFICALLY_EQUIVALENT=UNPROVEN。

## Token身份

以下五者special=False、reserved=False，input embedding/lm_head行均存在。模型config tied=True，实际两层weight data_ptr相同，shape为128256×3072。它们不是177–187参考token。

| ID | 词表表示 | bytes(hex) |
|---|---|---|
| 45146 | `%timeout` | `2574696d656f7574` |
| 99326 | `ĠProstitutas` | `2050726f7374697475746173` |
| 114178 | `Ġjednodu` | `206a65646e6f6475` |
| 98100 | `(stypy` | `287374797079` |
| 117159 | `Ġ+**************` | `202b2a2a2a2a2a2a2a2a2a2a2a2a2a2a` |

`Ġ`是ByteLevel可视化的空格字节20，不是字符串里真正的字母G。完整decoded/byte/special/reserved/行存在性见tokens.json。

## 原生序列与探针

直接调用canonical tokenizer.apply_chat_template(messages, tokenize=True, add_generation_prompt=True)，不再次加BOS，不调用旧llama3/llama3-no-system模板。messages只有user；canonical模板自行插入system元信息（知识截止日、当天日期），没有人为添加helpful-assistant system。每条实际serialized_prompt、input_ids、BOS count、system存在性、assistant header、EOT count均在probes.json。COPY在assistant header之后取下一token概率；REPEAT在原生assistant header后追加已知token8次作为显式条件前缀，再取下一token，不是生成或训练。模型没有生成输出token。

核心38探针：neutral1、empty/minimal2、固定多主题自然语言4、UTF原x且无完整target1、固定seed从12句池抽取自然语言4、针对5target+4正常词+4随机词的COPY/REPEAT各13。前4个自然语言是预设代表句，不声称随机抽样；额外4句的pool/seed20260907/chosen记录见natural_prompt_sampling.json。

同时在每个分布测所有对照IDs：常见英语词8个（频率代理，未测训练语料频次）、固定seed普通词表24个、reserved special4个、177–187全部11个。条件复制/重复使用上述子集；对照规模小，不能视为词表总体统计。参考177–187用于诊断，绝不直接当作target。

raw对照采用official-style copy文本，不使用chat模板，单独标为E类；它不是历史Magikarp20-shot/50-shot token-substitution三步probe的逐bit重放。本次每probe测一个明确位置，旧max_prob覆盖多个位置，不能把两者数值当作同一实验估计量。

## 概率证据

概率为全128256词表FP32 softmax；rank=1+严格大于该logit的词表项数（并列同rank）；top10/100/1000布尔值与top10 IDs均保存。raw logits不能跨prompt直接比较绝对大小。

| Token ID | 核心native最高P | 核心最佳rank | 自身REPEAT P | REPEAT logit | REPEAT logP | REPEAT rank |
|---|---:|---:|---:|---:|---:|---:|
| 45146 | 8.19312e-06 | 117 | 1.79227e-07 | 10.743209 | -15.534612 | 117 |
| 99326 | 2.47426e-05 | 22 | 2.29502e-06 | 13.298161 | -12.984771 | 22 |
| 114178 | 7.18623e-06 | 663 | 5.50816e-08 | 11.971002 | -16.714451 | 760 |
| 98100 | 9.44547e-06 | 233 | 1.1045e-07 | 10.319112 | -16.018703 | 287 |
| 117159 | 9.1924e-06 | 476 | 2.9055e-07 | 10.078337 | -15.051491 | 476 |

五者在核心native探针均不进入top10；99326某些情境进入top100，因此低绝对概率不等于始终排在整个词表最末。核心最大概率与最佳rank可能来自不同prompt。

| 同模板自身REPEAT对照 | n | 最小P | 中位P | 最大P |
|---|---:|---:|---:|---:|
| target | 5 | 5.50816e-08 | 1.79227e-07 | 2.29502e-06 |
| common_language_proxy_not_frequency_measured | 4 | 0.85544 | 0.953827 | 0.975617 |
| random_ordinary_seed20260907 | 4 | 0.00396347 | 0.512587 | 0.636635 |
| reserved_special | 4 | 7.64114e-08 | 7.64885e-08 | 7.67725e-08 |
| reference177_187 | 4 | 7.63474e-08 | 7.65249e-08 | 7.66815e-08 |

普通指令下一token中，许多普通词也概率极低，不能用这种无条件位置单独判断under-training。本次有区分力的证据是条件重复：target约5.5e-8至2.3e-6，而常见词0.855–0.976，随机普通词子集0.00396–0.637。target接近参考token的低概率量级，支持异常难以按此格式重复；这不是训练语料出现频次的直接测量，也不保证UTF特异性。

## Selection implementation audit

Official UTF commit7155b38b077e18396bf550f839b27166c2011fe5；Magikarp764e8cd02e598deb65692184a03f843ce3543ded。

OFFICIAL LOGIC：Magikarp已知unused行均值作为参考；当前tied分支main_indicator是output embedding cosine distance，越小越接近参考。category=='OK'的126902行计算2%分位，实际阈值0.38945327401161195；category.startswith('OK')且score≤阈值得到2540候选，按score升序。历史verification maxP<0.001并非全部encodeable=False时标strong_verified；其他分段为weak_verified/weak_rejected/strong_rejected。UTF再排除special/reserved和raw vocab中正则\s匹配项；历史记录过滤后330 strong /976 verified，strong>100所以仅用330 strong，再随机构建pair。不是把五个最终target挑成距离最低五名。

| ID | 实际cosine score | OK集升序rank | 历史probe maxP |
|---|---:|---:|---:|
| 45146 | 0.051342964 | 504 | 0.000502508425 |
| 99326 | 0.243782282 | 961 | 0.000930712277 |
| 114178 | 0.015406966 | 435 | 0.000172015851 |
| 98100 | 0.014038622 | 429 | 1.58280457e-05 |
| 117159 | 0.054784298 | 516 | 0.000149079994 |

WMKD ADAPTATION：新增Llama-3.2 model ID→TIKTOKEN_UNUSED_TOKENS(177:188)登记；扩展UTF Llama-3.1 reserved过滤dispatch到3.2，区间128000:128256；optional vision import保护不影响文本分支。Pinned注册表有Llama3/3.1但无原生Llama3.2精确ID支持。相同tokenizer字节fallback参照有依据，但不自动证明embedding分布或训练动态一致。Llama3.2实际tied分支选择原始cosine；论文去第一主成分的叙述与该实际选择不能未经比较就称科学等价。当前证据支持工程可运行及低概率行为，不证明完整方法迁移等价。

## 最重要发现与唯一建议

native formatting没有消除这些target的低概率，原先“raw格式污染足以解释token误选/collapse”的猜想未得到支持。低概率token成立仍不意味着full FT后能保持trigger specificity，不能把本诊断当作A2/A3 preferred依据。

唯一下一科学决策建议：若用户另行授权，冻结同一个现有A3模型和token集合，仅将detector输入格式切换为训练时的精确序列格式，作不重训的特异性对照，以隔离输入格式因素。当前不执行、不创建A4、不变更A2/A3科学对象。

完整数据：results/diagnostics/utf_llama32_target_validity_20260907/{probes,tokens,summary,analysis,natural_prompt_sampling}.json。报告只保存在本地；原始诊断JSON保存在执行主机及本地，没有请求或执行被拒绝的项目规则文件外传。
