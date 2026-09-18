"""Resume only utility after missing ARC train split, before any scoring occurred."""
import json,os,shutil,subprocess,time
from pathlib import Path
from pnfp_7b_teacher_supervisor import ROOT,P,OUT

def main():
    old=json.loads((OUT/'state.json').read_text())
    assert old=={'status':'FAILED_STOPPED','stage':'utility','exit_code':1,'distillation_started':False},old
    assert "KeyError: 'train'" in (OUT/'utility.log').read_text()
    assert not (OUT/'utility.json').exists()
    assert not subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader'],text=True).strip()
    subprocess.run(['nvidia-smi'],check=True);subprocess.run(['df','-h',str(ROOT)],check=True)
    env=dict(os.environ,PATH=str(ROOT/'env/bin')+':/root/miniconda3/bin:/usr/local/cuda/bin:/usr/bin:/bin',PYTHONPATH=str(ROOT/'bnb_0500'),WANDB_MODE='disabled',WANDB_DISABLED='true',TOKENIZERS_PARALLELISM='false',HF_HOME=str(ROOT/'cache/huggingface'),OMP_NUM_THREADS='8',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
    cmd=[str(ROOT/'env/bin/python'),str(P/'scripts/pnfp_7b_final_utility.py'),'--base',str(ROOT/'models/Llama-2-7b-chat-hf'),'--a2',str(OUT/'final_model'),'--output',str(OUT/'utility.json'),'--batch-size','8']
    peaks=json.loads((OUT/'utility_exit.json').read_text())['cumulative_peaks_sampled_2s']
    start=time.time()
    with (OUT/'utility_cont1.log').open('x') as log,(OUT/'utility_cont1_resources.jsonl').open('x') as samples:
        child=subprocess.Popen(cmd,cwd=P,env=env,stdout=log,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL)
        (OUT/'state.json').write_text(json.dumps({'status':'RUNNING','stage':'utility_cont1','pid':child.pid,'supervisor':os.getpid(),'distillation_started':False},indent=2))
        while child.poll() is None:
            row={'time':time.time(),'host_cgroup_bytes':int(Path('/sys/fs/cgroup/memory.current').read_text()),'gpu_nvidia_smi_mib':int(subprocess.check_output(['nvidia-smi','--query-gpu=memory.used','--format=csv,noheader,nounits'],text=True).strip()),'disk_used_bytes':shutil.disk_usage(ROOT).used}
            for k in peaks:peaks[k]=max(peaks[k],row[k])
            samples.write(json.dumps(row)+'\n');samples.flush();time.sleep(2)
    (OUT/'utility_final_exit.json').write_text(json.dumps({'exit_code':child.returncode,'wall_seconds':time.time()-start,'cumulative_peaks_sampled_2s':peaks,'engineering_fix':'Restore canonical ARC train/validation split for lm_eval initialization; original failure preceded scoring; unchanged test data and scoring.'},indent=2))
    (OUT/'state.json').write_text(json.dumps({'status':'TEACHER_EVALUATIONS_COMPLETE_AWAITING_ASSESSMENT' if child.returncode==0 else 'FAILED_STOPPED','stage':'utility_cont1','exit_code':child.returncode,'distillation_started':False,'peaks_sampled_2s':peaks},indent=2))
if __name__=='__main__':main()
