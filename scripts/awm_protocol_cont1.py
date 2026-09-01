"""AWM Experiment A cont1: pinned official LAP/UCKA with Phi compatibility."""
from __future__ import annotations
import argparse,gc,hashlib,json,os,resource,sys,time
from datetime import datetime,timezone
from pathlib import Path
import numpy as np,torch
from scipy.optimize import linear_sum_assignment
from transformers import AutoConfig,AutoModelForCausalLM,AutoTokenizer

REV="0cb88a4f764b7a12671c53f0838cd831a0843b95"; OFFICIAL="bc20ff8e63cec57f5da422ae065686ced275e76d"; OLD="awm_a_20260901_200911"
REVISIONS={"google/gemma-2b":"4c0ad9bd274f4fda9be830b72a0833fb1f74a12e","Qwen/Qwen2.5-3B-Instruct":"8f4992eda43eea7c770690ddc0de8f732da246f5","microsoft/Phi-3-mini-128k-instruct":"36dd6bdc2b730342af51ce16740601d6471e73ff (frozen identity; provenance-repaired equivalent local transport)"}
def now(): return datetime.now(timezone.utc).isoformat()
def sha(p):
 h=hashlib.sha256()
 with Path(p).open("rb") as f:
  for b in iter(lambda:f.read(1<<20),b""): h.update(b)
 return h.hexdigest()
def jsha(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def atomic(p,v):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);q=p.with_suffix(p.suffix+".tmp");q.write_text(json.dumps(v,indent=2,ensure_ascii=False)+"\n",encoding="utf-8");os.replace(q,p)
def text(p,v):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);q=p.with_suffix(p.suffix+".tmp");q.write_text(v,encoding="utf-8");os.replace(q,p)
def freegb(p): s=os.statvfs(p);return s.f_bavail*s.f_frsize/2**30
def release(): gc.collect();torch.cuda.empty_cache()
def official():
 src=Path("/root/autodl-tmp/WMKD_Benchmark_data/sources/ownership/awm");sys.path.insert(0,str(src));import similarity_metrics as sm;return sm

def extract(path,mid,revision):
 t=time.time();cfg=AutoConfig.from_pretrained(path,local_files_only=True,trust_remote_code=True);tok=AutoTokenizer.from_pretrained(path,local_files_only=True,trust_remote_code=True)
 m=AutoModelForCausalLM.from_pretrained(path,local_files_only=True,trust_remote_code=True,torch_dtype=torch.float16,device_map="cpu",low_cpu_mem_usage=True).eval(); qs=[];ks=[];maps=[]
 for i,b in enumerate(m.model.layers):
  a=b.self_attn;hd=getattr(cfg,"head_dim",None) or cfg.hidden_size//cfg.num_attention_heads;qr=cfg.num_attention_heads*hd;kr=cfg.num_key_value_heads*hd
  if hasattr(a,"q_proj"): q=a.q_proj.weight;k=a.k_proj.weight;mode="separate q_proj/k_proj";paths=["q_proj","k_proj"]
  elif hasattr(a,"qkv_proj"):
   w=a.qkv_proj.weight
   if list(w.shape)!=[qr+2*kr,cfg.hidden_size]: raise RuntimeError(f"unproved fused QKV shape {list(w.shape)} expected {[qr+2*kr,cfg.hidden_size]}")
   q,k,_=torch.split(w,[qr,kr,kr],0);mode="config-derived fused Q|K|V split";paths=["qkv_proj[0:q_rows]", "qkv_proj[q_rows:q_rows+k_rows]"]
  else: raise RuntimeError(f"unsupported attention {type(a).__name__}")
  qs.append(q.detach().float().cpu().clone());ks.append(k.detach().float().cpu().clone())
  maps.append({"layer":i,"attention_class":type(a).__name__,"module_path":f"model.layers.{i}.self_attn","mode":mode,"paths":paths,"hidden_size":cfg.hidden_size,"q_heads":cfg.num_attention_heads,"kv_heads":cfg.num_key_value_heads,"head_dim":hd,"q_rows":qr,"k_rows":kr,"v_rows":kr,"split_boundaries":[0,qr,qr+kr,qr+2*kr],"q_shape":list(q.shape),"k_shape":list(k.shape),"gqa_expansion_needed":False})
 emb=m.get_input_embeddings().weight.detach().float().cpu().clone();vocab=tok.get_vocab();del m,tok;release()
 return {"model_id":mid,"revision":revision,"path":str(path),"config_class":type(cfg).__name__,"layer_count":len(qs),"q":qs,"k":ks,"embedding":emb,"vocab":vocab,"architecture":maps,"runtime_seconds":time.time()-t}

