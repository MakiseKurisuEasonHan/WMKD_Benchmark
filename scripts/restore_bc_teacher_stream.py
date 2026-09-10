"""Stream the exact archived iSeal Teacher through old CPU to new GPU; no tokens forwarded."""
import datetime,hashlib,json,os,subprocess,sys,time
from pathlib import Path
P=Path('/root/autodl-tmp/WMKD_Benchmark')
Q=P/'results/logit_distillation/same_lineage_bc/iseal'
M=Q/'teacher_source_manifest.json'
ROOTS={'iseal':str(P)+'_data/runs/iseal/a6/iseal_a6_20260830_132300/checkpoints/teacher_merged','scw':str(P)+'_data/runs/scw/a2/scw_a2_20260831_214339/models/Llama-3.2-3B-Instruct_scw_a2_20260831_214339_French_WMKD_SCW_A'}
REPOS={'iseal':'MakiseKurisuEasonHan/WMKD-iSeal-A6-Teacher','scw':'MakiseKurisuEasonHan/WMKD-SCW-A2-Teacher'}
def select(method):
 global Q,M
 assert method in ROOTS
 Q=P/'results/logit_distillation/same_lineage_bc'/method;M=Q/'teacher_source_manifest.json'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(2<<20),b''):h.update(b)
 return h.hexdigest()
def receive():
 a=os.environ['SSH_ORIGINAL_COMMAND'].split();assert len(a) in (3,4) and a[0]=='bc-restore';select(a[1])
 m=json.loads(M.read_text());x=m['files'][int(a[2])];assert Path(x['path']).name==x['path']
 root=Path(m['source_artifact_path']);assert root==Path(ROOTS[a[1]])
 root.mkdir(parents=True,exist_ok=True);p=root/x['path'];part=p.with_name(p.name+'.bc-restore-partial')
 assert not p.is_symlink() and not part.is_symlink()
 if len(a)==4:
  assert a[3]=='status'
  ok=p.exists() and p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
  assert not p.exists() or ok
  print(json.dumps({'complete':ok}));return
 if p.exists():
  assert p.stat().st_size==x['bytes'] and sha(p)==x['sha256'];print('ALREADY_SHA_PASS',flush=True);return
 # Preserve any interrupted partial; append only after identical incoming prefix verification.
 offset=part.stat().st_size if part.exists() else 0;assert offset<=x['bytes']
 h=hashlib.sha256();count=0
 with part.open('a+b') as out:
  out.seek(0)
  while count<offset:
   b=sys.stdin.buffer.read(min(2<<20,offset-count));assert b and out.read(len(b))==b
   h.update(b);count+=len(b)
  out.seek(0,2)
  while b:=sys.stdin.buffer.read(2<<20):
   count+=len(b);assert count<=x['bytes'];out.write(b);h.update(b)
  out.flush();os.fsync(out.fileno())
 assert count==x['bytes'] and h.hexdigest()==x['sha256'];part.rename(p);print('SHA_PASS',flush=True)
def send():
 import modelscope_passive5_ba_student_archive as helper
 method=sys.argv[1] if len(sys.argv)>1 else 'iseal';select(method)
 m=json.loads(M.read_text());repo=m['repo_id'];assert repo==REPOS[method]
 api=helper.api_client();assert helper.is_private(api.get_repo(repo,'model'))
 remote={f.path:f for f in api.list_repo_files(repo,'model',revision='master',recursive=True) if not f.is_dir}
 r={'status':'RUNNING','pid':os.getpid(),'repo':repo,'retrieval_ref':'master','identity_basis':'historical frozen full-file SHA; no mutable-ref equivalence claim','files':[]}
 def save():
  r['updated_at']=datetime.datetime.now(datetime.timezone.utc).isoformat();t=Q/'teacher_restore_receipt.tmp';t.write_text(json.dumps(r,indent=2)+'\n');t.replace(Q/'teacher_restore_receipt.json')
 ssh=['ssh','-T','-p','49453','-i','/root/.ssh/id_ed25519','-o','IdentitiesOnly=yes','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile=/root/.ssh/wmkd_xbb_known_hosts','-o','ConnectTimeout=20','root@connect.westd.seetacloud.com']
 save()
 try:
  for i,x in enumerate(m['files']):
   rf=remote[x['path']];lfs=rf.lfs or {};identity=lfs.get('sha256') or str(lfs.get('oid','')).removeprefix('sha256:') or rf.sha256
   assert rf.size==x['bytes'] and identity==x['sha256'],x['path']
   st=json.loads(subprocess.check_output(ssh+[f'bc-restore {method} {i} status'],text=True))
   if st['complete']:
    r['files'].append(dict(x,verified=True,reused=True));save();continue
   r.update(current_file=x['path'],received_bytes=0);save()
   child=subprocess.Popen(ssh+[f'bc-restore {method} {i}'],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
   response=api.downloader._client.download_stream(repo,'model',x['path'],'master',headers=api.downloader._build_download_headers());response.raise_for_status()
   h=hashlib.sha256();count=0;last=time.monotonic()
   with response:
    for b in response.iter_content(chunk_size=2<<20):
     if not b:continue
     count+=len(b);assert count<=x['bytes'];h.update(b);child.stdin.write(b)
     if time.monotonic()-last>15:r['received_bytes']=count;save();last=time.monotonic()
   child.stdin.close();out=child.stdout.read();assert child.wait()==0 and b'SHA_PASS' in out
   assert count==x['bytes'] and h.hexdigest()==x['sha256']
   r['files'].append(dict(x,verified=True));save()
  r.update(status='PASS',current_file=None);save()
 except Exception as exc:r.update(status='ERROR_REVIEW_REQUIRED',error=type(exc).__name__+': '+str(exc));save();raise
if __name__=='__main__':send()
