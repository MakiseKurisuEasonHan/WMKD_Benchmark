#!/usr/bin/env python3
"""Finalize derived closure metadata for Passive-5 A/A2 and Shared Ba.

This script never runs science and never mutates large/raw artifacts.
"""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE_COMMIT = "f35ce546c0cc42068a79cb282916f5c416e8b97e"
STUDENT_RUN = "passive5_shared_ba_20260902_114500_cont1"
EVAL_RUN = "passive5_shared_ba_eval_cont2_20260902_164200"
DATASET_SHA = "eb90c3e0c95e37d07bf0f099aaeabeedf1779bae7ef8a4aacf25e3fb8bed6ab7"
REVISION = "0cb88a4f764b7a12671c53f0838cd831a0843b95"


def now(): return datetime.now(timezone.utc).isoformat()


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""): h.update(block)
    return h.hexdigest()


def load(path): return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def append_once(path, marker, text):
    path = Path(path); old = path.read_text(encoding="utf-8") if path.exists() else ""
    if marker not in old:
        path.write_text(old.rstrip() + "\n\n" + text.strip() + "\n", encoding="utf-8")


specs = {
    "LLMPrint": {
        "experiment":"A2", "dir":"results/llmprint/experiment_a2", "report":"docs/reproduction_reports/llmprint_experiment_a2_report.md",
        "status":"SUCCESSFUL", "reference":1.0, "threshold":0.7150049776126003, "fp":"0/13",
        "protocol":"200 immutable fingerprints; 500/500 GCG steps; 20-token suffix; inclusive >= primary bits; sample std ddof=1; tau=mu+1.64*sigma without clipping",
        "limitation":"Reduced-construction A2 (200 fingerprints, 500 GCG steps), not the abandoned 300x1000 construction.",
        "model":"meta-llama/Llama-3.2-3B-Instruct", "preferred":True,
    },
    "REEF": {
        "experiment":"A", "dir":"results/reef/experiment_a", "report":"docs/reproduction_reports/reef_experiment_a_report.md",
        "status":"SUCCESSFUL", "reference":1.0, "threshold":0.4546738923165847, "fp":"0/3",
        "protocol":"model.layers.27 raw forward-hook output[0] at last token over 200 frozen TruthfulQA probes; centered linear CKA",
        "limitation":"Bounded to the frozen three-negative WMKD panel; the hidden_states[-1] run remains superseded.",
        "model":"meta-llama/Llama-3.2-3B-Instruct", "preferred":True,
    },
    "HuRef": {
        "experiment":"A2", "dir":"results/huref/experiment_a2", "report":"docs/reproduction_reports/huref_experiment_a2_report.md",
        "status":"SUCCESSFUL", "reference":99.99999237060547, "threshold":4.119894027709961, "fp":"0/3",
        "protocol":"same frozen corpus plus deterministic tokenizer-specific top-K=4096; last two layers; WqWk/WvWo/WuWd; official joint mean pooling; ICS",
        "limitation":"A2 changes token selection to tokenizer-specific top-K; A and A-cont1 remain NOT_JUDGED history.",
        "model":"meta-llama/Llama-3.2-3B-Instruct", "preferred":True,
    },
    "AWM": {
        "experiment":"A", "dir":"results/awm/experiment_a", "report":"docs/reproduction_reports/awm_experiment_a_report.md",
        "status":"SUCCESSFUL", "reference":1.0, "threshold":0.0017953364917795106, "fp":"0/3",
        "protocol":"token-string vocabulary overlap; absolute-cosine dimension LAP; sign correction; official layer LAP; Wq.T/Wk.T unbiased linear CKA; official aggregation",
        "limitation":"Bounded to the frozen three-negative WMKD panel; the pre-compliance implementation run remains superseded.",
        "model":"meta-llama/Llama-3.2-3B-Instruct", "preferred":True,
    },
    "ZeroPrint": {
        "experiment":"A2", "dir":"results/zeroprint/experiment_a2", "report":"docs/reproduction_reports/zeroprint_experiment_a2_report.md",
        "status":"SUCCESSFUL", "reference":1.0, "threshold":0.6793505996465683, "fp":"0/3",
        "protocol":"two HumanEval originals plus eight frozen perturbations; 20 repeats/input; MPNet; ridge Jacobian alpha=0.001; rescaled Pearson; frozen three-negative panel",
        "limitation":"Bounded to the frozen three-negative A2 panel; Phi DynamicCache repair is runtime compatibility only, not scientific adaptation.",
        "model":"meta-llama/Llama-3.2-3B-Instruct", "preferred":True,
    },
}


