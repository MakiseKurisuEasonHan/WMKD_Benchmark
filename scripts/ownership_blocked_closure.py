"""Create an evidence-backed terminal BLOCKED closure for an ownership method."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path


METHODS = {
    "reef": {
        "name": "REEF", "commit": "48329f6f3695a8aea33975832159e7ce44ad73f9",
        "blockers": [
            "formal_authorized=false in the fixed REEF Experiment A config",
            "the exact 200 TruthfulQA probe identities and content hashes are not frozen",
            "the unrelated-model negative panel is not frozen",
            "the controlling threshold/calibration rule is not frozen",
        ],
    },
    "awm": {
        "name": "AWM", "commit": None,
        "blockers": [
            "formal_authorized=false in the fixed AWM Experiment A config",
            "the exact official layer aggregation is not frozen",
            "the unrelated-model negative panel is not frozen",
            "the controlling threshold/calibration rule is not frozen",
        ],
    },
    "huref": {
        "name": "HuRef", "commit": None,
        "blockers": [
            "formal_authorized=false in the fixed HuRef Experiment A config",
            "the official-semantics canonical sorted-token list and its hash are not frozen in the formal config",
            "the unrelated-model negative panel and controlling calibration are not frozen",
        ],
    },
    "zeroprint": {
        "name": "ZeroPrint", "commit": None,
        "blockers": [
            "formal_authorized=false in the fixed ZeroPrint Experiment A config",
            "the exact HumanEval rows/content hash are not frozen",
            "the official continuation and perturbation implementation is not frozen",
            "the official-budget generation-speed gate is not recorded as passed",
            "the negative panel and controlling calibration are not frozen",
        ],
    },
}

REVISION = "0cb88a4f764b7a12671c53f0838cd831a0843b95"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def atomic_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(value, encoding="utf-8")
    os.replace(temporary, path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--method", choices=sorted(METHODS), required=True)
    args = parser.parse_args()
    method = METHODS[args.method]
    config = args.project / "configs" / "watermark" / f"{args.method}_experiment_a.yaml"
    smoke = args.project / "results" / args.method / "smoke" / f"{args.method}_smoke_20260901.json"
    config_text = config.read_text(encoding="utf-8")
    if "formal_authorized: false" not in config_text or "PREPARATION_SMOKE_ONLY" not in config_text:
        raise RuntimeError("fixed config no longer proves formal authorization is absent")
    smoke_value = json.loads(smoke.read_text(encoding="utf-8"))
    if smoke_value.get("status") != "COMPLETED" or smoke_value.get("smoke_only") is not True:
        raise RuntimeError("bounded smoke evidence is missing or not explicitly smoke-only")
    out = args.project / "results" / args.method / "experiment_a"
    blocker = {
        "type": "UNFROZEN_SCIENTIFIC_PROTOCOL_BLOCKER",
        "formal_run_started": False,
        "scientific_config_modified": False,
        "reasons": method["blockers"],
        "policy": "No scientific semantics were invented, tuned, or inferred. Formal A was not launched.",
    }
    common = {
        "schema_version": "wmkd.ownership-experiment-a-closure.v1", "method": args.method,
        "method_display_name": method["name"], "experiment": "A", "status": "BLOCKED", "terminal": True,
        "official_commit": method["commit"], "canonical_revision": REVISION, "model_modified": False,
        "formal_result": None, "preferred_fingerprint": False, "ba_ready": False,
        "missing_values_policy": "unavailable_not_reconstructed", "blocker": blocker,
    }
    atomic_json(out / "summary.json", {**common, "artifact_type": "none_formal_not_started",
                                        "bounded_smoke_status": "COMPLETED_COMPATIBILITY_ONLY"})
    atomic_json(out / "detector_results.json", {**common, "detector_status": "NOT_CALIBRATED",
                                                 "native_metric": None, "threshold": None,
                                                 "positive_evidence": None, "negative_baseline": None})
    provenance = {**common, "config": {"path": str(config.relative_to(args.project)), "sha256": sha256(config)},
                  "smoke": {"path": str(smoke.relative_to(args.project)), "sha256": sha256(smoke)},
                  "transport_adaptations": [], "teacher_checkpoint_created": False, "ba_started": False}
    atomic_json(out / "provenance_manifest.json", provenance)
    artifact = {**common, "artifact_type": "no_formal_artifact", "formal_artifacts": [],
                "preserved_smoke_artifact": provenance["smoke"]}
    atomic_json(out / "artifact_manifest.json", artifact)
    full = {**common, "role": "preferred_fingerprint", "scientific_status": "BLOCKED",
            "identity": {"official_commit": method["commit"], "canonical_revision": REVISION},
            "wmkd_config": {"path": str(config.relative_to(args.project)), "sha256": sha256(config)},
            "runtime": {"formal_started": False}, "fingerprint_extraction": {},
            "detector": {"status": "NOT_CALIBRATED"}, "raw_artifacts": [provenance["smoke"]],
            "failures": [blocker], "continuations": [], "utility_applicability": "not_applicable_passive_fingerprint",
            "bounded_conclusion": f"{method['name']} formal reproduction not judged because the fixed protocol is incomplete.",
            "closure_completed_at": now(), "ba_started": False}
    atomic_json(out / "full_experiment_log.json", full)
    report = f"""# {method['name']} Experiment A terminal closure report

## Outcome

**Terminal status: BLOCKED. Formal scientific reproduction was not started or judged.**

The bounded smoke remains compatibility/resource evidence only. It is not positive-vs-negative detector evidence and was not promoted into a formal result.

## Fixed-protocol blockers

""" + "\n".join(f"- {reason}" for reason in method["blockers"]) + """

No scientific configuration, negative identity, threshold, or detector semantics were invented. No model weights were modified, no preferred fingerprint was selected, and Ba remains NOT STARTED.
"""
    atomic_text(args.project / "docs" / "reproduction_reports" / f"{args.method}_experiment_a_report.md", report)
    index_path = args.project / "results" / "experiment_full_logs_index.json"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    objects = [row for row in index["objects"] if not (row.get("method") == method["name"] and row.get("experiment") == "A")]
    full_path = out / "full_experiment_log.json"
    objects.append({"method": method["name"], "role": "preferred_fingerprint", "experiment": "A", "run_id": None,
                    "full_log_path": str(full_path.relative_to(args.project)).replace("\\", "/"),
                    "full_log_sha256": sha256(full_path), "final_model_manifest": None, "modelscope_repo": None,
                    "scientific_status": "BLOCKED", "watermark_evaluation_available": False,
                    "utility_available": False, "checkpoint_localization_support": False, "telemetry_records": 0,
                    "artifact_type": "no_formal_artifact", "model_modified": False, "preferred_fingerprint": "no"})
    index.update(generated_at=now(), object_count=len(objects), objects=objects)
    atomic_json(index_path, index)


if __name__ == "__main__":
    main()
