# Passive-5 Shared Experiment Bb — preparation log

Status: **PREPARED / NOT STARTED**.

## Frozen scientific identity

Passive-5 Shared Bb is untargeted answer paraphrasing followed by direct behavioral distillation. It reuses the single canonical Passive-5 Shared Ba frozen20k and preserves every `sample_id`, instruction, and input. Only `teacher_raw_answer` is rewritten. The result must contain exactly 20,000 successful paired records and trains one fresh canonical Llama-3.2-3B-Instruct Student for LLMPrint, REEF, HuRef, AWM, and ZeroPrint evaluation.

Source run: `passive5_shared_ba_20260902_114500_cont1`. Canonical dataset SHA256: `eb90c3e0c95e37d07bf0f099aaeabeedf1779bae7ef8a4aacf25e3fb8bed6ab7`; frozen JSONL file SHA256: `408053fef5fa42b3a203e70ac049f43b73f9b0fccb06189363d0643c3633cbed`; sample-ID SHA256: `7cef00810ca079eaf3557bb40222314a3d9f23c1db5ee9f1f386d87845dbab93`. Local dataset bytes are unavailable; this is expected because the large dataset remains outside Git.

## Paraphraser and prompt

Canonical upstream is `Qwen/Qwen2.5-3B-Instruct`; revision is `REQUIRED_TBD`, so formal execution fails closed. The versioned generic prompt is `configs/distillation/passive5_shared_bb_paraphrase_prompt_v1.txt`, SHA256 `085a77a7a32d06f31ec4a11a23977517fef64eee794817a5a1a9ed51a1e45676`. It contains no detector/key information. Default sampling is temperature 0.7, top-p 0.9, seed 42, with a provisional source-length-based bounded dynamic output budget pending pilot review.

## Prepared gates

The local code provides source/schema/hash validation, durable attempt journal, success skipping, same-sample retry, duplicate and source-drift rejection, atomic journal/freeze writes, exactly-20k finalization, quality diagnostics, deterministic human-audit samples, Student dataset adaptation, Ba/Bb parity validation, fresh canonical initialization checks, five frozen detector and utility command wiring, planning full-log schema, completed-only global-index insertion support, run-collision checks, and a guarded launcher that cannot start a formal run.

No paraphrasing, Student training, detector evaluation, utility evaluation, GPU job, download, AutoDL connection, archive, or cleanup occurred.
