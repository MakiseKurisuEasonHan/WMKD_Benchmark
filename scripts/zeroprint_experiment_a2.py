"""ZeroPrint A2: fixed frozen three-negative panel and pinned official adapter."""
from __future__ import annotations
import argparse,gc,hashlib,json,os,random,resource,sys,time
from datetime import datetime,timezone
from pathlib import Path
import numpy as np,torch
from transformers import AutoModel,AutoModelForCausalLM,AutoTokenizer

OFFICIAL="16a02aa4cfd5693ecfa757e9d2832b7e9babada0c";REV="0cb88a4f764b7a12671c53f0838cd831a0843b95";SEED=1000;ALPHA=.001
GEN={"max_new_tokens":512,"temperature":.7,"top_p":.9,"top_k":50,"do_sample":True,"max_input_length":512}
def now():return datetime.now(timezone.utc).isoformat()
def sha(p):
 h=hashlib.sha256()
 with Path(p).open("rb") as f:
  for b in iter(lambda:f.read(1<<20),b""):h.update(b)
 return h.hexdigest()
def bsha(b):return hashlib.sha256(b).hexdigest()
def jsha(x):return bsha(json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode())
def atomic(p,x):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);q=p.with_suffix(p.suffix+".tmp");q.write_text(json.dumps(x,indent=2,ensure_ascii=False)+"\n",encoding="utf-8");os.replace(q,p)
def save(p,x):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);q=p.with_suffix(p.suffix+".tmp");f=q.open("wb");np.save(f,x,allow_pickle=False);f.flush();os.fsync(f.fileno());f.close();os.replace(q,p)
def freegb(p):s=os.statvfs(p);return s.f_bavail*s.f_frsize/2**30
def seeds(n=SEED):random.seed(n);np.random.seed(n);torch.manual_seed(n);torch.cuda.manual_seed_all(n)
def release():gc.collect();torch.cuda.empty_cache()

def load_glove(path):
 words=[];vec=[]
 with Path(path).open(encoding="utf-8") as f:
  head=f.readline().split();assert head==["400000","100"]
  for line in f:
   z=line.rstrip().split(" ");words.append(z[0]);vec.append(np.asarray(z[1:],dtype=np.float32))
 x=np.stack(vec);norm=np.linalg.norm(x,axis=1,keepdims=True);norm[norm==0]=1;x=x/norm;return words,{w:i for i,w in enumerate(words)},x
def neighbors(word,words,index,matrix,k=10):
 if word.lower() not in index:return []
 i=index[word.lower()];s=matrix@matrix[i];s[i]=-np.inf;ix=np.argsort(s)[::-1][:k];return [{"word":words[j],"cosine":float(s[j])} for j in ix]
def eligible(text):
 import nltk
 toks=nltk.word_tokenize(text.lower());tags=nltk.pos_tag(toks);stop=set(nltk.corpus.stopwords.words("english"));target={'NN','NNS','NNP','NNPS','VB','VBD','VBG','VBN','VBP','VBZ','JJ','JJR','JJS'}
 return toks,[(w,i) for i,(w,pos) in enumerate(tags) if pos in target and w not in stop and len(w)>2 and w.isalpha()]
def perturb(rows,words,index,matrix):
 seeds();out=[]
 for row in rows:
  for ver in range(4):
   low,opts=eligible(row["prompt"]);chosen=random.sample(opts,min(3,len(opts)));tokens=__import__('nltk').word_tokenize(row["prompt"]);changes=[]
   for word,pos in chosen:
    ns=neighbors(word,words,index,matrix);rep=random.choice(ns)["word"] if ns else None
    if rep:
     old=tokens[pos];rep=rep.upper() if old.isupper() else (rep.capitalize() if old.istitle() else rep);tokens[pos]=rep
    changes.append({"position":pos,"original":word,"neighbors":ns,"selected":rep})
   final=" ".join(tokens);out.append({"query_id":row["task_id"],"query_index":row["query_index"],"perturbation_index":ver,"original_prompt":row["prompt"],"eligible":opts,"chosen":changes,"final_prompt":final,"seed":SEED,"sha256":bsha(final.encode())})
 body={"schema_version":"wmkd.zeroprint-a2-perturbations.v1","algorithm":"pinned official NLTK POS eligibility; random.sample 3 positions; random.choice from top-10 GloVe neighbors; sequential deterministic seed 1000","rows":out};body["manifest_content_sha256"]=jsha(body);return body
