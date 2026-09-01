"""Formal passive-ownership Experiment A runner.

The frozen JSON protocols are executable contracts.  Any mismatch or unavailable
resource terminates only the current method and is recorded; it is never repaired
by changing scientific semantics.
"""
from __future__ import annotations
import argparse, gc, hashlib, json, os, platform, subprocess, sys, time, traceback
from datetime import datetime, timezone
from pathlib import Path
import numpy as np

REV="0cb88a4f764b7a12671c53f0838cd831a0843b95"
COMMITS={"reef":"48329f6f3695a8aea33975832159e7ce44ad73f9","awm":"bc20ff8e63cec57f5da422ae065686ced275e76d","huref":"9c34548a6f6c1e78780e1fd07de56c7a3357f6ef","zeroprint":"16a02aa4cfd5693ecfa757e9d2832b7e9babada0c"}
NAMES={"reef":"REEF","awm":"AWM","huref":"HuRef","zeroprint":"ZeroPrint"}
TERMINAL={"COMPLETED","FAILED","BLOCKED","TIME_BUDGET_BLOCKED","GLOBAL_BLOCKED"}
def now(): return datetime.now(timezone.utc).isoformat()
def sha(p):
 h=hashlib.sha256()
 with Path(p).open("rb") as f:
  for b in iter(lambda:f.read(1<<20),b""): h.update(b)
 return h.hexdigest()
def atomic(p,v):
 p=Path(p); p.parent.mkdir(parents=True,exist_ok=True); t=p.with_suffix(p.suffix+".tmp"); t.write_text(json.dumps(v,indent=2,ensure_ascii=False)+"\n",encoding="utf-8"); os.replace(t,p)
def atext(p,v):
 p=Path(p); p.parent.mkdir(parents=True,exist_ok=True); t=p.with_suffix(p.suffix+".tmp"); t.write_text(v,encoding="utf-8"); os.replace(t,p)
def loadj(p): return json.loads(Path(p).read_text(encoding="utf-8"))
def canonical(data): return data/"models/base/Llama-3.2-3B-Instruct"
def negpaths(data):
 return [("google/gemma-2b",data/"models/llmprint_validation/google/gemma-2b"),("Qwen/Qwen2.5-3B-Instruct",data/"models/llmprint_validation/models/Qwen--Qwen2.5-3B-Instruct/snapshots/master"),("microsoft/Phi-3-mini-128k-instruct",data/"models/llmprint_validation/models/microsoft--Phi-3-mini-128k-instruct/snapshots/master")]
def release():
 import torch; gc.collect()
 if torch.cuda.is_available(): torch.cuda.empty_cache()
def env():
 import torch
 return {"python":platform.python_version(),"pytorch":torch.__version__,"cuda":torch.version.cuda,"gpu":torch.cuda.get_device_name(0) if torch.cuda.is_available() else None}
def centered_cka(x,y):
 import torch
 x=x.float(); y=y.float(); x=x-x.mean(0); y=y-y.mean(0); xy=torch.linalg.norm(x.T@y)**2; xx=torch.linalg.norm(x.T@x); yy=torch.linalg.norm(y.T@y); return float((xy/(xx*yy)).cpu())
def reef_fp(path,texts):
 import torch
 from transformers import AutoModelForCausalLM,AutoTokenizer
 tok=AutoTokenizer.from_pretrained(path,local_files_only=True,trust_remote_code=True); m=AutoModelForCausalLM.from_pretrained(path,local_files_only=True,trust_remote_code=True,torch_dtype=torch.float16,device_map="cuda:0").eval()
 acts=[]
 with torch.inference_mode():
  for s in texts:
   z=tok(s,return_tensors="pt",truncation=True).to("cuda:0"); o=m(**z,output_hidden_states=True,use_cache=False); acts.append(o.hidden_states[28][0,-1].float().cpu())
 del m,tok; release(); return torch.stack(acts)
def run_reef(a,proto,raw):
 rows=loadj(a.project/proto["scientific_design"]["probe_manifest"])["rows"]; texts=[r["text"] for r in rows]
 if len(texts)!=200: raise RuntimeError("frozen REEF manifest is not exactly 200 probes")
 ref=reef_fp(canonical(a.data_root),texts); fresh=reef_fp(canonical(a.data_root),texts); ref_score=centered_cka(ref,fresh); scores=[]
 for mid,p in negpaths(a.data_root): scores.append({"model_id":mid,"score":centered_cka(ref,reef_fp(p,texts))})
 tau=max(x["score"] for x in scores); return {"native_metric":"centered_linear_CKA","reference_score":ref_score,"reload_consistency":ref_score,"negative_scores":scores,"threshold":tau,"positive_rule":"score > tau","positive":ref_score>tau,"false_positives":sum(x["score"]>tau for x in scores)}, {"reference_shape":list(ref.shape)}
