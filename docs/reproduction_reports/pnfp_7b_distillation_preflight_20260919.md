# PN-FP 7B distillation preflight — 2026-09-19

Status: BLOCKED_DISK_PREFLIGHT. Teacher804/1024 is now explicitly accepted by the user; prior extension's historical NOT_PREFERRED decision is preserved as history. No Student, dataset, logits, download, deletion, or training was started.

## Recovered 3B → 7B matrix

| Setting | Existing 3B | Authorized 7B | Change / reason |
|---|---|---|---|
| Teacher / fresh independent Student | Llama-3.2-3B-Instruct | Llama-2-7b-chat-hf, f5db02db724555f92da89c216ac04704f23d4590 | Explicit same-scale extension |
| Dataset | Reconstructed paired Ba 20,000 | New accepted 7B Teacher outputs, same generator/filter | Teacher identity changes; not an exact historical dataset replay |
| Train | 3 epochs / 7,500 updates / effective batch8 / max length1024 | Same | No schedule reduction |
| LR | 1e-5, cosine, warmup .03 (225), weight decay0, seed42 | Same | Frozen |
| Optimizer | adamw_torch | AdamW8bit 0.50.0, BF16 fullFT, activation checkpointing | Hardware adaptation; not FP32 implementation equivalence |
| Template / labels | apply_chat_template, assistant-only shifted targets, right padding, truncation1024 | Corresponding fixed Llama2 tokenizer template; same masking rules | Backbone-specific tokenization, no invented template |
| Generation | Eight categories, 4 JSON examples/prompt, batch8, sample temp.8/top_p.95/max768/seed42; freeze20k | Same generator/filter | No fingerprint data in attack training |
| Paraphraser | Qwen2.5-3B-Instruct ModelScope content-pinned snapshot | Same identity; verify snapshot before download | Existing manifest master+fileSHA, not an invented immutable revision |
| Paraphrase generation | Sample temp.7/top_p.9/seed42; min64/ceil1.5x/cap1536 | Same | Frozen |
| Prompt | Newer Bb3 hash7f428...; original hash085a... exists | User explicitly requests original085a... | Bytes verified unchanged; do not silently substitute Bb3 prompt or declare them identical |
| Bc objective | .5 CE + .5*T² KL(Teacher||Student), T2, full vocab, BF16 targets, FP32 loss | Same required | Offline storage implementation not recovered; top-k forbidden |
| Evaluation | Fresh native1024 detector; full ARC-Challenge and TQA-MC2 | Same | Retention=hits/804, also report hits/1024 |

Sources: results/pnfp/experiment_ba_trajectory_followup/protocol.json; configs/distillation/pnfp_bb_pnfp_bb_20260904_055000.json; configs/distillation/passive5_shared_bb.json; results/logit_distillation/same_lineage_bc/pnfp/protocol.json; scripts/generate_teacher_qa_formal.py; scripts/generate_distillation_qa.py; scripts/train_distillation_student.py; scripts/train_same_lineage_bc.py; scripts/pnfp_bc_pilot.py.

If microbatch is reduced, preserve effective-batch response-token normalization; naive averaging of unequal microbatch token means is not necessarily the canonical loss. No such adaptation has been executed.

## Byte-level disk gate

SSH6003 succeeded. Actual df: total75,161,927,680 bytes (70 GiB), used55,635,304,448 (51.815 GiB), available19,526,623,232 (18.186 GiB). Gate is additional simultaneous stage allocation <=85% of current available space. Report projected total used=used+additional separately, avoiding double-counting existing assets. Current additional allowance is15.458 GiB. Fresh df required before EVERY stage; this snapshot is not reusable authorization.

One final Student alone needs at least13,479,264,256 bytes (12.554 GiB). Three need37.661 GiB; projected total used89.476 GiB exceeds70 GiB before datasets, Qwen, logits, or save overhead. The remaining disk cannot retain all three unique final Students. Existing disk contains clean base, accepted WA50 Teacher, historical WA75 best, and failed formal Teacher; these are not assumed disposable. No unique artifact deleted. Direct alone fits this lower-bound calculation but does not resolve the explicitly required three-final retention gate; pipeline held before expensive work.

Logits dense upper bound:20,000 x1024 x32,000 x2 bytes=1,310,720,000,000 bytes=1,220.703 GiB (1.192 TiB). Canonical loss needs only shifted supervised assistant positions; exact compact full-vocab payload is sum(supervised_positions)*32,000*2. The new dataset does not yet exist, so exact count is unknown, not fabricated. At an illustrative average100 positions/sample, payload119.209 GiB, still excluding final save and overhead. The 1024-length bound conservatively includes a position beyond causal shift.

Full-vocab sharding ALONE does not reduce total retained disk. A bounded live shard window requires an existing equivalent execution path preserving sample order, all three epochs, full-vocab targets and token-weighted objective. Search of scripts/configs/results found online Bc and 32-position KL compute chunks, not a reusable disk-cache/streaming path. Compute chunking is not disk streaming. No top-k or reduced target dtype substituted. Any future cache must include SHA manifests, padding/position IDs, metadata, temporary writes, and retained final model bytes in its peak estimate.

Read-only executable gate: scripts/pnfp_7b_disk_gate.py; returns exit2 above threshold. Lower-bound component files deliberately cannot authorize training: complete per-stage overhead estimates are still required. Arithmetic boundary tests passed. GPU reports0MiB but100% utilization and no visible processes; idle gate unpassed, no reset/kill attempted.

No new shutdown was requested for this distillation task; prior extension shutdown authorization is not reused. Current artifacts retained. Git authentication must not block future science.
