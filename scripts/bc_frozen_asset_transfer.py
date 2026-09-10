"""Exact-manifest transfer with prefix-verified continuation; no model substitution."""
import hashlib,json,os,subprocess,sys,time
from pathlib import Path
P=Path('/root/autodl-tmp/WMKD_Benchmark')
Q=P/'results/logit_distillation/same_lineage_bc/evertracer'
M=Q/'transfer_recovery_manifest.json'
def select_method(method):
 global Q,M
 assert method in ('evertracer','passive_shared')
 Q=P/'results/logit_distillation/same_lineage_bc'/method
 M=Q/'transfer_recovery_manifest.json'
def digest(p,limit=None):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while limit is None or limit>0:
   b=f.read(min(8<<20,limit) if limit is not None else 8<<20)
   if not b:break
   h.update(b)
   if limit is not None:limit-=len(b)
 return h.hexdigest()
def receive():
 a=os.environ['SSH_ORIGINAL_COMMAND'].split();assert a[0]=='bc-receive'
 if a[1]=='passive_shared':select_method(a.pop(1))
 op,i=a[1:3];x=json.loads(M.read_text())['files'][int(i)];p=Path(x['path'])
 assert p.resolve().is_relative_to(Path(str(P)+'_data')) and not p.is_symlink()
 size=p.stat().st_size if p.exists() else 0;assert size<=x['bytes']
 if op=='status':print(json.dumps({'bytes':size,'sha256':digest(p) if p.exists() else hashlib.sha256(b'').hexdigest()}));return
 assert op=='append' and len(a)==5 and size==int(a[3])
 assert (digest(p) if p.exists() else hashlib.sha256(b'').hexdigest())==a[4]
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('ab') as f:
  while b:=sys.stdin.buffer.read(2<<20):
   size+=len(b);assert size<=x['bytes'];f.write(b)
  f.flush();os.fsync(f.fileno())
 assert size==x['bytes'] and digest(p)==x['sha256'];print('SHA_PASS')
def send():
 rows=json.loads(M.read_text())['files'];r={'status':'RUNNING','pid':os.getpid(),'files':[]}
 def save():
  r['updated_at']=time.time();(Q/'direct_transfer_receipt.json').write_text(json.dumps(r,indent=2)+'\n')
 ssh=['ssh','-T','-p','49453','-i','/root/.ssh/id_ed25519','-o','IdentitiesOnly=yes','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile=/root/.ssh/wmkd_xbb_known_hosts','-o','ConnectTimeout=20','-o','ServerAliveInterval=15','root@connect.westd.seetacloud.com']
 save()
 try:
  for i,x in enumerate(rows):
   p=Path(x.get('source',x['path']));assert p.stat().st_size==x['bytes'] and digest(p)==x['sha256']
   prefix='bc-receive passive_shared' if Q.name=='passive_shared' else 'bc-receive'
   st=json.loads(subprocess.check_output(ssh+[f'{prefix} status {i}'],text=True));offset=st['bytes'];assert offset<=x['bytes'] and digest(p,offset)==st['sha256']
   r.update(current_file=str(p),starting_offset=offset);save()
   if offset<x['bytes']:
    child=subprocess.Popen(ssh+[f"{prefix} append {i} {offset} {st['sha256']}"],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
    with p.open('rb') as f:
     f.seek(offset)
     while b:=f.read(2<<20):child.stdin.write(b)
    child.stdin.close();out=child.stdout.read();assert child.wait()==0 and b'SHA_PASS' in out
   r['files'].append(dict(x,verified=True));save()
  r.update(status='PASS',current_file=None);save()
 except Exception as exc:r.update(status='ERROR_REVIEW_REQUIRED',error=str(exc));save();raise
if __name__=='__main__':
 if len(sys.argv)>2:select_method(sys.argv[2])
 if sys.argv[1]=='receive':receive()
 else:send()
