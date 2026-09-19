"""Acquire one unchanged negative identity, with per-file transport hashes and disk gate."""
import argparse, hashlib, json, os, shutil, time
from pathlib import Path
from urllib.parse import quote
import requests
from pnfp_7b_disk_gate import budget

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(8<<20),b''):h.update(b)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--slot',type=int,required=True);ap.add_argument('--root',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    p=Path(__file__).resolve().parents[1]
    row=json.loads((p/'results/llmprint/validation_negative_panel_manifest.json').read_text())['models'][a.slot-1]
    model=row['modelscope_id']; rev=row['modelscope_revision']
    api=f'https://www.modelscope.cn/api/v1/models/{model}/repo/files?Revision=master&Recursive=true'
    session=requests.Session(); session.headers['User-Agent']='WMKD_Benchmark/LLMPrint7B'
    response=session.get(api,timeout=90);response.raise_for_status();allfiles=response.json()['Data']['Files']
    weights=[x for x in allfiles if x.get('Type')=='blob' and '/' not in x['Path'] and x['Path'].endswith(('.safetensors','.bin'))]
    assert any(x.get('Revision')==rev for x in weights),'Frozen negative weight revision not present'
    safe=any(x['Path'].endswith('.safetensors') for x in weights)
    rows=[x for x in allfiles if x.get('Type')=='blob' and '/' not in x['Path'] and
          (x['Path'].endswith(('.json','.model','.txt','.tiktoken')) or
           x['Path'].endswith('.safetensors' if safe else '.bin'))]
    # Avoid alternate serialization index for a format not selected.
    rows=[x for x in rows if not (safe and x['Path']=='pytorch_model.bin.index.json')]
    required={}
    if row.get('provenance_evidence'):
        repair=json.loads((p/row['provenance_evidence']).read_text())
        required={x['path']:x for x in repair.get('canonical_file_identity',[])}
        for name,r in required.items():
            match=next((x for x in rows if x['Path']==name),None)
            assert match and match['Sha256']==r['sha256'] and match['Size']==r['bytes'],f'Canonical identity mismatch: {name}'
    for x in rows:assert x.get('Sha256') and int(x['Size'])>=0
    root=a.root/f'slot-{a.slot:02d}';root.mkdir(parents=True,exist_ok=True)
    missing=[x for x in rows if not (root/x['Path']).exists() or (root/x['Path']).stat().st_size!=x['Size'] or sha(root/x['Path'])!=x['Sha256']]
    gate=budget(*shutil.disk_usage(a.root),{'negative_missing_files':sum(x['Size'] for x in missing),'metadata_overhead':2**30})
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.with_suffix('.disk_gate.json').write_text(json.dumps(gate,indent=2))
    assert gate['passed'],'Negative download disk gate failed'
    start=time.time()
    for x in rows:
        file=root/x['Path']
        if file.exists() and file.stat().st_size==x['Size'] and sha(file)==x['Sha256']:continue
        # Immutable per-file blob revision, checked against frozen weight identity.
        url=f'https://www.modelscope.cn/models/{model}/resolve/{x["Revision"]}/{quote(x["Path"])}'
        for attempt in range(3):
            try:
                tmp=file.with_suffix(file.suffix+'.partial')
                with session.get(url,stream=True,timeout=(30,120)) as r:
                    r.raise_for_status()
                    with tmp.open('wb') as out:
                        for block in r.iter_content(4<<20):out.write(block)
                assert tmp.stat().st_size==x['Size'] and sha(tmp)==x['Sha256'],'Downloaded file SHA mismatch'
                tmp.replace(file);break
            except Exception:
                if attempt==2:raise
                time.sleep(3)
    config=json.loads((root/'config.json').read_text())
    assert config['model_type']==row['model_type'] and config['vocab_size']==row['vocab_size']
    assert row['architecture'] in config['architectures'] and not config.get('quantization_config')
    receipt=dict(slot=a.slot,model=model,revision=rev,local_path=str(root),model_metadata=row,
        transport='ModelScope pinned per-file revisions and SHA',replacement=False,files=rows,
        canonical_repair_files_verified=list(required),runtime_seconds=time.time()-start,
        total_bytes=sum(x['Size'] for x in rows),all_files_sha_verified=True)
    a.output.write_text(json.dumps(receipt,indent=2)+'\n')

if __name__=='__main__':main()
