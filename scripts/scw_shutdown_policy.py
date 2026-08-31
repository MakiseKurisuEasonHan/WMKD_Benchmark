"""Explicit, reversible shutdown policy for WMKD SCW orchestrators."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Mapping

ENV_NAME = "WMKD_AUTO_SHUTDOWN_ENABLED"


def auto_shutdown_enabled(env: Mapping[str, str] | None = None) -> bool:
    value = (env or os.environ).get(ENV_NAME, "false").strip().lower()
    if value not in {"true", "false"}:
        raise ValueError(f"{ENV_NAME} must be true or false")
    return value == "true"


def apply_shutdown_policy(status: dict, run_root: str | Path, env: Mapping[str, str] | None = None):
    """Update terminal status and return an optional command; never execute it."""
    enabled = auto_shutdown_enabled(env)
    status.update(
        auto_shutdown_enabled=enabled,
        shutdown_method="/usr/bin/shutdown" if enabled else "SHUTDOWN_REQUIRED_MANUAL",
        shutdown_requested=enabled,
        shutdown_command_issued=enabled,
        shutdown_confirmed=False,
    )
    marker = Path(run_root) / "SHUTDOWN_REQUIRED_MANUAL"
    if enabled:
        marker.unlink(missing_ok=True)
        return ["/bin/bash", "/usr/bin/shutdown"]
    marker.write_text("AUTO_SHUTDOWN_ENABLED=false\nSHUTDOWN_REQUIRED_MANUAL\n", encoding="utf-8")
    return None
