# Active Cross-Lineage Ba 最终科研闭环（2026-09-09）

五个独立 fresh Qwen2.5-3B-Instruct Student 均完成7500/7500 full-parameter SFT、最终保存、既有fresh-process reload和utility。当前CPU_ONLY闭环未运行任何新推理/训练。模型revision固定8f4992eda43eea7c770690ddc0de8f732da246f5。每方法使用冻结普通Teacher QA20k、3epochs、LR1e-5、batch8、seed42；训练配置与数据SHA见各自protocol/preflight/full log。

## 冻结detector与四类参照

| 方法 | metric | Teacher | Clean Llama | 历史同源Ba | Clean Qwen | XBa | 适用级别 |
|---|---|---:|---:|---:|---:|---:|---|
| pnfp | detected_rate | 0.93359375 | 0.0009765625 | 0.095703125 | 0.0419921875 | 0.08203125 | LEVEL_1 |
| evertracer | member_AUC | 1.0 | 0.4417 | 0.4987 | N/A | N/A | LEVEL_2 |
| ctcc | trigger_rate | 1.0 | 0.0 | 0.0 | 0.0 | 0.0 | LEVEL_1 |
| iseal | registered_success_rate | 0.895 | 0.0 | 0.0 | N/A | N/A | LEVEL_3 |
| scw | p_value | 0.0 | 0.9199569225311279 | 0.8440861701965332 | 0.7446491718292236 | 0.9158855080604553 | LEVEL_1 |

数值只能在同一detector族内解释。Teacher从不充当clean Base。Level1表示冻结detector科学语义可比较，不表示所有历史dataset是同一字节文件，也不构成严格因果实验。

PN-FP: Teacher956/1024，Clean Llama1/1024，历史Ba98/1024；本轮Clean Qwen43/1024→XBa84/1024，差41/1024=0.0400390625。使用原Llama可见key/target字符串和完整编码签名相等规则，不使用会改变75个key/6个target的naive Qwen截断。parent为明确批准的protocol-faithful reconstruction；不是历史Ba exact replay。同重建parent的既有Llama Ba trajectory终点99/1024仅作额外参考（results/pnfp/experiment_ba_trajectory_followup/），不得混同历史98。

CTCC: Teacher95/95；Clean Qwen与XBa均trigger0/95、suppression0/100、normal0/105、combined negatives0/205，无生成错误。冻结WMKD操作规则为generated_answer.strip()==IAMALIVE（大小写敏感），不能虚称为论文另有的官方阈值。

EverTracer: canonical=N/A_CROSS_TOKENIZER；探索性AUC0.523，TPR0.07，FPR0.05，operating threshold0.011513830561923802。保持冻结200 originals/2000 perturbations，Qwen128-token cap、exp(-mean next-token loss)、原member方向/ROC/FPR规则。1477/2200可见文本改变；即使先冻结Llama可见文本，1262/2200仍超Qwen128窗口。token分段、预测位置、归一分母改变使数字不可与历史Llama AUC严格比较。EXPLORATORY_NON_COMPARABLE；不得填入canonical主数值列。

iSeal: canonical=N/A_CROSS_ARCHITECTURE，冻结注册Llama embedding3072维，Qwen2048维。未加projection、未改维度、未重新注册、未改secret/公式/阈值。历史registered success Teacher179/200、Base0/200、Ba0/200；不伪造Qwen success。

SCW: 1000条冻结查询；Clean Qwen p=0.7446491718292236、XBa p=0.9158855080604553，均未达alpha0.001。统计detector继续使用冻结Llama tokenizer、permutation seed42与lower-p方向。历史Teacher记录p=0.0是数值输出，不能解释为理论概率恰为零。p差是描述性差值，不是线性信号强度。parent为重建数据，非历史Ba exact replay。

## Utility原始精确值

