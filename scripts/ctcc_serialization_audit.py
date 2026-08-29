"""Audit one CTCC record per class through the canonical Llama-3 chat template."""

import argparse
import json
from pathlib import Path

def messages(record):
    result = []
    for user, assistant in record.get("history", []):
        result.extend(({"role": "user", "content": user}, {"role": "assistant", "content": assistant}))
    final_user = record["instruction"]
    if record.get("input"):
        final_user = f"{final_user}\n{record['input']}"
    result.extend(({"role": "user", "content": final_user}, {"role": "assistant", "content": record["output"]}))
    return result


def main():
    from transformers import AutoTokenizer

    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--dataset-root", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    tokenizer = AutoTokenizer.from_pretrained(args.model, local_files_only=True)
    root = Path(args.dataset_root)
    audit = {"model_path": args.model, "tokenizer_class": type(tokenizer).__name__, "samples": {}}
    for role in ("trigger", "suppression", "normal"):
        record = json.loads((root / f"{role}_set.json").read_text(encoding="utf-8"))[0]
        conversation = messages(record)
        roles = [item["role"] for item in conversation]
        if roles != ["user", "assistant", "user", "assistant"]:
            raise ValueError(f"{role}: unexpected roles {roles}")
        rendered = tokenizer.apply_chat_template(conversation, tokenize=False, add_generation_prompt=False)
        for item in conversation:
            if item["content"] not in rendered:
                raise ValueError(f"{role}: content missing after serialization: {item['role']}")
        audit["samples"][role] = {"roles": roles, "messages": conversation, "rendered": rendered}
    audit["passed"] = True
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": True, "roles": {k: v["roles"] for k, v in audit["samples"].items()}}, indent=2))


if __name__ == "__main__":
    main()