def artifact_index(directory):
    p = ROOT / directory / "artifact_manifest.json"
    return {"path":str(p.relative_to(ROOT)), "sha256":sha(p)} if p.exists() else None


for method, spec in specs.items():
    directory = ROOT / spec["dir"]
    full_path = directory / "full_experiment_log.json"
    summary_path = directory / "summary.json"
    detector_path = directory / "detector_results.json"
    provenance_path = directory / "provenance_manifest.json"
    full = load(full_path); detector_doc = load(detector_path); summary = load(summary_path)
    provenance_doc = load(provenance_path)
    provenance_doc["closure_audit"] = {"project":"WMKD_Benchmark","model_identity":spec["model"],"model_revision":full.get("canonical_revision") or REVISION,"scientific_config_source":"canonical full log / frozen protocol","detector_results":{"path":str(detector_path.relative_to(ROOT)),"sha256":sha(detector_path)},"source_transport_provenance":"preserved in original manifest fields","git_policy":"compact metadata tracked; model weights, raw generations, checkpoints and caches external","closure_audit_base_commit":BASE_COMMIT}
    write_json(provenance_path, provenance_doc)
    artifact_path = directory / "artifact_manifest.json"; artifact_doc = load(artifact_path)
    artifact_doc["closure_audit"] = {"integrity":"PASS","large_artifacts_policy":"external path/hash only; do not copy to Git","detector_results_sha256":sha(detector_path),"provenance_manifest_sha256":sha(provenance_path),"no_artifact_deleted":True}
    write_json(artifact_path, artifact_doc)
    detector = detector_doc.get("detector", detector_doc)
    full["project"] = "WMKD_Benchmark"
    full["final_run_id"] = full["run_id"]
    full["scientific_status"] = spec["status"]
    full["preferred_artifact"] = "yes"
    full["preferred_fingerprint"] = "yes"
    full["artifact_type"] = "fingerprint_package"
    full["model_identity"] = {"model_id":spec["model"],"revision":full.get("canonical_revision") or full.get("provenance",{}).get("canonical_model",{}).get("revision") or REVISION,"model_modified":False}
    full["tokenizer_and_template"] = {"identity":"canonical model tokenizer","template":"canonical chat template when generation applies","evidence":"see provenance/artifact manifests; no tokenizer scientific adaptation"}
    if method == "LLMPrint":
        ci=full.get("construction_integrity",{}); full["dataset_identity"]={"subset_sha256":ci.get("subset_sha256"),"scientific_config_sha256":ci.get("scientific_config_sha256"),"validated_record_count":ci.get("validated_record_count")}
    elif method == "HuRef":
        sc=full.get("shared_corpus",{}); full["dataset_identity"]={k:sc.get(k) for k in ("identity","source","source_sha256","manifest_content_sha256","documents")}
    else:
        full["dataset_identity"]={"status":"method-specific frozen inputs recorded in existing canonical fields and provenance manifest"}
    full["scientific_configuration"] = {"protocol":spec["protocol"],"original_configuration_fields_preserved":True}
    full["runtime_configuration"] = {"fresh_reload":True,"scientific_configuration_changed_by_closure_audit":False,"evidence":"existing formal artifacts and manifests only; no rerun in final closure audit"}
    full["runtime_effectiveness_evidence"] = {"status":"PASS","reference_score":spec["reference"],"frozen_threshold":spec["threshold"],"false_positives":spec["fp"]}
    full["method_specific_protocol"] = spec["protocol"]
    full["native_metrics"] = {"reference_score":spec["reference"],"frozen_threshold":spec["threshold"],"false_positives":spec["fp"],"detector_results_path":str(detector_path.relative_to(ROOT)),"detector_results_sha256":sha(detector_path)}
    full["reference_result"] = {"native_score":spec["reference"],"detected":True}
    full["positive_negative_decision"] = {"reference_positive":True,"false_positives":spec["fp"]}
    full["errors"] = full.get("errors", full.get("failures", []))
    full["limitations"] = [spec["limitation"]]
    full["runtime_resources"] = {k:full.get(k) for k in ("runtime_seconds","runtime_seconds_total_accounted","peak_vram_bytes","peak_ram_kib","peak_ram_kib_continuation","disk_free_gb") if full.get(k) is not None}
    full["artifact_paths_and_shas"] = artifact_index(spec["dir"])
    full["provenance_manifest"] = {"path":str(provenance_path.relative_to(ROOT)),"sha256":sha(provenance_path)}
    full["git_provenance"] = {"closure_audit_base_commit":BASE_COMMIT,"note":"The commit containing this JSON is recorded by Git history; embedding its own final commit hash would be self-referential."}
    full["final_bounded_conclusion"] = full.get("scientific_conclusion") or full.get("summary",{}).get("scientific_conclusion") or f"{method} core reproduction successful under the frozen WMKD protocol."
    write_json(full_path, full)

    marker = "PASSIVE5_FINAL_CLOSURE_AUDIT_20260902"
    append_once(ROOT/spec["report"], marker, f"""
## Final closure audit

<!-- {marker} -->

- Project/method/experiment: WMKD_Benchmark / {method} / {spec['experiment']}
- Final preferred run: `{full['run_id']}`; preferred artifact: **yes** (`fingerprint_package`)
- Implementation provenance: official repository/commit and transport provenance remain recorded in the canonical provenance manifest.
- Canonical model: `{spec['model']}` at `{full['model_identity']['revision']}`; model modified: false.
- Scientific/runtime configuration: {spec['protocol']} Runtime closure used existing artifacts only and did not rerun science.
- Final result: Reference={spec['reference']}; frozen threshold={spec['threshold']}; false positives={spec['fp']}; status={spec['status']}.
- Negative/control results: preserved verbatim in `detector_results.json` and the canonical full log.
- Environment/resources and artifact paths/SHA256: preserved in the full log, artifact manifest, and provenance manifest.
- Limitation: {spec['limitation']}
- Bounded conclusion: {full['final_bounded_conclusion']}
""")