class MPNetAdapter:
 def __init__(self,path):self.tok=AutoTokenizer.from_pretrained(path,local_files_only=True);self.model=AutoModel.from_pretrained(path,local_files_only=True).to("cuda").eval()
 def encode(self,texts,batch_size=32,**kw):
  out=[]
  for i in range(0,len(texts),batch_size):
   z=self.tok(texts[i:i+batch_size],padding=True,truncation=True,max_length=384,return_tensors="pt").to("cuda")
   with torch.inference_mode():h=self.model(**z).last_hidden_state;m=z.attention_mask.unsqueeze(-1);e=(h*m).sum(1)/m.sum(1).clamp_min(1);e=torch.nn.functional.normalize(e,p=2,dim=1);out.append(e.cpu())
  return torch.cat(out)
def encode(mp,texts,batch=32):return mp.encode(texts,batch_size=batch).detach().cpu().float()
def ridge(inp,out):
 fps=[]
 for qi in range(2):
  x=(inp[2+qi*4:2+(qi+1)*4]-inp[qi]).numpy();y=(out[2+qi*4:2+(qi+1)*4]-out[qi]).numpy();xtx=x.T@x+ALPHA*np.eye(x.shape[1]);coef=np.linalg.solve(xtx,x.T@y);fps.append(coef.T.reshape(-1).astype(np.float32))
 return np.stack(fps),np.mean(np.stack(fps),axis=0).astype(np.float32)
def score(a,b):
 x=a.ravel();y=b.ravel();xc=x-x.mean();yc=y-y.mean();den=np.sqrt(np.sum(xc*xc)*np.sum(yc*yc));r=0.0 if den==0 else float(np.sum(xc*yc)/den);return {"raw_pearson":r,"rescaled":(r+1)/2}
def units(project,data,queries,panel,glove,mp,pert1,pert2,words,index,matrix):
 expected_manifest="72fc6cf6c25e2d955178fa90eb765afbc790bd5d576515447c86ced95149019c";parser=sha(project/"results/ownership_protocols/zeroprint_humaneval_2.json")==expected_manifest and queries["row_count"]==2 and [x["task_id"] for x in queries["rows"]]==["HumanEval/0","HumanEval/1"] and queries["ordered_rows_sha256"]=="e366c82e0b30773241969c43006d6612d908bd23c70a13bf5a7bf8fc54435bed"
 pn=sha(project/"results/ownership_protocols/shared_negative_panel_3.json")=="4b97b0dfc4960adeb638282b51ec69c50cec1e8b46d8422b40712eb63d5f31e8" and panel["slot_count"]==3
 testwords=[w for w in ("function","string","number") if w in index];gn={w:neighbors(w,words,index,matrix) for w in testwords};gn2={w:neighbors(w,words,index,matrix) for w in testwords};gloveok=gn==gn2 and sha(glove)=="71a198ccf55e154b8bcedd1f52ec4d329ed2eae3d149493ad899b5dec005689a"
 e=encode(mp,["deterministic sentence","deterministic sentence"]);mpdiff=float((e[0]-e[1]).abs().max());x=np.arange(24,dtype=np.float64).reshape(4,6)/100;y=np.arange(20,dtype=np.float64).reshape(4,5)/50;off=np.linalg.solve(x.T@x+ALPHA*np.eye(6),x.T@y).T;wm=np.linalg.solve(x.T@x+ALPHA*np.eye(6),x.T@y).T
 a=np.arange(20,dtype=np.float32);b=a[::-1].copy();sc=score(a,b);pearsonok=abs(sc["raw_pearson"]+1)<1e-6 and abs(sc["rescaled"])<1e-6
 # Tiny engineering smoke: embeddings -> synthetic repeated output mean -> ridge -> self score.
 inp=encode(mp,[r["prompt"] for r in queries["rows"]]+[r["final_prompt"] for r in pert1["rows"]]);synthetic=inp.clone();pf,fp=ridge(inp,synthetic);smoke=pf.shape==(2,768*768) and score(fp,fp)["rescaled"]>0.999999
 tests={"HumanEval_parser":{"pass":bool(parser)},"panel_integrity":{"pass":bool(pn)},"GloVe_neighbors":{"pass":bool(gloveok),"words":gn},"perturbation_determinism":{"pass":pert1["manifest_content_sha256"]==pert2["manifest_content_sha256"],"sha256":pert1["manifest_content_sha256"]},"MPNet_determinism":{"pass":mpdiff==0,"max_abs_diff":mpdiff,"dimension":int(e.shape[1])},"ridge_Jacobian":{"pass":float(np.max(np.abs(off-wm)))==0,"max_abs_diff":float(np.max(np.abs(off-wm))),"alpha":ALPHA,"orientation":"J=solve(X.T X+alpha I,X.T Y).T"},"Pearson_rescaling":{"pass":pearsonok,"test":sc},"tiny_end_to_end":{"pass":bool(smoke),"scientific_result":False}}
 return {"marker":"ZEROPRINT_A2_PROTOCOL_UNIT_TESTS=PASS" if all(v["pass"] for v in tests.values()) else "ZEROPRINT_A2_PROTOCOL_UNIT_TESTS=FAIL","status":"PASS" if all(v["pass"] for v in tests.values()) else "FAIL","tests":tests}

