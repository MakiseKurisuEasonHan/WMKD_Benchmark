"""Observe owned worker process groups without treating warnings/silence as failure."""
import os, time, signal
from common import *

def group_snapshot(pid,rr):
    processes=[]; cpu=0
    for path in Path('/proc').glob('[0-9]*/stat'):
        try:
            raw=path.read_text(); fields=raw[raw.rindex(')')+2:].split()
            if int(fields[2])!=pid: continue
            cpu+=int(fields[11])+int(fields[12])
            processes.append({'pid':int(path.parent.name),'state':fields[0],'wchan':(path.parent/'wchan').read_text(),'command':(path.parent/'cmdline').read_bytes().decode(errors='replace').replace('\0',' ')[:500]})
        except (OSError,ValueError,IndexError): continue
    latest=0; size=0
    for p in Path(rr).rglob('*'):
        try:
            if p.is_file(): st=p.stat(); latest=max(latest,st.st_mtime); size+=st.st_size
        except OSError: pass
    return {'cpu_ticks':cpu,'processes':processes,'output_bytes':size,'latest_output_mtime':latest}

def quiescent():
    # All five methods must already be terminal; this gate also rejects orphan workers/uploads.
    me=os.getpid(); conflicts=[]
    for path in Path('/proc').glob('[0-9]*/cmdline'):
        try:
            pid=int(path.parent.name)
            if pid==me: continue
            text=path.read_bytes().decode(errors='replace')
            if any(x in text for x in ('methods_11_15/worker.py','methods_11_15/archive.py','methods_11_15/eaaw_eval.py','methods_11_15/double_i_eval.py','methods_11_15/utf_eval.py')): conflicts.append(pid)
        except OSError: pass
    return gpu_free() and not conflicts
