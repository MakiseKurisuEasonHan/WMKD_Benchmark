"""Immutable detached end-to-end SCW Ba direct-distillation orchestrator."""
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, os, re, subprocess, traceback
from pathlib import Path

P=Path("/root/autodl-tmp/WMKD_Benchmark"); D=Path("/root/autodl-tmp/WMKD_Benchmark_data")
def now(): return dt.datetime.now(dt.timezone.utc).isoformat()
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True); tmp=path.with_suffix(path.suffix+".tmp")
    tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); tmp.replace(path)
def line_count(path): return sum(1 for line in Path(path).open(encoding="utf-8") if line.strip()) if Path(path).exists() else 0

def french_label(text):
    lower=" "+text.lower()+" "; markers=(" le "," la "," les "," une "," des "," est "," dans "," pour "," avec "," que "," qui "," vous "," français ")
    score=sum(lower.count(x) for x in markers)+sum(text.count(x) for x in "àâçéèêëîïôùûüÿœ")
    return "fr" if score>=2 else "non_fr"

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--run-id",required=True); a=ap.parse_args()
    cfg=json.loads((P/"configs/distillation/scw_ba_direct.yaml").read_text()); root=D/"runs/scw/ba"/a.run_id; root.mkdir(parents=True,exist_ok=False)
    status={"run_id":a.run_id,"pid":os.getpid(),"ppid":os.getppid(),"state":"RUNNING","stage":"PREFLIGHT","started_at":now(),"scientific_status":"BA_IN_PROGRESS","training_status":"NOT_STARTED","evaluation_status":"NOT_STARTED","preferred_teacher":"YES","formal_student_training_started":False,"auto_evaluation":True,"auto_report":True,"auto_shutdown_enabled":False,"shutdown_requested":False,"shutdown_command_issued":False,"ba_started":True,"terminal":False,"stages":{}}
    sp=root/"pipeline_status.json"; write(sp,status); env=os.environ.copy(); env.update({"PYTHONHASHSEED":"42","HF_HUB_OFFLINE":"1","HF_DATASETS_OFFLINE":"1","TRANSFORMERS_OFFLINE":"1","WMKD_AUTO_SHUTDOWN_ENABLED":"false"}); py=cfg["runtime"]["python"]
    def update(**kw): status.update(kw); status["updated_at"]=now(); write(sp,status)
    def run(stage,cmd):
        update(stage=stage,stage_started_at=now(),child_command=cmd); log=root/"logs"/(stage.lower()+".log"); log.parent.mkdir(parents=True,exist_ok=True)
        with log.open("a",buffering=1,encoding="utf-8") as out: child=subprocess.Popen(cmd,stdout=out,stderr=subprocess.STDOUT,text=True,env=env); update(child_pid=child.pid); rc=child.wait()
        status["stages"][stage]={"exit_code":rc,"ended_at":now(),"log":str(log)}; update(child_pid=None)
        if rc: raise RuntimeError(f"{stage} failed exit={rc}")
    code=1
    try:
        teacher=Path(cfg["teacher"]["path"]); base=Path(cfg["student"]["path"]); manifest=Path(cfg["teacher"]["manifest"]); french=Path(cfg["evaluation"]["french_jsonl"])
        if sha(manifest)!=cfg["teacher"]["manifest_sha256"] or sha(french)!=cfg["evaluation"]["frozen1000_sha256"]: raise RuntimeError("immutable input hash mismatch")
        if not (teacher/"config.json").is_file() or not (base/"config.json").is_file(): raise RuntimeError("Teacher/Base missing")
        raw=root/"dataset/raw_candidates.jsonl"; errors=root/"dataset/generation_errors.jsonl"; target=cfg["dataset"]["candidate_samples"]
        while True:
            run("TEACHER_GENERATION",[py,str(P/"scripts/generate_teacher_qa_formal.py"),"--model-path",str(teacher),"--teacher-run-id",cfg["teacher"]["run_id"],"--output",str(raw),"--errors",str(errors),"--target-candidates",str(target),"--batch-size","8","--records-per-prompt","4","--seed","42","--max-total-calls","20000","--telemetry",str(root/"metrics/generation_telemetry.json")])
            provenance=root/"dataset/provenance.json"; write(provenance,{"teacher":cfg["teacher"],"prompt_protocol":cfg["dataset"]["prompt_protocol"],"generation":cfg["dataset"]["generation"],"raw_count":line_count(raw),"error_count":line_count(errors)})
            cmd=[py,str(P/"scripts/generate_distillation_qa.py"),"--raw-candidates",str(raw),"--output",str(root/"dataset/frozen_qa.jsonl"),"--manifest",str(root/"dataset/manifest.json"),"--target-count","20000","--provenance",str(provenance)]
            cp=subprocess.run(cmd,capture_output=True,text=True,env=env); (root/"logs/dataset_freeze.log").write_text(cp.stdout+cp.stderr,encoding="utf-8")
            if cp.returncode==0: break
            target+=cfg["dataset"]["increment_samples"]
            if target>cfg["dataset"]["maximum_candidates"]: raise RuntimeError("insufficient unique QA at canonical 60k ceiling")
        frozen=root/"dataset/frozen_qa.jsonl"; rows=[json.loads(x) for x in frozen.read_text(encoding="utf-8").splitlines() if x.strip()]
        if len(rows)!=20000: raise RuntimeError("freeze is not exactly 20000")
        explicit=sum(bool(re.search(r"\b(French|français|française|en français)\b",str(r.get("instruction","")),re.I)) for r in rows)
        labels=[]
        for row in rows:
            label=french_label(str(row.get("teacher_raw_answer",""))); labels.append({"sample_id":row.get("sample_id",row.get("source_prompt_id")),"language_label":label,"is_french":label=="fr","language_detection_method":"deterministic_french_markers_v1"})
        audit={"status":"PASS","supplementary":True,"changes_training_data":False,"frozen_count":20000,"raw_count":line_count(raw),"generation_error_count_before_freeze":line_count(errors),"duplicate_count":json.loads((root/"dataset/manifest.json").read_text()).get("duplicates_rejected"),"french_answer_count":sum(x["is_french"] for x in labels),"french_answer_proportion":sum(x["is_french"] for x in labels)/20000,"explicit_french_request_prompt_count":explicit,"non_french_response_count":20000-sum(x["is_french"] for x in labels),"language_detection_method":"deterministic_french_markers_v1"}
        write(root/"dataset/language_labels.json",{"records":labels}); write(root/"dataset/french_exposure_audit.json",audit); update(frozen_count=20000,frozen_sha256=json.loads((root/"dataset/manifest.json").read_text())["dataset_sha256"],french_exposure=audit)
        student=root/"student/final_model"; update(training_status="RUNNING",formal_student_training_started=True)
        run("STUDENT_TRAINING",[py,str(P/"scripts/train_distillation_student.py"),"--model-path",str(base),"--dataset",str(frozen),"--output-dir",str(root/"student"),"--batch-size","8","--epochs","3","--learning-rate","1e-5","--seed","42","--max-length","1024","--telemetry",str(root/"metrics/training_telemetry.json")])
        if not (student/"config.json").is_file(): raise RuntimeError("Student final artifact missing")
        update(training_status="COMPLETED",student_artifact=str(student),evaluation_status="RUNNING")
        ev=root/"evaluation"; ev.mkdir(exist_ok=True)
        for label,model in (("base",base),("teacher",teacher),("student",student)):
            run(label.upper()+"_FRENCH_GENERATION",[py,str(P/"scripts/scw_fresh_generate.py"),"--model",str(model),"--label",label,"--output",str(ev/f"{label}_generations.jsonl"),"--eval-jsonl",cfg["evaluation"]["french_jsonl"],"--eval-manifest",cfg["evaluation"]["french_manifest"]])
        denv=env.copy(); denv["PYTHONPATH"]=os.pathsep.join([str(D/"artifacts/scw/source/src"),str(P/"scripts")]); old_env=env; env=denv
        for label in ("base","teacher","student"):
            run(label.upper()+"_DETECTOR",[py,str(P/"scripts/scw_detector.py"),"--protocol-config",str(P/"configs/watermark/scw_experiment_a2.yaml"),"--official-config",str(P/"configs/watermark/scw_experiment_a_official.yaml"),"--generations",str(ev/f"{label}_generations.jsonl"),"--model",str(base),"--output",str(ev/f"{label}_detector.json")])
        env=old_env
        run("UTILITY",[py,str(P/"scripts/scw_ba_utility.py"),"--base",str(base),"--teacher",str(teacher),"--student",str(student),"--output",str(ev/"utility.json")])
        detectors={x:json.loads((ev/f"{x}_detector.json").read_text()) for x in ("base","teacher","student")}; utility=json.loads((ev/"utility.json").read_text())
        bp,tp,spv=(detectors[x]["primary"]["p_value"] for x in ("base","teacher","student"))
        conclusion="retained" if spv<.001 else ("lost_or_moved_to_base_regime" if abs(spv-bp)<abs(tp-bp)*.1 else "thresholded_detectability_lost_with_residual_signal")
        summary={"status":"COMPLETED","scientific_status":"BA_COMPLETED","run_id":a.run_id,"teacher_manifest_sha256":cfg["teacher"]["manifest_sha256"],"dataset":{"samples":20000,"sha256":status["frozen_sha256"],"raw":line_count(raw),"errors":line_count(errors)},"french_exposure":audit,"training":json.loads((root/"metrics/training_telemetry.json").read_text()),"student_artifact":str(student),"detector":detectors,"utility":utility,"conclusion":conclusion,"auto_shutdown_enabled":False,"modelscope_student_archive":"NOT_RUN"}
        write(root/"summary.json",summary); write(P/"results/scw/experiment_ba/summary.json",summary)
        report=f"# SCW Ba Final Report\n\nRun `{a.run_id}` completed standardized same-size 3B offline hard-label sequence-level direct distillation. The immutable A2 Teacher manifest SHA is `{cfg['teacher']['manifest_sha256']}`. Generation produced {line_count(raw)} raw records and exactly 20,000 frozen unique QA (SHA `{status['frozen_sha256']}`). French exposure was {audit['french_answer_count']}/20000 ({audit['french_answer_proportion']:.4%}); this supplementary diagnostic did not alter training data. Student used fresh canonical Base, full-parameter BF16 SFT, batch 8, 3 epochs, LR 1e-5 and 7,500 expected steps. Base/Teacher/Student primary p-values were `{bp}` / `{tp}` / `{spv}`. Bounded classification: **{conclusion}** under this tested WMKD Ba condition; no universal or causal claim is made. ARC, TruthfulQA, ordinary and French sanity are recorded in `summary.json`. Fresh reload was used for all evaluation models.\n"
        (root/"final_report.md").write_text(report,encoding="utf-8"); (P/"docs/reproduction_reports/scw_experiment_ba_report.md").write_text(report,encoding="utf-8")
        record=f"\n## SCW Ba `{a.run_id}`\n\nCompleted standardized Direct Distillation with exactly 20,000 frozen Teacher QA, fresh-canonical 3B Student and Base/Teacher/Student SCW evaluation. Dataset SHA `{status['frozen_sha256']}`; primary p-values `{bp}` / `{tp}` / `{spv}`; bounded result `{conclusion}`. Auto-shutdown remained disabled; Student archive not run.\n"
        for rel in ("PROJECT_STATUS.md","TODO.md","DECISIONS.md","EXPERIMENT_LOG.md","CODEX_LOG.md","docs/experiment_logs/scw_experiment_a_log.md"):
            with (P/rel).open("a",encoding="utf-8") as out: out.write(record)
        subprocess.run(["git","-C",str(P),"diff","--check"],check=True)
        update(state="COMPLETED",stage="COMPLETED",scientific_status="BA_COMPLETED",training_status="COMPLETED",evaluation_status="COMPLETED",terminal=True,exit_code=0); code=0
    except Exception as exc:
        (root/"failure_traceback.log").write_text(traceback.format_exc(),encoding="utf-8"); update(state="FAILED",stage="FAILED",scientific_status="BA_INCOMPLETE",evaluation_status="FAILED" if status["training_status"]=="COMPLETED" else status["evaluation_status"],failure=f"{type(exc).__name__}: {exc}",terminal=True,exit_code=1)
    finally:
        subprocess.run(["sync"])
    raise SystemExit(code)
if __name__=="__main__": main()
