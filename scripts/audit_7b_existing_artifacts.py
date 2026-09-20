"""CPU-only read/hash audit; never loads a model or runs an evaluator."""
import argparse,hashlib,json,pathlib,subprocess,time

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    return h.hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--inputs',required=True);ap.add_argument('--output',required=True);args=ap.parse_args()
    payload=json.loads(pathlib.Path(args.inputs).read_text());out=pathlib.Path(args.output);out.mkdir(parents=True,exist_ok=True)
    progress=out/'verification_progress.json'
    previous=json.loads(progress.read_text()) if progress.exists() else {}
    result=dict(started=previous.get('started',time.time()),mode='CPU_ONLY_READ_HASH_EXISTING_ARTIFACTS',groups=[],evidence=[],no_science_executed=True)
    for group in payload['groups']:
        root=pathlib.Path(group['root']);rows=[]
        normalized=[dict(path=x.get('path',x.get('Path')),sha256=x.get('sha256',x.get('Sha256')),**({'bytes':x.get('bytes',x.get('Size'))} if 'bytes' in x or 'Size' in x else {})) for x in group['files']]
        prior=next((x for x in previous.get('groups',[]) if x['name']==group['name'] and x['passed']),None)
        if prior and len(prior['files'])==len(normalized):
            old={x['path']:x for x in prior['files']}
            if all(str(root/x['path']) in old and old[str(root/x['path'])]['sha256']==x['sha256'] and (root/x['path']).stat().st_size==old[str(root/x['path'])]['bytes'] and (root/x['path']).stat().st_mtime<result['started'] for x in normalized):
                result['groups'].append(prior);print(json.dumps(dict(group=group['name'],reused_same_audit_hashes=True)),flush=True);continue
        for x in normalized:
            f=root/x['path'];assert f.resolve().is_relative_to(root.resolve())
            row=dict(path=str(f),exists=f.is_file(),expected_sha256=x['sha256'])
            if f.is_file():
                row.update(bytes=f.stat().st_size,sha256=sha(f));row['passed']=row['sha256']==x['sha256'] and ('bytes' not in x or row['bytes']==x['bytes'])
            else:row['passed']=False
            rows.append(row)
        r=dict(name=group['name'],files=rows,passed=all(x['passed'] for x in rows));result['groups'].append(r)
        (out/'verification_progress.json').write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps(dict(group=r['name'],files=len(rows),passed=r['passed'])),flush=True)
    repo=pathlib.Path('/root/autodl-tmp/WMKD_Benchmark')
    for x in payload['local_evidence']:
        f=repo/x['path'];actual=sha(f) if f.is_file() else None
        result['evidence'].append(dict(path=x['path'],local_sha256=x['sha256'],remote_sha256=actual,passed=actual==x['sha256']))
    result.update(ended=time.time(),passed=all(x['passed'] for x in result['groups']) and all(x['passed'] for x in result['evidence']))
    result['disk']=subprocess.check_output(['df','-B1','/root/autodl-tmp'],text=True)
    lines=subprocess.check_output(['ps','-eo','pid,args'],text=True).splitlines()
    names=['awm_7b_campaign.py','llmprint_7b_campaign.py','llmprint_7b_construct.py','pnfp_7b_distill_worker.py','generate_teacher_qa_formal.py']
    result['science_worker_pids']=[int(line.split()[0]) for line in lines if any(n in line for n in names)]
    (out/'verification_final.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'passed':result['passed'],'elapsed_seconds':result['ended']-result['started']}),flush=True)
if __name__=='__main__':main()
