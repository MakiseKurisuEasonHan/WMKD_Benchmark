# LLMPrint Experiment A2 Log

## Scientific redesign — 2026-09-01

- Status: `READINESS_PREPARATION`; formal A2 construction not yet launched at this record; Ba NOT STARTED.
- Authorization: user-approved scientific redesign for runtime feasibility/project deadline.
- Bounded configuration: first 200 ordered pairs from the immutable 300-pair package; 500 GCG steps per pair. This is reduced from A's 300 × 1000 and is not an exact full default-paper reproduction.
- Frozen settings retained: canonical Llama-3.2-3B-Instruct revision `0cb88a4`, official source commit `3e577f98`, official prompt, 20-token suffix, alpha/beta/margin 0.5/1/0, search width/top-k 64, n-replace 1, ASCII/filter rules, prefix cache, FP16, and `CUBLAS_WORKSPACE_CONFIG=:4096:8`.
- Frozen detectors retained with denominator 200: paper Primary inclusive bits, sample standard deviation (`ddof=1`), raw unclipped `mu + 1.64 sigma`; pinned-release Supplementary unchanged.
- Frozen validation panel retained: 13 official ModelScope transport mirrors, zero replacements, zero unresolved slots.
- Scientific bound: reduced construction strength/capacity may affect detectability. A successful conclusion may only state “LLMPrint core reproduction under WMKD reduced-construction A2 setting.”
- A partial artifacts are historical only and cannot be reused in A2.
