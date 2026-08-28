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
        "TORCH_HOME": root / "cache/torch",
        "TMPDIR": root / "tmp",
    }
    for key, value in values.items():
        value.mkdir(parents=True, exist_ok=True)
        os.environ[key] = str(value)
