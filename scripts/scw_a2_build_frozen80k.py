"""Build the frozen 80k-unique SCW A2 stream from pinned local ModelScope files."""
from __future__ import annotations
import argparse, hashlib, json, os, subprocess, sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
from datasets import Dataset
from transformers import AutoTokenizer
from scw_materialized_stream import canonical_json, file_sha256

ADAPTATION="SCW_A2_WMKD_DOMESTIC_DATA_80K_UNIQUE_TWO_PASS"
ROLE_NAMES=("AyaFrench","MSInstruct","MSOpenWebText")
LOSSES=("watermark","anti-watermark-tv","anti-watermark-tv")
EXPECTED=(47773,16291,15936)

def content_hash(row):
 p={k:row[k] for k in ("input_ids","attention_mask","official_label","source_dataset","loss_type","lambda","source_identity")}
 return hashlib.sha256(canonical_json(p).encode()).hexdigest()

def write_pool(path, role, rows, required):
 digest=hashlib.sha256(); count=0
 with path.open("x",encoding="utf-8",newline="\n") as out:
  for ids,mask,identity in rows:
   if count>=required: break
   row={"source_local_index":count,"source_identity":identity,"input_ids":list(ids),"attention_mask":list(mask),"official_label":role,"source_dataset":ROLE_NAMES[role],"loss_type":LOSSES[role],"lambda":1}
   row["content_sha256"]=content_hash(row); digest.update(bytes.fromhex(row["content_sha256"])); out.write(canonical_json(row)+"\n"); count+=1
 if count!=required: raise RuntimeError(f"role {role} insufficient unique records: {count}/{required}")
 return {"records":count,"sha256":file_sha256(path),"ordered_digest":digest.hexdigest(),"path":str(path)}

def general_rows(dataset, tokenizer, text_adapter, source_file, sequence_length=512, batch_size=1000):
 from robust_fp.finetuning.dataset import tokenize_function,group_texts
 for start in range(0,len(dataset),batch_size):
  stop=min(start+batch_size,len(dataset)); texts=[text_adapter(dataset[i]) for i in range(start,stop)]
  grouped=group_texts(tokenize_function({"text":texts},tokenizer),sequence_length)
  for j,(ids,mask) in enumerate(zip(grouped["input_ids"],grouped["attention_mask"])):
   yield ids,mask,{"local_file":source_file,"raw_batch_start":start,"chunk_in_batch":j}

def instruction_rows(path,tokenizer):
 with path.open(encoding="utf-8",errors="strict") as handle:
  for raw_index,line in enumerate(handle):
   try: row=json.loads(line)
   except json.JSONDecodeError: break
   prompt=str(row.get("prompt","")).strip(); completion=str(row.get("completion","")).strip()
   if not prompt or len(completion)<200: continue
   encoded=tokenizer.apply_chat_template([{"role":"user","content":prompt},{"role":"assistant","content":completion}],tokenize=True,max_length=512,padding="max_length",return_dict=True)
   ids=encoded["input_ids"]; mask=encoded["attention_mask"]
   if len(ids)==512: yield ids,mask,{"local_file":str(path),"raw_line_index":raw_index}