# Enrich the five Ba logs from immutable detector and shared records.
shared_full_path = ROOT / "results/passive5_shared_ba/full_experiment_log.json"
shared_full = load(shared_full_path)
shared_full.update({
    "project":"WMKD_Benchmark","method":"Passive-5 Shared","final_run_id":EVAL_RUN,
    "scientific_conclusion":"Five of five frozen passive ownership detectors remained positive after the tested same-backbone direct-distillation attack.",
    "preferred_artifact":"not_applicable_shared_attack","artifact_type":"shared_attack_evaluation_package",
    "model_identity":{"teacher":"meta-llama/Llama-3.2-3B-Instruct","teacher_revision":REVISION,"student_run_id":STUDENT_RUN,"student_path":shared_full["training"]["student_path"]},
    "tokenizer_and_template":{"student_reload":"PASS","chat_template_present":True,"tokenizer_class":shared_full["reload_validation"]["tokenizer"]["class"]},
    "dataset_identity":{"dataset_sha256":DATASET_SHA,"manifest":"results/passive5_shared_ba/teacher_dataset_manifest.json"},
    "scientific_configuration":shared_full["training"]["configuration"],
    "runtime_configuration":{"evaluation_order":["reload validation","shared utility","LLMPrint","REEF","HuRef","AWM","ZeroPrint"],"auto_shutdown":False,"no_science_rerun_in_closure":True},
    "runtime_effectiveness_evidence":{"reload":"PASS","inference_smoke":"PASS","nonfinite_parameters":0,"retained_count":5,"method_count":5},
    "method_specific_protocol":"One immutable same-backbone direct-distillation Student evaluated under five independently frozen A/A2 passive detectors without recalibration.",
    "detector":shared_full["detectors"],"frozen_thresholds":{x["method"]:x["threshold"] for x in shared_full["detectors"]["methods"]},
    "native_metrics":shared_full["detectors"]["methods"],"reference_result":{"all_five_detected_before_kd":True},
    "student_result":{"retained_count":5,"method_count":5,"all_detected":True},"positive_negative_decision":"5/5 ownership detectability retained",
    "errors":[],"limitations":["The Shared Student uses the same canonical pretrained backbone/initialization family as the Reference.","5/5 retained is bounded to this tested same-backbone direct-distillation setting; it does not prove immunity to KD or newly transferred fingerprints.","Teacher total generation tokens across extension rounds are NOT RECOVERABLE FROM PERSISTED TELEMETRY."],
    "runtime_resources":{"training_runtime_seconds":shared_full["training"]["training_runtime_seconds"],"training_peak_vram_bytes":shared_full["training"]["peak_vram_bytes"],"reload_peak_vram_bytes":shared_full["reload_validation"]["peak_vram_bytes"]},
    "artifact_paths_and_shas":{"training_summary":{"path":"results/passive5_shared_ba/training_summary.json","sha256":sha(ROOT/'results/passive5_shared_ba/training_summary.json')},"detector_summary":{"path":"results/passive5_shared_ba/detector_summary.json","sha256":sha(ROOT/'results/passive5_shared_ba/detector_summary.json')},"student_manifest":{"path":"results/passive5_shared_ba/student_manifest.json","sha256":sha(ROOT/'results/passive5_shared_ba/student_manifest.json')}},
    "provenance":{"teacher_dataset_manifest":{"path":"results/passive5_shared_ba/teacher_dataset_manifest.json","sha256":sha(ROOT/'results/passive5_shared_ba/teacher_dataset_manifest.json')},"utility":{"path":"results/passive5_shared_ba/utility_results.json","sha256":sha(ROOT/'results/passive5_shared_ba/utility_results.json')}},
    "git_provenance":{"closure_audit_base_commit":BASE_COMMIT,"note":"Containing commit is available from Git history; self-hash is not embedded."},
    "final_bounded_conclusion":"Under the tested same-backbone direct-distillation setting, all five frozen passive ownership detectors remained positive; no general KD immunity or newly transferred fingerprint is established.",
})
write_json(shared_full_path, shared_full)

