"""Pinned, hash-verified Chat snapshot; bounded retries and no duplicate cache."""
import concurrent.futures as cf
import hashlib, json, os, shutil, time, traceback
from pathlib import Path
import requests

ROOT=Path('/root/autodl-tmp/WMKD_Benchmark_data/scale_7b')
OUT=ROOT/'models/Llama-2-7b-chat-hf'
REV='299e68d813ff6f146741f8e8477ed0a57ded4765'
URL='https://modelscope.cn/api/v1/models/shakechen/Llama-2-7b-chat-hf/repo'
EXPECTED={
 'model-00001-of-00002.safetensors':'66dec18c9f1705b9387d62f8485f4e7d871ca388718786737ed3c72dbfaac9fb',
 'model-00002-of-00002.safetensors':'0fd6895090da1b2ccffdb93964847709a3b31e6b69fe7dc5a480dce37c811b1d',
 'config.json':'c904bd84ff892a2a0a454a35a4031914ccb65a82974ac8ab0fe34d3744656fc2',
 'tokenizer_config.json':'04aaa6eedd97412f3e63dd2493d2388b82347dd512b89192d3e9b4973a176417',
 'tokenizer.json':'bcd04f0eadf90287bd26e1a183ac487d8a141b09b06aecb7725bbdd343640f2e',
 'tokenizer.model':'9e556afd44213b6bd1be2b850ebbbd98f5481437a8021afaf58ee7fb1818d347',
 'special_tokens_map.json':'6fa06efa2785e450051989a6f8fb4416b10149ded485ddd3f127a40734f5cfd0',
 'generation_config.json':'4eb769d945b7c9a9d9b5ee0cff40ac23a62e218ac683f87ac68d8ad9cd18dd7f',
 'model.safetensors.index.json':'11b694a9d4bffdac71733db7f782be0df1f87a65fb9ef05bcf6d317029c22364',
 'LICENSE.txt':'8c17c2ebb0ea011be9981cc3922db8ca8fa61e828c5d3f44cb6ae342bf80460b',
}
def put(name,obj):
    p=ROOT/name;t=p.with_suffix('.tmp');t.write_text(json.dumps(obj,indent=2));t.replace(p)
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(8<<20),b''):h.update(b)
    return h.hexdigest()
def segment(name,fd,start,end,total):
    for attempt in range(3):
        try:
            with requests.get(URL,params={'Revision':REV,'FilePath':name},headers={'Range':f'bytes={start}-{end}'},stream=True,timeout=(20,45)) as r:
                r.raise_for_status()
                assert r.status_code==206 and r.headers['Content-Range']==f'bytes {start}-{end}/{total}',dict(r.headers)
                pos=start
                for b in r.iter_content(1<<20):
                    if b:
                        assert pos+len(b)<=end+1
                        n=os.pwrite(fd,b,pos);assert n==len(b);pos+=n
                assert pos==end+1,(pos,end)
            return end-start+1
        except Exception:
            if attempt==2:raise
            time.sleep(2)
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    files=json.loads((ROOT/'probes/modelscope_chat_identity.json').read_text())['Data']['Files']
    files={x['Path']:x for x in files}
    for n,h in EXPECTED.items():assert files[n]['Sha256']==h,(n,'canonical mismatch')
    total=sum(files[n]['Size'] for n in EXPECTED)
    assert shutil.disk_usage(ROOT).free>total+8*1024**3
    started=time.monotonic();done=0;manifest=[]
    # Download metadata first, then weights. Full-file hash checks are mandatory.
    for name in sorted(EXPECTED,key=lambda n:files[n]['Size']):
        item=files[name];path=OUT/name
        if path.exists():
            assert path.stat().st_size==item['Size'] and sha(path)==EXPECTED[name]
            done+=item['Size'];manifest.append(item);continue
        part=path.with_name(path.name+'.partial')
        assert not part.exists(),'Inspect interrupted download before resuming'
        fd=os.open(part,os.O_CREAT|os.O_EXCL|os.O_RDWR,0o600)
        try:
            if item['Size']<16*1024**2:
                r=requests.get(URL,params={'Revision':REV,'FilePath':name},timeout=45);r.raise_for_status()
                assert len(r.content)==item['Size'];os.write(fd,r.content);done+=len(r.content)
            else:
                block=64*1024**2
                sample_start=time.monotonic()
                n=segment(name,fd,0,min(block,item['Size'])-1,item['Size']);done+=n
                elapsed=time.monotonic()-sample_start
                speed=n/elapsed/1e6
                put('chat_download_speed.json',{'file':name,'bytes':n,'seconds':elapsed,'MB_s':speed,'single_connection_full_eta_seconds':total/(n/elapsed),'expected_bytes':total,'free_bytes':shutil.disk_usage(ROOT).free})
                assert speed>=1,'Transport under 1 MB/s: stop and inspect alternatives'
                with cf.ThreadPoolExecutor(max_workers=8) as pool:
                    jobs=[pool.submit(segment,name,fd,s,min(s+block,item['Size'])-1,item['Size']) for s in range(block,item['Size'],block)]
                    for job in cf.as_completed(jobs):
                        done+=job.result(); elapsed=time.monotonic()-started
                        put('download_progress.json',{'status':'RUNNING','bytes':done,'total':total,'wall_seconds':elapsed,'aggregate_MB_s':done/elapsed/1e6,'active_file':name,'pid':os.getpid()})
            os.fsync(fd)
        finally:os.close(fd)
        assert part.stat().st_size==item['Size'] and sha(part)==EXPECTED[name],name
        part.replace(path);manifest.append(item)
        print('VERIFIED',name,flush=True)
    put('model_manifest.json',{'status':'COMPLETE','canonical_upstream':'meta-llama/Llama-2-7b-chat-hf','canonical_revision':'f5db02db724555f92da89c216ac04704f23d4590','transport_repo':'shakechen/Llama-2-7b-chat-hf','transport_revision':REV,'canonical_hash_reference':'results/methods_11_15/utf/engineering_resume_20260907/receipts/MODEL_DATA_READY.5.json (model files only)','path':str(OUT),'files':manifest,'seconds':time.monotonic()-started,'bytes':total})
    put('download_exit.json',{'returncode':0})
if __name__=='__main__':
    try:main()
    except BaseException:
        put('download_exit.json',{'returncode':1,'error':traceback.format_exc()});raise