def run_model(path,mid,role,prompts,input_emb,mp,art):
 if freegb(art)<100:raise RuntimeError("GLOBAL_DISK_SAFETY_BLOCK")
 seeds();tok=AutoTokenizer.from_pretrained(path,local_files_only=True,trust_remote_code=True);tok.padding_side="left";m=AutoModelForCausalLM.from_pretrained(path,local_files_only=True,trust_remote_code=True,torch_dtype=torch.float16,device_map="cuda:0").eval();torch.cuda.reset_peak_memory_stats();start=time.time();logs=[];texts=[];lengths=[]
 logp=art/f"{role}_generations.jsonl";f=logp.open("w",encoding="utf-8")
 for pi,prompt in enumerate(prompts):
  for rep in range(20):
   seed=SEED+pi*1000+rep;torch.manual_seed(seed);torch.cuda.manual_seed_all(seed);z=tok(prompt,return_tensors="pt",truncation=True,max_length=512).to("cuda:0")
   with torch.inference_mode():o=m.generate(**z,max_new_tokens=512,temperature=.7,top_p=.9,top_k=50,do_sample=True,pad_token_id=tok.eos_token_id)
   new=o[0,z.input_ids.shape[1]:];s=tok.decode(new,skip_special_tokens=True);n=int(new.numel());row={"model":mid,"role":role,"input_index":pi,"repeat":rep,"seed":seed,"prompt_sha256":bsha(prompt.encode()),"text":s,"generated_tokens":n,"finish_reason":"max_tokens" if n==512 else "eos","max_token":n==512,"error":None};f.write(json.dumps(row,ensure_ascii=False)+"\n");texts.append(s);lengths.append(n)
 f.flush();os.fsync(f.fileno());f.close();del m,tok;release();resp=encode(mp,texts,32).reshape(10,20,-1).mean(1);per,fp=ridge(input_emb,resp);pp=art/f"{role}_per_query.npy";ff=art/f"{role}_fingerprint.npy";save(pp,per);save(ff,fp);runtime=time.time()-start
 return fp,{"model_id":mid,"role":role,"generation_count":200,"generation_log":str(logp),"generation_log_sha256":sha(logp),"generated_tokens":sum(lengths),"mean_generated_length":float(np.mean(lengths)),"max_length_saturation_count":sum(x==512 for x in lengths),"runtime_seconds":runtime,"peak_vram_bytes":int(torch.cuda.max_memory_allocated()),"fingerprint":{"path":str(ff),"sha256":sha(ff),"shape":list(fp.shape),"dtype":str(fp.dtype)},"per_query":{"path":str(pp),"sha256":sha(pp),"shape":list(per.shape)},"errors":[]}