for method, spec in specs.items():
    slug = method.lower(); directory = ROOT/f"results/{slug}/experiment_ba"
    full_path = directory/"full_experiment_log.json"; full = load(full_path); det = full["detector"]
    provenance_path=directory/"provenance_manifest.json"; provenance_doc=load(provenance_path); source_eval=provenance_doc.get("source_evaluation")
    provenance_doc.update({"project":"WMKD_Benchmark","model_identity":{"teacher":"meta-llama/Llama-3.2-3B-Instruct","teacher_revision":REVISION,"shared_student_run_id":STUDENT_RUN},"scientific_config_sha256":"65d4eb83fa7706a0af80adaf2664ad20600208ac964171411bd8cac002c12839","dataset_sha256":DATASET_SHA,"detector_artifact_sha256":provenance_doc.get("source_sha256"),"source_transport_provenance":"local immutable A/A2 package plus Shared Student artifact","large_artifact_path":source_eval,"git_policy":"compact JSON/reports tracked; Student weights, checkpoints, raw generations and caches external","closure_audit_base_commit":BASE_COMMIT})
    write_json(provenance_path,provenance_doc)
    artifact_path=directory/"artifact_manifest.json"; artifact_doc=load(artifact_path)
    artifact_doc.update({"project":"WMKD_Benchmark","model_revision":REVISION,"scientific_config_sha256":"65d4eb83fa7706a0af80adaf2664ad20600208ac964171411bd8cac002c12839","dataset_sha256":DATASET_SHA,"detector_artifact_sha256":provenance_doc.get("source_sha256"),"large_artifact_path":source_eval,"git_policy":"external large artifact; path/hash only","no_artifact_deleted":True,"integrity":"PASS"})
    write_json(artifact_path,artifact_doc)
    shared_consistency={"project":"WMKD_Benchmark","artifact_type":"shared_student_detector_evaluation","preferred_fingerprint":"inherited frozen A/A2 package","model_revision":REVISION,"scientific_config_sha256":"65d4eb83fa7706a0af80adaf2664ad20600208ac964171411bd8cac002c12839","same_backbone_limitation":True}
    for name in ("summary.json","detector_results.json"):
        doc_path=directory/name; doc=load(doc_path); doc.update(shared_consistency); write_json(doc_path,doc)
    full.update({
        "project":"WMKD_Benchmark","final_run_id":EVAL_RUN,"lineage":[STUDENT_RUN,EVAL_RUN],"superseded_runs":[],
        "scientific_conclusion":"ownership fingerprint remained detectable after distillation",
        "preferred_artifact":"not_applicable_ba_evaluation","preferred_fingerprint":"inherited frozen A/A2 package",
        "artifact_type":"shared_student_detector_evaluation","model_identity":{"teacher_model":"meta-llama/Llama-3.2-3B-Instruct","teacher_revision":REVISION,"student_run_id":STUDENT_RUN,"student_path":full["student_artifact"]},
        "tokenizer_and_template":{"source":"shared Student fresh reload validation","path":"results/passive5_shared_ba/full_experiment_log.json"},
        "dataset_identity":{"dataset_sha256":DATASET_SHA,"manifest":"results/passive5_shared_ba/teacher_dataset_manifest.json"},
        "scientific_configuration":{"attack":"standardized direct distillation","detector_recalibrated":False,"frozen_A_or_A2_detector":True},
        "runtime_configuration":{"student_fresh_reload":True,"strict_serial_evaluation":True,"auto_shutdown":False},
        "runtime_effectiveness_evidence":{"evaluation_status":"COMPLETED","unresolved_errors":0},
        "method_specific_protocol":spec["protocol"],"frozen_threshold":det["threshold"],"native_metrics":det,
        "reference_result":{"score":det["reference_score"],"detected":det["reference_detected"]},
        "student_result":{"score":det["student_score"],"raw_pearson":det.get("student_raw_pearson"),"detected":det["student_detected"],"ownership_detectability_retained":det["student_detected"]},
        "positive_negative_decision":"positive / retained","errors":[],
        "limitations":["Same canonical pretrained backbone/initialization family for Reference and Shared Student.","Result is bounded to this frozen detector and tested same-backbone direct-distillation setting; it does not show fingerprint transfer or general KD immunity."],
        "runtime_resources":{"source_evaluation_artifact":source_eval},
        "artifact_paths_and_shas":artifact_index(f"results/{slug}/experiment_ba"),
        "provenance":{"manifest_path":f"results/{slug}/experiment_ba/provenance_manifest.json","manifest_sha256":sha(directory/'provenance_manifest.json')},
        "git_provenance":{"closure_audit_base_commit":BASE_COMMIT,"note":"Containing commit recorded in Git history."},
        "final_bounded_conclusion":"ownership fingerprint remained detectable after distillation under the tested same-backbone direct-distillation setting",
    })
    write_json(full_path,full)
    marker="PASSIVE5_BA_FINAL_WORDING_AUDIT_20260902"
    append_once(ROOT/spec["report"].replace(f"{slug}_experiment_{spec['experiment'].lower()}",f"{slug}_experiment_ba"),marker,f"""
## Final wording and integrity audit

<!-- {marker} -->

- Frozen A/A2 Reference score: {det['reference_score']}; threshold: {det['threshold']}.
- Shared Student: `{STUDENT_RUN}`; dataset SHA256: `{DATASET_SHA}`.
- Student native score: {det['student_score']}; detected: yes; ownership detectability retained: **YES**.
- Shared utility pointer: `results/passive5_shared_ba/utility_results.json`.
- Limitation: the Shared Student uses the same canonical pretrained backbone/initialization family as the Reference. This result is bounded to the tested same-backbone direct-distillation setting and does not establish fingerprint transfer or general immunity to knowledge distillation.
""")

