"""Delete only seven identity-pinned optimizer.pt files after explicit user approval."""
import json
import os
import stat
import subprocess
from datetime import datetime, timezone
from pathlib import Path

D = Path('/root/autodl-tmp/WMKD_Benchmark_data')
O = Path('/root/autodl-tmp/WMKD_Benchmark/results/cross_method_audit_20260907')

def now(): return datetime.now(timezone.utc).isoformat()
def free():
    s=os.statvfs(D)
    return s.f_bavail*s.f_frsize

def main(payload):
    assert payload['user_approved_exact_seven'] is True
    assert payload['scw_ba_original_dataset_exception_approved'] is True
    assert payload['no_resume_or_retraining'] is True
    rows=payload['candidates'];assert len(rows)==7 and len({r['path'] for r in rows})==7
    protected=list(payload['protected'])
    target_paths={r['path'] for r in rows}
    known={r['path'] for r in protected}
    for r in rows:
        p=Path(r['path'])
        for root in [p.parent,p.parent.parent/'final_model']:
            for f in root.rglob('*'):
                if f.is_file() and str(f) not in target_paths and str(f) not in known:
                    s=f.stat();protected.append({'path':str(f),'bytes':s.st_size,'inode':s.st_ino,'mtime_ns':s.st_mtime_ns})
                    known.add(str(f))
    for r in rows:
        p=Path(r['path']);s=p.lstat()
        assert p.is_relative_to(D/'runs') and p.resolve()==p
        assert p.name=='optimizer.pt' and p.parent.name=='checkpoint-7500'
        assert stat.S_ISREG(s.st_mode) and s.st_nlink==1
        assert (s.st_ino,s.st_dev,s.st_size,s.st_mtime_ns)==(r['inode'],r['device'],r['bytes'],r['mtime_ns'])
        assert r['identity_match'] and r['optimizer_structure'] and not r['active_references']
    for r in protected:
        p=Path(r['path']);s=p.stat()
        assert (s.st_size,s.st_mtime_ns,s.st_ino)==(r['bytes'],r['mtime_ns'],r['inode']),str(p)
    paths={r['path'] for r in rows}
    for proc in Path('/proc').iterdir():
        if not proc.name.isdigit() or int(proc.name)==os.getpid():continue
        try:
            cmd=(proc/'cmdline').read_bytes().replace(b'\0',b' ').decode(errors='replace')
            assert not any(p in cmd or str(Path(p).parent) in cmd for p in paths), 'active command reference'
            maps=(proc/'maps').read_text(errors='replace')
            assert not any(p in maps for p in paths),'active mmap reference'
            for fd in (proc/'fd').iterdir():
                assert str(fd.resolve()) not in paths,'active open file reference'
        except (OSError,PermissionError):continue
    O.mkdir(parents=True,exist_ok=True)
    receipt=O/'optimizer_cleanup_execution.json'
    assert not receipt.exists(), 'receipt already exists; inspect it instead of replaying deletion'
    result={'started_at':now(),'status':'VALIDATED_BEFORE_DELETE','authorization':payload['authorization'],
            'scw_ba_original_dataset_exception_approved':True,'protected_file_count':len(protected),
            'free_before_bytes':free(),'deleted':[]}
    def save():
        temp=receipt.with_suffix('.tmp');temp.write_text(json.dumps(result,indent=2)+'\n');os.replace(temp,receipt)
    save()
    for r in rows:
        p=Path(r['path']);before=free();p.unlink()
        assert not p.exists()
        result['deleted'].append({'path':str(p),'logical_bytes':r['bytes'],
          'released_allocated_bytes':r['allocated_bytes'],'df_free_delta_bytes':free()-before,'deleted_at':now()})
        save()
    for r in protected:
        s=Path(r['path']).stat()
        assert (s.st_size,s.st_mtime_ns,s.st_ino)==(r['bytes'],r['mtime_ns'],r['inode']),r['path']
    result.update(status='COMPLETE',ended_at=now(),free_after_bytes=free(),
                  released_allocated_bytes=sum(r['released_allocated_bytes'] for r in result['deleted']),
                  protected_stat_verification='PASS',other_deleted_paths=[],training_started=False)
    result['df_free_delta_bytes']=result['free_after_bytes']-result['free_before_bytes']
    result['df_h']=subprocess.run(['df','-h',str(D)],capture_output=True,text=True).stdout
    save();print(json.dumps(result,indent=2))
