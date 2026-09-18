"""One detached pilot, resource samples, no continuation or automatic retry."""
import json, os, shutil, subprocess, time
from pathlib import Path
ROOT=Path('/root/autodl-tmp/WMKD_Benchmark_data/scale_7b');P=Path('/root/autodl-tmp/WMKD_Benchmark')
OUT=ROOT/os.environ.get('PNFP_GPU_BF16_RUN','gpu_bf16_pilot_v1')

def main():
    OUT.mkdir(exist_ok=False)
    assert not subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader'],text=True).strip()
    assert shutil.disk_usage(ROOT).free>20*1024**3
    (OUT/'prelaunch.txt').write_text(subprocess.check_output(['nvidia-smi'],text=True)+'\n'+subprocess.check_output(['df','-h',str(ROOT)],text=True))
    env=dict(os.environ,PATH=str(ROOT/'env/bin')+':/root/miniconda3/bin:/usr/local/cuda/bin:/usr/bin:/bin',PYTHONPATH=str(ROOT/'ds_bf16_0196'),WANDB_MODE='disabled',WANDB_DISABLED='true',TOKENIZERS_PARALLELISM='false',HF_HOME=str(ROOT/'cache/huggingface'),TORCH_EXTENSIONS_DIR=str(ROOT/'cache/torch_extensions_bf16_0196'),MAX_JOBS='4',OMP_NUM_THREADS='8',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
    cmd=[str(ROOT/'env/bin/python'),'-m','deepspeed.launcher.runner','--num_gpus=1','--master_port=29604',str(P/'scripts/pnfp_7b_gpu_bf16_pilot.py')]
    peaks={'host_cgroup_bytes':0,'gpu_nvidia_smi_mib':0,'disk_used_bytes':0}
    with (OUT/'train.log').open('x') as log, (OUT/'resource_samples.jsonl').open('x') as samples:
        child=subprocess.Popen(cmd,cwd=P,env=env,stdout=log,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL)
        (OUT/'launch.json').write_text(json.dumps({'pid':child.pid,'supervisor':os.getpid(),'command':cmd,'teacher_authorized':False},indent=2))
        while child.poll() is None:
            gpu=int(subprocess.check_output(['nvidia-smi','--query-gpu=memory.used','--format=csv,noheader,nounits'],text=True).strip())
            row={'time':time.time(),'host_cgroup_bytes':int(Path('/sys/fs/cgroup/memory.current').read_text()),'gpu_nvidia_smi_mib':gpu,'disk_used_bytes':shutil.disk_usage(ROOT).used}
            for k in peaks:peaks[k]=max(peaks[k],row[k])
            samples.write(json.dumps(row)+'\n');samples.flush();time.sleep(1)
    (OUT/'exit.json').write_text(json.dumps({'exit_code':child.returncode,'peaks_sampled_1s':peaks,'teacher_started':False,'automatic_retry':False},indent=2))

if __name__=='__main__':main()
