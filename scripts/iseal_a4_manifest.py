import argparse,hashlib,json
from pathlib import Path
import yaml
from datasets import load_dataset
p=argparse.ArgumentParser();p.add_argument("--config",required=True);p.add_argument("--cache",required=True);p.add_argument("--output",required=True);a=p.parse_args();c=yaml.safe_load(Path(a.config).read_text());d=c["dataset"]
ds=load_dataset(d["id"],split=d["split"],cache_dir=a.cache).shuffle(seed=d["shuffle_seed"]);train=[i for s,e in d["registered_index_ranges"] for i in range(s,e)];held=list(range(*d["held_out_index_range"]));assert len(train)==100 and len(held)==100 and not set(train)&set(held)
def rows(ids):return [{"order":j,"shuffled_index":i,"plaintext_sha256":hashlib.sha256(ds[i]["text"].encode()).hexdigest()} for j,i in enumerate(ids)]
tr=rows(train);he=rows(held);assert len({x["plaintext_sha256"] for x in tr})==100 and not {x["plaintext_sha256"] for x in tr}&{x["plaintext_sha256"] for x in he}
o={"dataset":d["id"],"split":d["split"],"shuffle_seed":d["shuffle_seed"],"training":tr,"held_out":he,"historical_A3_registered_10_are_training_prefix":train[:10]==list(range(10)),"index_overlap_count":0,"plaintext_hash_overlap_count":0};o["manifest_sha256"]=hashlib.sha256(json.dumps(o,sort_keys=True,separators=(",",":")).encode()).hexdigest();Path(a.output).write_text(json.dumps(o,indent=2)+"\n");print(json.dumps({k:v for k,v in o.items() if k not in ("training","held_out")},indent=2))
