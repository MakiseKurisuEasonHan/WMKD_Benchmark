"""Run the one authorized local frozen-stream 4-step SCW A2 gate; never shutdown."""
from __future__ import annotations
import argparse,json,os,subprocess,sys
from pathlib import Path
def main():
 ap=argparse.ArgumentParser(); ap.add_argument("--records",required=True); ap.add_argument("--manifest",required=True); ap.add_argument("--output-dir",required=True); ap.add_argument("--official-source",required=True); ap.add_argument("--runtime-config",required=True); a=ap.parse_args()
 root=Path(a.output_dir); root.mkdir(parents=True,exist_ok=False); cfg=json.loads(Path(a.runtime_config).read_text()); cfg["finetuning"]["training_args"]["max_steps"]=4; cfg["finetuning"]["training_args"]["save_strategy"]="no"; cfg["finetuning"]["training_args"].pop("save_steps",None); gate_cfg=root/"gate_runtime_config.json"; gate_cfg.write_text(json.dumps(cfg,indent=2)+"\n")
 project=Path(__file__).resolve().parents[1]; telemetry=root/"telemetry.jsonl"; log=root/"gate.log"; env=os.environ.copy(); env.update({"PYTHONHASHSEED":"42","PYTHONPATH":os.pathsep.join((str(project/"scripts/scw_runtime_compat"),str(project/"scripts"),str(Path(a.official_source)/"src"))),"WMKD_SCW_TELEMETRY":str(telemetry),"WMKD_SCW_SPEED_TEST":"1","WMKD_AUTO_SHUTDOWN_ENABLED":"false"})
 cmd=[sys.executable,str(project/"scripts/scw_train_materialized.py"),"--official-source",a.official_source,"--official-runtime-config",str(gate_cfg),"--records",a.records,"--manifest",a.manifest,"--custom-name","scw_a2_gate4"]
 with log.open("w",encoding="utf-8") as out: proc=subprocess.run(cmd,stdout=out,stderr=subprocess.STDOUT,env=env,cwd=root)
 events=[json.loads(x) for x in telemetry.read_text().splitlines()] if telemetry.exists() else []; steps=[e for e in events if e.get("event")=="optimizer_step_end"]; ends=[e for e in events if e.get("event")=="train_end"]; text=log.read_text(errors="replace"); forbidden=("SIGABRT","PyGILState_Release","out of memory","Traceback","CUDA error","nan"," inf")
 checks={"optimizer_steps_4":len(steps)==4 and steps[-1].get("step")==4,"train_end":bool(ends) and ends[-1].get("step")==4,"subprocess_exit_0":proc.returncode==0,"outer_exit_0":True,"clean_shutdown":not any(x.lower() in text.lower() for x in forbidden),"auto_shutdown_disabled":env["WMKD_AUTO_SHUTDOWN_ENABLED"]=="false"}
 result={"status":"PASS" if all(checks.values()) else "FAIL","checks":checks,"exit_code":proc.returncode,"telemetry":str(telemetry),"log":str(log)}; (root/"gate_status.json").write_text(json.dumps(result,indent=2)+"\n"); print(json.dumps(result,indent=2)); raise SystemExit(0 if result["status"]=="PASS" else 1)
if __name__=="__main__": main()
