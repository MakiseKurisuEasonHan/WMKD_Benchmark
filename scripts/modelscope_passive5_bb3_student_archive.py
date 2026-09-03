#!/usr/bin/env python3
"""Archive the canonical Passive-5 Shared Bb3 Student with Ba's audited machinery."""
from pathlib import Path

import modelscope_passive5_ba_student_archive as archive


archive.ARCHIVE_SLUG = "passive5_shared_bb3"
archive.EXPERIMENT_LABEL = "Bb3"
archive.OBJECT_SLUG = "canonical_passive5_shared_bb3_final_student"
archive.SCHEMA_VERSION = "wmkd.modelscope-passive5-shared-bb3-student.v1"
archive.EVALUATION_RUN_ID = "passive5_shared_bb3_20260903_164929"
archive.REPO_NAME = "Llama-3.2-WMKD-Passive5-Shared-Bb3-Student"
archive.REPO_ID = f"{archive.NAMESPACE}/{archive.REPO_NAME}"
archive.SOURCE = Path("/root/autodl-tmp/WMKD_Benchmark_data/runs/passive5_shared_bb3/passive5_shared_bb3_20260903_164929/student/final_model")
archive.SOURCE_MANIFEST = Path("/root/autodl-tmp/WMKD_Benchmark/results/passive5_shared_bb3/student_manifest.json")
archive.TRAINING_SUMMARY = Path("/root/autodl-tmp/WMKD_Benchmark/results/passive5_shared_bb3/training_summary.json")
archive.FULL_LOG = Path("/root/autodl-tmp/WMKD_Benchmark/results/passive5_shared_bb3/full_experiment_log.json")


if __name__ == "__main__":
    archive.main()