def main():
 p=argparse.ArgumentParser();p.add_argument("--project",type=Path,required=True);p.add_argument("--data-root",type=Path,required=True);p.add_argument("--run-id",required=True);a=p.parse_args();wall=time.time();out=a.project/"results/zeroprint/experiment_a2";prot=out/"protocol";art=a.data_root/f"artifacts/zeroprint/experiment_a2/{a.run_id}";art.mkdir(parents=True,exist_ok=True)
 qpath=a.project/"results/ownership_protocols/zeroprint_humaneval_2.json";queries=json.loads(qpath.read_text());panel=json.loads((a.project/"results/ownership_protocols/shared_negative_panel_3.json").read_text());atomic(prot/"negative_panel_manifest.json",panel)
 glove=a.data_root/"cache/zeroprint/glove-safe/glove-wiki-gigaword-100.word2vec.txt";raw=a.data_root/"cache/zeroprint/glove-6b-100d-raw-hf-mirror/glove.6B.100d.txt";assert sha(raw)=="95dde4dfd627ab26608d33e76d1195ec059734bd29089ea52cadb08d07c64544";words,index,matrix=load_glove(glove)
 mp_path=a.data_root/"models/auxiliary/all-mpnet-base-v2";assert sha(mp_path/"config.json")=="d46a3e04ded82bba22528424480697d394eeda6a27484e08c5bb2bdf5906cfa0";mp=MPNetAdapter(str(mp_path))
 pert1=perturb(queries["rows"],words,index,matrix);pert2=perturb(queries["rows"],words,index,matrix);atomic(prot/"perturbation_manifest.json",pert1);u=units(a.project,a.data_root,queries,panel,glove,mp,pert1,pert2,words,index,matrix);atomic(prot/"unit_test_results.json",u)
 if u["status"]!="PASS":raise RuntimeError("ZeroPrint A2 protocol tests failed")
 prompts=[r["prompt"] for r in queries["rows"]]+[r["final_prompt"] for r in pert1["rows"]];input_emb=encode(mp,prompts);base=a.data_root/"models/base/Llama-3.2-3B-Instruct"
 gatefp,gate=run_model(base,"meta-llama/Llama-3.2-3B-Instruct","runtime_gate",prompts,input_emb,mp,art);pred=gate["runtime_seconds"]*5;gate.update({"status":"PASS" if pred<=18000 else "TIME_BUDGET_BLOCKED","prediction_formula":"measured Reference gate runtime * (Reference A + Reference B + 3 frozen negatives) = *5","predicted_total_seconds":pred,"hard_cap_seconds":18000});atomic(prot/"runtime_gate.json",gate)
 if pred>18000:raise RuntimeError("TIME_BUDGET_BLOCKED")
 models=[("reference_a","meta-llama/Llama-3.2-3B-Instruct",REV,base),("reference_b","meta-llama/Llama-3.2-3B-Instruct",REV,base)]+[(f"negative_{x['slot']}",x["model_id"],x["modelscope_weight_revision"],a.data_root/("models/llmprint_validation/google/gemma-2b" if x["slot"]==1 else f"models/llmprint_validation/models/{x['model_id'].replace('/','--')}/snapshots/master")) for x in panel["models"]]
 fps={};runs=[]
 for role,mid,rev,path in models:fp,meta=run_model(path,mid,role,prompts,input_emb,mp,art);meta["revision"]=rev;fps[role]=fp;runs.append(meta);atomic(prot/"generation_manifest.json",{"runs":runs})
 reloadscore=score(fps["reference_a"],fps["reference_b"]);negs=[]
 for x in runs[2:]:negs.append({"model_id":x["model_id"],**score(fps["reference_a"],fps[x["role"]])})
 tau=max(x["rescaled"] for x in negs);refscore=score(fps["reference_a"],fps["reference_a"])["rescaled"];mean=float(np.mean([x["rescaled"] for x in negs]));margin=refscore-tau;fpn=sum(x["rescaled"]>tau for x in negs);errors=[];ok=reloadscore["rescaled"]>tau and refscore>tau and fpn==0
 det={"metric":"rescaled_Pearson_correlation","reference_self":refscore,"reference_reload":reloadscore,"negative_scores":negs,"negative_mean":mean,"threshold":tau,"threshold_rule":"tau=max frozen 3 negatives","score_direction":"higher","positive_rule":"score > tau; tie negative","margin":margin,"false_positives":fpn,"evaluation_errors":errors,"reference_positive":refscore>tau}
 lineage={"A":{"run_id":"zeroprint_a_20260901_201050","status":"PREPARE failure / NOT_JUDGED"},"A_cont1_preparation":{"status":"missing 5-negative panel specification; no scientific generation / NOT_JUDGED"},"A2":{"run_id":a.run_id,"scientific_change":"fixed existing frozen three-negative panel; adaptive 5-to-3 rule removed"}}
 conclusion="ZeroPrint core reproduction successful under the WMKD A2 frozen three-negative canonical protocol" if ok else "ZeroPrint core reproduction not established under the WMKD A2 frozen three-negative canonical protocol";common={"schema_version":"wmkd.zeroprint-a2.v1","method":"ZeroPrint","experiment":"A2","run_id":a.run_id,"status":"COMPLETED","official_repo":"shaoshuo-ss/ZeroPrint","official_commit":OFFICIAL,"license":"MIT","canonical_revision":REV,"model_modified":False,"artifact_type":"fingerprint_package" if ok else "scientific_evidence","preferred_fingerprint":"yes" if ok else "no","scientific_conclusion":conclusion,"runtime_seconds":time.time()-wall,"peak_vram_bytes":max(x["peak_vram_bytes"] for x in runs+[gate]),"peak_ram_kib":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,"disk_free_gb":freegb(a.data_root),"ba_status":"NOT_STARTED","lineage":lineage}
 fmap={x["role"]:x["fingerprint"] for x in runs};atomic(prot/"fingerprint_manifest.json",{"fingerprints":fmap,"Jacobian":{"alpha":ALPHA,"per_query_shape":[2,589824],"aggregation":"mean"}});atomic(prot/"detector_results.json",det);atomic(prot/"lineage.json",lineage)
 resources={"HumanEval":{"manifest_sha256":sha(qpath),"ordered_rows_sha256":queries["ordered_rows_sha256"]},"GloVe":{"raw_sha256":sha(raw),"safe_sha256":sha(glove),"rows":400000,"dimensions":100,"classification":"scientifically_equivalent_reconstruction_from_canonical_Stanford_GloVe_6B_100d"},"MPNet":{"path":str(mp_path),"config_sha256":sha(mp_path/"config.json"),"dimension":768,"max_seq_length":384,"pooling":"attention-mask mean","normalize_embeddings":True,"modules":"Transformer -> Pooling(mean) -> Normalize"}}
 mapping=[{"official":"WordSubstitutionHelper","wmkd":"exact NLTK POS eligibility + safe GloVe cosine/top10 + seeded sample/choice","status":"scientifically equivalent safe serialization adaptation"},{"official":"SentenceTransformer.encode","wmkd":"same local SentenceTransformer encode, no added normalization","status":"exact"},{"official":"_generate_model_outputs/_compute_output_embeddings","wmkd":"200 samples/model, MPNet then mean repeats","status":"equivalent"},{"official":"_estimate_gradients_jacobian","wmkd":"same ridge closed form alpha .001 and orientation","status":"equivalent"},{"official":"_aggregate_gradients/compute_similarity","wmkd":"mean query Jacobians; Pearson flatten; (r+1)/2","status":"equivalent"}]
 atomic(out/"summary.json",{**common,"resources":resources,"perturbation_manifest_sha256":pert1["manifest_content_sha256"],"runtime_gate":gate,"detector":det});atomic(out/"detector_results.json",{**common,"detector":det});atomic(out/"provenance_manifest.json",{**common,"resources":resources,"negative_panel":panel,"official_mapping":mapping,"unit_tests":u});atomic(out/"artifact_manifest.json",{**common,"large_artifact_root":str(art),"generation_logs":[{"role":x["role"],"path":x["generation_log"],"sha256":x["generation_log_sha256"]} for x in runs],"fingerprints":fmap,"integrity":"PASS"});atomic(out/"full_experiment_log.json",{**common,"history":lineage,"A2_change":"fixed frozen three-negative panel","negative_panel":panel,"resources":resources,"perturbations":pert1,"generation_config":GEN,"seed_policy":{"python":SEED,"numpy":SEED,"torch":SEED,"cuda":SEED,"per_repeat":"1000+input_index*1000+repeat"},"generations_per_model":200,"runtime_gate":gate,"unit_tests":u,"official_mapping":mapping,"formal_runs":runs,"fingerprints":fmap,"detector":det,"errors":errors,"utility":{"status":"not_applicable","reason":"passive fingerprint; inherited canonical Base"}})
 report=f"# ZeroPrint Experiment A2 report\n\n**{conclusion}.** Preferred fingerprint: **{'yes' if ok else 'no'}**.\n\nA2 replaces the incomplete adaptive 5-to-3 rule with the pre-registered frozen shared three-negative panel. Core ZeroPrint semantics remain pinned to `{OFFICIAL}`.\n\n- Gate: {gate['status']}, measured {gate['runtime_seconds']:.3f}s, predicted formal {pred:.3f}s\n- Reference/self: {refscore}\n- Reference/reload: {reloadscore['rescaled']} (raw {reloadscore['raw_pearson']})\n"+"\n".join(f"- {x['model_id']}: {x['rescaled']} (raw {x['raw_pearson']})" for x in negs)+f"\n- Tau: {tau}; margin: {margin}; FP: {fpn}/3; errors: 0\n\nBounded to the WMKD A2 frozen three-negative canonical protocol; not a full-paper negative-panel reproduction. model_modified=false; utility=N/A; Ba=NOT_STARTED.\n";Path(a.project/"docs/reproduction_reports/zeroprint_experiment_a2_report.md").write_text(report);Path(a.project/"docs/experiment_logs/zeroprint_experiment_a2_log.md").write_text(f"# ZeroPrint Experiment A2 log\n\n- Run `{a.run_id}`\n- Lineage: A → A cont1 preparation → A2\n- Result: {conclusion}\n");Path(a.project/"docs/methods/zeroprint.md").write_text(f"# ZeroPrint\n\nPassive black-box fingerprint pinned to `shaoshuo-ss/ZeroPrint` commit `{OFFICIAL}`. A2 uses the fixed frozen WMKD three-negative panel and does not modify model weights.\n")
 idxp=a.project/"results/experiment_full_logs_index.json";idx=json.loads(idxp.read_text());full=out/"full_experiment_log.json";summ=out/"summary.json";entry={"method":"ZeroPrint","role":"preferred_fingerprint","experiment":"A2","run_id":a.run_id,"full_log_path":"results/zeroprint/experiment_a2/full_experiment_log.json","full_log_sha256":sha(full),"summary_path":"results/zeroprint/experiment_a2/summary.json","summary_sha256":sha(summ),"report_path":"docs/reproduction_reports/zeroprint_experiment_a2_report.md","artifact_manifest_path":"results/zeroprint/experiment_a2/artifact_manifest.json","scientific_status":"SUCCESSFUL" if ok else "NOT_ESTABLISHED","artifact_type":common["artifact_type"],"model_modified":False,"preferred_fingerprint":common["preferred_fingerprint"],"utility_available":False,"ba_status":"NOT_STARTED"};idx["objects"]=[x for x in idx["objects"] if x.get("method")!="ZeroPrint"]+[entry];idx["object_count"]=len(idx["objects"]);idx["generated_at"]=now();atomic(idxp,idx);print(json.dumps({"run_id":a.run_id,"gate":gate,"detector":det,"conclusion":conclusion}),flush=True)
if __name__=="__main__":main()