def main():
 ap=argparse.ArgumentParser(); ap.add_argument("--config",required=True); ap.add_argument("--official-source",required=True); ap.add_argument("--role0",required=True); ap.add_argument("--role1",required=True); ap.add_argument("--role2",required=True); ap.add_argument("--output-dir",required=True); ap.add_argument("--creation-code-version",required=True); a=ap.parse_args()
 cfg=json.loads(Path(a.config).read_text()); out=Path(a.output_dir); out.mkdir(parents=True,exist_ok=False)
 if os.environ.get("PYTHONHASHSEED")!="42": raise RuntimeError("PYTHONHASHSEED must be 42")
 sys.path.insert(0,str(Path(a.official_source)/"src")); from robust_fp.finetuning.data_utils import add_chat_template
 tok=AutoTokenizer.from_pretrained(cfg["model"]["local_path"],padding_side="left"); tok=add_chat_template(tok) if tok.chat_template is None else tok; tok.pad_token=tok.eos_token
 schedule=np.random.Generator(np.random.PCG64(42)).choice(3,size=80000,p=[.6,.2,.2]).astype(np.uint8); counts=tuple(np.bincount(schedule,minlength=3).tolist())
 if counts!=EXPECTED: raise RuntimeError(f"schedule mismatch {counts}")
 schedule_path=out/"source_schedule.uint8"; schedule_path.write_bytes(schedule.tobytes())
 r0=Dataset.from_parquet(a.role0); r2=Dataset.from_file(a.role2)
 pools=[out/f"pool_{name}.jsonl" for name in ROLE_NAMES]
 stats=[]
 stats.append(write_pool(pools[0],0,general_rows(r0,tok,lambda x:str(x["inputs"])+"\n"+str(x["targets"]),str(Path(a.role0).resolve())),counts[0]))
 stats.append(write_pool(pools[1],1,instruction_rows(Path(a.role1),tok),counts[1]))
 stats.append(write_pool(pools[2],2,general_rows(r2,tok,lambda x:str(x["text"]),str(Path(a.role2).resolve())),counts[2]))
 handles=[p.open(encoding="utf-8") for p in pools]; stream=out/"training_stream_a2_80k.jsonl"; digest=hashlib.sha256(); seen=set()
 with stream.open("x",encoding="utf-8",newline="\n") as dst:
  for index,role in enumerate(schedule.tolist()):
   row=json.loads(handles[role].readline()); identity=(role,canonical_json(row["source_identity"]));
   if identity in seen: raise RuntimeError("duplicate source identity in unique pool")
   seen.add(identity); final={"global_index":index,"source_schedule_label":role,**row}; digest.update(bytes.fromhex(row["content_sha256"])); dst.write(canonical_json(final)+"\n")
 for h in handles: h.close()
 manifest={"schema_version":3,"adaptation":ADAPTATION,"experiment":"SCW A2","creation_timestamp":datetime.now(timezone.utc).isoformat(),"creation_code_commit":a.creation_code_version,"model":cfg["model"],"datasets":cfg["datasets"],"source_schedule_rng":{"library":"NumPy","version":np.__version__,"algorithm":"PCG64","seed":42},"configured_probabilities":[.6,.2,.2],"source_counts":dict(zip(ROLE_NAMES,counts)),"observed_source_proportions":dict(zip(ROLE_NAMES,[x/80000 for x in counts])),"source_schedule_path":str(schedule_path),"source_schedule_sha256":file_sha256(schedule_path),"source_pools":dict(zip(ROLE_NAMES,stats)),"materialized_record_count":80000,"unique_record_count":80000,"formal_exposure_target":160000,"replay_passes":2,"replay_policy":"two sequential identical passes; no shuffle","training_length_contract":{"optimizer_steps":2500,"gradient_accumulation_steps":16,"per_device_train_batch_size":4,"expected_consumed_examples":160000},"records_file_sha256":file_sha256(stream),"records_file_size_bytes":stream.stat().st_size,"canonical_content_digest":digest.hexdigest(),"duplicates_policy":"no artificial duplicate filling; unique source identity required","pythonhashseed":42,"limitations":["training datasets differ from official SCW","unique pool is 80k and receives two deterministic exposures"]}
 manifest["local_source_files"]={"role0":{"path":str(Path(a.role0).resolve()),"size":Path(a.role0).stat().st_size,"sha256":file_sha256(a.role0)},"role1":{"path":str(Path(a.role1).resolve()),"size":Path(a.role1).stat().st_size,"sha256":file_sha256(a.role1)},"role2":{"path":str(Path(a.role2).resolve()),"size":Path(a.role2).stat().st_size,"sha256":file_sha256(a.role2)}}
 (out/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
 print(json.dumps({"status":"BUILT","counts":counts,"stream":str(stream),"sha256":manifest["records_file_sha256"]},indent=2),flush=True)
if __name__=="__main__": main()
