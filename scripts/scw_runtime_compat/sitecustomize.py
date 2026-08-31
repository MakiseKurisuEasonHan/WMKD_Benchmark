"""Process-level SCW runtime compatibility and non-scientific telemetry.

This module is loaded only when the WMKD SCW runner prepends this directory to
``PYTHONPATH``.  It does not modify the pinned official source tree.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path


_MIRROR = os.environ.get("WMKD_SCW_HF_MIRROR", "").rstrip("/")
_UPSTREAM = "https://huggingface.co"
_REVISIONS = {
    "OpenLLM-France/Lucie-Training-Dataset": "8d50ff7cfce1a2db7cc5a1ef37d73f5f455f8ad1",
    "vicgalle/alpaca-gpt4": "f7e3ded725cb81e8e564e32feb12860f376f2b51",
    "Skylion007/openwebtext": "79d93d786212f7344586290adb811d4ae6a1762c",
    "jpacifico/French-Alpaca-dataset-Instruct-55K": "c13216a7a935baf62fb81efc56eed1739b222d2f",
}


def _rewrite(value: str) -> str:
    if _MIRROR:
        return value.replace(_UPSTREAM + "/", _MIRROR + "/")
    return value


if _MIRROR:
    import requests

    _request = requests.sessions.Session.request

    def _mirror_request(self, method, url, *args, **kwargs):
        response = _request(self, method, _rewrite(str(url)), *args, **kwargs)
        for key in ("location", "link"):
            if key in response.headers:
                response.headers[key] = _rewrite(response.headers[key])
        body = getattr(response, "_content", b"")
        if body and _UPSTREAM.encode() in body:
            response._content = body.replace(_UPSTREAM.encode(), _MIRROR.encode())
        return response

    requests.sessions.Session.request = _mirror_request


try:
    import datasets

    _load_dataset = datasets.load_dataset

    def _pinned_load_dataset(path, *args, **kwargs):
        if path in _REVISIONS:
            requested = kwargs.setdefault("revision", _REVISIONS[path])
            if requested != _REVISIONS[path]:
                raise RuntimeError(f"SCW dataset revision mismatch for {path}: {requested}")
        return _load_dataset(path, *args, **kwargs)

    datasets.load_dataset = _pinned_load_dataset
except ImportError:
    pass


_telemetry_path = os.environ.get("WMKD_SCW_TELEMETRY")
if _telemetry_path:
    import psutil
    import torch
    from transformers import Trainer, TrainerCallback

    _path = Path(_telemetry_path)
    _path.parent.mkdir(parents=True, exist_ok=True)
    _microbatch_started = None
    _original_training_step = Trainer.training_step

    def _emit(event: dict) -> None:
        event["monotonic_seconds"] = time.monotonic()
        event["cpu_rss_bytes"] = psutil.Process().memory_info().rss
        if torch.cuda.is_available():
            event["cuda_allocated_bytes"] = torch.cuda.memory_allocated()
            event["cuda_reserved_bytes"] = torch.cuda.memory_reserved()
            event["cuda_max_allocated_bytes"] = torch.cuda.max_memory_allocated()
            event["cuda_max_reserved_bytes"] = torch.cuda.max_memory_reserved()
        with _path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, sort_keys=True) + "\n")

    def _timed_training_step(self, model, inputs, *args, **kwargs):
        started = time.monotonic()
        labels = inputs.get("labels")
        label_counts = {}
        if labels is not None:
            values, counts = torch.unique(labels.detach().cpu(), return_counts=True)
            label_counts = {str(int(v)): int(c) for v, c in zip(values, counts)}
        output = _original_training_step(self, model, inputs, *args, **kwargs)
        _emit({
            "event": "microbatch_end",
            "duration_seconds": time.monotonic() - started,
            "loss_label_counts": label_counts,
            "autocast_enabled": torch.is_autocast_enabled(),
            "autocast_gpu_dtype": str(torch.get_autocast_dtype("cuda")),
        })
        return output

    Trainer.training_step = _timed_training_step

    _original_create_optimizer = Trainer.create_optimizer

    def _create_optimizer_with_numeric_lr_guard(self):
        optimizer = _original_create_optimizer(self)
        converted = []
        for index, group in enumerate(optimizer.param_groups):
            value = group.get("lr")
            if isinstance(value, str):
                parsed = float(value)
                if parsed != float(self.args.learning_rate):
                    raise RuntimeError(
                        f"optimizer group {index} LR {value!r} does not match configured LR {self.args.learning_rate!r}"
                    )
                group["lr"] = parsed
                converted.append(index)
            elif not isinstance(value, (float, int)):
                raise RuntimeError(f"optimizer group {index} has unsupported LR type {type(value).__name__}")
        if converted:
            _emit({
                "event": "optimizer_lr_type_compatibility",
                "converted_group_indices": converted,
                "configured_learning_rate": float(self.args.learning_rate),
            })
        return optimizer

    Trainer.create_optimizer = _create_optimizer_with_numeric_lr_guard

    class _TelemetryCallback(TrainerCallback):
        def on_train_begin(self, args, state, control, model=None, optimizer=None, **kwargs):
            torch.cuda.reset_peak_memory_stats()
            dtypes = {}
            for parameter in model.parameters():
                key = str(parameter.dtype)
                dtypes[key] = dtypes.get(key, 0) + parameter.numel()
            _emit({
                "event": "train_begin",
                "optimizer_class": type(optimizer).__name__,
                "parameter_dtype_counts": dtypes,
                "trainer_bf16": bool(args.bf16),
                "trainer_fp16": bool(args.fp16),
                "gradient_checkpointing": bool(args.gradient_checkpointing),
                "pythonhashseed": os.environ.get("PYTHONHASHSEED"),
            })

        def on_step_begin(self, args, state, control, **kwargs):
            _emit({"event": "optimizer_step_begin", "step": int(state.global_step + 1)})

        def on_step_end(self, args, state, control, **kwargs):
            _emit({"event": "optimizer_step_end", "step": int(state.global_step)})

        def on_train_end(self, args, state, control, **kwargs):
            _emit({"event": "train_end", "step": int(state.global_step)})

    _original_init = Trainer.__init__

    def _trainer_init(self, *args, **kwargs):
        _original_init(self, *args, **kwargs)
        self.add_callback(_TelemetryCallback())
        recorded = {"done": False}

        def _forward_dtype_hook(_module, _inputs, output):
            if recorded["done"]:
                return
            recorded["done"] = True
            logits = getattr(output, "logits", None)
            _emit({"event": "first_forward", "logits_dtype": str(getattr(logits, "dtype", None))})

        self.model.register_forward_hook(_forward_dtype_hook)

    Trainer.__init__ = _trainer_init

    if os.environ.get("WMKD_SCW_SPEED_TEST") == "1":
        def _skip_speed_test_model_save(self, *args, **kwargs):
            _emit({"event": "speed_test_model_save_skipped"})

        Trainer.save_model = _skip_speed_test_model_save
