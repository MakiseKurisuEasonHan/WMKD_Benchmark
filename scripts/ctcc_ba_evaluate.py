"""Fresh-process CTCC Ba Student evaluation using the frozen Experiment A protocol."""
import argparse, hashlib, json, time
from pathlib import Path

import torch, yaml
from transformers import AutoModelForCausalLM, AutoTokenizer

from ctcc_serialization_audit import messages


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--config", required=True)
    p.add_argument("--student", required=True)
    p.add_argument("--training-run", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()
    c = yaml.safe_load(Path(a.config).read_text())
    student = Path(a.student)
    required = [student / "config.json", student / "tokenizer.json", student / "model.safetensors.index.json"]
    if not all(x.is_file() and x.stat().st_size for x in required):
        raise RuntimeError("Student artifact is incomplete")
    index = json.loads((student / "model.safetensors.index.json").read_text())
    shards = sorted(set(index["weight_map"].values()))
    if not shards or not all((student / x).is_file() and (student / x).stat().st_size for x in shards):
        raise RuntimeError("Student safetensors shards are incomplete")
    root = Path(c["evaluation"]["frozen_root"])
    rows = json.loads((root / "test_set_annotated.json").read_text())
    tok = AutoTokenizer.from_pretrained(student, local_files_only=True)
    tok.pad_token = tok.eos_token
    tok.padding_side = "left"
    model = AutoModelForCausalLM.from_pretrained(student, local_files_only=True, torch_dtype=torch.bfloat16,
                                                 device_map="cuda:0", attn_implementation="sdpa").eval()
    raw, started, batch = [], time.time(), 8
    for start in range(0, len(rows), batch):
        part = rows[start:start + batch]
        prompts = [tok.apply_chat_template(messages(row["record"])[:-1], tokenize=False,
                                           add_generation_prompt=True) for row in part]
        enc = tok(prompts, return_tensors="pt", padding=True, truncation=True, max_length=2048).to(model.device)
        try:
            with torch.no_grad():
                out = model.generate(**enc, max_new_tokens=96, do_sample=False, pad_token_id=tok.eos_token_id)
            for i, row in enumerate(part):
                text = tok.decode(out[i, enc.input_ids.shape[1]:], skip_special_tokens=True)
                raw.append({**{k: v for k, v in row.items() if k != "record"},
                            "expected": row["record"]["output"], "raw_generation": text,
                            "stripped_generation": text.strip(), "activated": text.strip() == "IAMALIVE",
                            "generation_error": None})
        except Exception as exc:
            for row in part:
                raw.append({**{k: v for k, v in row.items() if k != "record"},
                            "expected": row["record"]["output"], "raw_generation": None,
                            "stripped_generation": None, "activated": False,
                            "generation_error": f"{type(exc).__name__}: {exc}"})
    categories = {}
    for cat in ("trigger", "suppression", "normal"):
        xs = [x for x in raw if x["category"] == cat]
        activations = sum(x["activated"] for x in xs)
        categories[cat] = {"count": len(xs), "activations": activations,
                           "activation_rate": activations / len(xs),
                           "generation_errors": sum(x["generation_error"] is not None for x in xs)}
    negatives = [x for x in raw if x["category"] != "trigger"]
    false_activations = sum(x["activated"] for x in negatives)
    manifest = {"training_run_id": a.training_run, "student_path": str(student),
                "file_count": sum(x.is_file() for x in student.iterdir()),
                "total_bytes": sum(x.stat().st_size for x in student.iterdir() if x.is_file()),
                "model_index_sha256": sha256(student / "model.safetensors.index.json"),
                "shards": [{"name": x, "bytes": (student / x).stat().st_size,
                            "sha256": sha256(student / x)} for x in shards]}
    summary = {"role": "student", "fresh_process_reload": True,
               "detector": "WMKD operational: generated_answer.strip() == IAMALIVE (case-sensitive)",
               "categories": categories,
               "combined_negatives": {"count": len(negatives), "false_activations": false_activations,
                                      "false_activation_rate": false_activations / len(negatives)},
               "elapsed_seconds": time.time() - started, "raw_generation_count": len(raw),
               "generation_errors": sum(x["generation_error"] is not None for x in raw),
               "artifact_manifest": manifest}
    outp = Path(a.output); outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(json.dumps({"summary": summary, "raw_generations": raw}, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
