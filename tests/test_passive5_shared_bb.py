import copy
import json
import tempfile
import unittest
from pathlib import Path

from scripts.passive5_shared_bb import (
    adapt_student_dataset, audit, audit_journal, atomic_jsonl, build_pair, dynamic_budget, file_sha256,
    freeze, generation_identity, load_attempts, load_config, planning_full_log, quality_flags, read_jsonl,
    records_sha256, run_records, text_sha256, update_global_index, validate_full_log,
    validate_source, validate_training_parity,
)
from scripts.passive5_shared_bb_orchestrator import build_plan
from scripts.passive5_shared_bb_paraphrase_runner import sanitize_boundary_tags

ROOT = Path(__file__).parents[1]


def rows(count=3):
    return [{"sample_id": f"qa_{i}", "instruction": f"Question {i}?", "input": "",
             "teacher_raw_answer": f"Paris is the capital of France number {i}."} for i in range(count)]


def config_for(source, path):
    cfg = json.loads((ROOT / "configs/distillation/passive5_shared_bb.json").read_text(encoding="utf-8"))
    cfg["source_dataset"].update(record_count=len(source), dataset_sha256=records_sha256(source),
        sample_ids_sha256=records_sha256([{"sample_id": row["sample_id"]} for row in source]),
        frozen_jsonl_sha256=file_sha256(path))
    cfg["quality"]["human_audit_sample_count"] = 2
    return cfg


def good_answer(row, attempt, budget):
    answer = f"France has Paris as its principal city and national capital, item {row['sample_id']}."
    return answer, len(answer.split()), "stop", None


