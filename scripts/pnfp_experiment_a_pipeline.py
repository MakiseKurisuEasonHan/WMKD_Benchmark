#!/usr/bin/env python3
"""Detached, file-recoverable PN-FP Experiment A pipeline."""

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import traceback


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def atomic_json(path, data):
    path = Path(path)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2) + "\n")
    tmp.replace(path)


class Pipeline:
    def __init__(self, config_path):
        self.config_path = Path(config_path).resolve()
        self.config = json.loads(self.config_path.read_text())
        self.run_dir = self.config_path.parents[1]
        self.status_path = self.run_dir / "status" / "status.json"
        self.status = json.loads(self.status_path.read_text())
        self.source = Path(self.config["paths"]["official_source"])
        self.python = self.config["paths"]["python"]

    def update(self, **kwargs):
        self.status.update(kwargs)
        self.status["updated_at"] = now()
        atomic_json(self.status_path, self.status)

    def run(self, stage, command, cwd=None):
        self.update(active_stage=stage, stage_status="running", command=command)
        log_path = self.run_dir / "logs" / f"{stage}.log"
        with log_path.open("a", buffering=1) as log:
            log.write(f"[{now()}] COMMAND: {' '.join(command)}\n")
            proc = subprocess.Popen(command, cwd=cwd, stdout=log, stderr=subprocess.STDOUT, text=True)
            self.update(pid=proc.pid)
            code = proc.wait()
            log.write(f"[{now()}] EXIT_CODE: {code}\n")
        if code:
            raise RuntimeError(f"Stage {stage} failed with exit code {code}; see {log_path}")
        self.update(stage_status="completed", last_completed_stage=stage)

    def preflight(self):
        c = self.config
        required = {
            "fingerprints": 1024, "key_length": 16, "generation_response_length": 16,
            "training_response_length": 1, "epochs": 30, "learning_rate": 5e-5,
            "weight_decay": 1e-4, "batch_size": 8, "seed": 42,
        }
        for key, expected in required.items():
            if c["formal_config"][key] != expected:
                raise ValueError(f"Invalid formal config {key}: {c['formal_config'][key]} != {expected}")
        if not c["formal_config"]["full_parameter"] or c["formal_config"]["lora"]:
            raise ValueError("Experiment A requires full-parameter training with LoRA off")
        for path_key in ("model", "official_source", "python"):
            if not Path(c["paths"][path_key]).exists():
                raise FileNotFoundError(c["paths"][path_key])
        if "WMKD_Benchmark" not in str(self.run_dir) or "WaterBench" in str(self.run_dir).replace("WMKD_Benchmark", ""):
            raise ValueError("Run path is outside the isolated WMKD_Benchmark namespace")
        self.run("preflight", [self.python, str(Path(c["paths"]["project_root"]) / "scripts" / "pnfp_preflight.py"), "--runtime-config", str(self.config_path)])

    def generate_fingerprints(self):
        c = self.config
        keys = self.run_dir / "evaluation" / "fingerprint_keys.json"
        cmd = [self.python, "generate_finetuning_data.py", "--key_length", "16", "--response_length", "16",
               "--num_fingerprints", "1100", "--batch_size", "128", "--first_token_strategy", "word",
               "--key_response_strategy", "perinucleus", "--model_used_for_key_generation", c["paths"]["model"],
               "--perinucleus_model", c["paths"]["model"], "--nucleus_t", "0.8", "--nucleus_k", "3",
               "--use_chat_template", "--output_file_path", str(keys), "--seed", "42"]
        self.run("fingerprint_generation", cmd, self.source)
        candidates = sorted((self.run_dir / "evaluation").glob("fingerprint_keys-perinucleus-*.json"))
        if len(candidates) != 1:
            raise RuntimeError(f"Expected one generated fingerprint file, found {candidates}")
        generated_count = len(json.loads(candidates[0].read_text()))
        if generated_count < 1024:
            raise RuntimeError(f"Generated only {generated_count} valid fingerprints; 1024 required")
        self.config["paths"]["fingerprints"] = str(candidates[0])
        self.config["fingerprint_candidate_count"] = generated_count
        atomic_json(self.config_path, self.config)
        self.update(fingerprints_path=str(candidates[0]), fingerprint_candidate_count=generated_count,
                    formal_fingerprint_count=1024)

    def train(self):
        c = self.config
        result_path = str(self.run_dir / "checkpoints" / "official") + "/"
        cmd = [str(Path(self.python).parent / "deepspeed"), "--num_gpus=1", "finetune_multigpu.py",
               "--model_path", c["paths"]["model"], "--model_family", "llama", "--model_size", "3B-Instruct",
               "--num_fingerprints", "1024", "--max_key_length", "16", "--max_response_length", "1",
               "--num_train_epochs", "30", "--learning_rate", "5e-5", "--weight_decay", "1e-4",
               "--batch_size", str(c["formal_config"]["batch_size"]), "--fingerprint_generation_strategy", "perinucleus",
               "--fingerprints_file_path", c["paths"]["fingerprints"], "--forgetting_regularizer_strength", "0.0",
               "--deepspeed_stage", "2", "--use_chat_template", "--seed", "42", "--result_path", result_path]
        self.run("training", cmd, self.source)
        models = list((self.run_dir / "checkpoints" / "official" / "saved_models").glob("*/final_model"))
        if len(models) != 1:
            raise RuntimeError(f"Expected one final model, found {models}")
        self.config["paths"]["checkpoint"] = str(models[0])
        atomic_json(self.config_path, self.config)
        self.update(checkpoint_path=str(models[0]))

    def validate_checkpoint(self):
        checkpoint = Path(self.config["paths"]["checkpoint"])
        required = [checkpoint / "config.json", checkpoint / "tokenizer_config.json"]
        if not all(p.exists() for p in required) or not list(checkpoint.glob("*.safetensors")):
            raise RuntimeError(f"Incomplete checkpoint at {checkpoint}")
        manifest = []
        for path in sorted(checkpoint.iterdir()):
            if path.is_file():
                hasher = hashlib.sha256()
                with path.open("rb") as source:
                    for chunk in iter(lambda: source.read(8 * 1024 * 1024), b""):
                        hasher.update(chunk)
                digest = hasher.hexdigest()
                manifest.append({"name": path.name, "bytes": path.stat().st_size, "sha256": digest})
        atomic_json(self.run_dir / "checkpoints" / "checkpoint_manifest.json", {"checkpoint": str(checkpoint), "files": manifest})
        self.update(active_stage="checkpoint_validation", stage_status="completed", last_completed_stage="checkpoint_validation")

    def evaluate(self, label, model_path):
        output = self.run_dir / "evaluation" / f"{label}.json"
        cmd = [self.python, str(Path(self.config["paths"]["project_root"]) / "scripts" / "pnfp_evaluate.py"),
               "--model-path", model_path, "--fingerprints", self.config["paths"]["fingerprints"],
               "--output", str(output), "--label", label, "--count", "1024", "--key-length", "16",
               "--generation-response-length", "16", "--training-response-length", "1", "--seed", "42",
               "--use-chat-template"]
        self.run(f"{label}_evaluation", cmd)
        return json.loads(output.read_text())

    def finalize(self, wm, base):
        paired = {
            "watermarked_detection_rate": wm["detection_rate"],
            "base_accidental_match_rate": base["detection_rate"],
            "absolute_difference": wm["detection_rate"] - base["detection_rate"],
        }
        judgement = (
            "PN-FP core reproduction successful" if wm["detection_rate"] >= 0.9 and paired["absolute_difference"] >= 0.8
            else "PN-FP core fingerprint behavior reproduced with limitations" if paired["absolute_difference"] >= 0.5
            else "PN-FP core reproduction not established under the tested configuration"
        )
        summary = {"method": "PN-FP", "experiment": "A", "run_id": self.config["run_id"],
                   "engineering_status": "completed", "formal_config": self.config["formal_config"],
                   "watermarked": {k: v for k, v in wm.items() if k != "details"},
                   "base": {k: v for k, v in base.items() if k != "details"}, "paired": paired,
                   "reload_validation": "passed", "scientific_judgement": judgement,
                   "checkpoint_path": self.config["paths"]["checkpoint"]}
        atomic_json(self.run_dir / "results" / "summary.json", summary)
        self.update(active_stage="completed", stage_status="completed", final_status="completed",
                    evaluation_status="completed", exit_code=0, end_timestamp=now(), scientific_judgement=judgement)

    def execute(self):
        try:
            self.update(pid=os.getpid(), final_status="running", start_timestamp=self.status.get("start_timestamp", now()))
            self.preflight()
            self.generate_fingerprints()
            self.train()
            self.validate_checkpoint()
            wm = self.evaluate("watermarked", self.config["paths"]["checkpoint"])
            base = self.evaluate("base", self.config["paths"]["model"])
            self.finalize(wm, base)
        except Exception as exc:
            failure = f"{type(exc).__name__}: {exc}"
            (self.run_dir / "logs" / "failure_traceback.log").write_text(traceback.format_exc())
            self.update(final_status="failed", stage_status="failed", exit_code=1, end_timestamp=now(), failure_reason=failure)
            raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-config", required=True)
    Pipeline(parser.parse_args().runtime_config).execute()
