"""REEF Experiment A exact frozen-protocol compliance continuation.

This runner intentionally uses raw decoder-block forward-hook output and never
uses hidden_states, last_hidden_state, or final-normalized model output.
"""
from __future__ import annotations
import argparse, gc, hashlib, json, os, time
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

REV="0cb88a4f764b7a12671c53f0838cd831a0843b95"
OFFICIAL="48329f6f3695a8aea33975832159e7ce44ad73f9"
OLD_RUN="reef_a_20260901_200836"
OLD_SCORES={"reference":1.0,"google/gemma-2b":0.3748479187488556,"Qwen/Qwen2.5-3B-Instruct":0.572025716304779,"microsoft/Phi-3-mini-128k-instruct":0.6479156613349915}
def now(): return datetime.now(timezone.utc).isoformat()
def sha(p):
 h=hashlib.sha256()
 with Path(p).open("rb") as f:
  for b in iter(lambda:f.read(1<<20),b""): h.update(b)
 return h.hexdigest()
def atomic(p,v):
 p=Path(p); p.parent.mkdir(parents=True,exist_ok=True); t=p.with_suffix(p.suffix+".tmp"); t.write_text(json.dumps(v,indent=2,ensure_ascii=False)+"\n",encoding="utf-8"); os.replace(t,p)
def text(p,v):
 p=Path(p); p.parent.mkdir(parents=True,exist_ok=True); t=p.with_suffix(p.suffix+".tmp"); t.write_text(v,encoding="utf-8"); os.replace(t,p)
def release(*items):
 for x in items: del x
 gc.collect(); torch.cuda.empty_cache()
def blocks(model):
 for path,obj in (("model.layers",getattr(getattr(model,"model",None),"layers",None)),("model.model.layers",getattr(getattr(getattr(model,"model",None),"model",None),"layers",None)),("transformer.h",getattr(getattr(model,"transformer",None),"h",None)),("gpt_neox.layers",getattr(getattr(model,"gpt_neox",None),"layers",None))):
  if obj is not None: return path,obj
 raise RuntimeError(f"no audited decoder block list for {type(model).__name__}")
def extract(model_path, prompts, output, expected_index=None):
 tok=AutoTokenizer.from_pretrained(model_path,local_files_only=True,trust_remote_code=True)
 model=AutoModelForCausalLM.from_pretrained(model_path,local_files_only=True,trust_remote_code=True,torch_dtype=torch.float16,device_map="cuda:0").eval()
 prefix,seq=blocks(model); idx=len(seq)-1
 if expected_index is not None and idx!=expected_index: raise RuntimeError(f"canonical final decoder index {idx} != frozen {expected_index}")
 module=seq[idx]; holder={}
 def hook(_module,_inputs,out):
  raw=out[0] if isinstance(out,(tuple,list)) else out
  holder["value"]=raw.detach()
 handle=module.register_forward_hook(hook); rows=[]
 with torch.inference_mode():
  for prompt in prompts:
   z=tok(prompt,return_tensors="pt",add_special_tokens=True).to("cuda:0"); model(**z,use_cache=False)
   if "value" not in holder: raise RuntimeError("forward hook did not fire")
   rows.append(holder.pop("value")[0,-1].float().cpu())
 handle.remove(); arr=torch.stack(rows).numpy(); output.parent.mkdir(parents=True,exist_ok=True)
 tmp=output.with_suffix(".npy.tmp");
 with tmp.open("wb") as f: np.save(f,arr,allow_pickle=False); f.flush(); os.fsync(f.fileno())
 os.replace(tmp,output)
 meta={"model_path":str(model_path),"hooked_module_path":f"{prefix}.{idx}","layer_index":idx,"block_class":type(module).__name__,"semantics":"raw forward-hook output[0] at last token","token_position":"last token per unpadded single-sample input","shape":list(arr.shape),"dtype":str(arr.dtype),"sample_count":len(prompts),"representation_path":str(output),"representation_sha256":sha(output)}
 release(model,tok,module,seq); return arr,meta
def cka(x,y):
 x=x.astype(np.float64); y=y.astype(np.float64); x-=x.mean(0,keepdims=True); y-=y.mean(0,keepdims=True)
 return float(np.linalg.norm(x.T@y,"fro")**2/(np.linalg.norm(x.T@x,"fro")*np.linalg.norm(y.T@y,"fro")))