class Passive5SharedBbTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.root = Path(self.temp.name)
        self.source = rows(); self.source_path = self.root / "source.jsonl"; atomic_jsonl(self.source_path, self.source)
        self.config = config_for(self.source, self.source_path)

    def tearDown(self): self.temp.cleanup()

    def test_source_validation(self): self.assertEqual(validate_source(self.source, self.config, self.source_path)["status"], "PASS")
    def test_source_hash_mismatch(self):
        bad=copy.deepcopy(self.source);bad[0]["teacher_raw_answer"]="changed"
        with self.assertRaisesRegex(ValueError,"HASH_MISMATCH"): validate_source(bad,self.config)
    def test_duplicate_source_id(self):
        bad=copy.deepcopy(self.source);bad[1]["sample_id"]=bad[0]["sample_id"]
        with self.assertRaisesRegex(ValueError,"DUPLICATE"): validate_source(bad,self.config)
    def test_dynamic_budget_min(self): self.assertEqual(dynamic_budget(1,self.config["paraphrase"]["dynamic_max_new_tokens"]),64)
    def test_dynamic_budget_cap(self): self.assertEqual(dynamic_budget(9999,self.config["paraphrase"]["dynamic_max_new_tokens"]),1536)
    def test_generation_identity_stable(self): self.assertEqual(generation_identity(self.config),generation_identity(copy.deepcopy(self.config)))
    def test_exact_copy_detection(self):
        result=quality_flags("same words","same words","stop",self.config)
        self.assertIn("exact_copy",result["diagnostics"]);self.assertTrue(result["pass"])
    def test_processing_modes_distinguish_qwen_identity_and_paraphrase(self):
        identity=build_pair(self.source[0],self.source[0]["teacher_raw_answer"],8,8,1,"stop",None,self.config)
        changed=build_pair(self.source[0],"France has Paris as its capital.",8,7,1,"stop",None,self.config)
        self.assertEqual(identity["processing_mode"],"qwen_identity_output")
        self.assertEqual(changed["processing_mode"],"qwen_paraphrased")
    def test_bb3_atomic_and_qwen_modes(self):
        bb3=load_config(ROOT/"configs/distillation/passive5_shared_bb3.json")
        atomic=build_pair(self.source[0],self.source[0]["teacher_raw_answer"],1,1,1,"atomic_identity_preserved",None,bb3)
        identity=build_pair(self.source[0],self.source[0]["teacher_raw_answer"],2,2,1,"stop",None,bb3)
        self.assertEqual(atomic["processing_mode"],"atomic_identity_preserved")
        self.assertEqual(identity["processing_mode"],"qwen_identity_output")
    def test_empty_detection(self): self.assertIn("empty_output",quality_flags("answer","","error",self.config)["failures"])
    def test_truncation_detection(self): self.assertTrue(quality_flags("answer words","rewritten answer words","length",self.config)["truncated"])
    def test_diagnostic_thresholds_do_not_drop_valid_pairs(self):
        result=quality_flags("17","The value provided is 17.","stop",self.config)
        self.assertIn("length_ratio_out_of_bounds",result["diagnostics"]);self.assertTrue(result["pass"])
    def test_prompt_boundary_tag_sanitizer_is_narrow(self):
        self.assertEqual(sanitize_boundary_tags("<SOURCE_ANSWER>null</SOURCE_ANSWER>"),("null",True))
        self.assertEqual(sanitize_boundary_tags("paraphrase the answer below"),("paraphrase the answer below",False))
    def test_prompt_leakage(self): self.assertIn("prompt_leakage",quality_flags("answer","<SOURCE_ANSWER> leaked text","stop",self.config)["failures"])
    def test_instruction_echo_leakage_is_phrase_based(self):
        output="Regarding the provided response, ensure all pertinent details remain intact during rephrasing."
        result=quality_flags("tech",output,"stop",self.config)
        self.assertIn("instruction_echo_leakage",result["failures"])
        self.assertIn("ensure all pertinent details",result["instruction_echo_leakage"])
    def test_real_cont4_meta_task_output_is_rejected(self):
        output="Regarding the technical aspect, the provided response needs to incorporate distinct phrasing without altering the core information."
        result=quality_flags("tech",output,"stop",self.config)
        self.assertIn("instruction_echo_leakage",result["failures"]);self.assertTrue(result["meta_response"])
        self.assertIn("provided response",result["meta_response_evidence"]["meta_objects"])
    def test_real_cont2_meta_task_output_is_rejected(self):
        output="Regarding the provided response, ensure all pertinent details, entities, figures, assertions, limitations, and protocols remain intact during rephrasing."
        self.assertIn("instruction_echo_leakage",quality_flags("tech",output,"stop",self.config)["failures"])
    def test_normal_paraphrase_is_accepted_by_meta_validator(self):
        output="Technology is the relevant category."
        result=quality_flags("tech",output,"stop",self.config)
        self.assertNotIn("instruction_echo_leakage",result["failures"]);self.assertFalse(result["meta_response"])
    def test_instruction_echo_does_not_reject_single_generic_words(self):
        for output in ("rewrite", "paraphrase", "response", "meaning", "wording", "A rewritten response is useful.",
                       "The word paraphrase has the same meaning in this discussion."):
            self.assertNotIn("instruction_echo_leakage",quality_flags("answer",output,"stop",self.config)["failures"])
    def test_short_source_exact_copy_remains_valid(self):
        result=quality_flags("tech","tech","stop",self.config)
        self.assertTrue(result["pass"]);self.assertIn("exact_copy",result["diagnostics"])
        self.assertFalse(result["meta_response"])
    def test_instruction_phrase_preserved_when_present_in_source(self):
        phrase="The instruction asks students to compare both texts."
        self.assertNotIn("instruction_echo_leakage",quality_flags(phrase,phrase,"stop",self.config)["failures"])
    def test_control_token_leakage(self): self.assertIn("chat_control_token_leakage",quality_flags("answer","<|im_start|> rewritten answer","stop",self.config)["failures"])
    def test_retry_then_success(self):
        def generator(row,attempt,budget): return ("",0,"error","failure") if attempt==1 else good_answer(row,attempt,budget)
        progress=run_records(self.source,self.root/"attempts.jsonl",self.config,generator)
        self.assertTrue(progress["complete"]);self.assertEqual(progress["retry_count"],3)
    def test_partial_recovery_skips_success(self):
        calls=[]
        def generator(row,attempt,budget): calls.append(row["sample_id"]);return good_answer(row,attempt,budget)
        run_records(self.source,self.root/"attempts.jsonl",self.config,generator,limit=1)
        run_records(self.source,self.root/"attempts.jsonl",self.config,generator)
        self.assertEqual(calls.count("qa_0"),1)
    def test_retry_exhaustion_uses_identity_fallback(self):
        progress=run_records(self.source,self.root/"attempts.jsonl",self.config,lambda r,a,b:("rejected output",2,"stop","failed"))
        self.assertTrue(progress["complete"]);self.assertEqual(progress["identity_fallback_count"],3)
        records=read_jsonl(self.root/"attempts.jsonl");final=records[3]
        self.assertTrue(final["identity_fallback"]);self.assertEqual(final["failed_attempt_count"],3)
        self.assertEqual(final["paraphrased_answer"],self.source[0]["teacher_raw_answer"])
        self.assertEqual(final["source_answer_sha256"],final["final_answer_sha256"])
        self.assertEqual(final["fallback_reason"],"paraphrase_retry_exhausted_semantic_preservation")
        self.assertEqual(len(final["rejected_attempts"]),3)
    def test_generation_error_is_durable(self):
        run_records(self.source,self.root/"attempts.jsonl",self.config,lambda r,a,b:("",0,"error","model_error"))
        record=read_jsonl(self.root/"attempts.jsonl")[0];self.assertEqual(record["status"],"failed");self.assertEqual(record["error"],"model_error")
    def test_duplicate_attempt_fails(self):
        pair=build_pair(self.source[0],"A fully rewritten response with distinct language and adequate length.",9,10,1,"stop",None,self.config)
        atomic_jsonl(self.root/"attempts.jsonl",[pair,pair])
        with self.assertRaisesRegex(ValueError,"DUPLICATE_SAMPLE_ATTEMPT"): load_attempts(self.root/"attempts.jsonl",{r["sample_id"]:r for r in self.source})
    def test_journal_source_hash_mismatch(self):
        pair=build_pair(self.source[0],"A fully rewritten response with distinct language and adequate length.",9,10,1,"stop",None,self.config);pair["source_answer_sha256"]="0"*64
        atomic_jsonl(self.root/"attempts.jsonl",[pair])
        with self.assertRaisesRegex(ValueError,"SOURCE_HASH_MISMATCH"): load_attempts(self.root/"attempts.jsonl",{r["sample_id"]:r for r in self.source})
    def test_freeze_and_sha_stability(self):
        journal=self.root/"attempts.jsonl";run_records(self.source,journal,self.config,good_answer)
        one=freeze(self.source,journal,self.root/"one.jsonl",self.config);two=freeze(self.source,journal,self.root/"two.jsonl",self.config)
        self.assertEqual(one["paired_dataset_sha256"],two["paired_dataset_sha256"])
    def test_freeze_requires_exact_count(self):
        run_records(self.source,self.root/"attempts.jsonl",self.config,good_answer,limit=1)
        with self.assertRaisesRegex(RuntimeError,"EXACT_COUNT"): freeze(self.source,self.root/"attempts.jsonl",self.root/"out.jsonl",self.config)
    def test_freeze_output_collision(self):
        journal=self.root/"attempts.jsonl";run_records(self.source,journal,self.config,good_answer);target=self.root/"out.jsonl";target.write_text("occupied")
        with self.assertRaisesRegex(FileExistsError,"OUTPUT_COLLISION"):freeze(self.source,journal,target,self.config)
    def test_quality_audit_and_human_sample(self):
        journal=self.root/"attempts.jsonl";run_records(self.source,journal,self.config,good_answer);freeze(self.source,journal,self.root/"out.jsonl",self.config)
        result=audit(read_jsonl(self.root/"out.jsonl"),self.root/"audit",self.config)
        self.assertEqual(result["sample_count"],3);self.assertTrue((self.root/"audit/human_audit_samples.md").is_file())
    def test_audit_distinguishes_natural_exact_and_fallback(self):
        answers={"qa_0":0}
        def generator(row,attempt,budget):
            if row["sample_id"]=="qa_0": return "",0,"error","failed"
            if row["sample_id"]=="qa_1": return row["teacher_raw_answer"],8,"stop",None
            return good_answer(row,attempt,budget)
        journal=self.root/"attempts.jsonl";run_records(self.source,journal,self.config,generator)
        result=audit_journal(self.source,journal,self.root/"audit",self.config)
        self.assertEqual(result["identity_fallback_count"],1);self.assertEqual(result["natural_exact_copy_count"],1)
        self.assertEqual(result["total_identity_output_count"],2)
        self.assertEqual(result["qwen_submitted_count"],3)
    def test_identity_fallback_aggregate_gate(self):
        self.config["paraphrase"]["identity_fallback"]["full20k_max_count"]=1
        with self.assertRaisesRegex(RuntimeError,"IDENTITY_FALLBACK_AGGREGATE_GATE"):
            run_records(self.source,self.root/"attempts.jsonl",self.config,lambda r,a,b:("",0,"error","failed"))
    def test_partial_pilot_audit(self):
        journal=self.root/"attempts.jsonl";run_records(self.source,journal,self.config,good_answer,limit=1)
        result=audit_journal(self.source,journal,self.root/"pilot_audit",self.config);self.assertEqual(result["sample_count"],1);self.assertTrue(result["pilot_or_partial"])
    def test_student_adapter(self):
        journal=self.root/"attempts.jsonl";run_records(self.source,journal,self.config,good_answer);freeze(self.source,journal,self.root/"out.jsonl",self.config)
        manifest=adapt_student_dataset(read_jsonl(self.root/"out.jsonl"),self.root/"student.jsonl")
        self.assertEqual(manifest["sample_count"],3);self.assertIn("teacher_raw_answer",read_jsonl(self.root/"student.jsonl")[0])
    def test_training_parity(self):
        ba=json.loads((ROOT/"configs/distillation/passive5_shared_ba.json").read_text());self.assertEqual(validate_training_parity(ba,self.config)["status"],"PASS")
    def test_bb2_prompt_and_protocol_are_frozen_without_short_bypass(self):
        bb2=load_config(ROOT/"configs/distillation/passive5_shared_bb2.json")
        self.assertEqual(bb2["identity"],"passive5_shared_bb2")
        self.assertFalse(bb2["paraphrase"]["short_answer_preprocessing_bypass"])
        self.assertTrue(bb2["paraphrase"]["qwen_identity_preservation"])
        ba=json.loads((ROOT/"configs/distillation/passive5_shared_ba.json").read_text())
        self.assertEqual(validate_training_parity(ba,bb2)["status"],"PASS")
    def test_training_parity_mismatch(self):
        ba=json.loads((ROOT/"configs/distillation/passive5_shared_ba.json").read_text());bad=copy.deepcopy(self.config);bad["training"]["scheduler"]="linear"
        with self.assertRaisesRegex(ValueError,"PARITY_MISMATCH"):validate_training_parity(ba,bad)
    def test_wrong_student_revision(self):
        ba=json.loads((ROOT/"configs/distillation/passive5_shared_ba.json").read_text());bad=copy.deepcopy(self.config);bad["student"]["revision"]="wrong";ba["student"]["revision"]="wrong"
        with self.assertRaisesRegex(ValueError,"WRONG_STUDENT_REVISION"):validate_training_parity(ba,bad)
    def test_wrong_student_initialization(self):
        ba=json.loads((ROOT/"configs/distillation/passive5_shared_ba.json").read_text());bad=copy.deepcopy(self.config);bad["student"]["initialization"]="Ba Student"
        with self.assertRaisesRegex(ValueError,"PARITY_MISMATCH"):validate_training_parity(ba,bad)
    def test_full_log_schema(self): self.assertEqual(validate_full_log(planning_full_log(self.config))["status"],"PASS")
    def test_full_log_missing(self):
        bad=planning_full_log(self.config);del bad["detectors"]
        with self.assertRaisesRegex(ValueError,"FULL_LOG_SCHEMA_MISSING"):validate_full_log(bad)
    def test_index_rejects_planning_log(self):
        full=self.root/"full.json";full.write_text(json.dumps(planning_full_log(self.config)))
        index=self.root/"index.json";index.write_text(json.dumps({"objects":[],"object_count":0}))
        with self.assertRaisesRegex(ValueError,"COMPLETED"):update_global_index(index,full,"results/x.json",{"run_id":"x"})
    def test_index_accepts_completed_log_and_rejects_collision(self):
        value=planning_full_log(self.config);value["status"]="COMPLETED";full=self.root/"full.json";full.write_text(json.dumps(value))
        index=self.root/"index.json";index.write_text(json.dumps({"objects":[],"object_count":0}))
        update_global_index(index,full,"results/x.json",{"run_id":"x","method":"Passive-5 Shared"})
        self.assertEqual(json.loads(index.read_text())["object_count"],1)
        with self.assertRaisesRegex(ValueError,"COLLISION"):update_global_index(index,full,"results/x.json",{"run_id":"x"})
    def test_orchestrator_dry_run_and_detector_wiring(self):
        plan=build_plan(ROOT,self.root,"passive5_shared_bb_test",ROOT/"configs/distillation/passive5_shared_bb.json",True)
        self.assertEqual(plan["status"],"DRY_RUN_ONLY");self.assertEqual(len(plan["commands"]["detectors"]),4);self.assertIn("llmprint",plan["commands"]);self.assertIn("utility",plan["commands"])
    def test_existing_run_collision(self):
        (self.root/"runs/passive5_shared_bb/collision").mkdir(parents=True)
        with self.assertRaises(FileExistsError):build_plan(ROOT,self.root,"collision",ROOT/"configs/distillation/passive5_shared_bb.json",True)
    def test_unresolved_revision_blocks_formal_plan(self):
        config = json.loads((ROOT/"configs/distillation/passive5_shared_bb.json").read_text())
        config["paraphraser"]["revision"] = "REQUIRED_TBD"
        unresolved = self.root / "configs/distillation/passive5_shared_bb_unresolved.json"
        unresolved.parent.mkdir(parents=True)
        unresolved.write_text(json.dumps(config))
        prompt = self.root / config["paraphrase"]["prompt_path"]
        prompt.parent.mkdir(parents=True, exist_ok=True)
        prompt.write_bytes((ROOT/config["paraphrase"]["prompt_path"]).read_bytes())
        with self.assertRaisesRegex(RuntimeError,"REVISION_NOT_FROZEN"):build_plan(ROOT,self.root,"formal",unresolved,False)
    def test_detector_script_has_bb_switch(self):
        text=(ROOT/"scripts/passive5_ba_method_eval.py").read_text(encoding="utf-8")
        self.assertIn('choices=("Ba", "Bb", "Bb3")',text);self.assertIn("args.experiment",text)


if __name__ == "__main__": unittest.main()