def load_weights(path):
 from transformers import AutoModelForCausalLM,AutoTokenizer
 import torch
 tok=AutoTokenizer.from_pretrained(path,local_files_only=True,trust_remote_code=True); m=AutoModelForCausalLM.from_pretrained(path,local_files_only=True,trust_remote_code=True,torch_dtype=torch.float16,device_map="cpu").eval()
 q=[b.self_attn.q_proj.weight.detach().float().clone() for b in m.model.layers]; k=[b.self_attn.k_proj.weight.detach().float().clone() for b in m.model.layers]; emb=m.get_input_embeddings().weight.detach().float().clone(); vocab=tok.get_vocab(); del m,tok; release(); return q,k,emb,vocab
def ucka(x,y):
 src=Path("/root/autodl-tmp/WMKD_Benchmark_data/sources/ownership/awm"); sys.path.insert(0,str(src)); from similarity_metrics import cka_from_features
 return float(cka_from_features(x.T,y.T,kernel="linear",unbiased=True,device="cuda"))
def awm_score(ref,cand):
 import torch
 from scipy.optimize import linear_sum_assignment
 rq,rk,re,rv=ref; cq,ck,ce,cv=cand; common=sorted(set(rv)&set(cv)); ri=torch.tensor([rv[w] for w in common]); ci=torch.tensor([cv[w] for w in common]); a=re[ri]; b=ce[ci]
 base_first=a.shape[1]>=b.shape[1]; base,target=(a,b) if base_first else (b,a); sim=torch.nn.functional.normalize(base.T,dim=1)@torch.nn.functional.normalize(target.T,dim=1).T; bi,ti=linear_sum_assignment((1-sim.abs()).numpy()); order=np.argsort(ti); idx=torch.tensor(bi[order]); signs=torch.sign(sim[idx,torch.arange(len(idx))])
 def align(w,first):
  if base.shape[1]==target.shape[1]: return w
  if first==base_first: return w[:,idx]*signs
  return w
 pairs=list(zip(range(len(rq)),range(len(cq)))) if len(rq)==len(cq) else list(zip(*linear_sum_assignment(np.abs(np.subtract.outer(np.arange(len(rq))/len(rq),np.arange(len(cq))/len(cq))))))
 vals=[]
 for i,j in pairs: vals += [ucka(align(rq[i],True),align(cq[j],False)),ucka(align(rk[i],True),align(ck[j],False))]
 return float(np.mean(vals)),{"matched_layers":pairs,"overlap_vocab":len(common),"aligned_dimensions":len(idx)}
def run_awm(a,proto,raw):
 ref=load_weights(canonical(a.data_root)); rs,align=awm_score(ref,ref); scores=[]
 for mid,p in negpaths(a.data_root): cand=load_weights(p); s,info=awm_score(ref,cand); scores.append({"model_id":mid,"score":s,"alignment":info}); del cand; release()
 tau=max(x["score"] for x in scores); return {"native_metric":"official_mean_Wq_Wk_unbiased_linear_CKA","reference_score":rs,"negative_scores":scores,"threshold":tau,"positive_rule":"score > tau","positive":rs>tau,"false_positives":sum(x["score"]>tau for x in scores)},align
