import subprocess,json,time,os
from pathlib import Path
E=Path("/root/autodl-tmp/WMKD_Benchmark/results/scw/experiment_ba_trajectory_followup")
CE=E/"continuation_cont3"
cmd=["/root/autodl-tmp/WMKD_Benchmark_data/artifacts/scw/env_py311/bin/python","-B","/root/autodl-tmp/WMKD_Benchmark/scripts/scw_ba_trajectory_continuation.py",str(E/"run_spec.json")]
with (CE/"worker_stdout.log").open("x") as out:
 w=subprocess.Popen(cmd,stdout=out,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL)
 (CE/"launch_record.json").write_text(json.dumps(dict(worker_pid=w.pid,supervisor_pid=os.getpid(),command=cmd,time=time.time(),resume_step=50)))
 with (CE/"resource_samples.jsonl").open("x") as log:
  while w.poll() is None:
   r=dict(time=time.time(),memory_current=Path("/sys/fs/cgroup/memory.current").read_text().strip(),events=Path("/sys/fs/cgroup/memory.events").read_text())
   try:r["worker_status"]=Path(f"/proc/{w.pid}/status").read_text()
   except FileNotFoundError:pass
   log.write(json.dumps(r)+"\n");log.flush();time.sleep(5)
 (CE/"exit_record.json").write_text(json.dumps(dict(returncode=w.returncode,time=time.time(),automatic_retry=False)))
