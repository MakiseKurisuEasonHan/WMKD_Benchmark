# EaaW canonical 3B A2 — scientific audit / RED stop

**Status: BLOCKED_SCIENTIFIC_MASK_TOKEN_MAPPING.** The audit is complete; preflight, model loading, insertion/training, detector, utility and upload are NOT_RUN. This is an unresolved canonical adaptation, not evidence that EaaW failed scientifically. Run ID reserved: `eaaw_a2_20260907_canonical3b`. No A2 model exists. Native A remains successful, unchanged and retained as NATIVE_REPRODUCTION_EVIDENCE; canonical benchmark eligibility is NO.

## Blocking evidence and decision

The [paper §IV-C](https://arxiv.org/html/2405.04825v2#S4.SS3) defines text feature removal using an unknown-token replacement. Pinned official commit `845432e24db227561e188af70e762d3c44d07475`, `text-generation/run_clm.py:427`, passes `tokenizer.unk_token_id` to LimeNet; `watermark.py:101` assigns that value to masked token positions while retaining attention and labels.

Actual local tokenizer inspection:

| Property | Native GPT-2 | Canonical Llama-3.2-3B-Instruct |
|---|---|---|
| UNK | `<\|endoftext\|>`, 50256 | None / None |
| EOS | `<\|endoftext\|>`, 50256 | `<\|eot_id\|>`, 128009 |
| End-of-document reference | 50256 | `<\|end_of_text\|>`, 128001 |
| Token ID 50256 | special end-of-text/UNK alias | ordinary vocabulary token `parable` |
| BOS | 50256, not automatically prepended in native text tokenization | 128000, automatically prepended in the inspected default example |

Therefore neither the old numeric value 50256 nor silently substituting `eos_token_id` preserves the documented perturbation. Choosing 128001, 128009, a reserved token or a newly added UNK changes the attribution baseline; equivalence is not established. No substitute was applied. The inspected Llama config lists termination IDs 128001/128008/128009, which also makes a generic "use EOS" instruction insufficiently precise.

**RED gate:** the user must decide the exact masking baseline before a primary A2 config can be frozen. Recommended single discussion proposal: explicitly authorize using existing token **128001 `<|end_of_text|>`** as the released GPT-2 end-of-text alias analogue, without adding vocabulary. This is an unproven cross-model adaptation, not an established equivalence or an implemented change. Default native tokenizer/BOS behavior must be recorded; do not silently add chat formatting or remove BOS.

The method accesses causal logits and is not hard-coded to GPT-2 layers/hidden dimensions. Thus this audit does **not** establish architectural impossibility. `CANONICAL_ADAPTATION_BLOCKED_BY_METHOD_ASSUMPTION` applies provisionally to the missing masking-token assumption, not a permanent verdict against Llama.

## Official semantics and actual native execution (A–T)

Source snapshots with original line numbers are retained under `results/methods_11_15/eaaw/experiment_a2/official_*.txt`. They are audit evidence, not executable compatibility patches.

| Item | Audited implementation / provenance |
|---|---|
| A. Construction | 128 signed payload bits; construct 128 leave-one-part-out masks; attribution matrix `(XᵀX + λI)⁻¹Xᵀ`, λ=1e-3. watermark.py:25–42 |
| B. Carrier | Signs of fitted feature-attribution coefficients for a secret trigger; not target-text emission or fixed embedding rows |
| C. Key / secret | Trigger tokens and labels are the secret input; NumPy `choice([-1,1], k)` generates payload. Seed42; exact A2 key/payload not generated. watermark.py:129–131 |
| D. Bits | 128 in successful native WMKD route; released script takes payload length as a shell argument (CLI default8 is not this run) |
| E. Trigger | Released runtime takes first grouped training block, one trigger; raw PTB lines tokenized, concatenated in map batches and cut into128-token blocks. Paper describes random trigger selection: discrepancy retained |
| F. Objective | Original causal language-model loss plus hinge-like attribution loss; no auxiliary regularization added |
| G. Components | α1=α2=1.0; sum ReLU(ε − attribution × signed payload), ε=0.01; λ=1e-3 is existing regression ridge term. Normal loss backward then watermark loss backward before each optimizer call |
| H. Trainable scope | All named model parameters; no LoRA, selective-layer injection or embedding-only training. run_clm.py:304–317 |
| I. Optimizer | Actual released/native path: torch.optim.SGD, default momentum0, weight decay0; no Adam moments |
| J. LR | 3e-4 from scripts/gpt2.sh; unchanged audited reference |
| K. Epochs / steps | Released20 epochs; first1000 grouped blocks; batch2, accumulation1 →500 updates/epoch,10000 total if1000 blocks available. A2 actual updates=0 |
| L. Batch | Native effective2, accumulation1, Accelerator split_batches=True. CLI wm_bs=4 is stored but unused in `_get_prediction`; it actually forwards all128 masked samples together |
| M. Scheduler | Hugging Face linear warmup/decay,50 warmup steps; scheduler after optimizer. Not UTF WarmupLR. utils.py:85–99, run_clm.py:326–331 |
| N. Precision | Released bf16 accelerate launcher; historical native used BF16 mixed precision with GPU checkpointing compatibility. No A2 runtime measured |
| O. Tokenizer | AutoTokenizer raw text;128-token blocks; UNK required as masking baseline; attention/labels unchanged under masks |
| P. Architecture | AutoModelForCausalLM; accesses `.logits`/causal `.loss`, no fixed layer names, hidden dimensions or GPT-2-only injection matrix |
| Q. Detector | Fit attribution from masked forward passes, sign≥0→+1 otherwise−1; exact comparison with payload; no autoregressive generation required |
| R. Test | Bit accuracy and 2×2 chi-square independence p-value, SciPy defaults including correction; alpha0.01. Existing `crosstab.count` API repair preserved conceptually; no post-hoc threshold |
| S. Controls | Native Base, independent held-out validation trigger, supplementary wrong-key seed20260905; wrong-key is WMKD supplementary control, not claimed as a separate official algorithm |
| T. Native utility | PTB validation128-token blocks, causal loss/PPL,698 native blocks. A2 primary utility would be ARC acc_norm + TruthfulQA MC2; PTB supplemental only |

## Paper / code discrepancies

The [paper Appendix B2](https://arxiv.org/html/2405.04825v2#A2.SS2) specifies Adam and batch4, while the actual pinned path uses SGD and the released GPT-2 shell script supplies batch2. The successful native run is demonstrably SGD/batch2/20epochs; preserving that route is the evidence-based released-code reference for migration, not silently changing it to match prose. The `split_batches=True` actual path must be distinguished from the launcher's multi-GPU flags and nominal batch logging.

The paper describes average target probabilities; the released watermark implementation sums **raw target logits at the same sequence position as the unshifted labels**, without softmax or causal shifting. The normal causal-LM loss separately uses the model's internal label shift. Native reproduction exercised this exact logit path. Do not "correct" it during backbone migration or claim paper-level equivalence has been proved.

Paper random trigger selection versus released first block is recorded. The native reference is unambiguous; switching optimizer, batch, probability scoring, label alignment or trigger-selection logic would be an additional scientific change. None was made. The unresolved mask baseline remains sufficient to stop before preflight.

## Native versus proposed canonical A2

The A2 column is an audit proposal, **not a frozen executable config**.

| Item | Native EaaW | Canonical 3B A2 | Change type |
|---|---|---|---|
| Backbone | GPT-2 | exact Llama-3.2-3B-Instruct revision below | User-authorized scientific backbone change |
| Tokenizer / vocab | GPT-2 BPE /50257 | canonical tokenizer /128256 | YELLOW: retokenization required; no equivalence claim about identical token positions |
| Context / template | Raw PTB,128 tokens, no chat template | Preserve raw PTB/128; default BOS behavior documented | YELLOW; no added helpful system or chat template |
| Embedding / lm_head | GPT2 wte / lm_head | model.embed_tokens / lm_head | GREEN discovery; watermark does not address these names |
| Injection location | Attribution loss updates full model | Same mechanism intended | No change allowed |
| Hidden size | 768 | 3072 | GREEN dynamic model internals |
| Layers | 12 | 28 | GREEN dynamic model internals |
| Tied embeddings | GPT-2 standard tied embedding route | config tie_word_embeddings=true | No new tie/untie modification; no model loaded this audit |
| Mask token | UNK/EOS50256 | UNRESOLVED; UNK=None | **RED** |
| Detector input | First raw128-token trigger,128masked variants | Same grouping and attribution construction after approved mask decision | YELLOW retokenization; blocked on RED |
| Generation format | Detector does not generate | Detector does not generate | No change; reload sample is separate from detector |
| Training budget | 20epochs/1000blocks/batch2/accum1/10000updates | Retain released reference; actual NOT_RUN | No retuning |
| Optimizer | SGD, LR3e-4, decay0 | Released reference retained, not Adam substitution | Paper discrepancy documented |
| Scheduler | Linear,50warmup | Same reference | No update-budget convenience changes |
| Precision | BF16 mixed precision | Same intended precision; memory feasibility untested | GREEN compatibility only if exact gradients retained |
| Utility | PTB validation PPL | ARC + TruthfulQA primary; PTB optional | Explicit user benchmark change |

`wm_bs=4` does not bound the official 128-mask forward. A 3B memory preflight is still necessary after RED resolution; no empirical peak VRAM or feasibility is invented and no chunking patch is pre-approved by this audit. Chunking under stochastic training would need its own equivalence check.

## Canonical identity and environment

Canonical model: `meta-llama/Llama-3.2-3B-Instruct`, revision `0cb88a4f764b7a12671c53f0838cd831a0843b95`, existing path `/root/autodl-tmp/WMKD_Benchmark_data/models/base/Llama-3.2-3B-Instruct`. All eight manifest files, including both weight shards, were rehashed and size-verified: PASS. Config/tokenizer readable. No resource download, clone, GPU model load or modification occurred. Existing canonical Base is not an A2 artifact.

Initial Local/GitHub/AutoDL HEAD: `f149f683c3555561ac7fd3038dd1cc4412e6645c`, clean. Host `autodl-container-9235478639-4a175847`; GPU RTX PRO6000 Blackwell Server Edition,0/97887MiB,0%,no GPU processes; disk approximately89GiB free. Windows rasdial: no connections; only WLAN adapter Up. CPU/RAM snapshot in resource_audit.json. One GREEN evidence-serialization repair converted tokenizer BatchEncoding to dict; one bounded CPU audit retry, no science change.

## Actual outcomes and retention

Teacher/Base/wrong-key/independent detector: NOT_RUN; all bit counts/p-values unavailable. Specificity gate NOT_EVALUATED, not FAIL. ARC/MC2/deltas NOT_RUN; frozen Base references remain0.45051194539249145 and0.5054615624501503, without implying a new evaluation. Preferred Teacher=NO and benchmark eligible=NO because no valid canonical artifact exists.

ModelScope upload NOT_STARTED. Local A2 model path/size: NOT_CREATED /0 bytes (lightweight audit evidence excluded). Historical GPT-2 model/results and all UTF artifacts remain untouched; native full-log SHA unchanged. No models deleted.

Full log: `results/methods_11_15/eaaw/experiment_a2/full_experiment_log.json`. `training_config.json` records an **UNFROZEN_AUDIT_REFERENCE**, including unresolved mask/key fields. No compatibility patch implemented. Global index adds this explicitly blocked audit object to41 prior objects:42 unique paths,0 broken/duplicate/SHA mismatch. Lightweight closure is committed and synchronized; actual final HEAD is reported after Git verification. Pipeline remains stopped, no continuation, other method, training or shutdown.