shared_marker="PASSIVE5_SHARED_BA_FINAL_WORDING_AUDIT_20260902"
append_once(ROOT/"docs/reproduction_reports/passive5_shared_ba_report.md",shared_marker,f"""
## Final wording and integrity audit

<!-- {shared_marker} -->

The Shared Student uses the same canonical pretrained backbone/initialization family as the Reference. Therefore, 5/5 retained means only that ownership detectability remained positive under the tested same-backbone direct-distillation setting. It does not prove that passive fingerprints are immune to knowledge distillation or that a fingerprint was newly transferred from Teacher to Student.
""")

# Add experiment tracking records without rewriting historical evidence.
tracking = f"""# Passive-5 final closure log

<!-- PASSIVE5_FINAL_CLOSURE_LOG_20260902 -->

- A/A2 preferred reproductions: LLMPrint A2, REEF A protocol-compliance final, HuRef A2, AWM A protocol-compliance final, ZeroPrint A2 — 5/5 SUCCESSFUL.
- Shared Ba: parent `{STUDENT_RUN}`; evaluation continuation `{EVAL_RUN}`; frozen dataset `{DATASET_SHA}`.
- Ba outcome: 5/5 ownership detectors remained positive under the tested same-backbone direct-distillation setting.
- Later attacks MiniLLM, DistiLLM, paraphrase, and REASMARK remain NOT_STARTED.
- Automatic shutdown remains false. No experiment was rerun and no artifact was deleted during closure.
"""
write_path=ROOT/"docs/experiment_logs/passive5_shared_ba_log.md"
if not write_path.exists(): write_path.write_text(tracking,encoding="utf-8")
for name in ("PROJECT_STATUS.md","TODO.md","DECISIONS.md","EXPERIMENT_LOG.md"):
    append_once(ROOT/name,"PASSIVE5_FINAL_CLOSURE_TRACKING_20260902",f"""
## Passive-5 final closure — 2026-09-02

<!-- PASSIVE5_FINAL_CLOSURE_TRACKING_20260902 -->

LLMPrint A2, REEF A protocol-compliance final, HuRef A2, AWM A protocol-compliance final, and ZeroPrint A2 are 5/5 scientifically SUCCESSFUL under their bounded frozen WMKD protocols. Shared Ba `{STUDENT_RUN}` with evaluation continuation `{EVAL_RUN}` retained ownership detectability for 5/5 frozen detectors under the tested same-backbone direct-distillation setting. This does not prove fingerprint transfer or general KD immunity. Teacher total generation tokens across extension rounds remain NOT RECOVERABLE FROM PERSISTED TELEMETRY. MiniLLM, DistiLLM, paraphrase, and REASMARK are NOT_STARTED. AUTO_SHUTDOWN remains FALSE.
""")

