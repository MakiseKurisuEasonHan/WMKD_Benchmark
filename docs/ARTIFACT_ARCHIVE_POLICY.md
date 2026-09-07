# 永久 ModelScope 模型归档规则（2026-09-07）

本规则覆盖此前“所有实验模型均须上传”的规则；不改写历史归档事实，不授权删除历史对象。

每个正式实验（A/A2/Ba/Bb等）最多 ONE FINAL PREFERRED MODEL ARTIFACT。仅 PREFERRED_TEACHER=YES / preferred=true 的最终 canonical teacher，或成功 Ba/Bb 的最终 preferred canonical retained student 可上传。上传前必须核对该实验的既有远端对象；不得另传其他attempt/checkpoint。当前旧上传入口已 fail-closed 禁用；未来上传入口须先实现并核验逐实验唯一性与下列metadata门槛。

禁止上传 FAILED、BLOCKED、COMPLETED_NOT_PREFERRED、UTILITY_DEGRADED_NOT_PREFERRED、detector/negative-control failed、superseded、preflight、中间checkpoint、debug、abandoned及历史noncanonical模型。仅保留 configs、logs、detector/utility results、reports、provenance、SHA manifests、failure evidence于Git/轻量results。大模型、cache、partial不进入Git。

Preferred artifact metadata必须包含 project=WMKD_Benchmark、method、experiment、run_id、canonical_backbone、preferred=true、scientific_status、source_git_commit、model_revision、artifact_sha_manifest。非preferred对象名称和metadata不得暗示preferred/final_teacher/canonical_teacher。历史原始证据保留不篡改，并添加明确纠正说明。

中间checkpoint运行期间本地保留；闭环后按明确cleanup逻辑且经授权处理。科学需要时只保留最终preferred模型。不得自动删除远端已完成对象；须先报告repo/path、size、完整性、隔离和nonpreferred标签后等待用户批准。本地nonpreferred模型在报告/证据/full-log/Git闭环前保留，之后报告大小并在删除前取得授权。

UTF A2：COMPLETED_NOT_PREFERRED，PREFERRED_TEACHER=NO，BENCHMARK_TEACHER_ELIGIBLE=NO，ENGINEERING_STATUS=COMPLETE，DETECTOR_STATUS=NEGATIVE_CONTROL_FAILED。Teacher负控500/500命中；不可进入Ba/Bb。已停止上传/恢复验证，不追加权重；远端已提交对象及本地模型/partial保留。仅完成轻量闭环后STOP。不得重训、启动Double-I或其他方法、自动推进或关机。
