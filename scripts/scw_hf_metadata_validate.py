"""Tiny exact-revision HF metadata/schema validation; no bulk materialization."""
import argparse,json,urllib.parse
from pathlib import Path
from datasets import load_dataset

SOURCES=(
 ("LucieFr","OpenLLM-France/Lucie-Training-Dataset","RedPajama-fr","train","8d50ff7cfce1a2db7cc5a1ef37d73f5f455f8ad1"),
 ("AlpacaGPT4","vicgalle/alpaca-gpt4",None,"train","f7e3ded725cb81e8e564e32feb12860f376f2b51"),
 ("OpenWebText","Skylion007/openwebtext",None,"train","79d93d786212f7344586290adb811d4ae6a1762c"),
 ("FrenchEvaluation","jpacifico/French-Alpaca-dataset-Instruct-55K",None,"train","c13216a7a935baf62fb81efc56eed1739b222d2f"),
)
def main():
 p=argparse.ArgumentParser();p.add_argument("--audit",required=True);p.add_argument("--output",required=True);a=p.parse_args(); results=[]
 for name,repo,config,split,revision in SOURCES:
  ds=load_dataset(repo,config,split=split,revision=revision,streaming=True)
  features=None if ds.features is None else {k:str(v) for k,v in ds.features.items()}
  schema_source="metadata"
  if features is None:
   sample=next(iter(ds.take(1))); features={k:type(v).__name__ for k,v in sample.items()}; schema_source="one_exact-revision_sample"
  results.append({"name":name,"repo":repo,"config":config,"split":split,"revision":revision,"metadata_reachable":True,"schema_reachable":features is not None,"schema_source":schema_source,"features":features})
 rows=[json.loads(x) for x in Path(a.audit).read_text(encoding="utf-8").splitlines()]
 hosts=sorted({urllib.parse.urlparse(x["final_url"]).hostname for x in rows}); leaks=[x for x in rows if urllib.parse.urlparse(x["final_url"]).hostname=="huggingface.co"]
 out={"status":"PASS" if all(x["schema_reachable"] for x in results) and not leaks else "FAIL","sources":results,"final_hosts":hosts,"request_count":len(rows),"huggingface_co_leaks":leaks}
 Path(a.output).write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n",encoding="utf-8"); print(json.dumps(out,indent=2,ensure_ascii=False))
 if out["status"]!="PASS": raise SystemExit(1)
if __name__=="__main__":main()