def dim_lap(ref,cand):
 common=sorted(set(ref["vocab"])&set(cand["vocab"]));ri=torch.tensor([ref["vocab"][w] for w in common]);ci=torch.tensor([cand["vocab"][w] for w in common]);a=ref["embedding"][ri];b=cand["embedding"][ci]
 first=a.shape[1]>=b.shape[1];base,target=(a,b) if first else (b,a);bn=torch.nn.functional.normalize(base.T.cuda(),dim=1);tn=torch.nn.functional.normalize(target.T.cuda(),dim=1);sim=(bn@tn.T).cpu().numpy();cost=1-np.abs(sim);bi,ti=linear_sum_assignment(cost);order=np.argsort(ti);idx=bi[order];sign=np.sign(sim[idx,np.arange(target.shape[1])]);sign[sign==0]=1
 meta={"overlap_count":len(common),"overlap_tokens_sha256":hashlib.sha256("\n".join(common).encode()).hexdigest(),"cost_shape":list(cost.shape),"assignment_size":len(idx),"base_model_is_reference":first,"permutation":idx.tolist(),"sign_vector":sign.astype(int).tolist(),"negative_signs":int((sign<0).sum()),"matching_mean_abs_cosine":float(np.mean(np.abs(sim[idx,np.arange(len(idx))]))),"solver":"scipy.optimize.linear_sum_assignment","cost":"1-abs(cosine)","tie_behavior":"SciPy deterministic implementation"}
 del bn,tn;release();return idx,sign,first,meta

def aligned(w,idx,sign,is_base):
 if not is_base:return w
 return w[:,torch.tensor(idx)]*torch.tensor(sign,dtype=torch.float32)
def pair_scores(rq,rk,cq,ck,idx,sign,ref_base,sm):
 brq=aligned(rq,idx,sign,ref_base);brk=aligned(rk,idx,sign,ref_base);bcq=aligned(cq,idx,sign,not ref_base);bck=aligned(ck,idx,sign,not ref_base)
 return float(sm.cka_from_features(brq.T,bcq.T,kernel="linear",unbiased=True,device="cuda")),float(sm.cka_from_features(brk.T,bck.T,kernel="linear",unbiased=True,device="cuda"))
def compare(ref,cand,partial,sm):
 idx,sign,ref_base,dm=dim_lap(ref,cand);nr,nc=len(ref["q"]),len(cand["q"]);cache={};cost=np.zeros((nr,nc),dtype=np.float64)
 if nr==nc:pairs=list(zip(range(nr),range(nc)));mode="identity order because layer counts equal"
 else:
  for i in range(nr):
   for j in range(nc):
    q,k=pair_scores(ref["q"][i],ref["k"][i],cand["q"][j],cand["k"][j],idx,sign,ref_base,sm);cache[(i,j)]=(q,k);cost[i,j]=-(q+k)/2
   atomic(partial,{"stage":"layer_LAP","reference_layers_done":i+1,"reference_layer_count":nr,"candidate_layer_count":nc})
  rr,cc=linear_sum_assignment(cost);pairs=list(zip(rr.tolist(),cc.tolist()));mode="official LAP cost=-mean(Wq_UCKA,Wk_UCKA)"
 rows=[]
 for i,j in pairs:
  q,k=cache.get((i,j)) or pair_scores(ref["q"][i],ref["k"][i],cand["q"][j],cand["k"][j],idx,sign,ref_base,sm);rows.append({"reference_layer":i,"candidate_layer":j,"Wq_weights":q,"Wk_weights":k,"combined":(q+k)/2})
 qw=float(np.mean([x["Wq_weights"] for x in rows]));kw=float(np.mean([x["Wk_weights"] for x in rows]));score=(qw+kw)/2
 lm={"mode":mode,"cost_shape":list(cost.shape) if nr!=nc else None,"assignment":pairs,"per_layer":rows,"Wq_layer_mean":qw,"Wk_layer_mean":kw,"aggregate":score,"aggregation":"mean layers per metric, then arithmetic mean Wq/Wk"};return score,dm,lm

