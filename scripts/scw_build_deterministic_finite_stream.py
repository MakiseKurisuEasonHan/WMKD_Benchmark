"""Build the disclosed WMKD deterministic finite-stream SCW adaptation.

The source mixture is a fixed NumPy PCG64 draw.  Each source pool is built in
repository-path order from pinned Parquet objects using the unmodified official
preprocessing functions.  This intentionally does not reproduce the official
online shuffle/interleave realization.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from datasets import load_dataset
from huggingface_hub import HfApi
from transformers import AutoTokenizer

from scw_common import CANONICAL_MODEL, CANONICAL_REVISION, OFFICIAL_COMMIT, load_config
from scw_materialized_stream import canonical_json, file_sha256, training_length_contract
from scw_resumable_prefetch import ensure_cached

ADAPTATION = "DETERMINISTIC_FINITE_STREAM_SAMPLING_ADAPTATION"
LIMITATION = "The WMKD finite stream is not byte-identical to the official online streaming/shuffle realization."
SOURCES = (
    {"name":"LucieFr", "label":0, "repo":"OpenLLM-France/Lucie-Training-Dataset", "config":"RedPajama-fr", "split":"train", "revision":"8d50ff7cfce1a2db7cc5a1ef37d73f5f455f8ad1", "loss_type":"watermark", "lambda":1},
    {"name":"AlpacaGPT4", "label":1, "repo":"vicgalle/alpaca-gpt4", "config":None, "split":"train", "revision":"f7e3ded725cb81e8e564e32feb12860f376f2b51", "loss_type":"anti-watermark-tv", "lambda":1},
    {"name":"OpenWebText", "label":2, "repo":"Skylion007/openwebtext", "config":None, "split":"train", "revision":"79d93d786212f7344586290adb811d4ae6a1762c", "loss_type":"anti-watermark-tv", "lambda":1},
)
PROBABILITIES = (0.6, 0.2, 0.2)

def sha_payload(row: dict) -> str:
    payload={k:row[k] for k in ("input_ids","attention_mask","official_label","source_dataset","loss_type","lambda")}
    return hashlib.sha256(canonical_json(payload).encode()).hexdigest()

def schedule(count: int, seed: int) -> list[int]:
    return np.random.Generator(np.random.PCG64(seed)).choice(3, size=count, p=PROBABILITIES).astype(np.uint8).tolist()

def parquet_paths(api: HfApi, source: dict) -> list[str]:
    paths=sorted(p for p in api.list_repo_files(source["repo"], repo_type="dataset", revision=source["revision"]) if p.endswith(".parquet"))
    if source["name"] == "LucieFr": paths=[p for p in paths if "RedPajama-fr" in p]
    elif source["name"] == "OpenWebText": paths=[p for p in paths if p.startswith("plain_text/")]
    elif source["name"] == "AlpacaGPT4": paths=[p for p in paths if "train" in Path(p).name]
    if not paths: raise RuntimeError(f"no authoritative Parquet objects for {source['name']}")
    return paths

def official_preprocess(local_parquet: Path, source: dict, tokenizer, sequence_length: int):
    raw=load_dataset("parquet", data_files=str(local_parquet), split="train")
    from robust_fp.finetuning.dataset import tokenize_dataset
    from robust_fp.finetuning.data_utils import convert_sft_dataset, tokenize_dataset_with_chat
    if source["name"] in ("LucieFr","OpenWebText"):
        if "text" not in raw.column_names: raise RuntimeError(f"{source['name']} schema lacks text")
        return tokenize_dataset(raw, tokenizer, sequence_length=sequence_length)
    if not {"instruction","output"}.issubset(raw.column_names): raise RuntimeError("AlpacaGPT4 schema mismatch")
    def convert(example):
        return {"messages":[{"role":"user","content":example["instruction"]},{"role":"assistant","content":example["output"]}]}
    return tokenize_dataset_with_chat(convert_sft_dataset(raw, convert, min_response_length=200), tokenizer, max_length=sequence_length)

def build_pool(source: dict, required: int, pool_path: Path, tokenizer, api: HfApi, endpoint: str, cache_root: Path, sequence_length: int) -> dict:
    if pool_path.exists(): raise FileExistsError(pool_path)
    used=[]; produced=0; digest=hashlib.sha256()
    with pool_path.open("x",encoding="utf-8",newline="\n") as out:
        for repo_path in parquet_paths(api, source):
            url=f"{endpoint}/datasets/{source['repo']}/resolve/{source['revision']}/{repo_path}"
            cached,_cache_manifest=ensure_cached(url, cache_root)
            before=produced
            for example in official_preprocess(cached,source,tokenizer,sequence_length):
                if produced >= required: break
                row={"source_local_index":produced,"input_ids":list(example["input_ids"]),"attention_mask":list(example["attention_mask"]),"official_label":source["label"],"source_dataset":source["name"],"loss_type":source["loss_type"],"lambda":source["lambda"]}
                row["content_sha256"]=sha_payload(row); digest.update(bytes.fromhex(row["content_sha256"])); out.write(canonical_json(row)+"\n"); produced+=1
            used.append({"repository_relative_path":repo_path,"verified_cache_path":str(cached),"records_emitted":produced-before,"size":cached.stat().st_size,"sha256":file_sha256(cached)})
            print(json.dumps({"event":"pool_progress","source":source["name"],"records":produced,"required":required,"shard":repo_path}),flush=True)
            if produced >= required: break
    if produced != required: raise RuntimeError(f"{source['name']} source-order pool exhausted at {produced}/{required}")
    return {"records":produced,"pool_path":str(pool_path),"pool_sha256":file_sha256(pool_path),"ordered_content_digest":digest.hexdigest(),"objects":used}

def assemble(schedule_values: list[int], pools: list[Path], records: Path) -> dict:
    handles=[p.open(encoding="utf-8") for p in pools]; counts=Counter(); digest=hashlib.sha256()
    try:
        with records.open("x",encoding="utf-8",newline="\n") as out:
            for index,label in enumerate(schedule_values):
                line=handles[label].readline()
                if not line: raise RuntimeError(f"pool {label} exhausted at global index {index}")
                base=json.loads(line); row={"global_index":index,"source_schedule_label":label,**base}
                counts[base["source_dataset"]]+=1; digest.update(bytes.fromhex(base["content_sha256"])); out.write(canonical_json(row)+"\n")
        if any(h.readline() for h in handles): raise RuntimeError("per-source pool contains unused rows")
    finally:
        for h in handles: h.close()
    return {"materialized_record_count":len(schedule_values),"source_counts":dict(counts),"observed_source_proportions":{s["name"]:counts[s["name"]]/len(schedule_values) for s in SOURCES},"records_file_size_bytes":records.stat().st_size,"records_file_sha256":file_sha256(records),"canonical_content_digest":digest.hexdigest()}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--config",required=True); ap.add_argument("--official-runtime-config",required=True); ap.add_argument("--official-source",required=True); ap.add_argument("--records",required=True); ap.add_argument("--manifest",required=True); ap.add_argument("--cache-root",required=True); ap.add_argument("--creation-code-version",required=True); a=ap.parse_args()
    config=load_config(a.config); source_root=Path(a.official_source).resolve()
    if os.environ.get("PYTHONHASHSEED")!=str(config["training"]["pythonhashseed"]): raise RuntimeError("PYTHONHASHSEED mismatch")
    if subprocess.check_output(["git","-C",str(source_root),"rev-parse","HEAD"],text=True).strip()!=OFFICIAL_COMMIT: raise RuntimeError("official commit mismatch")
    if subprocess.run(["git","-C",str(source_root),"diff","--quiet","HEAD","--"]).returncode or subprocess.run(["git","-C",str(source_root),"diff","--cached","--quiet"]).returncode: raise RuntimeError("official tracked source dirty")
    sys.path.insert(0,str(source_root/"src")); from robust_fp.finetuning.data_utils import add_chat_template
    runtime=json.loads(Path(a.official_runtime_config).read_text()); ft=runtime["finetuning"]; contract=training_length_contract(ft["training_args"]["max_steps"],ft["training_args"]["gradient_accumulation_steps"],ft["training_args"]["per_device_train_batch_size"])
    values=schedule(contract["expected_consumed_examples"],42); label_counts=np.bincount(values,minlength=3).tolist()
    root=Path(a.records).parent; schedule_path=root/"source_schedule.uint8"; schedule_path.write_bytes(bytes(values))
    tokenizer=AutoTokenizer.from_pretrained(runtime["base_model"],padding_side="left"); tokenizer=add_chat_template(tokenizer) if tokenizer.chat_template is None else tokenizer
    endpoint=os.environ.get("HF_ENDPOINT","https://hf-mirror.com").rstrip("/"); api=HfApi(endpoint=endpoint); pools=[]; pool_stats={}
    for src,needed in zip(SOURCES,label_counts):
        path=root/f"pool_{src['name']}.jsonl"; pools.append(path); pool_stats[src["name"]]=build_pool(src,needed,path,tokenizer,api,endpoint,Path(a.cache_root),ft["sequence_length"])
    materialization=assemble(values,pools,Path(a.records))
    manifest={"schema_version":2,"adaptation":ADAPTATION,"adaptation_name":"WMKD deterministic finite-stream sampling adaptation","adaptation_rationale":"runtime/network reproducibility and feasibility","explicit_non_equivalence_statement":LIMITATION,"creation_timestamp":datetime.now(timezone.utc).isoformat(),"creation_code_commit":a.creation_code_version,"official_repo_commit":OFFICIAL_COMMIT,"model":{"id":CANONICAL_MODEL,"revision":CANONICAL_REVISION},"datasets":list(SOURCES),"source_schedule_rng":{"library":"NumPy","algorithm":"PCG64","seed":42,"numpy_version":np.__version__},"configured_probabilities":list(PROBABILITIES),"source_schedule_path":str(schedule_path),"source_schedule_sha256":file_sha256(schedule_path),"per_source_extraction_policy":"repository-path-order, shard-order, official preprocessing, first N valid tokenized records; no remote shuffle","preprocessing_provenance":"unmodified pinned official robust_fp functions tokenize_dataset, convert_sft_dataset, tokenize_dataset_with_chat","source_pools":pool_stats,"source_contract":list(SOURCES),"training_length_contract":contract,"duplicates_policy":"no deduplication; no replacement; no synthetic duplication",**materialization}
    manifest["pythonhashseed"]=42
    Path(a.manifest).write_text(json.dumps(manifest,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8",newline="\n")
    print(json.dumps({"status":"DETERMINISTIC_FINITE_STREAM_BUILT","required_per_source":label_counts,**materialization},indent=2),flush=True)
if __name__=="__main__": main()
