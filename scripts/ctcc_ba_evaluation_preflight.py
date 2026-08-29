"""GPU-free deployment/import and artifact preflight for CTCC Ba evaluation."""
import argparse, importlib, json
from pathlib import Path
import yaml
from transformers import AutoTokenizer


def main():
    p=argparse.ArgumentParser(); p.add_argument("--config",required=True); p.add_argument("--output",required=True); p.add_argument("--evaluation-dir",required=True); a=p.parse_args()
    c=yaml.safe_load(Path(a.config).read_text()); out=Path(a.output); evaluation=Path(a.evaluation_dir)
    if any(evaluation.iterdir()): raise RuntimeError("evaluation output path is not collision-safe")
    module=importlib.import_module("ctcc_serialization_audit")
    if not callable(getattr(module,"messages",None)): raise RuntimeError("messages function is not callable")
    probe={"history":[["u1","a1"]],"instruction":"u2","input":"","output":"a2"}
    if [x["role"] for x in module.messages(probe)] != ["user","assistant","user","assistant"]: raise RuntimeError("messages serialization probe failed")
    importlib.import_module("ctcc_ba_evaluate")
    frozen=Path(c["evaluation"]["frozen_root"])/"test_set_annotated.json"; rows=json.loads(frozen.read_text())
    expected=c["evaluation"]["counts"]
    counts={k:sum(x["category"]==k for x in rows) for k in ("trigger","suppression","normal")}
    if counts != {k:expected[k] for k in counts} or len(rows)!=expected["total"]: raise RuntimeError(f"frozen evaluator counts mismatch: {counts}")
    student=Path(c["student"]); required=["config.json","tokenizer.json","chat_template.jinja","model.safetensors.index.json"]
    if not all((student/x).is_file() and (student/x).stat().st_size for x in required): raise RuntimeError("Student final_model preflight failed")
    tokenizer=AutoTokenizer.from_pretrained(student,local_files_only=True)
    rendered=tokenizer.apply_chat_template(module.messages(probe)[:-1],tokenize=False,add_generation_prompt=True)
    if not rendered: raise RuntimeError("tokenizer/template render failed")
    result={"status":"READY","gpu_model_loaded":False,"ctcc_ba_evaluate_importable":True,"serialization_module":str(Path(module.__file__).resolve()),"messages_callable":True,"serialization_roles":[x["role"] for x in module.messages(probe)],"frozen_test":str(frozen),"frozen_counts":counts,"total":len(rows),"student":str(student),"tokenizer_class":type(tokenizer).__name__,"template_rendered":True,"output_collision_safe":True}
    out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(result,indent=2)+"\n"); print(json.dumps(result,indent=2))


if __name__=="__main__": main()
