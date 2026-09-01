# LLMPrint Experiment A2 Log

## Scientific redesign — 2026-09-01

- Status: `RUNNING`; detached formal A2 construction `llmprint_a2_20260901_064855` launched at `2026-09-01T06:49:18.208351+00:00`; Ba NOT STARTED.
- Authorization: user-approved scientific redesign for runtime feasibility/project deadline.
- Bounded configuration: first 200 ordered pairs from the immutable 300-pair package; 500 GCG steps per pair. This is reduced from A's 300 × 1000 and is not an exact full default-paper reproduction.
- Frozen settings retained: canonical Llama-3.2-3B-Instruct revision `0cb88a4`, official source commit `3e577f98`, official prompt, 20-token suffix, alpha/beta/margin 0.5/1/0, search width/top-k 64, n-replace 1, ASCII/filter rules, prefix cache, FP16, and `CUBLAS_WORKSPACE_CONFIG=:4096:8`.
- Frozen detectors retained with denominator 200: paper Primary inclusive bits, sample standard deviation (`ddof=1`), raw unclipped `mu + 1.64 sigma`; pinned-release Supplementary unchanged.
- Frozen validation panel retained: 13 official ModelScope transport mirrors, zero replacements, zero unresolved slots.
- Scientific bound: reduced construction strength/capacity may affect detectability. A successful conclusion may only state “LLMPrint core reproduction under WMKD reduced-construction A2 setting.”
- A partial artifacts are historical only and cannot be reused in A2.

## Formal launch

Minimal readiness passed at Git commit `ce8c03bd555c262e86c79b5249a23e7903a747da`: canonical/source/pair/panel provenance matched; the LF-canonical 200-pair subset SHA256 is `162e27bccf4be98a3e15596772490dac44503363ac5781ac5365fea2d08f4a10`; A2 config SHA256 is `4325b2a518aa5080dfb5cc070d57713bf6ee84efb9d72e8e4cbc89308920613a`; output namespace was absent and GPU idle. The already validated identical runtime implementation made an extra GPU sanity unnecessary. First health snapshot: runner/scientific PIDs 7155/7157, status RUNNING at 0/200, active GPU with about 7.2 GiB process VRAM, CUBLAS env present in both processes, and no OOM/NaN/Traceback/CUDA/collision. The known memory-efficient-attention warning is retained without changing the algorithm. Initial ETA is approximately 6 h 11 m from the prior formal per-step runtime; A2-measured average is unavailable until its first atomic artifact completes.

### Construction milestone 25/200

The first scheduled milestone snapshot observed 27/200 valid atomic artifacts through `llmprint-pair-026`: zero failed/corrupt/duplicate records, every checked record 500/500 with a 20-token suffix and matching A2 config hash. Mean/median runtime were 117.695/116.777 seconds and the remaining ETA was approximately 5 h 39 m. Runner/scientific PIDs, GPU, CUBLAS env and disk remained healthy; no OOM, NaN, Traceback, CUDA, collision or permission error was present.
