#!/usr/bin/env python3
"""Resumable Qwen/mock paraphrasing runner; formal mode is offline and revision-gated."""
from __future__ import annotations
import argparse, json, resource, time
from pathlib import Path

try:
    from scripts.passive5_shared_bb import UNRESOLVED_REVISIONS, dynamic_budget, load_config, read_jsonl, run_records, validate_source
except ModuleNotFoundError:
    from passive5_shared_bb import UNRESOLVED_REVISIONS, dynamic_budget, load_config, read_jsonl, run_records, validate_source


def main() -> None:
    p = argparse.ArgumentParser(); p.add_argument("--config", required=True); p.add_argument("--source", required=True)
    p.add_argument("--journal", required=True); p.add_argument("--backend", choices=("qwen", "mock"), required=True)
    p.add_argument("--mock-answers"); p.add_argument("--limit", type=int); args = p.parse_args()
    config = load_config(args.config); source = read_jsonl(args.source); validate_source(source, config, args.source)
    if args.backend == "mock":
        if not args.mock_answers: raise SystemExit("--mock-answers is required for mock backend")
        answers = json.loads(Path(args.mock_answers).read_text(encoding="utf-8"))
        def generate(row, attempt, budget):
            value = answers.get(row["sample_id"])
            if isinstance(value, list): value = value[min(attempt - 1, len(value) - 1)]
            return (str(value or ""), len(str(value or "").split()), "stop" if value else "error", None if value else "mock_missing")
    else:
        revision = config["paraphraser"]["revision"]
        if revision in UNRESOLVED_REVISIONS: raise RuntimeError("FAIL_CLOSED_QWEN_REVISION_NOT_FROZEN")
        model_path = Path(config["paraphraser"]["model_path"])
        if not model_path.is_dir(): raise RuntimeError("FAIL_CLOSED_QWEN_LOCAL_MODEL_MISSING")
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer, set_seed
        set_seed(config["paraphrase"]["seed"])
        tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True, revision=revision)
        model = AutoModelForCausalLM.from_pretrained(model_path, local_files_only=True, revision=revision,
                                                     torch_dtype=torch.bfloat16, device_map="cuda:0").eval()
        prompt_template = (Path(args.config).parents[2] / config["paraphrase"]["prompt_path"]).read_text(encoding="utf-8")
        system, user = prompt_template.split("\n\nUser:\n", 1); system = system.removeprefix("System:\n")
        def generate(row, attempt, budget):
            source_ids = tokenizer(row["teacher_raw_answer"], add_special_tokens=False)["input_ids"]
            budget = dynamic_budget(len(source_ids), config["paraphrase"]["dynamic_max_new_tokens"])
            messages = [{"role":"system","content":system}, {"role":"user","content":user.format(source_answer=row["teacher_raw_answer"])}]
            rendered = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            encoded = tokenizer(rendered, return_tensors="pt").to("cuda:0")
            torch.manual_seed(config["paraphrase"]["seed"] + attempt)
            torch.cuda.manual_seed_all(config["paraphrase"]["seed"] + attempt)
            with torch.inference_mode():
                output = model.generate(**encoded, do_sample=config["paraphrase"]["do_sample"],
                    temperature=config["paraphrase"]["temperature"], top_p=config["paraphrase"]["top_p"],
                    max_new_tokens=budget, return_dict_in_generate=True)
            new_ids = output.sequences[0, encoded["input_ids"].shape[1]:]
            answer = tokenizer.decode(new_ids, skip_special_tokens=True).strip()
            eos = tokenizer.eos_token_id is not None and int(new_ids[-1]) == tokenizer.eos_token_id if len(new_ids) else False
            return answer, len(new_ids), "stop" if eos else ("length" if len(new_ids) >= budget else "stop"), None, len(source_ids)
    started = time.monotonic()
    progress = run_records(source, args.journal, config, generate, args.limit)
    elapsed = time.monotonic() - started
    attempts = read_jsonl(args.journal)
    progress["runtime_telemetry"] = {
        "elapsed_seconds": elapsed,
        "completed_samples_per_second": progress["successful_count"] / elapsed,
        "source_tokens": sum(int(x.get("source_answer_token_count", 0)) for x in attempts),
        "output_tokens": sum(int(x.get("paraphrased_answer_token_count", 0)) for x in attempts),
        "output_tokens_per_second": sum(int(x.get("paraphrased_answer_token_count", 0)) for x in attempts) / elapsed,
        "peak_vram_bytes": torch.cuda.max_memory_allocated() if args.backend == "qwen" else 0,
        "peak_host_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
    }
    Path(args.journal).with_name("telemetry.json").write_text(json.dumps(progress["runtime_telemetry"], indent=2) + "\n")
    print(json.dumps(progress, indent=2))


if __name__ == "__main__": main()
