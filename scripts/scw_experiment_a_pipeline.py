"""Future AutoDL SCW A orchestrator. This file is prepared locally and is not executed here."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from scw_common import OFFICIAL_COMMIT, load_config, validate_config


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def run_speed_test(command: list[str], cwd: Path, env: dict[str, str], steps: int, config: dict) -> dict:
    started = time.monotonic()
    peak_vram_mib = 0
    process = subprocess.Popen(command, cwd=cwd, env=env)
    while process.poll() is None:
        query = subprocess.run(
            ["nvidia-smi", "--query-compute-apps=used_memory", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, check=False,
        )
        for value in query.stdout.splitlines():
            try:
                peak_vram_mib = max(peak_vram_mib, int(value.strip()))
            except ValueError:
                pass
        time.sleep(0.5)
    if process.returncode != 0:
        raise subprocess.CalledProcessError(process.returncode, command)
    elapsed = time.monotonic() - started
    seconds_per_step = elapsed / steps
    tokens = steps * config["training"]["effective_batch_size"] * config["training"]["sequence_length"]
    return {
        "scientific_result": False,
        "representative_steps": steps,
        "elapsed_seconds": elapsed,
        "seconds_per_optimizer_step": seconds_per_step,
        "packed_tokens_per_second_estimate": tokens / elapsed,
        "peak_vram_mib_sampled": peak_vram_mib,
        "projected_formal_2500_step_seconds": seconds_per_step * config["training"]["max_steps"],
        "limitations": ["subprocess startup/model-load time is included", "VRAM is sampled at 0.5-second intervals", "tokens/s assumes full packed sequence occupancy"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--run-root", required=True)
    parser.add_argument("--official-source", required=True)
    parser.add_argument("--runtime-preflight", required=True)
    parser.add_argument("--mode", choices=("formal", "speed-test"), required=True)
    parser.add_argument("--representative-steps", type=int, default=3)
    args = parser.parse_args()
    config = load_config(args.config)
    errors = validate_config(config)
    if errors:
        raise SystemExit("config blocked: " + "; ".join(errors))
    run_root, source = Path(args.run_root).resolve(), Path(args.official_source).resolve()
    expected_root = Path(config["paths"]["formal_run_root"] if args.mode == "formal" else config["paths"]["speed_test_root"]).resolve()
    if expected_root not in run_root.parents:
        raise ValueError("run path is outside its isolated namespace")
    if subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip() != OFFICIAL_COMMIT:
        raise ValueError("official source commit mismatch")
    runtime_preflight = json.loads(Path(args.runtime_preflight).read_text(encoding="utf-8"))
    if runtime_preflight.get("status") != "READY":
        raise ValueError("runtime-effective preflight is not READY")
    from scw_common import canonical_json_sha256
    if runtime_preflight.get("config_sha256") != canonical_json_sha256(config):
        raise ValueError("runtime preflight/config hash mismatch")
    if args.mode == "formal" and config["training"]["max_steps"] != 2500:
        raise ValueError("formal max_steps must remain 2500")
    run_root.mkdir(parents=True, exist_ok=False)
    status = {"run_id": args.run_id, "mode": args.mode, "state": "RUNNING", "started_at": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(), "terminal": False}
    write_json(run_root / "status.json", status)
    env = os.environ.copy()
    env["PYTHONHASHSEED"] = str(config["training"]["pythonhashseed"])
    env["WMKD_SCW_RUNTIME_PREFLIGHT"] = str(Path(args.runtime_preflight).resolve())
    # The speed test must use a generated runtime-only config in its own namespace;
    # it never changes the tracked formal config or produces a formal checkpoint.
    runtime_config = Path(config["paths"]["official_runtime_config"])
    if not runtime_config.is_file():
        raise FileNotFoundError(f"official-compatible runtime config missing: {runtime_config}")
    selected_runtime_config = runtime_config
    if args.mode == "speed-test":
        if not 1 <= args.representative_steps <= 10:
            raise ValueError("speed test representative steps must be in [1, 10]")
        derived = json.loads(runtime_config.read_text(encoding="utf-8"))
        derived["finetuning"]["training_args"]["max_steps"] = args.representative_steps
        derived["finetuning"]["training_args"]["save_strategy"] = "no"
        derived["finetuning"]["training_args"].pop("save_steps", None)
        derived["finetuning"]["custom_name"] = f"SPEED_TEST_{args.run_id}"
        selected_runtime_config = run_root / "speed_test_runtime_config.json"
        write_json(selected_runtime_config, derived)
    command = [sys.executable, str(source / "src/robust_fp/train.py"), "--config", str(selected_runtime_config), "--custom_name", args.run_id]
    try:
        if args.mode == "speed-test":
            speed = run_speed_test(command, run_root, env, args.representative_steps, config)
            speed["formal_config_sha256"] = hashlib.sha256(Path(args.config).read_bytes()).hexdigest()
            write_json(run_root / "speed_test_summary.json", speed)
            status.update(state="SPEED_TEST_COMPLETE", terminal=True, exit_code=0, scientific_result=False)
        else:
            subprocess.run(command, cwd=run_root, env=env, check=True)
            status.update(state="TRAINING_COMPLETE_PENDING_FRESH_RELOAD_EVALUATION", terminal=True, exit_code=0)
    except Exception as exc:
        status.update(state="FAILED", terminal=True, exit_code=1, failure=f"{type(exc).__name__}: {exc}")
        raise
    finally:
        status["ended_at"] = datetime.now(timezone.utc).isoformat()
        write_json(run_root / "status.json", status)


if __name__ == "__main__":
    main()