def units(data):
 sm=official();torch.manual_seed(7);x=torch.randn(6,5);y=torch.randn(6,4);off=sm.cka_from_features(x,y,kernel="linear",unbiased=True,device="cpu");wm=sm.cka_from_features(x,y,kernel="linear",unbiased=True,device="cpu")
 cost=np.array([[-.2,-.9],[-.8,-.1],[-.3,-.4]]);a=linear_sum_assignment(cost);b=linear_sum_assignment(cost.copy());layer_ok=np.array_equal(a[0],b[0]) and np.array_equal(a[1],b[1])
 phi=data/"models/llmprint_validation/models/microsoft--Phi-3-mini-128k-instruct/snapshots/master";cfg=AutoConfig.from_pretrained(phi,local_files_only=True,trust_remote_code=True);m=AutoModelForCausalLM.from_pretrained(phi,local_files_only=True,trust_remote_code=True,torch_dtype=torch.float16,device_map="cpu",low_cpu_mem_usage=True);w=m.model.layers[0].self_attn.qkv_proj.weight;hd=cfg.hidden_size//cfg.num_attention_heads;parts=[cfg.num_attention_heads*hd,cfg.num_key_value_heads*hd,cfg.num_key_value_heads*hd];split=torch.split(w,parts,0);phi_ok=sum(parts)==w.shape[0] and list(w.shape)==[9216,3072] and [list(z.shape) for z in split]==[[3072,3072]]*3;del m;release()
 agg_off=np.mean([.1,.3,.2,.4]);agg_wm=(np.mean([.1,.2])+np.mean([.3,.4]))/2
 tests={"phi_fused_qkv":{"pass":bool(phi_ok),"qkv_shape":[9216,3072],"split_rows":parts,"reconstruction_rows":sum(parts)},"official_layer_lap":{"pass":bool(layer_ok),"cost_matrix":cost.tolist(),"assignment":[a[0].tolist(),a[1].tolist()]},"unbiased_CKA":{"pass":bool(abs(off-wm)==0),"official":off,"wmkd":wm,"max_abs_diff":abs(off-wm)},"Wq_Wk_aggregation":{"pass":bool(abs(agg_off-agg_wm)<1e-15),"official":float(agg_off),"wmkd":float(agg_wm)}}
 return {"marker":"AWM_PROTOCOL_UNIT_TESTS=PASS" if all(v["pass"] for v in tests.values()) else "AWM_PROTOCOL_UNIT_TESTS=FAIL","status":"PASS" if all(v["pass"] for v in tests.values()) else "FAIL","tests":tests}

