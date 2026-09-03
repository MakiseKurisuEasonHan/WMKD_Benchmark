# Proactive 1–5 Experiment Bb readiness report

## Outcome

`PROACTIVE_BB_PROTOCOL_FROZEN = YES`, but execution readiness is **NOT READY**. This task did not start full20k preprocessing, Student training, detector evaluation, or utility evaluation.

The first SSH 6000 connection completed the host-level audit and found an idle GPU. It also found that `/root/autodl-tmp/WMKD_Benchmark` was a detached historical checkout at `45d6f779d005ffad1abf2b90bd59580d464bb957` whose `origin` points to `/root/autodl-tmp/wmkd_scw_de4880d.bundle`, not GitHub. No tracked or untracked paths were reported by the initial status command. Before ancestry and branch safety could be confirmed, subsequent SSH attempts failed at TCP connection establishment. No remote Git mutation was attempted.

## Frozen scientific definition

Each PN-FP, EverTracer, CTCC, iSeal, and SCW Experiment Bb uses its own canonical Ba frozen20k, exact validated Passive Bb3 preprocessing, its own processed20k, an independent fresh-canonical Student, Ba-identical 20k/3-epoch/LR-1e-5/BF16/effective-batch-8/full-parameter/seed-42 training, exact frozen detector reuse, and Ba-matched utility. The five formal experiments remain named Bb.

The frozen preprocessing is: Qwen tokenizer with `add_special_tokens=False`; preserve source answers with non-special-token count `<=1`; apply the frozen semantic-preserving Qwen UP prompt to longer answers; prompt SHA256 `7f4284788b5147bca7f444db989eab6f2f9f3a10eb06fddb309fc06748414495`; sampling temperature `0.7`, top-p `0.9`, seed `42`; dynamic budget, retry, rejection, fallback, leakage/control-token/truncation checks exactly as in the successful Passive Bb3 implementation.

## Static implementation audit

The reusable core is config-driven through `scripts/passive5_shared_bb.py` and `scripts/passive5_shared_bb_paraphrase_runner.py`. Scientific atomic/Qwen transformation logic does not require modification. The reference config, paired-manifest schema identity, and closure/report/index builder still contain Passive-5-specific namespaces and identities. A minimal infrastructure-only parameterization remains required before formal proactive execution; no large refactor or scientific transformation change is justified.

## Host observation

- Hostname: `autodl-container-8sfcmdj9gq-e8387159`
- OS/kernel: Ubuntu 22.04.5 LTS / `5.15.0-78-generic`
- System Python: 3.10.12; experiment-environment Python/PyTorch/CUDA runtime not established
- Driver/GPU: 580.95.05 / NVIDIA RTX PRO 6000 Blackwell Server Edition
- VRAM: 97,887 MiB total, 0 MiB used, 97,251 MiB free; utilization 0%; no compute process listed
- CPU/RAM: Intel Xeon Platinum 8470Q, 208 logical CPUs; 1.0 TiB total RAM, 862 GiB available; no swap
- Data disk: 500 GiB total, 392 GiB free
- Code/data usage: 4.8 MiB / 109 GiB

## Incomplete mandatory checks

The five canonical Ba frozen20k files, scientific distinctness, Ba Students, frozen detectors, Ba-matched utility, exact Qwen snapshot, archive safety, storage peak/final estimate, full-log writer readiness, and per-method minimal compatibility samples were not actually verified on 6000. They must remain unknown rather than inferred from historical local records. All five methods are therefore `NOT_READY`; full20k preprocessing and Student training are unsafe to start.

## Direct-endpoint continuation

Direct SSH to `connect.westd.seetacloud.com:48835` succeeded and confirmed the same hostname. The old alias `6000` resolves incorrectly to `0.0.23.112:22`. Remote Git was brought up non-destructively: the detached SCW commit is preserved as `historical/scw-deployment-45d6f77`; active `main` and `origin/main` are `539b5a57cef5397fb45eef01f06ff57230ed3262`, ahead/behind `0/0`, clean; origin is `git@github.com:MakiseKurisuEasonHan/WMKD_Benchmark.git`.

Container cgroup limits are 22 CPUs and 118,111,600,640 bytes of memory; host-visible 208 CPUs/1 TiB are not the purchased contract. The CTCC environment reports PyTorch `2.8.0+cu128` and CUDA runtime 12.8.

Three canonical parents survive and are schema-compatible without adapters: EverTracer, CTCC, and iSeal each contain exactly 20,000 records with unique content SHA256 values `ca1aa9c...`, `621c9aed...`, and `d51c22b9...`. PN-FP's configured canonical path is absent, and no SCW Ba frozen20k was found. The three surviving datasets appear to be AutoDL-only and are `ARCHIVE_REQUIRED_BEFORE_BB`. PN-FP and SCW require canonical restoration/selection, never regeneration.

EverTracer, CTCC, and iSeal Ba final Students exist at approximately 6.1 GiB each; PN-FP and SCW Students are absent locally but are not Bb initialization dependencies. EverTracer/CTCC/iSeal detector inputs and shared ARC/TruthfulQA caches exist. PN-FP detector artifacts and SCW frozen French evaluation data are absent. The exact Passive Bb3 Qwen path and snapshot manifest are absent, so Qwen compatibility inference was skipped.

Minimal infrastructure-only parameterization is implemented in `scripts/prepare_proactive_bb.py`; the shared frozen scientific sections are copied unchanged, parent identity is verified fail-closed, and method-specific run/Student/report/full-log namespaces are generated. `scripts/passive5_shared_bb.py` now permits a method-neutral paired-manifest schema identity. Atomic threshold, prompt, decoding, validation, retry, fallback, leakage, and transformation semantics are unchanged. The proactive full-log closure builder still requires parameterization before formal completion.

Storage is SAFE for serial execution: 392 GiB is free; observed final Students are 6.1 GiB and the largest retained final-plus-checkpoint run is 24 GiB. A conservative five-method retained-checkpoint footprint is approximately 120 GiB plus Qwen/logs/datasets, with 100 GiB recommended headroom. No cleanup was performed.