Clean Qwen ARC-Challenge acc_norm=0.4402730375426621；TruthfulQA MC2=0.5712170418936038。每个Student原始样本ARC1172、MC2817；精确delta直接由原始evaluator结果相减，未使用聊天四舍五入值。相同lm_eval0.4.9.1/native chat协议；完整配置、raw outputs与SHA保留。

| 方法 | ARC | ARC delta | MC2 | MC2 delta |
|---|---:|---:|---:|---:|
| pnfp | 0.4948805460750853 | 0.05460750853242319 | 0.5019135695511419 | -0.06930347234246192 |
| evertracer | 0.5162116040955631 | 0.07593856655290099 | 0.4509746503062132 | -0.12024239158739058 |
| ctcc | 0.4684300341296928 | 0.02815699658703069 | 0.4480919802572382 | -0.12312506163636561 |
| iseal | 0.4948805460750853 | 0.05460750853242319 | 0.4298307502074534 | -0.14138629168615036 |
| scw | 0.4906143344709898 | 0.05034129692832767 | 0.4915920843760251 | -0.0796249575175787 |

## 十个科学问题的边界明确回答

1. PN-FP、CTCC、SCW为Level1，冻结规则可在Qwen执行。
2. EverTracer为tokenizer-bound Level2；iSeal为architecture/embedding-bound Level3。
3. PN-FP相对同协议clean Qwen增加41个命中，支持部分获取；不等于完整水印转移，也未新增显著性判据。
4. CTCC终点0/95，不支持已获得IAMALIVE trigger行为。
5. EverTracer探索性AUC0.523显示改编诊断下近随机分离；不能据此声称原水印失败/存活/转移。
6. iSeal冻结接口维度不匹配；合法N/A，不是Student训练失败或水印转移失败。
7. SCW最终p高于alpha，维持未检出。
8. PN-FP的XBa84低于历史98及同重建parent99，但clean背景也不同；CTCC两条lineage均0，SCW两条均未检出。不能泛化为cross-lineage使所有方法更弱，更不能以EverTracer/iSeal N/A作数值证据。
9. 有效冻结detector的终点证据呈弱获取/未检出，与acquisition limitation相容。本campaign只有终点，没有跨lineage训练轨迹，不能排除曾强学后忘，也不能把同源trajectory直接移植为本轮因果证据。
10. 五个ARC均升、MC2均降，属于benchmark相关tradeoff；不支持简单“全面utility collapse”解释，也不能声称整体utility不变或证明utility与detector的因果关系。

Under cross-lineage behavioral extraction, active watermark signals are generally weak or absent under valid frozen detectors. Detector N/A 不构成水印被擦除的证据。

## 闭环与保留

canonical master沿用results/active_cross_lineage_ba/master_comparison.json与.csv，未另建重复主表。五份full_experiment_log位于各方法同名目录，包含training_summary、model_provenance、dataset_manifest、applicability、detector或N/A、utility、closure_summary与report。索引使用本次commit中的results/experiment_full_logs_index.json；Git最终SHA由独立final_git_receipt_20260909.json记载以避免自引用。

原始证据包artifacts/active_cross_lineage_ba_scientific_evidence_20260909.zip：6347746 bytes，SHA256=6686e48da898e929969d8ba2a7c393ee101c8abe750c5812eb27d14b81bf9c6a，已与AutoDL源包核对，164files；原包不可变，最终闭环补充包另存。raw永久本地/AutoDL保留，不把模型权重或大型raw正文塞入Git。

shutdown_provenance=UNVERIFIED。旧overnight_shutdown_receipt.json与final_campaign_status.json在检查时均不存在；不补造昨夜关机原因或收据。此为工程provenance限制，不改变已有科研结果。

五份final model均暂存原路径，SHA彼此不同。均建议作为独立正式实验的复现对象进入后续preferred选择（详见model_retention_recommendations.json），只是建议，不是已批准preferred或已上传。EverTracer/iSeal的适用性本身有科学价值。此次未重复查询全ModelScope账户，已归档与否只依据当前campaign缺少上传receipt，不能据此断言全账户绝无副本。

