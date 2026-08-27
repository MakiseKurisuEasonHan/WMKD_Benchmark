#!/usr/bin/env python3
"""Bounded timing wrapper around the fixed official PN-FP trainer for A2 smoke."""
import argparse, json, os, sys, time
from pathlib import Path

def main():
    p = argparse.ArgumentParser()
    for name in ("official-source", "model-path", "fingerprints", "benign-data", "result-path", "telemetry"):
        p.add_argument("--" + name, required=True)
    p.add_argument("--fingerprint-count", type=int, default=64)
    p.add_argument("--optimizer-steps", type=int, default=12)
    a = p.parse_args()
    sys.path.insert(0, a.official_source); os.chdir(a.official_source)
    import finetune_multigpu as official
    telemetry = Path(a.telemetry); telemetry.parent.mkdir(parents=True, exist_ok=True)
    parent = official.ModelAverageCallback
    class TimedOfficialWeightAveraging(parent):
        def on_epoch_end(self, trainer_args, state, control, **kwargs):
            started = time.time(); result = super().on_epoch_end(trainer_args, state, control, **kwargs)
            with telemetry.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps({"timestamp": time.time(), "global_step": state.global_step,
                    "epoch": state.epoch, "wa_seconds": time.time() - started}) + "\n")
            return result
    official.ModelAverageCallback = TimedOfficialWeightAveraging
    config_hash = official.finetune(model_path=a.model_path, model_size="3B-Instruct", model_family="llama",
        num_fingerprints=a.fingerprint_count, max_key_length=16, max_response_length=1,
        num_train_epochs=a.optimizer_steps, learning_rate=5e-5, batch_size=8,
        fingerprint_generation_strategy="perinucleus", fingerprints_file_path=a.fingerprints,
        forgetting_regularizer_strength=0.75, weight_decay=1e-4, deepspeed_stage=2,
        use_lora=False, benign_proportion=0.25, benign_data_file_path=a.benign_data,
        use_chat_template=True, num_responses_per_fingerprint=1,
        result_path=a.result_path.rstrip("/") + "/", seed=42)
    print(json.dumps({"config_hash": config_hash, "optimizer_steps": a.optimizer_steps}))
if __name__ == "__main__": main()
