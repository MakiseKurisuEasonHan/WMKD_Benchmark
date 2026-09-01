"""Explicit, reversible shutdown policy for WMKD SCW orchestrators."""
from __future__ import annotations

import os
import json
from pathlib import Path
from typing import Mapping

ENV_NAME = "WMKD_AUTO_SHUTDOWN_ENABLED"
PROJECT_POLICY = Path(__file__).resolve().parents[1] / "configs/runtime/auto_shutdown.json"


def project_auto_shutdown_enabled(policy_path: str | Path = PROJECT_POLICY) -> bool:
    """Return the project-wide kill switch; missing policy fails safely closed."""
    path = Path(policy_path)
    if not path.is_file():
        return False
    value = json.loads(path.read_text(encoding="utf-8")).get("auto_shutdown_enabled")
    if not isinstance(value, bool):
        raise ValueError("auto_shutdown_enabled must be a JSON boolean")
    return value


def auto_shutdown_enabled(env: Mapping[str, str] | None = None, policy_path: str | Path = PROJECT_POLICY) -> bool:
    value = (env or os.environ).get(ENV_NAME, "false").strip().lower()
    if value not in {"true", "false"}:
        raise ValueError(f"{ENV_NAME} must be true or false")
    return project_auto_shutdown_enabled(policy_path) and value == "true"


def apply_shutdown_policy(
    status: dict,
    run_root: str | Path,
    env: Mapping[str, str] | None = None,
    policy_path: str | Path = PROJECT_POLICY,
):
    """Update terminal status and return an optional command; never execute it."""
    enabled = auto_shutdown_enabled(env, policy_path)
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