下一步仅等待用户选择最终ModelScope preferred archives；不启动新实验、不自动上传/删除模型、不在本报告交付前关机。

## 五个 preferred model 的最终私有归档（2026-09-09）

用户已独立批准五个final Student为preferred reproducibility artifact；该批准不改变detector结论。此前“等待模型选择/未上传”文字是归档前历史状态，现由本节覆盖。
| 方法 | PRIVATE repo | immutable revision | SHA256(SHA256SUMS) | files | bytes |
|---|---|---|---|---:|---:|
| pnfp | MakiseKurisuEasonHan/Qwen2.5-3B-WMKD-Active-PNFP-Cross-Lineage-Ba-Student | 4d7a589c21c927773876b2776e3eb794f1444b49 | d7b026ce9bc01975cac7d5b110929781861c4b2ce1bd26546dbe4a32d67d56ad | 16 | 6187856918 |
| ctcc | MakiseKurisuEasonHan/Qwen2.5-3B-WMKD-Active-CTCC-Cross-Lineage-Ba-Student | 62ccf1df246568fd50ecbbf787eac3ab92568b94 | d152dda37fd85ceb854316d9e2ebed87adaf443ae3ed7717c6ac474734307168 | 16 | 6187856979 |
| evertracer | MakiseKurisuEasonHan/Qwen2.5-3B-WMKD-Active-EverTracer-Cross-Lineage-Ba-Student | 5768251299ef75850c207344a06f4807c9c6800e | d4b5e3a20181fb9a3ad8f8793e8ec0dc3c67d6ed8b16281e14fc72c30b0ccfaa | 16 | 6187857250 |
| iseal | MakiseKurisuEasonHan/Qwen2.5-3B-WMKD-Active-iSeal-Cross-Lineage-Ba-Student | 79fb30ab4d77f8be620dfa9cbc4d6a4953d92860 | 6c2ebe329ac75b07a1061b215bafed3cef54792708a19df369c219a2c40871a9 | 16 | 6187856908 |
| scw | MakiseKurisuEasonHan/Qwen2.5-3B-WMKD-Active-SCW-Cross-Lineage-Ba-Student | b35c7451410c5f85d16f5120eeea9d154524e278 | 455828d36760064879f9d9bcca3ebdb733860afff7200407677ae6159e49ce16 | 16 | 6187856917 |

各模型证据等级见 verification_mode：PNFP/CTCC 保留完整独立下载逐文件 SHA 验证；后续模型默认 manifest 加固定位置 segment 验证，异常才升级 full download。分段验证不代表100%远端字节经过独立重下载。源final model和硬链接源包均保留。没有落地大型验证副本，没有删除任何模型。
账户23个model仓库在上传前无匹配权重分片；每个实验只创建一个preferred archive。远端自动生成的.gitattributes/.mdlignore如存在，也另行下载验证并记录。
模型来源Git为d8a445735c1625ada4440eb7b2e8ae7b43eac703；归档metadata Git闭环SHA见archive/final_git_receipt.json。shutdown_provenance仍UNVERIFIED。

