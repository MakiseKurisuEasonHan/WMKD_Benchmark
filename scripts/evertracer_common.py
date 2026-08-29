#!/usr/bin/env python3
"""Shared, dependency-light helpers for WMKD EverTracer Experiment A."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import random
from typing import Any

def load_config(path: str | Path) -> dict[str, Any]:
    import yaml
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if data["project"] != "WMKD_Benchmark" or data["method"] != "EverTracer" or data["experiment"] != "A":
        raise ValueError("not an EverTracer Experiment A config")
    return data


def write_json(path: str | Path, data: Any) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temp = target.with_suffix(target.suffix + ".tmp")
    temp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temp.replace(target)


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_split_indices(length: int, seed: int, counts: tuple[int, int, int]) -> dict[str, list[int]]:
    if sum(counts) > length:
        raise ValueError("requested split is larger than dataset")
    indices = list(range(length))
    random.Random(seed).shuffle(indices)
    dtr, dref, dunseen = counts
    result = {
        "dtr": indices[:dtr],
        "dref": indices[dtr:dtr + dref],
        "dunseen": indices[dtr + dref:dtr + dref + dunseen],
    }
    sets = [set(values) for values in result.values()]
    if any(sets[i] & sets[j] for i in range(3) for j in range(i + 1, 3)):
        raise AssertionError("split overlap")
    return result


def empirical_fsr(member_scores: list[float], nonmember_scores: list[float], fpr_limit: float) -> dict[str, float]:
    """Maximum attainable TPR among thresholds whose empirical FPR is <= limit."""
    members = [float(x) for x in member_scores]
    nonmembers = [float(x) for x in nonmember_scores]
    if not members or not nonmembers:
        raise ValueError("member and nonmember score sets must be non-empty")
    thresholds = [float("inf"), *sorted(set(members + nonmembers), reverse=True)]
    eligible = []
    for threshold in thresholds:
        tpr = sum(score >= threshold for score in members) / len(members)
        fpr = sum(score >= threshold for score in nonmembers) / len(nonmembers)
        if fpr <= fpr_limit + 1e-12:
            eligible.append((tpr, threshold, fpr))
    # Prefer the lowest threshold among equally optimal TPR values.
    best_tpr = max(row[0] for row in eligible)
    tpr, threshold, fpr = min((row for row in eligible if row[0] == best_tpr), key=lambda row: row[1])
    wins = sum(m > n for m in members for n in nonmembers)
    ties = sum(m == n for m in members for n in nonmembers)
    auc = (wins + 0.5 * ties) / (len(members) * len(nonmembers))
    return {
        "auc": float(auc), "fsr": float(tpr), "threshold": float(threshold),
        "fpr": float(fpr), "tpr": float(tpr),
        "positive_count": len(members), "negative_count": len(nonmembers),
    }


def configure_cache(data_root: str | Path) -> None:
    root = Path(data_root)
    values = {
        "HF_HOME": root / "cache/huggingface",
        "HF_HUB_CACHE": root / "cache/huggingface/hub",
        "HF_DATASETS_CACHE": root / "cache/huggingface/datasets",
        "TORCH_HOME": root / "cache/torch",
        "TMPDIR": root / "tmp",
    }
    for key, value in values.items():
        value.mkdir(parents=True, exist_ok=True)
        os.environ[key] = str(value)


def corrected_detector_metrics(scores: list[dict[str, Any]], fpr_limit: float) -> dict[str, Any]:
    """Aggregate saved EverTracer scores using official and equivalent member directions."""
    members = [float(row["calibrated_score"]) for row in scores if row["subset"] == "dtr"]
    nonmembers = [float(row["calibrated_score"]) for row in scores if row["subset"] == "dunseen"]
    if not members or not nonmembers:
        raise ValueError("saved scores must contain both dtr members and dunseen non-members")
    member_metrics = empirical_fsr([-score for score in members], [-score for score in nonmembers], fpr_limit)
    official_auc = (
        sum(nonmember > member for nonmember in nonmembers for member in members)
        + 0.5 * sum(nonmember == member for nonmember in nonmembers for member in members)
    ) / (len(members) * len(nonmembers))
    if abs(official_auc - member_metrics["auc"]) > 1e-12:
        raise AssertionError("official and member-oriented AUC must be equivalent")
    return {
        "official_definition": {
            "member_label": 0, "nonmember_label": 1,
            "score": "C = suspect_variation - reference_variation",
            "positive_threshold": "C >= gamma predicts non-member",
        },
        "official_auc_nonmember_positive": float(official_auc),
        "member_oriented_definition": {
            "member_label": 1, "nonmember_label": 0,
            "score": "member_score = -C",
            "positive_threshold": "member_score >= gamma predicts member",
            "note": "Equivalent reparameterization of the official detector for benchmark readability.",
        },
        "member_oriented_auc": member_metrics["auc"],
        "member_oriented_tpr_at_fpr_limit": member_metrics["tpr"],
        "member_oriented_fpr": member_metrics["fpr"],
        "member_oriented_threshold": member_metrics["threshold"],
        "fpr_limit": float(fpr_limit),
        "member_count": len(members), "nonmember_count": len(nonmembers),
    }


def validate_utility_local_artifacts(utility: dict[str, Any]) -> dict[str, Any]:
    """Fail fast unless every pinned utility snapshot and prepared dataset is local."""
    result = {}
    for name, spec in utility["datasets"].items():
        snapshot, prepared = Path(spec["snapshot"]), Path(spec["prepared"])
        if snapshot.name != str(spec["revision"]):
            raise ValueError(f"{name} snapshot revision mismatch")
        if not snapshot.is_dir() or not any(snapshot.rglob("*.parquet")):
            raise FileNotFoundError(f"{name} pinned snapshot is missing or incomplete: {snapshot}")
        if not prepared.is_dir() or not (prepared / "dataset_info.json").is_file() or not any(prepared.glob("*.arrow")):
            raise FileNotFoundError(f"{name} prepared offline dataset is missing or incomplete: {prepared}")
        result[name] = {"id": spec["id"], "config": spec["config"], "revision": spec["revision"], "snapshot": str(snapshot), "prepared": str(prepared)}
    return result


def resolve_t5_local_snapshot(verification: dict[str, Any]) -> Path:
    """Resolve and validate the pinned T5 snapshot without any Hub fallback."""
    revision = str(verification["t5_revision"])
    snapshot = Path(verification["t5_local_path"])
    if snapshot.name != revision:
        raise ValueError(f"T5 local snapshot revision mismatch: {snapshot.name} != {revision}")
    required = (
        "config.json", "generation_config.json", "tokenizer.json",
        "spiece.model", "model.safetensors",
    )
    missing = [name for name in required if not (snapshot / name).is_file()]
    if missing:
        raise FileNotFoundError(f"T5 local snapshot incomplete at {snapshot}: missing {missing}")
    expected_sha = verification.get("t5_model_sha256")
    if expected_sha and sha256_file(snapshot / "model.safetensors") != expected_sha:
        raise ValueError(f"T5 model.safetensors SHA-256 mismatch at {snapshot}")
    return snapshot