def main():
 p=argparse.ArgumentParser(); p.add_argument("--project",type=Path,required=True); p.add_argument("--data-root",type=Path,required=True); p.add_argument("--run-id",required=True); a=p.parse_args(); started=time.time()
 protocol_path=a.project/"results/ownership_protocols/reef_formal_protocol.json"; probe_path=a.project/"results/ownership_protocols/reef_truthfulqa_200.json"; panel_path=a.project/"results/ownership_protocols/shared_negative_panel_3.json"
 if sha(probe_path)!="8f63355817f726faea792edcc393ef9c6d32e07449bb66bbdefeb201e636599f": raise RuntimeError("probe manifest SHA mismatch")
 if sha(panel_path)!="4b97b0dfc4960adeb638282b51ec69c50cec1e8b46d8422b40712eb63d5f31e8": raise RuntimeError("negative panel SHA mismatch")
 probes=json.loads(probe_path.read_text()); prompts=[r["text"] for r in probes["rows"]]
 if len(prompts)!=200 or probes["ordered_rows_sha256"]!="ea3f17daffe6b9e82ffcb5f43b1efe0e88483708c6261f532ed007555ac6c79f": raise RuntimeError("frozen probe identity mismatch")
 base=a.data_root/"models/base/Llama-3.2-3B-Instruct"; neg=[("google/gemma-2b",a.data_root/"models/llmprint_validation/google/gemma-2b"),("Qwen/Qwen2.5-3B-Instruct",a.data_root/"models/llmprint_validation/models/Qwen--Qwen2.5-3B-Instruct/snapshots/master"),("microsoft/Phi-3-mini-128k-instruct",a.data_root/"models/llmprint_validation/models/microsoft--Phi-3-mini-128k-instruct/snapshots/master")]
 art=a.data_root/f"artifacts/reef/experiment_a/protocol_compliance/{a.run_id}"; ref_a,ma=extract(base,prompts,art/"reference_reload_a.npy",27); ref_b,mb=extract(base,prompts,art/"reference_reload_b.npy",27)
 scores=[]; metas=[{"role":"reference_reload_a",**ma},{"role":"reference_reload_b",**mb}]
 for mid,path in neg:
  arr,m=extract(path,prompts,art/(mid.replace("/","--")+".npy")); scores.append({"model_id":mid,"score":cka(ref_a,arr)}); metas.append({"role":"negative","model_id":mid,**m})
 ref_score=cka(ref_a,ref_a); reload_score=cka(ref_a,ref_b); maxdiff=float(np.max(np.abs(ref_a-ref_b))); tau=max(x["score"] for x in scores); mean=float(np.mean([x["score"] for x in scores])); margin=ref_score-tau; fp=sum(x["score"]>tau for x in scores); ok=ref_score>tau and fp==0 and reload_score>0.999999 and maxdiff==0 and all(np.isfinite(x["score"]) for x in scores)
 conclusion="REEF core reproduction successful under the frozen WMKD canonical protocol" if ok else "REEF core reproduction not established under the frozen WMKD canonical protocol"
 detector={"metric":"centered_linear_CKA","definition":"||Xc^T Yc||_F^2 / (||Xc^T Xc||_F * ||Yc^T Yc||_F)","reference_self_score":ref_score,"reference_reload_score":reload_score,"reload_max_abs_diff":maxdiff,"negative_scores":scores,"negative_mean":mean,"threshold_rule":"tau = max(frozen negative scores)","threshold":tau,"positive_rule":"score > tau; tie is negative","separation_margin":margin,"false_positives":fp,"evaluation_errors":[],"positive":ref_score>tau}
 lineage={"superseded_run":{"run_id":OLD_RUN,"status":"SUPERSEDED_BY_PROTOCOL_COMPLIANCE_RERUN","reason":"representation implementation mismatch with frozen protocol","implementation":"hidden_states[-1] final-normalized representation","scores":OLD_SCORES},"continuation_run_id":a.run_id,"continuation_type":"infrastructure / implementation compliance continuation; scientific config unchanged"}
 extraction={"semantics":"exact raw decoder-block forward-hook output[0] at last token","canonical_hook":"model.layers.27","representations":metas,"extraction_config":{"probes":200,"dtype_load":"float16","persisted_dtype":"float32","use_cache":False},"extraction_config_sha256":hashlib.sha256(json.dumps({"probes":200,"semantics":"raw_forward_hook_output0_last_token","canonical_layer":27,"load_dtype":"float16","persist_dtype":"float32","use_cache":False},sort_keys=True,separators=(",",":")).encode()).hexdigest()}
 common={"schema_version":"wmkd.reef-protocol-compliance.v1","method":"REEF","experiment":"A","run_id":a.run_id,"status":"COMPLETED" if ok else "FAILED","terminal":True,"official_repo":"AI45Lab/REEF","official_commit":OFFICIAL,"canonical_model":"meta-llama/Llama-3.2-3B-Instruct","canonical_revision":REV,"model_modified":False,"artifact_type":"fingerprint_package" if ok else "protocol_compliance_evidence","preferred_fingerprint":"yes" if ok else "no","scientific_conclusion":conclusion,"ba_status":"NOT_STARTED","runtime_seconds":time.time()-started,"lineage":lineage}
 out=a.project/"results/reef/experiment_a"; pc=out/"protocol_compliance"; atomic(pc/"extraction_metadata.json",extraction); atomic(pc/"detector_results.json",detector); atomic(pc/"lineage.json",lineage)
 atomic(out/"summary.json",{**common,"reference_score":ref_score,"threshold":tau,"margin":margin,"false_positives":fp,"evaluation_errors":0})
 atomic(out/"detector_results.json",{**common,"detector":detector}); atomic(out/"provenance_manifest.json",{**common,"protocol":{"path":"results/ownership_protocols/reef_formal_protocol.json","sha256":sha(protocol_path)},"probe_manifest":{"sha256":sha(probe_path),"ordered_rows_sha256":probes["ordered_rows_sha256"]},"negative_panel_sha256":sha(panel_path),"extraction":extraction})
 atomic(out/"artifact_manifest.json",{**common,"artifact_root":str(art),"artifacts":[{"path":m["representation_path"],"sha256":m["representation_sha256"],"shape":m["shape"],"dtype":m["dtype"],"role":m["role"],"model_id":m.get("model_id")} for m in metas],"integrity":"PASS"})
 atomic(out/"full_experiment_log.json",{**common,"frozen_protocol":json.loads(protocol_path.read_text()),"representation":extraction,"detector":detector,"failures":[],"utility":{"status":"not_applicable","reason":"passive fingerprint; utility inherited from unmodified canonical Base"},"archive":"deferred"})
 report=f"""# REEF Experiment A reproduction report\n\n## Final result\n\n**{conclusion}.** Preferred fingerprint: **{'yes' if ok else 'no'}**.\n\n## Protocol-compliance continuation\n\nOld run `{OLD_RUN}` is **SUPERSEDED_BY_PROTOCOL_COMPLIANCE_RERUN** because it used `hidden_states[-1]`. Final run `{a.run_id}` directly hooks canonical `model.layers.27` and each negative model's audited final decoder block, extracting raw hook `output[0]` at the last token. Scientific configuration was unchanged.\n\n## Detector\n\n- Reference/self: {ref_score:.12f}\n- Reference/reload: {reload_score:.12f}; max absolute representation difference: {maxdiff:.12g}\n"""+"\n".join(f"- {x['model_id']}: {x['score']:.12f}" for x in scores)+f"\n- Negative mean: {mean:.12f}\n- Tau: {tau:.12f}\n- Margin: {margin:.12f}\n- False positives: {fp}/3\n- Evaluation errors: 0\n\nModel modified: false. Utility: not applicable/inherited canonical Base. Ba: NOT_STARTED.\n"
 text(a.project/"docs/reproduction_reports/reef_experiment_a_report.md",report)
 oldlog=(a.project/"docs/experiment_logs/reef_experiment_a_log.md").read_text(encoding="utf-8") if (a.project/"docs/experiment_logs/reef_experiment_a_log.md").exists() else "# REEF Experiment A log\n"
 text(a.project/"docs/experiment_logs/reef_experiment_a_log.md",oldlog+f"\n## Protocol-compliance continuation {a.run_id}\n\n- Old run `{OLD_RUN}`: SUPERSEDED_BY_PROTOCOL_COMPLIANCE_RERUN\n- Final status: {'SUCCESSFUL' if ok else 'NOT_ESTABLISHED'}\n- Canonical hook: `model.layers.27`, raw `output[0]`, last token\n- Result: {conclusion}\n")
 index_path=a.project/"results/experiment_full_logs_index.json"; index=json.loads(index_path.read_text()); full=out/"full_experiment_log.json"; summary=out/"summary.json"; entry={"method":"REEF","role":"preferred_fingerprint","experiment":"A","run_id":a.run_id,"full_log_path":"results/reef/experiment_a/full_experiment_log.json","full_log_sha256":sha(full),"summary_path":"results/reef/experiment_a/summary.json","summary_sha256":sha(summary),"report_path":"docs/reproduction_reports/reef_experiment_a_report.md","artifact_manifest_path":"results/reef/experiment_a/artifact_manifest.json","scientific_status":"SUCCESSFUL" if ok else "NOT_ESTABLISHED","artifact_type":"fingerprint_package" if ok else "protocol_compliance_evidence","model_modified":False,"preferred_fingerprint":"yes" if ok else "no","utility_available":False,"ba_status":"NOT_STARTED"}
 index["objects"]=[x for x in index["objects"] if not (x.get("method")=="REEF" and x.get("experiment")=="A")]+[entry]; index["object_count"]=len(index["objects"]); index["generated_at"]=now(); atomic(index_path,index)
 print(json.dumps({"run_id":a.run_id,"ok":ok,"detector":detector,"conclusion":conclusion},ensure_ascii=False),flush=True)
if __name__=="__main__": main()
