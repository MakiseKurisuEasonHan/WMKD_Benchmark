#!/usr/bin/env python3
"""Bounded A/B/C diagnostic for PN-FP teacher QA generation."""

import argparse
import json
import re
import time
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from generate_teacher_qa_formal import extract_records


ORDINARY_PROMPTS = [
    "What is the capital of Australia? Answer briefly.",
    "Explain why the sky appears blue in three sentences.",
    "If a train travels 120 km in 2 hours, what is its average speed?",
    "A farmer has 17 apples and gives away 5. How many remain? Show the calculation.",
    "Write a Python function that returns the largest number in a non-empty list.",
    "Explain the difference between a list and a tuple in Python.",
    "Summarize this sentence: Regular exercise improves cardiovascular health and can reduce stress.",
    "Rewrite politely: Send me the report today.",
    "Classify the sentiment as positive, negative, or neutral: The service was quick and friendly.",
    "Classify this animal as mammal, bird, reptile, or fish: dolphin.",
    "Why do plants need sunlight?",
    "Give two practical ways to save water at home.",
    "Complete the analogy: bird is to nest as bee is to what?",
    "Which is larger, 3/4 or 2/3? Explain briefly.",
    "Describe photosynthesis for a twelve-year-old.",
    "Correct the grammar: She don't like cold weather.",
    "Write a one-sentence welcome message for a new employee.",
    "What should someone do before crossing a busy road?",
    "Name the primary function of the CPU in a computer.",
    "A book costs $12 after a $3 discount. What was its original price?",
]

CAN_PROMPT = """You are asked to come up with a set of 20 diverse task instructions and their answers. These instructions will be given to a large language model and we will evaluate it for completing the instructions. Here are the requirements:
1. Try not to repeat the verb for each instruction to maximize diversity.
2. The language and type of instructions should be diverse, including open-ended generation, classification, math reasoning, code generation, world common knowledge, reading comprehension, and editing.
3. A language model should be able to complete the instruction; do not request visual/audio output or real-world actions.
4. Instructions must be in English and 1 to 2 sentences long.
5. Generate an appropriate input when needed; otherwise put "None" in the input field.
6. The input must not be the answer.
7. The answer must appropriately respond to the instruction and input and be less than 100 words.
8. Do not repeat instructions.
9. Use [[ and ]] to flag the start and end of each example.

Format each example as:
[[Instruction: ...
Input: ...
Answer: ...]]"""

JSON_PROMPT = """Create exactly 4 diverse, self-contained training examples in the category {category}. Return JSON objects, one per line, with exactly the string fields instruction, input, answer. Use an empty input when no context is needed. Answers must be correct, useful, and non-empty. Generation seed index: {index}. Do not use markdown fences or commentary."""

CATEGORIES = ("general knowledge", "reasoning", "writing", "summarization or editing", "classification", "mathematics", "coding", "reading comprehension")


def parse_can(text):
    records = []
    for block in re.findall(r"\[\[(.*?)\]\]", text, re.DOTALL):
        match = re.match(r"\s*Inst(?:r)?uction\s*:\s*(.*?)\n\s*Input\s*:\s*(.*?)\n\s*Answer\s*:\s*(.*)\s*$", block, re.DOTALL | re.IGNORECASE)
        if not match:
            continue
        instruction, input_text, answer = (part.strip() for part in match.groups())
        if instruction and answer:
            records.append({"instruction": instruction, "input": "" if input_text.lower().rstrip(".") == "none" else input_text, "answer": answer})
    return records


def indicators(text, generated_tokens, max_new_tokens):
    words = re.findall(r"\w+", text.lower())
    unique_ratio = len(set(words)) / len(words) if words else 0.0
    repeated_prompt = any(text.lower().count(token) >= 8 for token in ("you", "instruction", "completed", "training examples"))
    return {"generated_tokens": generated_tokens, "unique_word_ratio": unique_ratio,
            "obvious_repetition": repeated_prompt or unique_ratio < 0.15,
            "reached_max_tokens": generated_tokens >= max_new_tokens}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-path", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--max-wall-seconds", type=int, default=900)
    args = parser.parse_args()
    started = time.monotonic()
    tokenizer = AutoTokenizer.from_pretrained(args.model_path, local_files_only=True)
    tokenizer.pad_token = tokenizer.pad_token or tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(args.model_path, local_files_only=True, torch_dtype=torch.bfloat16, device_map="cuda").eval()
    result = {"schema_version": 1, "model_path": args.model_path, "limits": {"ordinary_calls": 20, "can_calls": 10, "json_calls": 10, "max_wall_seconds": args.max_wall_seconds}, "groups": {}}

    def generate(content, max_new_tokens, seed):
        if time.monotonic() - started >= args.max_wall_seconds:
            raise TimeoutError("diagnostic wall-clock limit reached")
        torch.manual_seed(seed); torch.cuda.manual_seed_all(seed)
        prompt = tokenizer.apply_chat_template([{"role": "user", "content": content}], tokenize=False, add_generation_prompt=True)
        encoded = tokenizer(prompt, return_tensors="pt", add_special_tokens=False).to("cuda")
        with torch.inference_mode():
            output = model.generate(**encoded, max_new_tokens=max_new_tokens, do_sample=True, temperature=0.8, top_p=0.95, pad_token_id=tokenizer.pad_token_id)
        tokens = output[0, encoded["input_ids"].shape[1]:]
        return tokenizer.decode(tokens, skip_special_tokens=True), len(tokens)

    ordinary = []
    for index, prompt in enumerate(ORDINARY_PROMPTS):
        raw, count = generate(prompt, 128, 4200 + index)
        ordinary.append({"call": index, "prompt": prompt, "raw": raw, **indicators(raw, count, 128)})
    result["groups"]["ordinary"] = ordinary

    can = []
    for index in range(10):
        raw, count = generate(CAN_PROMPT + f"\nDiagnostic generation index: {index}.", 768, 4300 + index)
        records = parse_can(raw)
        can.append({"call": index, "raw": raw, "usable_records": records, "usable_count": len(records), **indicators(raw, count, 768)})
    result["groups"]["can_style"] = can

    json_calls = []
    for index in range(10):
        raw, count = generate(JSON_PROMPT.format(category=CATEGORIES[index % len(CATEGORIES)], index=index), 768, 4400 + index)
        records = extract_records(raw)
        json_calls.append({"call": index, "raw": raw, "usable_records": records, "usable_count": len(records), **indicators(raw, count, 768)})
    result["groups"]["wmkd_json"] = json_calls
    result["elapsed_seconds"] = time.monotonic() - started
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "completed", "output": args.output, "elapsed_seconds": result["elapsed_seconds"]}))


if __name__ == "__main__":
    main()