def huref_fp(path,ids):
 import torch
 from transformers import AutoModelForCausalLM
 m=AutoModelForCausalLM.from_pretrained(path,local_files_only=True,trust_remote_code=True,torch_dtype=torch.float16,device_map="cuda:0").eval(); x=m.get_input_embeddings().weight.detach()[ids].float(); feats=[]
 for block in m.model.layers[-2:]:
  q=block.self_attn.q_proj.weight.float(); k=block.self_attn.k_proj.weight.float(); v=block.self_attn.v_proj.weight.float(); o=block.self_attn.o_proj.weight.float()
  if k.shape[0]!=q.shape[0]: k=k.repeat_interleave(q.shape[0]//k.shape[0],0); v=v.repeat_interleave(q.shape[0]//v.shape[0],0)
  terms=(x@q.T@k@x.T,x@v.T@o.T@x.T,x@(block.mlp.gate_proj.weight.float().T*block.mlp.up_proj.weight.float().T)@block.mlp.down_proj.weight.float().T@x.T)
  for t in terms: feats.append(t.reshape(512,-1).mean(1).cpu()); del t
 del m; release(); z=torch.cat(feats); return ((z-z.mean())/z.std()).numpy()
def run_huref(a,proto,raw):
 ids=[r["token_id"] for r in loadj(Path(proto["scientific_design"]["token_manifest"]))["rows"]][:4096]
 if len(ids)!=4096: raise RuntimeError("HuRef K=4096 token manifest incomplete")
 ref=huref_fp(canonical(a.data_root),ids); score=lambda x:float(100*np.dot(ref,x)/(np.linalg.norm(ref)*np.linalg.norm(x))); rs=score(huref_fp(canonical(a.data_root),ids)); scores=[]
 for mid,p in negpaths(a.data_root): scores.append({"model_id":mid,"score":score(huref_fp(p,ids))})
 tau=max(x["score"] for x in scores); return {"native_metric":"ICS_percent","reference_score":rs,"negative_scores":scores,"threshold":tau,"positive_rule":"score > tau","positive":rs>tau,"false_positives":sum(x["score"]>tau for x in scores)}, {"K":4096,"layers":[26,27],"terms":["WqWk","WvWo","WuWd"],"feature_shape":list(ref.shape)}
def run_zeroprint(a,proto,raw):
 # Use the pinned official implementation; preparing an ad-hoc approximation is forbidden.
 gate=a.data_root/"gates/zeroprint/formal_runtime_gate.json"; source=a.data_root/"sources/ownership/zeroprint"
 if not gate.exists():
  cmd=[sys.executable,str(a.project/"scripts/ownership_phase0_gates.py"),"zeroprint","--model",str(canonical(a.data_root)),"--embedding-model",str(a.data_root/"models/auxiliary/all-mpnet-base-v2"),"--queries",str(a.project/proto["scientific_design"]["query_manifest"]),"--batch-size","8","--max-new-tokens","512","--output",str(gate)]
  subprocess.run(cmd,check=True)
 g=loadj(gate)
 if g.get("recommended_negative_count") not in (3,5): raise TimeoutError("ZeroPrint runtime gate: even Reference+3 exceeds 5h")
 raise RuntimeError("BLOCKED: pinned official ZeroPrint adapter is unavailable; runtime gate evidence preserved and no approximate fingerprint was substituted")
def close(a,status,reason=None,det=None,raw=None,started=None):
 out=a.project/f"results/{a.method}/experiment_a"; out.mkdir(parents=True,exist_ok=True); scientific="successful" if status=="COMPLETED" and det and det.get("positive") and det.get("false_positives",1)==0 else ("not established" if status=="COMPLETED" else "not judged")
 common={"schema_version":"wmkd.passive-ownership-a.v1","method":a.method,"experiment":"A","run_id":a.run_id,"status":status,"terminal":True,"model_modified":False,"artifact_type":"fingerprint_package" if status=="COMPLETED" else "partial_fingerprint_evidence","preferred_fingerprint":"yes" if scientific=="successful" else "no","ba_status":"NOT_STARTED","scientific_conclusion":scientific,"error":reason}
 atomic(out/"detector_results.json",{**common,"detector":det}); atomic(out/"provenance_manifest.json",{**common,"official_commit":COMMITS[a.method],"canonical_model":"meta-llama/Llama-3.2-3B-Instruct","canonical_revision":REV,"protocol_sha256":sha(a.project/f"results/ownership_protocols/{a.method}_formal_protocol.json"),"environment":env()}); atomic(out/"artifact_manifest.json",{**common,"artifacts":raw or {}}); atomic(out/"summary.json",{**common,"runtime_seconds":time.time()-started if started else None}); atomic(out/"full_experiment_log.json",{**common,"identity":{"official_repo":NAMES[a.method],"official_commit":COMMITS[a.method]},"paper_config":"official pinned semantics","wmkd_config":loadj(a.project/f"results/ownership_protocols/{a.method}_formal_protocol.json"),"detector":det,"fingerprint_extraction":raw,"failures":[] if not reason else [reason],"utility_degradation_attributable_to_experiment_A":"not_applicable","archive":"deferred"})
 title=NAMES[a.method]; atext(a.project/f"docs/methods/{a.method}.md",f"# {title}\n\nPassive ownership fingerprint; official commit `{COMMITS[a.method]}`. Experiment A does not modify model weights.\n"); atext(a.project/f"docs/experiment_logs/{a.method}_experiment_a_log.md",f"# {title} Experiment A log\n\n- Run: `{a.run_id}`\n- Status: **{status}**\n- Error: {reason or 'none'}\n"); atext(a.project/f"docs/reproduction_reports/{a.method}_experiment_a_report.md",f"# {title} Experiment A report\n\n**{status}** — scientific conclusion: **{scientific}**.\n\nDetector: `{json.dumps(det,ensure_ascii=False) if det else 'not completed'}`\n\nBa: NOT_STARTED.\n")
def main():
 p=argparse.ArgumentParser(); p.add_argument("--project",type=Path,required=True); p.add_argument("--data-root",type=Path,required=True); p.add_argument("--method",choices=sorted(NAMES),required=True); p.add_argument("--run-id",required=True); p.add_argument("--close-only",choices=sorted(TERMINAL)); p.add_argument("--reason"); a=p.parse_args(); started=time.time()
 if a.close_only: close(a,a.close_only,a.reason,started=started); return
 try:
  proto=loadj(a.project/f"results/ownership_protocols/{a.method}_formal_protocol.json"); raw={}; det,raw=globals()[f"run_{a.method}"](a,proto,raw); status="COMPLETED"; reason=None
 except TimeoutError as e: status="TIME_BUDGET_BLOCKED"; reason=str(e); det=None; raw={"traceback":traceback.format_exc()}
 except Exception as e: reason=str(e); status="BLOCKED" if reason.startswith("BLOCKED:") else "FAILED"; det=None; raw={"traceback":traceback.format_exc()}
 close(a,status,reason,det,raw,started); print(json.dumps({"method":a.method,"status":status,"run_id":a.run_id}),flush=True)
if __name__=="__main__": main()
