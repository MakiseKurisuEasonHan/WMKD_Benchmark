"""Finalize and verify the three bounded local ModelScope inputs for SCW A2."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
import pyarrow as pa
import pyarrow.ipc as ipc
import pyarrow.parquet as pq

ROOT=Path("/root/autodl-tmp/WMKD_Benchmark_data/datasets/scw_a2")
EXPECTED={
 "role0/french-train-00000-of-00003.parquet.part":"35c6904aa2b2aac50eef2c099697d2119b7e1b626115a582d3ba0c011a560429",
 "role2/openwebtext-train-00020-of-00083.arrow.part":"669ceafd21119934f3f1a381891e5b7b8abe80598d6573ddab8464a59da7d858",
}
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
 for rel,digest in EXPECTED.items():
  part=ROOT/rel
  if sha(part)!=digest: raise RuntimeError(f"SHA mismatch: {part}")
  final=part.with_suffix(""); part.replace(final)
 role0=ROOT/"role0/french-train-00000-of-00003.parquet"
 pf=pq.ParquetFile(role0)
 if not {"inputs","targets","language"}.issubset(pf.schema_arrow.names): raise RuntimeError("Role0 schema mismatch")
 role2=ROOT/"role2/openwebtext-train-00020-of-00083.arrow"
 with pa.memory_map(str(role2)) as source: schema=ipc.open_stream(source).schema
 if "text" not in schema.names: raise RuntimeError("Role2 schema mismatch")
 prefix=ROOT/"role1/instruct-prefix-64m.jsonl.part"; payload=prefix.read_bytes(); end=payload.rfind(b"\n")
 if end<0: raise RuntimeError("Role1 prefix has no complete JSONL records")
 final1=prefix.with_suffix(""); final1.write_bytes(payload[:end+1]); prefix.unlink()
 count=0
 with final1.open(encoding="utf-8") as handle:
  for count,line in enumerate(handle,1):
   row=json.loads(line)
   if not {"prompt","completion"}.issubset(row): raise RuntimeError(f"Role1 schema mismatch line {count}")
 result={"status":"PASS","role0":{"rows":pf.metadata.num_rows,"schema":pf.schema_arrow.names,"size":role0.stat().st_size,"sha256":sha(role0)},"role1":{"complete_rows":count,"schema":["prompt","completion"],"size":final1.stat().st_size,"prefix_sha256":sha(final1)},"role2":{"schema":schema.names,"size":role2.stat().st_size,"sha256":sha(role2)}}
 (ROOT/"local_source_verification.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
 print(json.dumps(result,indent=2))
if __name__=="__main__": main()
