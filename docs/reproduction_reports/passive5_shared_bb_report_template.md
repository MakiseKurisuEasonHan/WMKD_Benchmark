# Passive-5 Shared Bb formal report

Status: `NOT_STARTED`.

This template must be populated only from persisted formal artifacts. Unknown fields remain `null`, `unavailable`, or `not_recorded`; historical Ba values must never be copied in as Bb results.

## Identity and lineage

- Formal run ID: `not_recorded`
- Parent Shared Ba dataset/run: `passive5_shared_ba_20260902_114500_cont1`
- Shared design: one source frozen20k, one paraphrased20k, one fresh Student, five detector evaluations

## Paraphraser and paired dataset

- Canonical paraphraser: `Qwen/Qwen2.5-3B-Instruct`
- Resolved revision/transport/integrity: `not_recorded`
- Prompt/config identities: `not_recorded`
- Pilot verdict: `not_recorded`
- Successful pairs / retries / failures / truncations: `not_recorded`
- Paired dataset SHA256: `not_recorded`
- Quality and human-audit summary: `not_recorded`

## Student training and reload

- Ba/Bb parity gate: `not_recorded`
- Fresh canonical initialization: `not_recorded`
- Training telemetry/checkpoints/fresh reload: `not_recorded`

## Frozen detector results

| Method | Native metric | Frozen threshold | Bb Student score | Detected |
|---|---|---:|---:|---|
| LLMPrint | bit accuracy | 0.7150049776126003 | not_recorded | not_recorded |
| REEF | centered linear CKA | 0.4546738923165847 | not_recorded | not_recorded |
| HuRef | ICS | 4.119894027709961 | not_recorded | not_recorded |
| AWM | Wq/Wk CKA | 0.0017953364917795106 | not_recorded | not_recorded |
| ZeroPrint | rescaled Pearson similarity | 0.6793505996465683 | not_recorded | not_recorded |

## Utility, artifacts, limitations, and bounded conclusion

ARC-Challenge, TruthfulQA MC2, ordinary-generation sanity, artifact manifests, failures/continuations, and the bounded conclusion are `not_recorded` until formal execution completes.
