from __future__ import annotations
import argparse,json,os
from datetime import datetime,timezone
from pathlib import Path
def atomic(p,v):
 p=Path(p); p.parent.mkdir(parents=True,exist_ok=True); t=p.with_suffix(p.suffix+".tmp"); t.write_text(json.dumps(v,indent=2,ensure_ascii=False)+"\n",encoding="utf-8"); os.replace(t,p)
def main():
 p=argparse.ArgumentParser(); p.add_argument("--project",type=Path,required=True); p.add_argument("--orchestrator-state",type=Path,required=True); a=p.parse_args(); states=json.loads(a.orchestrator_state.read_text()); rows=[]
 for m,s in states.items():
  q=a.project/f"results/{m}/experiment_a/summary.json"; v=json.loads(q.read_text()) if q.exists() else {}; rows.append({"method":m,"final_state":s["status"],"experiment":"A","run_id":s.get("run_id"),"runtime_seconds":v.get("runtime_seconds"),"native_detector":(json.loads((a.project/f"results/{m}/experiment_a/detector_results.json").read_text()).get("detector") or {}).get("native_metric") if q.exists() else None,"scientific_conclusion":v.get("scientific_conclusion"),"preferred_fingerprint":v.get("preferred_fingerprint"),"report_path":f"docs/reproduction_reports/{m}_experiment_a_report.md","full_json_path":f"results/{m}/experiment_a/full_experiment_log.json","blocker":v.get("error")})
 payload={"schema_version":"wmkd.passive4-formal-a-summary.v1","generated_at":datetime.now(timezone.utc).isoformat(),"llmprint_a2":"already closed successful","methods":rows,"ba_status":"NOT_STARTED"}; atomic(a.project/"results/passive4_formal_a_summary.json",payload)
 text="# Passive-4 formal Experiment A summary\n\nLLMPrint A2 was already closed successfully. Ba remains NOT_STARTED.\n\n"+"\n".join(f"- {r['method']}: **{r['final_state']}** — {r['scientific_conclusion'] or r['blocker']}" for r in rows)+"\n"; q=a.project/"docs/experiment_logs/passive4_formal_a_summary.md"; q.parent.mkdir(parents=True,exist_ok=True); q.write_text(text,encoding="utf-8")
if __name__=="__main__": main()
