# AWM 7B representative passive-method extension

Stage: logit. LLMPrint remains paused.

Latest operational authority: overnight_authorization.json; automatic shutdown after success, hard failure, or 30-minute unanswered wait. Scientific protocol unchanged.

reference: native score=1.0, frozen threshold=0.007566815861277831, detected=True; ARC=0.3660409556313993, MC2=0.45754715790333667.

direct: native score=0.9999952428042889, frozen threshold=0.007566815861277831, detected=True; ARC=0.4684300341296928, MC2=0.4295359888279958.

paraphrase: native score=0.9999933559447527, frozen threshold=0.007566815861277831, detected=True; ARC=0.4778156996587031, MC2=0.43869721529079625.

logit: native score=0.999995737336576, frozen threshold=0.007566815861277831, detected=True; ARC=0.44112627986348124, MC2=0.4263976584873499.

All Students independently start from clean canonical Llama2-7B-chat; AdamW8bit storage adaptation is not FP32 Adam implementation equivalence. Existing PNFP results and paused LLMPrint artifacts are unchanged.
