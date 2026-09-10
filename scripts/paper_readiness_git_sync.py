"""Fast-forward the CPU audit checkout; preserve incoming untracked preimages."""
from pathlib import Path
import subprocess,sys,json,hashlib,tarfile,datetime
P=Path('/root/autodl-tmp/WMKD_Benchmark')
def git(*args):return subprocess.check_output(['git','-C',str(P),*args]).decode().strip()
before=git('rev-parse','HEAD');assert not git('diff','--cached','--name-only')
bundle=Path(sys.argv[1]);assert hashlib.sha256(bundle.read_bytes()).hexdigest()==sys.argv[2]
git('fetch',str(bundle),'main:refs/remotes/origin/main');target=git('rev-parse','origin/main')
subprocess.run(['git','-C',str(P),'merge-base','--is-ancestor',before,target],check=True)
incoming=set(git('diff','--name-only',before,target).splitlines())
changed=set(git('diff','--name-only','HEAD').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines())
conflicts=sorted(incoming&changed);stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
backup=Path('/root/autodl-tmp/WMKD_Benchmark_data/tmp')/('paper_audit_git_preimages_'+stamp+'.tar.gz')
with tarfile.open(backup,'w:gz') as out:
 for name in conflicts:
  f=P/name;assert f.is_file() and not f.is_symlink() and f.stat().st_size<64*1024**2
  out.add(f,arcname=name)
stash=None
if conflicts:
 git('stash','push','--include-untracked','-m','Preserve paper audit incoming preimages '+stamp,'--',*conflicts)
 stash=git('rev-parse','refs/stash')
git('merge','--ff-only','origin/main');assert git('rev-parse','HEAD')==target
receipt={'at':stamp,'before':before,'after':target,'bundle_sha256':sys.argv[2],'backup':str(backup),'backup_sha256':hashlib.sha256(backup.read_bytes()).hexdigest(),'preserved_stash':stash,'conflict_paths':conflicts,'mode':'FAST_FORWARD_ONLY','no_scientific_execution':True}
Path('/tmp/paper_audit_git_sync_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))