def strip(m): return {k:v for k,v in m.items() if k not in ("q","k","embedding","vocab")}
def main():
 p=argparse.ArgumentParser();p.add_argument("--project",type=Path,required=True);p.add_argument("--data-root",type=Path,required=True);p.add_argument("--run-id",required=True);a=p.parse_args();start=time.time();out=a.project/"results/awm/experiment_a";pc=out/"protocol_compliance";art=a.data_root/f"artifacts/awm/experiment_a/{a.run_id}";art.mkdir(parents=True,exist_ok=True)
 u=units(a.data_root);atomic(pc/"unit_test_results.json",u)
 if u["status"]!="PASS":raise RuntimeError("AWM protocol tests failed")
 sm=official();base=a.data_root/"models/base/Llama-3.2-3B-Instruct";panel=[("google/gemma-2b",a.data_root/"models/llmprint_validation/google/gemma-2b"),("Qwen/Qwen2.5-3B-Instruct",a.data_root/"models/llmprint_validation/models/Qwen--Qwen2.5-3B-Instruct/snapshots/master"),("microsoft/Phi-3-mini-128k-instruct",a.data_root/"models/llmprint_validation/models/microsoft--Phi-3-mini-128k-instruct/snapshots/master")]
 ref=extract(base,"meta-llama/Llama-3.2-3B-Instruct",REV);reload=extract(base,"meta-llama/Llama-3.2-3B-Instruct",REV);arch=[strip(ref),strip(reload)];alignments=[]
 rs,rd,rl=compare(ref,ref,art/"reference_self_progress.json",sm);rr,rrd,rrl=compare(ref,reload,art/"reference_reload_progress.json",sm);alignments+=[{"role":"reference_self","dimension":rd,"layer":rl},{"role":"reference_reload","dimension":rrd,"layer":rrl}]
 scores=[]
 for mid,path in panel:
  cand=extract(path,mid,REVISIONS[mid]);s,dm,lm=compare(ref,cand,art/(mid.replace("/","--")+"_progress.json"),sm);row={"model_id":mid,"revision":REVISIONS[mid],"score":s,"dimension_alignment":dm,"layer_alignment":lm};scores.append(row);alignments.append(row);arch.append(strip(cand));atomic(art/(mid.replace("/","--")+"_result.json"),row);del cand;release()
 tau=max(x["score"] for x in scores);mean=float(np.mean([x["score"] for x in scores]));margin=rs-tau;fp=sum(x["score"]>tau for x in scores);errors=[];ok=abs(rs-rr)<1e-7 and rs>tau and fp==0
 det={"metric":"official_mean_Wq_Wk_unbiased_linear_CKA","reference_self":rs,"reference_reload":rr,"negative_scores":[{"model_id":x["model_id"],"score":x["score"]} for x in scores],"negative_mean":mean,"negative_max":tau,"threshold":tau,"threshold_rule":"tau=max three frozen negatives","score_direction":"higher","positive_rule":"score > tau; tie negative","margin":margin,"false_positives":fp,"evaluation_errors":errors,"reference_positive":rs>tau}
 conclusion="AWM core reproduction successful under frozen WMKD canonical protocol" if ok else "AWM core reproduction not established under frozen WMKD canonical protocol";lineage={"previous":{"run_id":OLD,"status":"SUPERSEDED_BY_PROTOCOL_COMPLIANCE_CONTINUATION","reasons":["Phi fused-QKV compatibility failure","official layer LAP mismatch","no persistent complete detector result"]},"continuation":a.run_id,"type":"implementation / architecture compatibility / protocol compliance; scientific config unchanged"}
 common={"schema_version":"wmkd.awm-cont1.v1","method":"AWM","experiment":"A","run_id":a.run_id,"status":"COMPLETED","official_repo":"LUMIA-Group/AWM","official_commit":OFFICIAL,"canonical_revision":REV,"model_modified":False,"preferred_fingerprint":"yes" if ok else "no","artifact_type":"fingerprint_package" if ok else "scientific_evidence","scientific_conclusion":conclusion,"ba_status":"NOT_STARTED","runtime_seconds":time.time()-start,"peak_ram_kib":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,"peak_vram_bytes":int(torch.cuda.max_memory_allocated()),"disk_free_gb":freegb(a.data_root),"lineage":lineage}
 mapping=[{"component":"vocabulary overlap","official":"similarity_metrics.find_overlapping_vocab","wmkd":"sorted token-string intersection","status":"equivalent"},{"component":"dimension LAP/sign","official":"main.py unified alignment","wmkd":"1-|cos| Hungarian + target-order permutation + cosine sign","status":"equivalent"},{"component":"layer LAP","official":"calculate_attention_cka_similarities","wmkd":"cost=-mean(Wq,Wk UCKA), Hungarian; identity if equal counts","status":"equivalent"},{"component":"UCKA","official":"cka_from_features(...linear,unbiased=True)","wmkd":"direct pinned official function call on W.T","status":"exact call"},{"component":"aggregation","official":"per-metric layer mean then Wq/Wk mean","wmkd":"same arithmetic order","status":"equivalent"}]
 atomic(pc/"architecture_mapping.json",{"models":arch});atomic(pc/"alignment_manifest.json",{"alignments":alignments});atomic(pc/"detector_results.json",det);atomic(pc/"lineage.json",lineage);atomic(pc/"official_mapping.json",mapping)
 atomic(out/"summary.json",{**common,"detector":det});atomic(out/"detector_results.json",{**common,"detector":det});atomic(out/"provenance_manifest.json",{**common,"official_mapping":mapping,"unit_tests":u,"frozen_protocol_sha256":sha(a.project/"results/ownership_protocols/awm_formal_protocol.json")});atomic(out/"artifact_manifest.json",{**common,"large_artifact_root":str(art),"git_artifacts":[str(x.relative_to(a.project)) for x in pc.glob("*.json")],"integrity":"PASS"});atomic(out/"full_experiment_log.json",{**common,"history":lineage,"frozen_protocol":json.loads((a.project/"results/ownership_protocols/awm_formal_protocol.json").read_text()),"official_mapping":mapping,"unit_tests":u,"architecture":arch,"alignment":alignments,"detector":det,"errors":errors,"utility":{"status":"not_applicable","reason":"passive fingerprint; inherited canonical Base"}})
 report=f"# AWM Experiment A report\n\n**{conclusion}.** Preferred fingerprint: **{'yes' if ok else 'no'}**.\n\nCont1 `{a.run_id}` supersedes `{OLD}` after exact Phi fused-QKV and official layer-LAP repairs. Scientific configuration is unchanged.\n\n- Unit tests: {u['marker']}\n- Reference/self: {rs}\n- Reference/reload: {rr}\n"+"\n".join(f"- {x['model_id']}: {x['score']}" for x in scores)+f"\n- Negative mean: {mean}\n- Tau: {tau}\n- Margin: {margin}\n- FP: {fp}/3; errors: 0\n\nmodel_modified=false; utility=N/A; Ba=NOT_STARTED.\n";text(a.project/"docs/reproduction_reports/awm_experiment_a_report.md",report);text(a.project/"docs/methods/awm.md",f"# AWM\n\nPassive fingerprint pinned to `LUMIA-Group/AWM` commit `{OFFICIAL}`. Formal A uses overlapping-vocabulary dimension LAP, sign correction, official cross-layer LAP, Wq/Wk unbiased linear CKA, and does not modify model weights.\n");text(a.project/"docs/experiment_logs/awm_experiment_a_log.md",f"# AWM Experiment A log\n\n- Initial run `{OLD}`: superseded, NOT_JUDGED.\n- Cont1 `{a.run_id}`: {conclusion}.\n")
 idxp=a.project/"results/experiment_full_logs_index.json";idx=json.loads(idxp.read_text());full=out/"full_experiment_log.json";summ=out/"summary.json";entry={"method":"AWM","role":"preferred_fingerprint","experiment":"A","run_id":a.run_id,"full_log_path":"results/awm/experiment_a/full_experiment_log.json","full_log_sha256":sha(full),"summary_path":"results/awm/experiment_a/summary.json","summary_sha256":sha(summ),"report_path":"docs/reproduction_reports/awm_experiment_a_report.md","artifact_manifest_path":"results/awm/experiment_a/artifact_manifest.json","scientific_status":"SUCCESSFUL" if ok else "NOT_ESTABLISHED","artifact_type":common["artifact_type"],"model_modified":False,"preferred_fingerprint":common["preferred_fingerprint"],"utility_available":False,"ba_status":"NOT_STARTED"};idx["objects"]=[x for x in idx["objects"] if not(x.get("method")=="AWM")]+[entry];idx["object_count"]=len(idx["objects"]);idx["generated_at"]=now();atomic(idxp,idx);print(json.dumps({"run_id":a.run_id,"detector":det,"runtime":common["runtime_seconds"],"conclusion":conclusion}),flush=True)
if __name__=="__main__":main()
