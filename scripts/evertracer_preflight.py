#!/usr/bin/env python3
"""Minimal scientific/resource/config-effective preflight for EverTracer A."""
import argparse,json,os,shutil,subprocess
from pathlib import Path
import psutil,torch
from transformers import AutoConfig,AutoTokenizer
from evertracer_common import load_config,write_json

def main():
 p=argparse.ArgumentParser();p.add_argument("--config",required=True);p.add_argument("--dataset-root",required=True);p.add_argument("--output",required=True);a=p.parse_args();c=load_config(a.config);m=c["model"];r=c["runtime"]
 model=Path(m["path"]);files=[x for x in model.iterdir() if x.is_file()];total=sum(x.stat().st_size for x in files);manifest=json.loads((Path(a.dataset_root)/"manifest.json").read_text())
 source_head=subprocess.check_output(["git","-C",r["source_root"],"rev-parse","HEAD"],text=True).strip();free,total_v=torch.cuda.mem_get_info();disk=shutil.disk_usage(r["data_root"]);vm=psutil.virtual_memory()
 cfg=AutoConfig.from_pretrained(model,local_files_only=True);tok=AutoTokenizer.from_pretrained(model,local_files_only=True)
 result={"passed":True,"effective_config":c,"model":{"path":str(model),"file_count":len(files),"bytes":total,"expected_files":m["expected_files"],"expected_bytes":m["expected_bytes"],"model_type":cfg.model_type,"chat_template":bool(tok.chat_template)},"dataset_manifest":manifest,"official_source_head":source_head,"gpu":{"name":torch.cuda.get_device_name(0),"count":torch.cuda.device_count(),"bf16":torch.cuda.is_bf16_supported(),"free_vram_bytes":free,"total_vram_bytes":total_v},"ram":{"total":vm.total,"available":vm.available},"data_disk":{"total":disk.total,"used":disk.used,"free":disk.free}}
 checks=[len(files)==m["expected_files"],total==m["expected_bytes"],source_head==c["official_source"]["commit"],manifest["disjoint"],len(manifest["indices"]["dtr"])==100,len(manifest["indices"]["dref"])==1000,len(manifest["indices"]["dunseen"])==100,torch.cuda.device_count()==1,torch.cuda.is_bf16_supported(),free>70*1024**3,vm.available>60*1024**3,disk.free>100*1024**3,c["training"]["target_epochs"]==20,c["training"]["reference_epochs"]==4,c["verification"]["k"]==5,c["verification"]["perturbation_fraction"]==0.30]
 result["checks"]=checks;result["passed"]=all(checks);write_json(a.output,result);print(json.dumps(result,indent=2));raise SystemExit(0 if result["passed"] else 2)
if __name__=="__main__":main()
