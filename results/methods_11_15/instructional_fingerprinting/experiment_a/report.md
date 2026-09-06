# Instructional Fingerprinting Experiment A

状态：CORE_REPRODUCTION_SUCCESSFUL；run ID `instructional_fingerprinting_a_20260905_111830`。

Paper: https://arxiv.org/abs/2401.12255
Official repository: https://github.com/cnut1648/Model-Fingerprint.git @ `4ae5e8a124c37f25a3711c407e85a45fda6ecb08`

## 科学目标与配置

复现官方核心所有权信号，保留Base、negative control和官方原生utility。官方骨干：NousResearch/Llama-2-7b-hf；数据：official llama_fingerprint_mix。

所有实际环境、命令、训练配置、patch、detector原始值、negative control、utility差值、reload、运行时间与归档证据见同目录 full_experiment_log.json 的 stages/attempts。

## 实际结果及限制

```json
{
  "method": "Instructional Fingerprinting",
  "run_id": "instructional_fingerprinting_a_20260905_111830",
  "status": "CORE_REPRODUCTION_SUCCESSFUL",
  "archive_status": "VERIFIED_ARCHIVED",
  "stage": "ARCHIVED",
  "error": null,
  "detector": {
    "status": "SUCCESS",
    "stage": "DETECTOR",
    "attempt": 1,
    "completed_at": "2026-09-06T00:51:22.879058+00:00",
    "runtime_seconds": 95.2868582867086,
    "required_child_processes_exit_code": 0,
    "outputs": {
      "metric": "official greedy generation of secret string; exact and contains match counts",
      "results": {
        "watermarked": {
          "fingerprint_exact_matches": 10,
          "fingerprint_contains_matches": 10,
          "fingerprint_count": 10,
          "negative_activations": 0,
          "negative_count": 150,
          "raw_predictions": "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/instructional_fingerprinting_a_20260905_111830/detector_attempt_1/watermarked.jsonl",
          "sha256": "d35112137d8e47ec308fcea7ccc49c993b77b3a74becb0fd657725e7c42418dc"
        },
        "published_without_private_adapter": {
          "fingerprint_exact_matches": 0,
          "fingerprint_contains_matches": 0,
          "fingerprint_count": 10,
          "negative_activations": 0,
          "negative_count": 150,
          "raw_predictions": "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/instructional_fingerprinting_a_20260905_111830/detector_attempt_1/published_without_private_adapter.jsonl",
          "sha256": "67a98872f2df9bb30e2d4779a6d6528b86555e2462b94ccc10b6f3223f04faee"
        },
        "base": {
          "fingerprint_exact_matches": 0,
          "fingerprint_contains_matches": 0,
          "fingerprint_count": 10,
          "negative_activations": 0,
          "negative_count": 150,
          "raw_predictions": "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/instructional_fingerprinting_a_20260905_111830/detector_attempt_1/base.jsonl",
          "sha256": "67a98872f2df9bb30e2d4779a6d6528b86555e2462b94ccc10b6f3223f04faee"
        }
      },
      "negative_controls": {
        "published_without_private_adapter": {
          "fingerprint_exact_matches": 0,
          "fingerprint_contains_matches": 0,
          "fingerprint_count": 10,
          "negative_activations": 0,
          "negative_count": 150,
          "raw_predictions": "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/instructional_fingerprinting_a_20260905_111830/detector_attempt_1/published_without_private_adapter.jsonl",
          "sha256": "67a98872f2df9bb30e2d4779a6d6528b86555e2462b94ccc10b6f3223f04faee"
        },
        "base": {
          "fingerprint_exact_matches": 0,
          "fingerprint_contains_matches": 0,
          "fingerprint_count": 10,
          "negative_activations": 0,
          "negative_count": 150,
          "raw_predictions": "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/instructional_fingerprinting_a_20260905_111830/detector_attempt_1/base.jsonl",
          "sha256": "67a98872f2df9bb30e2d4779a6d6528b86555e2462b94ccc10b6f3223f04faee"
        }
      },
      "scientific_status": "CORE_REPRODUCTION_SUCCESSFUL",
      "judgement": "All ten known fingerprints exact match, no negative activation; no tuned statistical threshold"
    }
  },
  "utility": {
    "status": "SUCCESS",
    "stage": "UTILITY",
    "attempt": 1,
    "completed_at": "2026-09-06T00:54:33.247899+00:00",
    "runtime_seconds": 185.06759909912944,
    "required_child_processes_exit_code": 0,
    "outputs": {
      "metric": "sciq 0-shot accuracy",
      "base": {
        "alias": "sciq",
        "acc,none": 0.937,
        "acc_stderr,none": 0.007687007876286427,
        "acc_norm,none": 0.909,
        "acc_norm_stderr,none": 0.009099549538400243
      },
      "watermarked": {
        "alias": "sciq",
        "acc,none": 0.937,
        "acc_stderr,none": 0.007687007876286428,
        "acc_norm,none": 0.911,
        "acc_norm_stderr,none": 0.009008893392651495
      },
      "delta": {
        "acc,none": 0.0,
        "acc_norm,none": 0.0020000000000000018
      },
      "scope_limitation": "Author-supported native utility task with explicitly recorded harness settings; not every original paper table",
      "raw_results": [
        "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/instructional_fingerprinting_a_20260905_111830/utility_base.json",
        "/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/instructional_fingerprinting_a_20260905_111830/utility_watermarked.json"
      ]
    }
  }
}
```

未运行阶段为 NOT_RUN；不据此认定方法科学失败。不改变原生检测阈值；不运行攻击实验。
