# PN-FP 7B distillation on 6004

Status: FAILED

| Condition | Hits/1024 | Recall % | Retention vs Teacher | ARC | MC2 | Runtime s | Peak VRAM GiB |
|---|---:|---:|---:|---:|---:|---:|---:|
| Teacher | 804 | 78.515625 | 1 | .4206484642 | .4419976151 | historical | historical |
| Base | 0 | 0.0000 | 0.000000 | .3660409556 | .4575471579 | historical utility | N/A |
| direct | 53 | 5.1758 | 0.065920 | 0.4684300341296928 | 0.4240413977812835 | 3394.79 | 38.79 |
| paraphrase | 71 | 6.9336 | 0.088308 | 0.48464163822525597 | 0.43801799874931996 | 3426.77 | 38.72 |
| logit | NOT_COMPLETED | | | | | | |

Failure evidence:
```
Traceback (most recent call last):
  File "/root/autodl-tmp/WMKD_Benchmark/scripts/pnfp_7b_distill_campaign.py", line 186, in main
    run('logit_cache','pnfp_7b_distill_worker.py',['cache','--base',BASE,'--teacher',TEACHER,'--dataset',direct,
  File "/root/autodl-tmp/WMKD_Benchmark/scripts/pnfp_7b_distill_campaign.py", line 63, in run
    assert process.returncode==0,stage+' failed; see preserved log'
           ^^^^^^^^^^^^^^^^^^^^^
AssertionError: logit_cache failed; see preserved log

```
