"""Bounded HuRef scaling and ZeroPrint official-budget gates.

This module never writes model weights and never produces a formal detector result.
"""
from __future__ import annotations

import argparse, collections, hashlib, json, os, time
from pathlib import Path
import numpy as np
import torch
from transformers import AutoModel, AutoModelForCausalLM, AutoTokenizer


def atomic(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()


def iter_text(path: Path):
    with path.open(encoding="utf-8", errors="replace") as f:
        for line in f:
            try: obj=json.loads(line)
            except Exception: continue
            if isinstance(obj, dict):
                for key in ("text", "prompt", "instruction", "input", "output", "response"):
                    value=obj.get(key)
                    if isinstance(value, str) and value.strip(): yield value


def build_tokens(args) -> None:
    tok=AutoTokenizer.from_pretrained(args.model, local_files_only=True)
    counts=collections.Counter(); documents=0
    for text in iter_text(args.corpus):
        counts.update(tok.encode(text, add_special_tokens=False)); documents += 1
        if documents >= args.max_documents: break
    special=set(tok.all_special_ids)
    ranked=sorted(((n,i) for i,n in counts.items() if i not in special), key=lambda x:(-x[0],x[1]))
    rows=[{"rank":r,"token_id":i,"count":n,"token":tok.decode([i])} for r,(n,i) in enumerate(ranked[:args.max_k])]
    payload={"schema_version":"wmkd.huref-sorted-tokens.v1","corpus":str(args.corpus),"corpus_sha256":sha(args.corpus),"documents_read":documents,"tokenizer":str(args.model),"sorting":"descending corpus token frequency then ascending token ID","filter":"exclude tokenizer all_special_ids","max_k":args.max_k,"rows":rows}
    atomic(args.output,payload); print(json.dumps({"status":"COMPLETED","tokens":len(rows),"output":str(args.output)}))


def huref_terms(model, ids: list[int]):
    x=model.model.embed_tokens.weight.detach()[ids].float(); means=[]; shapes=[]
    for block in model.model.layers[-2:]:
        a=block.self_attn; mlp=block.mlp
        q=a.q_proj.weight.detach().float(); k=a.k_proj.weight.detach().float(); v=a.v_proj.weight.detach().float(); o=a.o_proj.weight.detach().float()
        if k.shape[0] != q.shape[0]:
            k=k.repeat_interleave(q.shape[0]//k.shape[0],dim=0); v=v.repeat_interleave(q.shape[0]//v.shape[0],dim=0)
        for term in (x@q.T@k@x.T, x@v.T@o.T@x.T, x@(mlp.gate_proj.weight.detach().float().T*mlp.up_proj.weight.detach().float().T)@mlp.down_proj.weight.detach().float().T@x.T):
            means.append(float(term.mean())); shapes.append(list(term.shape)); del term
    return means,shapes


def huref_gate(args) -> None:
    token_package=json.loads(args.tokens.read_text(encoding="utf-8")); all_ids=[r["token_id"] for r in token_package["rows"]]
    model=AutoModelForCausalLM.from_pretrained(args.model,local_files_only=True,torch_dtype=torch.float16).to("cuda:0").eval()
    points=[]
    for k in args.k:
        if len(all_ids)<k: raise RuntimeError(f"sorted token list has {len(all_ids)} < {k}")
        torch.cuda.empty_cache(); torch.cuda.reset_peak_memory_stats(); started=time.perf_counter()
        means,shapes=huref_terms(model,all_ids[:k]); torch.cuda.synchronize(); runtime=time.perf_counter()-started
        points.append({"k":k,"runtime_seconds":runtime,"peak_vram_bytes":int(torch.cuda.max_memory_allocated()),"term_shapes":shapes,"mean_pooling_feature":means})
        print(json.dumps(points[-1]),flush=True)
    ks=np.asarray([p["k"] for p in points],dtype=float); ts=np.asarray([p["runtime_seconds"] for p in points],dtype=float)
    coef=np.polyfit(ks*ks,ts,1)
    projections={str(k):float(max(0,coef[0]*k*k+coef[1])) for k in (1024,2048,4096)}
    feasible=[k for k in (4096,2048,1024) if projections[str(k)] <= 5*3600]
    selected=max(feasible) if feasible else None
    payload={"schema_version":"wmkd.huref-scaling-gate.v1","status":"COMPLETED" if selected else "TIME_BUDGET_BLOCKED","points":points,"fit":"least_squares runtime = a*K^2+b","projections_seconds":projections,"selected_k":selected,"experiment":"A" if selected==4096 else ("A2" if selected else None),"token_manifest":str(args.tokens),"token_manifest_sha256":sha(args.tokens),"model_modified":False,"scientific_semantics_changed":selected not in (None,4096)}
    atomic(args.output,payload)


def mean_pool(hidden,mask):
    return (hidden*mask.unsqueeze(-1)).sum(1)/mask.sum(1,keepdim=True).clamp_min(1)


def zeroprint_gate(args) -> None:
    data=json.loads(args.queries.read_text(encoding="utf-8")); base=data["queries"][:2]
    queries=[]
    for row in base:
        queries.extend([row["prompt"]]+row["perturbations"][:4])
    if len(queries)!=10: raise RuntimeError("gate requires 2 x (1 base + 4 perturbations)")
    tok=AutoTokenizer.from_pretrained(args.model,local_files_only=True); model=AutoModelForCausalLM.from_pretrained(args.model,local_files_only=True,torch_dtype=torch.float16).to("cuda:0").eval()
    expanded=[q for q in queries for _ in range(20)]; outputs=[]; generated=0; torch.cuda.reset_peak_memory_stats(); start=time.perf_counter()
    for i in range(0,len(expanded),args.batch_size):
        z=tok(expanded[i:i+args.batch_size],padding=True,truncation=True,return_tensors="pt").to("cuda:0")
        with torch.no_grad(): y=model.generate(**z,max_new_tokens=args.max_new_tokens,do_sample=True,temperature=args.temperature,top_p=args.top_p,top_k=args.top_k,pad_token_id=tok.eos_token_id)
        for j,row in enumerate(y):
            new=row[z.input_ids.shape[1]:]; generated += int(new.numel()); outputs.append(tok.decode(new,skip_special_tokens=True))
    torch.cuda.synchronize(); generation_seconds=time.perf_counter()-start; del model; torch.cuda.empty_cache()
    et=AutoTokenizer.from_pretrained(args.embedding_model,local_files_only=True); em=AutoModel.from_pretrained(args.embedding_model,local_files_only=True).to("cuda:0").eval(); estart=time.perf_counter(); vectors=[]
    for i in range(0,len(outputs),64):
        e=et(outputs[i:i+64],padding=True,truncation=True,return_tensors="pt").to("cuda:0")
        with torch.no_grad(): vectors.append(mean_pool(em(**e).last_hidden_state,e.attention_mask).cpu())
    vec=torch.cat(vectors).reshape(10,20,-1).mean(1); jac=vec.reshape(2,5,-1)[:,1:]-vec.reshape(2,5,-1)[:,:1]; fingerprint=jac.mean((0,1)); embedding_seconds=time.perf_counter()-estart
    runtime=generation_seconds+embedding_seconds; per_model=runtime; payload={"schema_version":"wmkd.zeroprint-official-budget-gate.v1","status":"COMPLETED","base_queries":2,"perturbations_per_query":4,"repeats":20,"total_generations":len(outputs),"generated_tokens":generated,"generation_seconds":generation_seconds,"embedding_and_jacobian_seconds":embedding_seconds,"total_seconds":runtime,"generated_tokens_per_second":generated/generation_seconds,"projected_seconds":{"reference_plus_3_negatives":per_model*4,"reference_plus_5_negatives":per_model*6},"recommended_negative_count":5 if per_model*6<=5*3600 else (3 if per_model*4<=5*3600 else None),"fingerprint_dimension":int(fingerprint.numel()),"peak_vram_bytes":int(torch.cuda.max_memory_allocated()),"model_modified":False,"query_manifest":str(args.queries),"query_manifest_sha256":sha(args.queries)}
    if payload["recommended_negative_count"] is None: payload["status"]="TIME_BUDGET_BLOCKED"
    atomic(args.output,payload); print(json.dumps(payload))


def main():
    p=argparse.ArgumentParser(); sub=p.add_subparsers(dest="mode",required=True)
    x=sub.add_parser("build-tokens"); x.add_argument("--model",type=Path,required=True); x.add_argument("--corpus",type=Path,required=True); x.add_argument("--max-documents",type=int,default=10000); x.add_argument("--max-k",type=int,default=4096); x.add_argument("--output",type=Path,required=True); x.set_defaults(fn=build_tokens)
    x=sub.add_parser("huref"); x.add_argument("--model",type=Path,required=True); x.add_argument("--tokens",type=Path,required=True); x.add_argument("--k",type=int,nargs="+",default=[128,256,512,1024]); x.add_argument("--output",type=Path,required=True); x.set_defaults(fn=huref_gate)
    x=sub.add_parser("zeroprint"); x.add_argument("--model",type=Path,required=True); x.add_argument("--embedding-model",type=Path,required=True); x.add_argument("--queries",type=Path,required=True); x.add_argument("--batch-size",type=int,default=8); x.add_argument("--max-new-tokens",type=int,default=32); x.add_argument("--temperature",type=float,default=0.7); x.add_argument("--top-p",type=float,default=0.9); x.add_argument("--top-k",type=int,default=50); x.add_argument("--output",type=Path,required=True); x.set_defaults(fn=zeroprint_gate)
    a=p.parse_args(); a.fn(a)

if __name__=="__main__": main()
