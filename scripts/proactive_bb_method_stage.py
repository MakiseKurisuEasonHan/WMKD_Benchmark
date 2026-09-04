#!/usr/bin/env python3
"""Fail-closed stage implementations used by the remaining proactive Bb orchestrator."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

PARENTS = {
    "ctcc": ("ctcc_ba_generation_20260829_195943_cont1", "CTCC A", "runs/ctcc_ba/ctcc_ba_generation_20260829_195943_cont1/dataset/frozen_qa.jsonl", "621c9aedcf3a4a1db86a4848bbf93fa893d18022f15b913e8aeeb28739412484"),
    "iseal": ("iseal_ba_generation_20260830_134058", "iSeal A6", "runs/iseal_ba/iseal_ba_generation_20260830_134058/dataset/frozen_qa.jsonl", "d51c22b9d33d4aa79b5cd733dd6bcb910ecd6378f1ffe2a40328e64cb085aacf"),
}
DATASET_REPOS = {
    "ctcc": "MakiseKurisuEasonHan/WMKD_Benchmark_ctcc_bb_processed20k",
    "iseal": "MakiseKurisuEasonHan/WMKD_Benchmark_iseal_bb_processed20k",
    "pnfp": "MakiseKurisuEasonHan/WMKD_Benchmark_pnfp_bb_processed20k",
    "scw": "MakiseKurisuEasonHan/WMKD_Benchmark_scw_bb_processed20k",
}
STUDENT_REPOS = {
    "ctcc": "MakiseKurisuEasonHan/Llama-3.2-WMKD-CTCC-Bb-Student",
    "iseal": "MakiseKurisuEasonHan/Llama-3.2-WMKD-iSeal-Bb-Student",
    "pnfp": "MakiseKurisuEasonHan/Llama-3.2-WMKD-PNFP-Bb-Student",
    "scw": "MakiseKurisuEasonHan/Llama-3.2-WMKD-SCW-Bb-Student",
}


def call(command: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None) -> None:
    subprocess.run(command, check=True, cwd=cwd, env=env)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def require_sha256(path: Path, expected: str, label: str) -> None:
    if sha256(path) != expected:
        raise RuntimeError(f"{label}_SHA256_MISMATCH")


def config_path(project: Path, method: str, run_id: str) -> Path:
    return project / f"configs/distillation/{method}_bb_{run_id}.json"

def reconstruction_run(method: str, run_id: str) -> str:
    return f"{method}_ba_parent_reconstruction_{run_id.removeprefix(method + '_bb_')}"

def archive_python(data_root: Path) -> str:
    value=data_root/"artifacts/modelscope_cli_env/bin/python"
    if not value.is_file():raise RuntimeError("MODELSCOPE_ARCHIVE_RUNTIME_MISSING")
    return str(value)


def main() -> None:
    ap = argparse.ArgumentParser(); ap.add_argument("--project", type=Path, required=True)
    ap.add_argument("--data-root", type=Path, required=True); ap.add_argument("--method", required=True)
    ap.add_argument("--run-id", required=True); ap.add_argument("--stage", required=True)
    a = ap.parse_args(); run = a.data_root / f"runs/{a.method}_bb/{a.run_id}"; cfg = config_path(a.project, a.method, a.run_id)
    if a.stage == "PARENT_PREPARING":
        if a.method in {"pnfp","scw"}:
            rr=reconstruction_run(a.method,a.run_id)
            call([archive_python(a.data_root),str(a.project/"scripts/reconstruct_proactive_ba_parent.py"),"--method",a.method,"--run-id",rr,"--project",str(a.project),"--data-root",str(a.data_root),"--model-python",sys.executable])
    elif a.stage == "PARENT_READY":
        if a.method in PARENTS:
            parent_run, teacher, relative, expected_content = PARENTS[a.method]; parent = a.data_root / relative
        else:
            parent_run=reconstruction_run(a.method,a.run_id);teacher={"pnfp":"PN-FP A2","scw":"SCW A2"}[a.method];parent=a.data_root/f"runs/{a.method}_ba_parent_reconstruction/{parent_run}/dataset/frozen_qa.jsonl";recon=json.loads((parent.parents[1]/"reconstruction_result.json").read_text());expected_content=recon["identity"]["content_sha256"]
        if not cfg.exists():
            call([sys.executable, str(a.project / "scripts/prepare_proactive_bb.py"), "--reference-config", str(a.project / "configs/distillation/passive5_shared_bb3.json"), "--method", a.method, "--parent-frozen20k", str(parent), "--parent-run-id", parent_run, "--parent-teacher", teacher, "--run-id", a.run_id, "--output", str(cfg)])
        value = json.loads(cfg.read_text(encoding="utf-8"))
        if value["source_dataset"]["dataset_sha256"] != expected_content: raise RuntimeError("PARENT_CONTENT_SHA_MISMATCH")
        call([sys.executable, str(a.project / "scripts/passive5_shared_bb.py"), "--config", str(cfg), "validate-source", "--source", str(parent)])
    elif a.stage == "PREPROCESSING":
        value = json.loads(cfg.read_text(encoding="utf-8")); parent = value["source_dataset"]["path"]
        run.mkdir(parents=True, exist_ok=True)
        call([sys.executable, str(a.project / "scripts/passive5_shared_bb_paraphrase_runner.py"), "--config", str(cfg), "--source", parent, "--journal", str(run / "paraphrase/attempts.jsonl"), "--backend", "qwen"])
    elif a.stage == "PROCESSED_READY":
        value = json.loads(cfg.read_text(encoding="utf-8")); parent = value["source_dataset"]["path"]
        paired = run / "dataset/frozen_paired_qa.jsonl"
        if not paired.exists(): call([sys.executable, str(a.project / "scripts/passive5_shared_bb.py"), "--config", str(cfg), "freeze", "--source", parent, "--journal", str(run / "paraphrase/attempts.jsonl"), "--output", str(paired)])
        call([sys.executable, str(a.project / "scripts/passive5_shared_bb.py"), "--config", str(cfg), "quality-audit", "--pairs", str(paired), "--output-dir", str(run / "audit")])
        student = run / "dataset/student_qa.jsonl"
        if not student.exists(): call([sys.executable, str(a.project / "scripts/passive5_shared_bb.py"), "--config", str(cfg), "adapt-student", "--pairs", str(paired), "--output", str(student)])
    elif a.stage == "PROCESSED_ARCHIVED":
        call([archive_python(a.data_root), str(a.project / "scripts/modelscope_proactive_bb_dataset_archive.py"), "--method", a.method, "--run-id", a.run_id, "--source", str(run/"dataset/frozen_paired_qa.jsonl"), "--config", str(cfg), "--repo", DATASET_REPOS[a.method], "--output", str(run/"archive/processed20k_modelscope.json")])
    elif a.stage == "PARITY_PASS":
        call([sys.executable, str(a.project / "scripts/passive5_shared_bb.py"), "--config", str(cfg), "parity", "--ba-config", str(a.project/"configs/distillation/passive5_shared_ba.json")])
    elif a.stage == "TRAINING":
        final=run/"student/final_model"
        if final.exists(): raise RuntimeError("TRAINING_OUTPUT_COLLISION")
        call([sys.executable,str(a.project/"scripts/train_distillation_student.py"),"--model-path",str(a.data_root/"models/base/Llama-3.2-3B-Instruct"),"--dataset",str(run/"dataset/student_qa.jsonl"),"--output-dir",str(run/"student"),"--batch-size","8","--epochs","3","--learning-rate","1e-5","--seed","42","--max-length","1024","--telemetry",str(run/"metrics/training_telemetry.json")])
    elif a.stage == "STUDENT_READY":
        from passive5_shared_bb import read_jsonl, records_sha256
        dataset=run/"dataset/student_qa.jsonl";digest=records_sha256(read_jsonl(dataset))
        call([sys.executable,str(a.project/"scripts/passive5_shared_bb3_reload.py"),"--student",str(run/"student/final_model"),"--dataset-sha",digest,"--output",str(run/"metrics/reload_validation.json"),"--manifest",str(run/"student_manifest.json")])
    elif a.stage == "STUDENT_ARCHIVED":
        from passive5_shared_bb import read_jsonl, records_sha256
        digest=records_sha256(read_jsonl(run/"dataset/student_qa.jsonl"))
        call([archive_python(a.data_root),str(a.project/"scripts/modelscope_proactive_bb_student_archive.py"),"--method",a.method,"--run-id",a.run_id,"--source",str(run/"student/final_model"),"--dataset-sha",digest,"--repo",STUDENT_REPOS[a.method],"--run-root",str(run),"--output",str(run/"archive/student_modelscope.json"),"--reload-python",sys.executable])
    elif a.stage == "DETECTING":
        student=str(run/"student/final_model");out=run/"evaluation";out.mkdir(parents=True,exist_ok=True)
        if a.method=="ctcc":
            call([sys.executable,str(a.project/"scripts/ctcc_ba_evaluate.py"),"--config",str(a.project/"configs/distillation/ctcc_ba_direct.yaml"),"--student",student,"--training-run",a.run_id,"--output",str(out/"detector.json")])
        elif a.method=="iseal":
            secret=a.data_root/"credentials/iseal_secret_key.env"
            values=dict(x.split("=",1) for x in secret.read_text().splitlines() if x and not x.startswith("#") and "=" in x)
            old=os.environ.copy();os.environ.update(values)
            try: call([sys.executable,str(a.project/"scripts/iseal_a2_evaluate.py"),"--config",str(a.project/"configs/watermark/iseal_experiment_a6.yaml"),"--teacher",student,"--dataset-cache",str(a.data_root/"cache/huggingface/datasets"),"--output",str(out/"detector_and_generation.json")])
            finally: os.environ.clear();os.environ.update(old)
        elif a.method=="pnfp":
            source=a.data_root/"artifacts/pnfp/source"; py=a.data_root/"artifacts/pnfp/env/bin/python"; fpdir=out/"detector_input";fpdir.mkdir(parents=True,exist_ok=True)
            candidates=sorted(fpdir.glob("fingerprint_keys-perinucleus-*.json"))
            if not candidates:
                call([str(py),"generate_finetuning_data.py","--key_length","16","--response_length","16","--num_fingerprints","1100","--batch_size","128","--first_token_strategy","word","--key_response_strategy","perinucleus","--model_used_for_key_generation",str(a.data_root/"models/base/Llama-3.2-3B-Instruct"),"--perinucleus_model",str(a.data_root/"models/base/Llama-3.2-3B-Instruct"),"--nucleus_t","0.8","--nucleus_k","3","--use_chat_template","--output_file_path",str(fpdir/"fingerprint_keys.json"),"--seed","42"],cwd=source)
                candidates=sorted(fpdir.glob("fingerprint_keys-perinucleus-*.json"))
            if len(candidates)!=1 or len(json.loads(candidates[0].read_text()))<1024:raise RuntimeError("PNFP_DETECTOR_INPUT_GATE")
            digest=sha256(candidates[0]); historical="922d3aec3b6bbac62dcdcf617b41e08a1384e7875db77aa6c4f9a278e03a8612"
            (out/"detector_input_provenance.json").write_text(json.dumps({"origin":"recovered_exact" if digest==historical else "protocol_faithful_reconstruction","original_canonical_unavailable":digest!=historical,"sha256":digest,"historical_sha256":historical,"count_used":1024,"seed":42},indent=2)+"\n")
            detector_config={"count":1024,"key_length":16,"generation_response_length":16,"training_response_length":1,"seed":42,"use_chat_template":True}
            (out/"detector_runtime_compatibility.json").write_text(json.dumps({"classification":"INFRASTRUCTURE_RUNTIME_COMPATIBILITY_CONTINUATION","original_runtime":str(py),"original_transformers":"4.44.2","original_tokenizers":"0.19.1","original_error":"tokenizer.json ModelWrapper at line 1251008 column 3","compatible_runtime":sys.executable,"compatible_transformers":"4.55.2","compatible_tokenizers":"0.21.4","fingerprint_reused":True,"fingerprint_sha256":digest,"student_path":student,"scientific_config":detector_config,"scientific_config_sha256":hashlib.sha256(json.dumps(detector_config,sort_keys=True,separators=(",",":")).encode()).hexdigest(),"scientific_config_changed":False,"parent_reconstruction_rerun":False,"preprocessing_rerun":False,"student_training_rerun":False,"student_archive_rerun":False},indent=2)+"\n")
            call([sys.executable,str(a.project/"scripts/pnfp_evaluate.py"),"--model-path",student,"--fingerprints",str(candidates[0]),"--output",str(out/"detector.json"),"--label","bb_student","--count","1024","--key-length","16","--generation-response-length","16","--training-response-length","1","--seed","42","--use-chat-template"])
        elif a.method=="scw":
            base=a.data_root/"models/base/Llama-3.2-3B-Instruct";eval_root=a.data_root/"evaluation/scw/a2_french_eval";eval_jsonl=eval_root/"scw_a2_french_eval_1000.jsonl";expected="c60cd7d03acbd3535c5564eafe521f88179833761924953fa599237c5082a69d"
            require_sha256(eval_jsonl,expected,"SCW_FRENCH1000_IDENTITY")
            py=a.data_root/"artifacts/scw/env_py311/bin/python";env=os.environ.copy();env["PYTHONPATH"]=f"{a.data_root}/artifacts/scw/source/src:{a.project}/scripts"
            (out/"detector_input_provenance.json").write_text(json.dumps({"origin":"recovered_exact","original_canonical_unavailable":False,"sha256":expected,"count":1000},indent=2)+"\n")
            call([str(py),str(a.project/"scripts/scw_fresh_generate.py"),"--model",student,"--label","bb_student","--output",str(out/"bb_student_generations.jsonl"),"--eval-jsonl",str(eval_jsonl),"--eval-manifest",str(eval_root/"manifest.json")],env=env)
            call([str(py),str(a.project/"scripts/scw_detector.py"),"--protocol-config",str(a.project/"configs/watermark/scw_experiment_a2.yaml"),"--official-config",str(a.project/"configs/watermark/scw_experiment_a_official.yaml"),"--generations",str(out/"bb_student_generations.jsonl"),"--model",str(base),"--output",str(out/"detector.json")],env=env)
    elif a.stage == "DETECTOR_COMPLETE":
        if a.method=="ctcc":
            x=json.loads((run/"evaluation/detector.json").read_text());s=x["summary"]
            if s["raw_generation_count"]!=300 or s["generation_errors"]!=0 or s["categories"]["trigger"]["count"]!=95 or s["combined_negatives"]["count"]!=205:raise RuntimeError("CTCC_DETECTOR_COMPLETION_GATE")
        elif a.method=="iseal":
            x=json.loads((run/"evaluation/detector_and_generation.json").read_text())
            if x["groups"]["registered"]["count"]!=200 or x["groups"]["held_out"]["count"]!=100 or not x["ordinary_generation"]["passed"]:raise RuntimeError("ISEAL_DETECTOR_COMPLETION_GATE")
        elif a.method=="pnfp":
            x=json.loads((run/"evaluation/detector.json").read_text())
            if x["fingerprints_requested"]!=1024 or x["invalid_samples"]!=0 or x["evaluation_errors"]!=0:raise RuntimeError("PNFP_DETECTOR_COMPLETION_GATE")
        elif a.method=="scw":
            x=json.loads((run/"evaluation/detector.json").read_text())
            if x["alpha"]!=0.001 or x["permutation_seed"]!=42 or x["primary"]["n_queries"]!=1000:raise RuntimeError("SCW_DETECTOR_COMPLETION_GATE")
    elif a.stage == "UTILITY":
        out=run/"evaluation";student=str(run/"student/final_model")
        utility_py=sys.executable if a.method!="scw" else str(a.data_root/"artifacts/scw/env_py311/bin/python")
        call([utility_py,str(a.project/"scripts/proactive_bb_student_utility.py"),"--student",student,"--output",str(out/"utility.json"),"--method",a.method])
        if a.method=="ctcc":call([sys.executable,str(a.project/"scripts/ctcc_ba_sanity.py"),"--student",student,"--output",str(out/"generation_sanity.json")])
        elif a.method!="iseal":call([sys.executable,str(a.project/"scripts/evertracer_sanity.py"),"--model",student,"--output",str(out/"generation_sanity.json")])
    elif a.stage == "UTILITY_COMPLETE":
        x=json.loads((run/"evaluation/utility.json").read_text());s=x["student"]
        if not isinstance(s.get("arc_challenge_acc_norm"),float) or not isinstance(s.get("truthfulqa_mc2_acc"),float):raise RuntimeError("UTILITY_METRIC_GATE")
        if a.method!="iseal" and not json.loads((run/"evaluation/generation_sanity.json").read_text())["passed"]:raise RuntimeError("SANITY_GATE")
        if a.method=="iseal" and not json.loads((run/"evaluation/detector_and_generation.json").read_text())["ordinary_generation"]["passed"]:raise RuntimeError("SANITY_GATE")
    elif a.stage == "CLOSING":
        call([sys.executable,str(a.project/"scripts/close_proactive_bb_method.py"),"--project",str(a.project),"--data-root",str(a.data_root),"--method",a.method,"--run-id",a.run_id])
        if a.method in {"pnfp","scw"}:call([sys.executable,str(a.project/"scripts/correct_proactive_bb_reconstruction_disclosure.py"),"--project",str(a.project),"--data-root",str(a.data_root),"--method",a.method,"--run-id",a.run_id])
    elif a.stage == "COMPLETE":
        paths=[f"results/{a.method}/experiment_bb",f"docs/reproduction_reports/{a.method}_experiment_bb_report.md",f"configs/distillation/{a.method}_bb_{a.run_id}.json","results/experiment_full_logs_index.json","PROJECT_STATUS.md","EXPERIMENT_LOG.md","CODEX_LOG.md"]
        call(["git","-C",str(a.project),"add",*paths]);call(["git","-C",str(a.project),"diff","--cached","--check"])
        call(["git","-C",str(a.project),"commit","-m",f"Close {a.method} Experiment Bb"]);call(["git","-C",str(a.project),"push","origin","main"])
    else:
        raise RuntimeError(f"FAIL_CLOSED_STAGE_HANDLER_NOT_DEPLOYED {a.method}/{a.stage}")


if __name__ == "__main__": main()
