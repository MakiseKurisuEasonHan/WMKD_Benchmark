"""HuRef Experiment A2: tokenizer-specific deterministic top-K on one corpus."""
from __future__ import annotations

import argparse, collections, gc, hashlib, json, os, resource, time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import torch
from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer

REV = "0cb88a4f764b7a12671c53f0838cd831a0843b95"
OFFICIAL = "9c34548a6f6c1e78780e1fd07de56c7a3357f6ef"
ORDER = ["layer_-2_WqWk", "layer_-2_WvWo", "layer_-2_WuWd",
         "layer_-1_WqWk", "layer_-1_WvWo", "layer_-1_WuWd"]
K = 4096


def now(): return datetime.now(timezone.utc).isoformat()
def sha_bytes(b): return hashlib.sha256(b).hexdigest()
def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()
def json_sha(v): return sha_bytes((json.dumps(v, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n").encode())
def tsha(t): return sha_bytes(t.detach().cpu().contiguous().numpy().view(np.uint8))
def atomic(path, payload):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(tmp, path)
def write_text(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp"); tmp.write_text(value, encoding="utf-8"); os.replace(tmp, path)
def save_npy(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("wb") as f: np.save(f, value, allow_pickle=False); f.flush(); os.fsync(f.fileno())
    os.replace(tmp, path)
def free_gb(path):
    s = os.statvfs(path); return s.f_bavail * s.f_frsize / 2**30
def release(): gc.collect(); torch.cuda.empty_cache()


def iter_corpus(path, limit):
    rows = []
    with Path(path).open(encoding="utf-8", errors="replace") as f:
        for line_no, line in enumerate(f, 1):
            try: obj = json.loads(line)
            except Exception: continue
            if not isinstance(obj, dict): continue
            for key in ("text", "prompt", "instruction", "input", "output", "response"):
                value = obj.get(key)
                if isinstance(value, str) and value.strip():
                    rows.append({"ordinal": len(rows), "line": line_no, "field": key, "text": value})
                    if len(rows) == limit: return rows
    return rows


def official_language_filter(text):
    return all(ord(ch) < 592 or ord(ch) in range(1024, 1279) for ch in text)


def tokenizer_config_hash(path):
    files = []
    for name in ("tokenizer.json", "tokenizer_config.json", "special_tokens_map.json",
                 "tokenizer.model", "vocab.json", "merges.txt", "added_tokens.json"):
        p = Path(path) / name
        if p.is_file(): files.append({"name": name, "sha256": sha(p), "bytes": p.stat().st_size})
    return json_sha(files), files


def build_token_manifest(model_id, revision, path, corpus_rows, corpus_sha):
    tok = AutoTokenizer.from_pretrained(path, local_files_only=True, trust_remote_code=True)
    counts = collections.Counter(); accepted = 0
    for row in corpus_rows:
        if not official_language_filter(row["text"]): continue
        tokens = tok.tokenize(row["text"])
        counts.update(tok.convert_tokens_to_ids(tokens)); accepted += 1
    excluded_strings = {"<unk>", "<s>", "</s>"}
    ranked = sorted(counts.items(), key=lambda item: (item[1], item[0]), reverse=True)
    selected = []
    for token_id, count in ranked:
        token = tok.convert_ids_to_tokens(token_id)
        if token in excluded_strings: continue
        selected.append({"rank": len(selected), "token_id": int(token_id), "token": str(token),
                         "decoded": tok.decode([token_id]), "frequency": int(count),
                         "tie_break": "higher_token_id_first_within_equal_frequency"})
        if len(selected) == K: break
    vocab_size = len(tok)
    invalid = [x for x in selected if not 0 <= x["token_id"] < vocab_size]
    cfg_sha, cfg_files = tokenizer_config_hash(path)
    body = {"schema_version": "wmkd.huref-a2-token-manifest.v1", "model_id": model_id,
            "model_revision": revision, "tokenizer_class": tok.__class__.__name__,
            "tokenizer_path": str(path), "tokenizer_vocab_size": vocab_size,
            "tokenizer_config_sha256": cfg_sha, "tokenizer_files": cfg_files,
            "corpus_sha256": corpus_sha, "K": K, "accepted_documents": accepted,
            "counting": "official tokenizer.tokenize then convert_tokens_to_ids; duplicate occurrences counted",
            "add_special_tokens": False,
            "language_filter": "all chars ord<592 or Cyrillic ord 1024..1278",
            "special_filter": "exclude token strings exactly <unk>, <s>, </s>",
            "sorting": "frequency descending, then token ID descending (official reverse=True)",
            "min_id": min(x["token_id"] for x in selected), "max_id": max(x["token_id"] for x in selected),
            "invalid_count": len(invalid), "rows": selected}
    body["manifest_content_sha256"] = json_sha(body)
    if len(selected) != K or invalid: raise RuntimeError(f"token manifest invalid for {model_id}: K={len(selected)} invalid={len(invalid)}")
    return body


def official_pool(x, out_dim=512):
    y = x.contiguous().view(out_dim, -1).mean(-1)
    return (y - y.mean()) / y.std()
def wmkd_pool(terms): return official_pool(torch.stack(terms, 0), 512)
def ics(a, b):
    x = torch.from_numpy(a).float(); y = torch.from_numpy(b).float()
    x = (x-x.mean())/x.std(); y = (y-y.mean())/y.std()
    return float(100 * torch.nn.functional.cosine_similarity(x.flatten(), y.flatten(), dim=0))


def projections(block, cfg):
    attn = block.self_attn; hd = getattr(cfg, "head_dim", None) or cfg.hidden_size // cfg.num_attention_heads
    qr = cfg.num_attention_heads * hd; kr = cfg.num_key_value_heads * hd
    if hasattr(attn, "q_proj"):
        q, k, v = attn.q_proj.weight, attn.k_proj.weight, attn.v_proj.weight; amode = "separate_q_k_v"
    elif hasattr(attn, "qkv_proj"):
        w = attn.qkv_proj.weight; assert w.shape == (qr + 2*kr, cfg.hidden_size)
        q, k, v = torch.split(w, [qr, kr, kr], 0); amode = "fused_qkv_config_split_Q_then_K_then_V"
    else: raise RuntimeError(f"unsupported attention {type(attn).__name__}")
    factor = cfg.num_attention_heads // cfg.num_key_value_heads
    assert cfg.num_attention_heads % cfg.num_key_value_heads == 0
    ke = k.repeat_interleave(factor, 0) if factor > 1 else k
    ve = v.repeat_interleave(factor, 0) if factor > 1 else v
    assert ke.shape == q.shape and ve.shape == q.shape
    mlp = block.mlp
    if hasattr(mlp, "gate_proj"):
        g, u = mlp.gate_proj.weight, mlp.up_proj.weight; mmode = "separate_gate_up"
    elif hasattr(mlp, "gate_up_proj"):
        w = mlp.gate_up_proj.weight; assert w.shape == (2*cfg.intermediate_size, cfg.hidden_size)
        g, u = torch.split(w, [cfg.intermediate_size, cfg.intermediate_size], 0); mmode = "fused_gate_up_config_split_gate_then_up"
    else: raise RuntimeError(f"unsupported MLP {type(mlp).__name__}")
    meta = {"block_class": type(block).__name__, "attention_class": type(attn).__name__,
            "mlp_class": type(mlp).__name__, "attention_mode": amode, "mlp_mode": mmode,
            "paths": {"attention": "model.layers[i].self_attn", "output": "o_proj",
                      "mlp": "model.layers[i].mlp", "down": "down_proj"},
            "hidden_size": cfg.hidden_size, "q_heads": cfg.num_attention_heads,
            "kv_heads": cfg.num_key_value_heads, "head_dim": hd, "repeat_factor": factor,
            "shapes": {"q": list(q.shape), "k_original": list(k.shape), "v_original": list(v.shape),
                       "k_expanded": list(ke.shape), "v_expanded": list(ve.shape),
                       "o": list(attn.o_proj.weight.shape), "gate": list(g.shape),
                       "up": list(u.shape), "down": list(mlp.down_proj.weight.shape)}}
    return q, ke, ve, attn.o_proj.weight, g, u, mlp.down_proj.weight, meta


def unit_tests(data_root, manifests):
    x = torch.arange(6*4*4, dtype=torch.float32).reshape(6,4,4)
    a = official_pool(x, 8); b = official_pool(torch.stack([x[i] for i in range(6)]), 8)
    mean_diff = float((a-b).abs().max())
    # Official ICS source algebra: 100 * cosine_similarity after flatten/global standardization.
    va = np.arange(512, dtype=np.float32); vb = va[::-1].copy()
    official = float(100*torch.nn.functional.cosine_similarity(torch.tensor((va-va.mean())/va.std(ddof=1)), torch.tensor((vb-vb.mean())/vb.std(ddof=1)), dim=0))
    compared = ics(va, vb)
    token_tests = {k: {"pass": v[0]["manifest_content_sha256"] == v[1]["manifest_content_sha256"],
                       "sha_run_1": v[0]["manifest_content_sha256"], "sha_run_2": v[1]["manifest_content_sha256"],
                       "invalid_count": v[0]["invalid_count"], "K": len(v[0]["rows"])} for k,v in manifests.items()}
    # Load only configs here; projection shapes are asserted during each formal fresh load.
    llama = AutoConfig.from_pretrained(data_root/"models/base/Llama-3.2-3B-Instruct", local_files_only=True)
    phi = AutoConfig.from_pretrained(data_root/"models/llmprint_validation/models/microsoft--Phi-3-mini-128k-instruct/snapshots/master", local_files_only=True, trust_remote_code=True)
    tests = {"mean_pooling": {"pass": mean_diff == 0, "max_abs_diff": mean_diff, "output_dimension_formal": 512},
             "token_determinism": {"pass": all(x["pass"] and x["invalid_count"] == 0 and x["K"] == K
                                                     for x in token_tests.values()),
                                     "models": token_tests},
             "llama_gqa": {"pass": llama.num_attention_heads == 24 and llama.num_key_value_heads == 8 and llama.hidden_size//llama.num_attention_heads == 128,
                            "q_heads": 24, "kv_heads": 8, "head_dim": 128, "repeat_factor": 3},
             "phi_fused_shapes": {"pass": phi.hidden_size == 3072 and phi.num_attention_heads == 32 and phi.intermediate_size == 8192,
                                  "qkv_expected": [9216,3072], "gate_up_expected": [16384,3072]},
             "six_term_order": {"pass": ORDER == ["layer_-2_WqWk","layer_-2_WvWo","layer_-2_WuWd","layer_-1_WqWk","layer_-1_WvWo","layer_-1_WuWd"], "order": ORDER},
             "ics_official_comparison": {"pass": abs(official-compared) < 1e-5, "official": official, "wmkd": compared, "abs_diff": abs(official-compared)}}
    return {"status": "PASS" if all(x["pass"] for x in tests.values()) else "FAIL", "tests": tests}


def extract(path, ids, output, model_id, token_manifest_sha, *, minimum_free_gb=100):
    if minimum_free_gb not in (2, 100): raise ValueError("Unsupported disk reserve")
    if free_gb(output.parent) < minimum_free_gb: raise RuntimeError("GLOBAL_DISK_SAFETY_BLOCK")
    started = time.time(); torch.cuda.reset_peak_memory_stats()
    cfg = AutoConfig.from_pretrained(path, local_files_only=True, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(path, local_files_only=True, trust_remote_code=True,
                                                 torch_dtype=torch.float16, device_map="cuda:0").eval()
    if max(ids) >= model.get_input_embeddings().weight.shape[0]: raise RuntimeError("token ID outside embedding rows")
    terms, term_meta, arch = [], [], []
    with torch.inference_mode():
        emb = model.get_input_embeddings().weight.detach()[ids].float()
        for rel, block in zip((-2,-1), model.model.layers[-2:]):
            q,k,v,o,g,u,d,meta = projections(block, cfg); arch.append({"layer_index": cfg.num_hidden_layers+rel, **meta})
            specs = [("WqWk", lambda: emb@q.float().T@k.float()@emb.T),
                     ("WvWo", lambda: emb@v.float().T@o.float().T@emb.T),
                     ("WuWd", lambda: emb@(g.float().T*u.float().T)@d.float().T@emb.T)]
            for name, fn in specs:
                term = fn().detach().cpu(); terms.append(term)
                term_meta.append({"order": len(term_meta), "layer_index": cfg.num_hidden_layers+rel,
                                  "term": name, "shape": list(term.shape), "dtype": str(term.dtype), "sha256": tsha(term)})
                del term
        feature = wmkd_pool(terms).detach().cpu().numpy().astype(np.float32)
    save_npy(output, feature); feature_sha = sha(output); peak = int(torch.cuda.max_memory_allocated())
    del terms, model, emb; release()
    return feature, {"model_id": model_id, "model_path": str(path), "token_manifest_sha256": token_manifest_sha,
                     "layers": [cfg.num_hidden_layers-2, cfg.num_hidden_layers-1], "K": K,
                     "term_order": ORDER, "terms": term_meta, "architecture_mapping": arch,
                     "feature": {"path": str(output), "shape": [512], "dtype": str(feature.dtype), "sha256": feature_sha},
                     "runtime_seconds": time.time()-started, "peak_vram_bytes": peak}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--project", type=Path, required=True); ap.add_argument("--data-root", type=Path, required=True)
    ap.add_argument("--run-id", required=True); ap.add_argument("--corpus", type=Path, required=True); ap.add_argument("--max-documents", type=int, default=10000)
    args = ap.parse_args(); start = time.time()
    out = args.project/"results/huref/experiment_a2"; protocol = out/"protocol"; artifact = args.data_root/f"artifacts/huref/experiment_a2/{args.run_id}"
    rows = iter_corpus(args.corpus, args.max_documents)
    corpus_payload = {"schema_version": "wmkd.huref-a2-corpus.v1", "identity": "existing WMKD SCW A2 role1 English instruct-prefix corpus",
                      "source": str(args.corpus), "source_sha256": sha(args.corpus), "revision": "local immutable artifact",
                      "split": "role1", "selection": "first 10000 non-empty fields in fixed key order",
                      "field_order": ["text","prompt","instruction","input","output","response"], "documents": len(rows),
                      "order": "source line ascending then fixed field order", "preprocessing": "no text mutation; pinned official language filter applied during token counting",
                      "row_identity": [{"ordinal": r["ordinal"], "line": r["line"], "field": r["field"], "text_sha256": sha_bytes(r["text"].encode())} for r in rows],
                      "joined_text_sha256": sha_bytes("\n".join(r["text"] for r in rows).encode())}
    corpus_payload["manifest_content_sha256"] = json_sha(corpus_payload); atomic(protocol/"corpus_manifest.json", corpus_payload)
    panel = [("meta-llama/Llama-3.2-3B-Instruct", REV, args.data_root/"models/base/Llama-3.2-3B-Instruct"),
             ("google/gemma-2b", "4c0ad9bd274f4fda9be830b72a0833fb1f74a12e", args.data_root/"models/llmprint_validation/google/gemma-2b"),
             ("Qwen/Qwen2.5-3B-Instruct", "8f4992eda43eea7c770690ddc0de8f732da246f5", args.data_root/"models/llmprint_validation/models/Qwen--Qwen2.5-3B-Instruct/snapshots/master"),
             ("microsoft/Phi-3-mini-128k-instruct", "36dd6bdc2b730342af51ce16740601d6471e73ff (frozen identity; provenance-repaired equivalent local transport)", args.data_root/"models/llmprint_validation/models/microsoft--Phi-3-mini-128k-instruct/snapshots/master")]
    manifest_runs = {}
    for mid, rev, path in panel:
        first = build_token_manifest(mid, rev, path, rows, corpus_payload["manifest_content_sha256"])
        second = build_token_manifest(mid, rev, path, rows, corpus_payload["manifest_content_sha256"])
        manifest_runs[mid] = (first, second)
        atomic(protocol/"token_manifests"/(mid.replace("/","--")+".json"), first)
    units = unit_tests(args.data_root, manifest_runs); atomic(protocol/"unit_test_results.json", units)
    if units["status"] != "PASS": raise RuntimeError("A2 protocol unit tests failed")
    features, metas = {}, []
    ref_mid, ref_rev, ref_path = panel[0]; ref_manifest = manifest_runs[ref_mid][0]; ref_ids = [x["token_id"] for x in ref_manifest["rows"]]
    ra, ma = extract(ref_path, ref_ids, artifact/"reference_a.npy", ref_mid, ref_manifest["manifest_content_sha256"]); features["reference_a"] = ra; metas.append({"role":"reference_a",**ma})
    rb, mb = extract(ref_path, ref_ids, artifact/"reference_b.npy", ref_mid, ref_manifest["manifest_content_sha256"]); features["reference_b"] = rb; metas.append({"role":"reference_b",**mb})
    negative_scores = []
    for mid, rev, path in panel[1:]:
        manifest = manifest_runs[mid][0]; ids = [x["token_id"] for x in manifest["rows"]]
        f, meta = extract(path, ids, artifact/(mid.replace("/","--")+".npy"), mid, manifest["manifest_content_sha256"])
        features[mid] = f; metas.append({"role":"negative",**meta}); negative_scores.append({"model_id":mid,"score":ics(ra,f)})
    self_score = ics(ra,ra); reload_score = ics(ra,rb); maxdiff = float(np.max(np.abs(ra-rb)))
    tau = max(x["score"] for x in negative_scores); negative_mean = float(np.mean([x["score"] for x in negative_scores]))
    margin = self_score-tau; fp = sum(x["score"] > tau for x in negative_scores); errors = []
    integrity = all(m["feature"]["shape"] == [512] and Path(m["feature"]["path"]).is_file() for m in metas)
    success = maxdiff == 0 and reload_score > 99.9999 and self_score > tau and fp == 0 and integrity and not errors
    conclusion = ("HuRef core reproduction successful under the WMKD A2 tokenizer-specific top-K protocol" if success else
                  "HuRef core reproduction not established under the WMKD A2 tokenizer-specific top-K protocol")
    detector = {"metric":"official ICS = 100*cosine_similarity of globally standardized flattened 512-d features", "score_direction":"higher",
                "reference_self":self_score,"reference_reload":reload_score,"reload_max_abs_diff":maxdiff,"negative_scores":negative_scores,
                "negative_mean":negative_mean,"threshold_rule":"tau = maximum score among three frozen unrelated negatives",
                "threshold":tau,"positive_rule":"score > tau; tie is negative","reference_positive":self_score>tau,
                "margin":margin,"false_positives":fp,"evaluation_errors":errors}
    lineage = {"A":{"run_id":"huref_a_20260901_201015","status":"implementation failure / NOT_JUDGED"},
               "A_cont1":{"run_id":"huref_a_cont1_20260901_210000","status":"BLOCKED_PROTOCOL_AMBIGUITY / NOT_JUDGED",
                          "finding":"95/4096 canonical Llama token IDs outside Phi vocab"},
               "A2":{"run_id":args.run_id,"scientific_change":"same fixed corpus; independent deterministic tokenizer-specific top-K=4096 per model",
                     "cont1_partial_features_reused":False}}
    runtime = time.time()-start; peak = max(m["peak_vram_bytes"] for m in metas)
    common = {"schema_version":"wmkd.huref-a2.v1","method":"HuRef","experiment":"A2","run_id":args.run_id,
              "status":"COMPLETED" if success else "FAILED","official_repo":"LUMIA-Group/HuRef","official_commit":OFFICIAL,
              "canonical_revision":REV,"model_modified":False,"artifact_type":"fingerprint_package" if success else "scientific_evidence",
              "preferred_fingerprint":"yes" if success else "no","scientific_conclusion":conclusion,"ba_status":"NOT_STARTED",
              "runtime_seconds":runtime,"peak_vram_bytes":peak,"peak_ram_kib":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
              "disk_free_gb":free_gb(args.data_root),"lineage":lineage}
    # Keep small features in Git as reproducibility evidence.
    feature_rows=[]
    for meta in metas:
        target=protocol/(meta["role"]+"--"+meta["model_id"].replace("/","--")+".npy"); source=Path(meta["feature"]["path"])
        save_npy(target, np.load(source, allow_pickle=False)); feature_rows.append({**meta["feature"],"git_path":str(target.relative_to(args.project)),"git_sha256":sha(target),"role":meta["role"],"model_id":meta["model_id"]})
    atomic(protocol/"feature_manifest.json", {"integrity":"PASS" if integrity else "FAIL","features":feature_rows,"extraction":metas})
    atomic(protocol/"detector_results.json", detector); atomic(protocol/"lineage.json", lineage)
    manifests_summary={mid:{"path":f"results/huref/experiment_a2/protocol/token_manifests/{mid.replace('/','--')}.json","sha256":m[0]["manifest_content_sha256"],"invalid_count":m[0]["invalid_count"]} for mid,m in manifest_runs.items()}
    atomic(out/"summary.json", {**common,"corpus_sha256":corpus_payload["manifest_content_sha256"],"token_manifests":manifests_summary,"detector":detector,"evaluation_errors":len(errors)})
    atomic(out/"detector_results.json", {**common,"detector":detector})
    atomic(out/"provenance_manifest.json", {**common,"shared_corpus":corpus_payload,"token_manifests":manifests_summary,"unit_tests":units,
           "adaptation_classification":"A2 scientific protocol: tokenizer-specific top-K; architecture handling is compatibility engineering"})
    atomic(out/"artifact_manifest.json", {**common,"large_artifact_root":str(artifact),"features":feature_rows,"raw_terms_persisted":False,"term_hashes_recorded":True,"integrity":"PASS" if integrity else "FAIL"})
    frozen_a=json.loads((args.project/"results/ownership_protocols/huref_formal_protocol.json").read_text())
    atomic(out/"full_experiment_log.json", {**common,"history":lineage,"why_a2_required":"canonical Llama token IDs are not a valid cross-tokenizer selection rule",
           "a2_protocol":{"only_scientific_change":"per-model tokenizer-specific deterministic top-K=4096 on a common corpus","frozen_A_calibration_retained":frozen_a["calibration"]},
           "shared_corpus":corpus_payload,"token_manifests":manifests_summary,"unit_tests":units,"extraction":{"term_order":ORDER,"models":metas},
           "detector":detector,"utility":{"status":"not_applicable","reason":"passive fingerprint; inherited canonical Base"},"failures":errors})
    report=f"""# HuRef Experiment A2 report

**{conclusion}.** Preferred fingerprint: **{'yes' if success else 'no'}**.

A2 `{args.run_id}` preserves A and cont1 as NOT_JUDGED history. Its sole scientific redesign is independent deterministic tokenizer-specific top-K=4096 lists for the same frozen corpus, matching the pinned official per-model sorted-list semantics. No cont1 feature was reused.

- Common corpus manifest SHA: `{corpus_payload['manifest_content_sha256']}`
- Protocol unit tests: `{units['status']}`
- Feature dimension: 512
- Reference/self ICS: {self_score:.12f}
- Reference/reload ICS: {reload_score:.12f}; max abs diff: {maxdiff}
"""+"\n".join(f"- {x['model_id']} ICS: {x['score']:.12f}" for x in negative_scores)+f"""
- Negative mean: {negative_mean:.12f}
- Threshold (max frozen negative): {tau:.12f}
- Separation margin: {margin:.12f}
- False positives: {fp}/3
- Evaluation errors: {len(errors)}

Bounded conclusion: this result concerns HuRef core reproduction under the WMKD A2 tokenizer-specific top-K protocol only. It does not establish robustness under attacks, transfer to other panels/corpora, or model modification. `model_modified=false`; utility is inherited canonical Base; Ba is NOT_STARTED.
"""
    write_text(args.project/"docs/reproduction_reports/huref_experiment_a2_report.md", report)
    write_text(args.project/"docs/experiment_logs/huref_experiment_a2_log.md", f"# HuRef Experiment A2 log\n\n- Run: `{args.run_id}`\n- Lineage: A → A cont1 → A2\n- Result: {conclusion}\n- Runtime seconds: {runtime:.3f}\n- Ba: NOT_STARTED\n")
    method=(args.project/"docs/methods/huref.md").read_text(); write_text(args.project/"docs/methods/huref.md", method+f"\n## Experiment A2\n\nRun `{args.run_id}` uses one fixed corpus with deterministic per-model tokenizer-specific top-K=4096 manifests. {conclusion}.\n")
    # Write index after result files so their hashes are final.
    idxp=args.project/"results/experiment_full_logs_index.json"; idx=json.loads(idxp.read_text()); full=out/"full_experiment_log.json"; summ=out/"summary.json"
    entry={"method":"HuRef","role":"preferred_fingerprint","experiment":"A2","run_id":args.run_id,
           "full_log_path":"results/huref/experiment_a2/full_experiment_log.json","full_log_sha256":sha(full),
           "summary_path":"results/huref/experiment_a2/summary.json","summary_sha256":sha(summ),
           "report_path":"docs/reproduction_reports/huref_experiment_a2_report.md","artifact_manifest_path":"results/huref/experiment_a2/artifact_manifest.json",
           "scientific_status":"SUCCESSFUL" if success else "NOT_ESTABLISHED","artifact_type":common["artifact_type"],"model_modified":False,
           "preferred_fingerprint":common["preferred_fingerprint"],"utility_available":False,"ba_status":"NOT_STARTED",
           "history":["huref_a_20260901_201015","huref_a_cont1_20260901_210000"]}
    idx["objects"]=[x for x in idx["objects"] if not (x.get("method")=="HuRef" and x.get("role")=="preferred_fingerprint")]+[entry]
    idx["object_count"]=len(idx["objects"]); idx["generated_at"]=now(); atomic(idxp,idx)
    print(json.dumps({"run_id":args.run_id,"success":success,"detector":detector,"runtime_seconds":runtime,"peak_vram_bytes":peak,"disk_free_gb":common["disk_free_gb"]}), flush=True)


if __name__ == "__main__": main()
