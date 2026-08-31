import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scw_materialized_stream import (  # noqa: E402
    audit_materialized, build_manifest, canonical_json, iter_materialized_records,
    materialize_records, training_length_contract, write_manifest,
)


def fixture(seed):
    # Synthetic post-official-interleave records: duplicates are intentional.
    schedule = [0, 0, 2, 1, 0, 2] if seed == 42 else [1, 0, 2, 0, 1, 0]
    for index, label in enumerate(schedule):
        token = 100 + ((index + seed) % 3)
        yield {"input_ids": [token, token + 1], "attention_mask": [1, 1], "labels": label}


class MaterializedStreamTests(unittest.TestCase):
    def test_detached_full_runner_and_shutdown_contract(self):
        launcher = (ROOT / "scripts/run_scw_materialized_full_experiment_a.sh").read_text(encoding="utf-8")
        pipeline = (ROOT / "scripts/scw_materialized_full_experiment_a.py").read_text(encoding="utf-8")
        self.assertIn("setsid nohup", launcher)
        self.assertIn('"DETERMINISTIC_FINITE_STREAM_BUILD"', pipeline)
        self.assertIn("DETERMINISTIC_FINITE_STREAM_SAMPLING_ADAPTATION", pipeline)
        self.assertIn('"LOCAL_MATERIALIZED_GATE"', pipeline)
        self.assertIn('"FORMAL_TRAINING"', pipeline)
        self.assertIn("apply_shutdown_policy", pipeline)
        self.assertIn("WMKD_AUTO_SHUTDOWN_ENABLED=false", launcher)
        policy = (ROOT / "scripts/scw_shutdown_policy.py").read_text(encoding="utf-8")
        self.assertIn("shutdown_confirmed=False", policy)
        self.assertNotIn("os._exit", pipeline)
        trainer = (ROOT / "scripts/scw_train_materialized.py").read_text(encoding="utf-8")
        self.assertIn('expected_optimizer_steps = 4 if os.environ.get("WMKD_SCW_SPEED_TEST") == "1"', trainer)

    def test_materializer_mirror_wrapper_blocks_upstream_leak(self):
        pipeline = (ROOT / "scripts/scw_materialized_full_experiment_a.py").read_text(encoding="utf-8")
        compat = (ROOT / "scripts/scw_runtime_compat/sitecustomize.py").read_text(encoding="utf-8")
        validator = (ROOT / "scripts/scw_hf_metadata_validate.py").read_text(encoding="utf-8")
        self.assertIn('"WMKD_SCW_HF_MIRROR":env["HF_ENDPOINT"]', pipeline)
        self.assertIn('"WMKD_SCW_NETWORK_AUDIT":str(mat/"network_requests.jsonl")', pipeline)
        self.assertIn("HF mirror leak blocked before request", compat)
        self.assertIn('hostname=="huggingface.co"', validator)
        self.assertIn('"WMKD_SCW_PARQUET_CACHE":str(D/"cache/scw/parquet_prefetch")', pipeline)
        self.assertIn("ensure_cached", compat)
        self.assertIn('content_range = f"bytes {start}-{end}/{total_size}"', compat)
        self.assertIn("range_value and cached is None", compat)

    def test_deterministic_finite_builder_contract(self):
        builder = (ROOT / "scripts/scw_build_deterministic_finite_stream.py").read_text(encoding="utf-8")
        self.assertIn("np.random.Generator(np.random.PCG64(seed))", builder)
        self.assertIn("PROBABILITIES = (0.6, 0.2, 0.2)", builder)
        self.assertIn("repository-path-order", builder)
        self.assertIn("official_preprocess", builder)
        self.assertIn("no deduplication; no replacement; no synthetic duplication", builder)
        self.assertIn("not byte-identical to the official online streaming/shuffle realization", builder)
        self.assertIn('AutoTokenizer.from_pretrained(runtime["base_model"]', builder)

    def test_auto_shutdown_is_disabled_for_all_terminal_states(self):
        from scw_shutdown_policy import apply_shutdown_policy
        with tempfile.TemporaryDirectory() as tmp:
            for terminal_state in ("SUCCESS", "FAILED", "BLOCKED"):
                root = Path(tmp) / terminal_state
                root.mkdir()
                status = {"state": terminal_state}
                command = apply_shutdown_policy(status, root, {"WMKD_AUTO_SHUTDOWN_ENABLED": "false"})
                self.assertIsNone(command)
                self.assertFalse(status["auto_shutdown_enabled"])
                self.assertFalse(status["shutdown_requested"])
                self.assertFalse(status["shutdown_command_issued"])
                self.assertEqual(status["shutdown_method"], "SHUTDOWN_REQUIRED_MANUAL")
                self.assertTrue((root / "SHUTDOWN_REQUIRED_MANUAL").is_file())

    def test_resumable_prefetch_contract(self):
        prefetch = (ROOT / "scripts/scw_resumable_prefetch.py").read_text(encoding="utf-8")
        self.assertIn('"--continue-at", "-"', prefetch)
        self.assertIn('filename + ".part"', prefetch)
        self.assertIn("download size mismatch", prefetch)
        self.assertIn("_parquet_check", prefetch)
        self.assertIn('"sha256": digest', prefetch)
        materializer = (ROOT / "scripts/scw_materialize_official.py").read_text(encoding="utf-8")
        self.assertIn("--tiny-validation-records", materializer)
        self.assertIn("TINY_VALIDATION_PASS", materializer)
        local_validation = (ROOT / "scripts/scw_local_prefetch_tiny_validate.py").read_text(encoding="utf-8")
        self.assertIn("tokenize_function", local_validation)
        self.assertIn("group_texts", local_validation)
        self.assertIn('"LucieFr": (0, "watermark")', local_validation)
        self.assertIn('"AlpacaGPT4": (1, "anti-watermark-tv")', local_validation)
        self.assertIn('"OpenWebText": (2, "anti-watermark-tv")', local_validation)

    def materialize(self, directory, seed=42, name="records.jsonl"):
        records = Path(directory) / name
        stats = materialize_records(fixture(seed), records, 6)
        contract = training_length_contract(3, 1, 2)
        provenance = {
            "official_repo_commit": "15bc1929569357130f2dbc0b09f91bbf4f4bd947",
            "creation_code_version": "test-version", "model": {"id": "fixture", "revision": "fixture"},
            "datasets": ["LucieFr", "AlpacaGPT4", "OpenWebText"], "pythonhashseed": seed,
            "explicit_rng_seeds": {"interleave": seed}, "configured_probabilities": [0.6, 0.2, 0.2],
            "stopping_strategy": "all_exhausted",
        }
        manifest = build_manifest(materialization=stats, contract=contract, provenance=provenance, creation_timestamp="2026-08-31T00:00:00+00:00")
        return records, manifest

    def test_same_seed_same_stream_and_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            a, ma = self.materialize(tmp, name="a.jsonl")
            b, mb = self.materialize(tmp, name="b.jsonl")
            self.assertEqual(a.read_bytes(), b.read_bytes())
            self.assertEqual(canonical_json(ma), canonical_json(mb))

    def test_different_seed_changes_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, first = self.materialize(tmp, 42, "a.jsonl")
            _, second = self.materialize(tmp, 43, "b.jsonl")
            self.assertNotEqual(first["canonical_content_digest"], second["canonical_content_digest"])

    def test_labels_losses_order_proportions_and_duplicates_are_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            records, manifest = self.materialize(tmp)
            rows = [json.loads(line) for line in records.read_text(encoding="utf-8").splitlines()]
            self.assertEqual([r["global_sample_index"] for r in rows], list(range(6)))
            self.assertEqual([r["label_id"] for r in rows], [0, 0, 2, 1, 0, 2])
            self.assertEqual(rows[0]["loss_type"], "watermark")
            self.assertTrue(all(rows[i]["loss_type"] == "anti-watermark-tv" for i in (2, 3, 5)))
            self.assertEqual(manifest["source_counts"], {"LucieFr": 3, "OpenWebText": 2, "AlpacaGPT4": 1})
            self.assertEqual(manifest["configured_probabilities"], [0.6, 0.2, 0.2])
            self.assertEqual(manifest["observed_source_proportions"]["LucieFr"], 0.5)
            self.assertEqual(len(rows), 6)  # no drop and no dedup

    def test_hashes_audit_and_local_loader_reproduce_exact_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            records, manifest = self.materialize(tmp)
            manifest_path = Path(tmp) / "manifest.json"
            write_manifest(manifest_path, manifest)
            self.assertEqual(audit_materialized(records, manifest)["status"], "PASS")
            loaded = list(iter_materialized_records(records, manifest))
            self.assertEqual([row["labels"] for row in loaded], [0, 0, 2, 1, 0, 2])
            damaged = records.read_text(encoding="utf-8").replace('"label_id":0', '"label_id":1', 1)
            records.write_text(damaged, encoding="utf-8")
            self.assertEqual(audit_materialized(records, manifest)["status"], "FAIL")

    def test_training_length_contract_and_short_stream_fail_closed(self):
        self.assertEqual(training_length_contract(2500, 16, 4)["expected_consumed_examples"], 160000)
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(RuntimeError, "exhausted"):
                materialize_records(iter([{"input_ids": [1], "attention_mask": [1], "labels": 0}]), Path(tmp) / "short.jsonl", 2)


if __name__ == "__main__":
    unittest.main()
