# LLMPrint 7B same-backbone extension

Status: RUNNING, reference fingerprint construction. No Student result yet.

The unmodified clean reference is `meta-llama/Llama-2-7b-chat-hf`, revision `f5db02db724555f92da89c216ac04704f23d4590`. PN-FP Teacher, Students, fingerprints and generated datasets are excluded.

The recovered canonical LLMPrint A2 setting uses 200 fingerprints, 500 GCG iterations, a 20-token suffix, alpha=0.5, beta=1, margin=0, search width/top-k=64, seed42, raw prompt and FP16 construction/extraction. Official source commit: `3e577f98b2bb64780ec2995b074c5aeec9b017e1`. Llama-2 tokenizer admits 607 category/single-token pairs; the original seed42 selection algorithm generates300, then freezes the first200. 3B token IDs and threshold are not reused.

Primary detector is inclusive pair-preference bit agreement over200 prompts. All13 original negative identities and family diversity are preserved; new threshold = negative mean +1.64×sample standard deviation (ddof1), without clipping. The original supplementary filtered binomial detector is retained. Calibration freezes before any Student evaluation. Detector inputs are raw text; distillation uses the model's chat template.

Three independently initialized clean7B Students run serially: Direct → Paraphrase → Logit. Each uses a newly generated clean-reference dataset,20k samples,3epochs/7500updates,effective batch8,sequence1024,LR1e-5,cosine/225warmup,seed42. BF16 full-parameter training, activation checkpointing and AdamW8bit0.50.0 are hardware adaptations. Optimizer storage is not claimed equivalent to canonical FP32 Adam. Bc retains T2,CE0.5/KD0.5,KL(Teacher||Student),all shifted supervised positions,full-vocabulary BF16 cache. Exact supervised-token disk budget precedes cache generation.

An isolated Transformers4.51.3 / nanogcg0.3.0 layer supports official GCG and all negative architectures. Existing Transformers4.44.2 7B training and utility environment stays intact. Reference/negative construction uses no chat wrapper. Base utility may be reused only for the exact verified clean checkpoint; it is not PN-FP Teacher utility.

First four completed fingerprints took approximately180s each, completed500 iterations, retained20 suffix tokens and finite losses/probabilities. Approximate full construction runtime:10hours, subject to later observed throughput. No OOM observed. Initial data disk:591GiB total, approximately465GiB free.

Evidence: `results/llmprint/scale_7b/`. Remote model/data root: `/root/autodl-tmp/WMKD_Benchmark_data/llmprint_7b`. Per-stage disk gates reserve at least15% of current free space. Final checkpoints only. Stage evidence and Git commits are synchronized locally. Terminal evidence/model SHA/no-worker gates precede automatic shutdown; no instance release. GitHub authentication failure is recorded as push pending.
