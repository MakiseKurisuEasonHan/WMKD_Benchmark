"""Single isolated AdamW8bit model pilot; no retries or Teacher continuation."""
import json,os,shutil,subprocess,time
from pathlib import Path
ROOT=Path('/root/autodl-tmp/WMKD_Benchmark_data/scale_7b');P=Path('/root/autodl-tmp/WMKD_Benchmark');OUT=ROOT/os.environ.get('PNFP_8BIT_RUN','adamw8bit_pilot_v1')
def main():
    assert json.loads((ROOT/'bnb_preflight.json').read_text())['status']=='PASS'
    assert not subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader'],text=True).strip()
    assert shutil.disk_usage(ROOT).free>20*1024**3
    OUT.mkdir(exist_ok=False)
    (OUT/'prelaunch.txt').write_text(subprocess.check_output(['nvidia-smi'],text=True)+'\n'+subprocess.check_output(['df','-h',str(ROOT)],text=True))
    env=dict(os.environ,PATH=str(ROOT/'env/bin')+':/root/miniconda3/bin:/usr/local/cuda/bin:/usr/bin:/bin',PYTHONPATH=str(ROOT/'bnb_0500'),WANDB_MODE='disabled',WANDB_DISABLED='true',TOKENIZERS_PARALLELISM='false',HF_HOME=str(ROOT/'cache/huggingface'),OMP_NUM_THREADS='8',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
    cmd=[str(ROOT/'env/bin/python'),str(P/'scripts/pnfp_7b_adamw8bit_pilot.py')]
    peaks={'host_cgroup_bytes':0,'gpu_nvidia_smi_mib':0,'disk_used_bytes':0}
    with (OUT/'train.log').open('x') as log,(OUT/'resource_samples.jsonl').open('x') as samples:
        child=subprocess.Popen(cmd,cwd=P,env=env,stdout=log,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL)
        (OUT/'launch.json').write_text(json.dumps({'pid':child.pid,'supervisor':os.getpid(),'command':cmd,'teacher_authorized':False},indent=2))
        while child.poll() is None:
            row={'time':time.time(),'host_cgroup_bytes':int(Path('/sys/fs/cgroup/memory.current').read_text()),'gpu_nvidia_smi_mib':int(subprocess.check_output(['nvidia-smi','--query-gpu=memory.used','--format=csv,noheader,nounits'],text=True).strip()),'disk_used_bytes':shutil.disk_usage(ROOT).used}
            for k in peaks:peaks[k]=max(peaks[k],row[k])
            samples.write(json.dumps(row)+'\n');samples.flush();time.sleep(1)
    (OUT/'exit.json').write_text(json.dumps({'exit_code':child.returncode,'peaks_sampled_1s':peaks,'teacher_started':False,'automatic_retry':False},indent=2))
if __name__=='__main__':main()