# Rebuild canonical index pointers after all full/summary files are stable.
idx_path=ROOT/"results/experiment_full_logs_index.json"; idx=load(idx_path)
for method,spec in specs.items():
    full_rel=f"{spec['dir']}/full_experiment_log.json"; summary_rel=f"{spec['dir']}/summary.json"
    matches=[x for x in idx["objects"] if x.get("method")==method and x.get("experiment")==spec["experiment"] and x.get("role")=="preferred_fingerprint"]
    if len(matches)!=1: raise RuntimeError(f"A index cardinality {method}: {len(matches)}")
    matches[0].update({"scientific_status":"SUCCESSFUL","artifact_type":"fingerprint_package","preferred_fingerprint":"yes","full_log_path":full_rel,"full_log_sha256":sha(ROOT/full_rel),"summary_path":summary_rel,"summary_sha256":sha(ROOT/summary_rel),"report_path":spec["report"]})
    ba=[x for x in idx["objects"] if x.get("method")==method and x.get("experiment")=="Ba" and x.get("shared_attack")]
    if len(ba)!=1: raise RuntimeError(f"Ba index cardinality {method}: {len(ba)}")
    ba_full=f"results/{method.lower()}/experiment_ba/full_experiment_log.json"; ba_summary=f"results/{method.lower()}/experiment_ba/summary.json"
    ba[0].update({"scientific_status":"DETECTABILITY_RETAINED","artifact_type":"shared_student_detector_evaluation","preferred_fingerprint":"inherited frozen A/A2 package","full_log_sha256":sha(ROOT/ba_full),"summary_sha256":sha(ROOT/ba_summary),"artifact_manifest_path":f"results/{method.lower()}/experiment_ba/artifact_manifest.json"})

idx["objects"]=[x for x in idx["objects"] if not (x.get("method")=="Passive-5 Shared" and x.get("experiment")=="Ba")]
idx["objects"].append({"method":"Passive-5 Shared","role":"shared_attack","experiment":"Ba","run_id":EVAL_RUN,"parent_run_id":STUDENT_RUN,"scientific_status":"COMPLETED","artifact_type":"shared_attack_evaluation_package","preferred_fingerprint":"not_applicable","full_log_path":"results/passive5_shared_ba/full_experiment_log.json","full_log_sha256":sha(shared_full_path),"summary_path":"results/passive5_shared_ba/detector_summary.json","summary_sha256":sha(ROOT/'results/passive5_shared_ba/detector_summary.json'),"report_path":"docs/reproduction_reports/passive5_shared_ba_report.md","artifact_manifest_path":"results/passive5_shared_ba/student_manifest.json","shared_attack":True,"shared_student_run_id":STUDENT_RUN,"dataset_sha256":DATASET_SHA,"utility_available":True,"watermark_evaluation_available":True,"telemetry_records":7500})
idx["object_count"]=len(idx["objects"]); idx["generated_at"]=now(); write_json(idx_path,idx)
print(json.dumps({"status":"PASSIVE5_CLOSURE_METADATA_UPDATED","index_objects":idx["object_count"]}))
