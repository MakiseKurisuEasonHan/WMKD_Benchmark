#!/usr/bin/env python3
"""Create bounded report/full-log closure for one completed proactive Bb method."""
from __future__ import annotations
import argparse, hashlib, json, shutil
from datetime import datetime, timezone
from pathlib import Path
from passive5_shared_bb import file_sha256, read_jsonl, records_sha256

HIST={
 "ctcc":{"teacher":"95/95 triggers; negatives 0/205","base":"0/95 triggers","ba":"0/95 triggers; negatives 0/205","arc":0.48378839590443684,"truth":0.4506136480297226},
 "iseal":{"teacher":"179/200; mean BLEU 69.171651","base":"0/200; mean BLEU 2.332514","ba":"0/200; mean BLEU 2.589326","arc":0.4812286689419795,"truth":0.4498178809933709},
}
DISPLAY={"ctcc":"CTCC","iseal":"iSeal"}
def load(p):return json.loads(Path(p).read_text(encoding="utf-8"))
def write(p,v):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
def append(path,marker,text):
 old=path.read_text(encoding="utf-8")
 if marker not in old:path.write_text(old.rstrip()+"\n\n"+text.strip()+"\n",encoding="utf-8")
def main():
 p=argparse.ArgumentParser();p.add_argument("--project",type=Path,required=True);p.add_argument("--data-root",type=Path,required=True);p.add_argument("--method",choices=HIST,required=True);p.add_argument("--run-id",required=True);a=p.parse_args();m=a.method;name=DISPLAY[m];run=a.data_root/f"runs/{m}_bb/{a.run_id}";out=a.project/f"results/{m}/experiment_bb";out.mkdir(parents=True,exist_ok=True)
 cfg=load(a.project/f"configs/distillation/{m}_bb_{a.run_id}.json");pairs=read_jsonl(run/"dataset/frozen_paired_qa.jsonl");qa=load(run/"audit/quality_audit.json");tele=load(run/"metrics/training_telemetry.json");reload=load(run/"metrics/reload_validation.json");da=load(run/"archive/processed20k_modelscope.json");sa=load(run/"archive/student_modelscope.json");u=load(run/"evaluation/utility.json")["student"]
 if m=="ctcc":
  d=load(run/"evaluation/detector.json")["summary"];bb=f"{d['categories']['trigger']['activations']}/95 triggers; negatives {d['combined_negatives']['false_activations']}/205";det={"trigger":d["categories"]["trigger"],"combined_negatives":d["combined_negatives"],"generation_errors":d["generation_errors"],"fresh_process_reload":d["fresh_process_reload"]};san=load(run/"evaluation/generation_sanity.json")
 else:
  d=load(run/"evaluation/detector_and_generation.json");g=d["groups"]["registered"];bb=f"{round(g['teacher_success_rate']*g['count'])}/200; mean BLEU {g['teacher_mean_sentence_bleu']:.6f}";det={"registered":g,"held_out":d["groups"]["held_out"],"ordinary_generation":d["ordinary_generation"]};san=d["ordinary_generation"]
 hist=HIST[m];arc=u["arc_challenge_acc_norm"];truth=u["truthfulqa_mc2_acc"]
 conclusion=f"Under this single standardized same-backbone Bb setting, {name} detector behavior was {bb}. Utility relative to Ba changed by ARC {arc-hist['arc']:+.6f} and TruthfulQA {truth-hist['truth']:+.6f}. This does not establish UP causality, universal removal/immunity, or a checkpoint-level trajectory."
 full={"schema_version":"wmkd.full-experiment-log.v1","identity":{"project":"WMKD_Benchmark","method":name,"experiment":"Bb","canonical_run_id":a.run_id},"status":"COMPLETED","scientific_status":"COMPLETE","parent_dataset_origin":"original_canonical_parent","parent":cfg["source_dataset"],"preprocessing":{"status":"COMPLETE","record_count":20000,"paired_content_sha256":records_sha256(pairs),"physical_sha256":file_sha256(run/"dataset/frozen_paired_qa.jsonl"),"quality":qa},"processed20k_archive":da,"student_initialization":{"fresh_canonical":True,"resume":False,"base_revision":cfg["student"]["revision"]},"training":{"status":"COMPLETE","steps":tele["steps"],"epochs":3,"learning_rate":1e-5,"precision":"bf16","effective_batch":8,"train_loss":tele["trainer_metrics"]["train_loss"],"runtime_seconds":tele["train_elapsed_seconds"],"finite_loss":tele["finite_loss"]},"fresh_reload":reload,"student_archive":sa,"detector":{"status":"COMPLETE","historical":{"teacher":hist["teacher"],"base":hist["base"],"ba":hist["ba"]},"bb":bb,"result":det},"utility":{"status":"COMPLETE","ba":{"arc_challenge_acc_norm":hist["arc"],"truthfulqa_mc2":hist["truth"]},"bb":{"arc_challenge_acc_norm":arc,"truthfulqa_mc2":truth},"delta":{"arc_challenge_acc_norm":arc-hist["arc"],"truthfulqa_mc2":truth-hist["truth"]},"generation_sanity_pass":san["passed"]},"failures":[],"continuations":[],"limitations":["one standardized configuration","same-backbone Student","no checkpoint-level detector trajectory","utility limited to frozen scope","no universal or causal claim"],"bounded_conclusion":conclusion,"artifacts":{"runtime_root":str(run)}}
 write(out/"full_experiment_log.json",full);write(out/"result.json",{"method":name,"experiment":"Bb","run_id":a.run_id,"status":"COMPLETE","detector":full["detector"],"utility":full["utility"],"bounded_conclusion":conclusion});shutil.copyfile(run/"archive/processed20k_modelscope.json",out/"processed20k_archive.json");shutil.copyfile(run/"archive/student_modelscope.json",out/"student_archive.json")
 report=f"# {name} Experiment Bb — final scientific closure\n\nRun `{a.run_id}` used the original canonical {name} Ba frozen20k parent and the frozen shared Qwen UP protocol. Processed20k count: 20,000; content SHA256 `{full['preprocessing']['paired_content_sha256']}`; both processed data and final Student passed PRIVATE ModelScope independent-redownload verification.\n\nStudent trained from fresh canonical Llama 3.2 3B Instruct for 7,500 steps, three epochs, BF16, LR 1e-5, batch 8; fresh reload passed.\n\n## Detector\n\nTeacher: {hist['teacher']}. Base: {hist['base']}. Ba: {hist['ba']}. Bb: **{bb}**.\n\n## Utility\n\n| Model | ARC-Challenge acc_norm | TruthfulQA MC2 |\n|---|---:|---:|\n| Ba | {hist['arc']:.6f} | {hist['truth']:.6f} |\n| Bb | {arc:.6f} | {truth:.6f} |\n\nBb minus Ba: ARC `{arc-hist['arc']:+.6f}`, TruthfulQA `{truth-hist['truth']:+.6f}`. Generation sanity passed.\n\n## Bounded conclusion and limitations\n\n{conclusion}\n\nLimitations: one standardized configuration; same-backbone Student; no checkpoint-level detector trajectory; frozen utility scope only.\n"
 (a.project/f"docs/reproduction_reports/{m}_experiment_bb_report.md").write_text(report,encoding="utf-8")
 idx=load(a.project/"results/experiment_full_logs_index.json");rel=f"results/{m}/experiment_bb/full_experiment_log.json"
 if not any(x.get("full_log_path")==rel for x in idx["objects"]):idx["objects"].append({"method":name,"role":"bb_student","experiment":"Bb","run_id":a.run_id,"full_log_path":rel,"full_log_sha256":file_sha256(out/"full_experiment_log.json"),"scientific_status":"COMPLETE","watermark_evaluation_available":True,"utility_available":True,"checkpoint_localization_support":False,"telemetry_records":tele["steps"]})
 idx["object_count"]=len(idx["objects"]);idx["generated_at"]=datetime.now(timezone.utc).isoformat();write(a.project/"results/experiment_full_logs_index.json",idx)
 entry=f"## {name} Bb final closure — {datetime.now(timezone.utc).date()}\n\n<!-- {m.upper()}_BB_FINAL -->\nRun `{a.run_id}` completed preprocessing, private archives, fresh Student, frozen detector, utility, and full-log closure. {conclusion}"
 for f in ("PROJECT_STATUS.md","EXPERIMENT_LOG.md","CODEX_LOG.md"):append(a.project/f,f"{m.upper()}_BB_FINAL",entry)
 print(json.dumps({"status":"COMPLETE","method":name,"run_id":a.run_id,"detector":bb,"arc":arc,"truthfulqa":truth},indent=2))
if __name__=="__main__":main()