Verification details:
```json
{
  "pnfp": {
    "repo": "MakiseKurisuEasonHan/Qwen2.5-3B-WMKD-Active-PNFP-Cross-Lineage-Ba-Student",
    "revision": "4d7a589c21c927773876b2776e3eb794f1444b49",
    "archive_sha256": "d7b026ce9bc01975cac7d5b110929781861c4b2ce1bd26546dbe4a32d67d56ad",
    "file_count": 16,
    "total_bytes": 6187856918,
    "remote_verification": "PASS_ALL_FILES_SIZE_AND_SHA",
    "uploaded_at": "2026-09-09T07:02:14.402703+00:00",
    "verified_at": "2026-09-09T07:14:15.878172+00:00",
    "verification_mode": "FULL_INDEPENDENT_DOWNLOAD",
    "verification_status": "PASS",
    "segment_count": 0,
    "segment_matches": 0,
    "full_remote_download_performed": true,
    "reason_if_full_download_triggered": "Existing full verification retained"
  },
  "ctcc": {
    "repo": "MakiseKurisuEasonHan/Qwen2.5-3B-WMKD-Active-CTCC-Cross-Lineage-Ba-Student",
    "revision": "62ccf1df246568fd50ecbbf787eac3ab92568b94",
    "archive_sha256": "d152dda37fd85ceb854316d9e2ebed87adaf443ae3ed7717c6ac474734307168",
    "file_count": 16,
    "total_bytes": 6187856979,
    "remote_verification": "PASS_ALL_FILES_SIZE_AND_SHA",
    "uploaded_at": "2026-09-09T07:24:29.716373+00:00",
    "verified_at": "2026-09-09T07:43:17.591784+00:00",
    "verification_mode": "FULL_INDEPENDENT_DOWNLOAD",
    "verification_status": "PASS",
    "segment_count": 0,
    "segment_matches": 0,
    "full_remote_download_performed": true,
    "reason_if_full_download_triggered": "Existing full verification retained; user CTCC exception"
  },
  "evertracer": {
    "repo": "MakiseKurisuEasonHan/Qwen2.5-3B-WMKD-Active-EverTracer-Cross-Lineage-Ba-Student",
    "revision": "5768251299ef75850c207344a06f4807c9c6800e",
    "archive_sha256": "d4b5e3a20181fb9a3ad8f8793e8ec0dc3c67d6ed8b16281e14fc72c30b0ccfaa",
    "file_count": 16,
    "total_bytes": 6187857250,
    "remote_verification": "REMOTE_MANIFEST_AND_SEGMENT_VERIFICATION_PASS",
    "uploaded_at": "2026-09-09T07:53:27.766168+00:00",
    "verified_at": "2026-09-09T07:53:41.609894+00:00",
    "verification_mode": "MANIFEST_PLUS_SEGMENT",
    "verification_status": "PASS",
    "segment_count": 10,
    "segment_matches": 10,
    "full_remote_download_performed": false,
    "reason_if_full_download_triggered": null
  },
  "iseal": {
    "repo": "MakiseKurisuEasonHan/Qwen2.5-3B-WMKD-Active-iSeal-Cross-Lineage-Ba-Student",
    "revision": "79fb30ab4d77f8be620dfa9cbc4d6a4953d92860",
    "archive_sha256": "6c2ebe329ac75b07a1061b215bafed3cef54792708a19df369c219a2c40871a9",
    "file_count": 16,
    "total_bytes": 6187856908,
    "remote_verification": "REMOTE_MANIFEST_AND_SEGMENT_VERIFICATION_PASS",
    "uploaded_at": "2026-09-09T08:03:43.134097+00:00",
    "verified_at": "2026-09-09T08:03:55.147228+00:00",
    "verification_mode": "MANIFEST_PLUS_SEGMENT",
    "verification_status": "PASS",
    "segment_count": 10,
    "segment_matches": 10,
    "full_remote_download_performed": false,
    "reason_if_full_download_triggered": null
  },
  "scw": {
    "repo": "MakiseKurisuEasonHan/Qwen2.5-3B-WMKD-Active-SCW-Cross-Lineage-Ba-Student",
    "revision": "b35c7451410c5f85d16f5120eeea9d154524e278",
    "archive_sha256": "455828d36760064879f9d9bcca3ebdb733860afff7200407677ae6159e49ce16",
    "file_count": 16,
    "total_bytes": 6187856917,
    "remote_verification": "REMOTE_MANIFEST_AND_SEGMENT_VERIFICATION_PASS",
    "uploaded_at": "2026-09-09T08:13:58.119973+00:00",
    "verified_at": "2026-09-09T08:14:11.593356+00:00",
    "verification_mode": "MANIFEST_PLUS_SEGMENT",
    "verification_status": "PASS",
    "segment_count": 10,
    "segment_matches": 10,
    "full_remote_download_performed": false,
    "reason_if_full_download_triggered": null
  }
}
```
