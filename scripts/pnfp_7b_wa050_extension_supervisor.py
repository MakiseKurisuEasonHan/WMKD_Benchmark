"""One bounded WA sensitivity pilot with serial conditional evaluation."""
import hashlib,json,os,shutil,subprocess,time
from pathlib import Path
ROOT=Path('/root/autodl-tmp/WMKD_Benchmark_data/scale_7b');P=Path('/root/autodl-tmp/WMKD_Benchmark');OUT=ROOT/'wa050_extension_v1'

def main():
    assert not OUT.exists(),'Output collision'
    assert not subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader'],text=True).strip()
    assert shutil.disk_usage(ROOT).free>15*1024**3
    OUT.mkdir()
    (OUT/'prelaunch.txt').write_text(subprocess.check_output(['nvidia-smi'],text=True)+'\n'+subprocess.check_output(['df','-h',str(ROOT)],text=True))
    env=dict(os.environ,PATH=str(ROOT/'env/bin')+':/root/miniconda3/bin:/usr/local/cuda/bin:/usr/bin:/bin',PYTHONPATH=str(ROOT/'bnb_0500'),WANDB_MODE='disabled',WANDB_DISABLED='true',TOKENIZERS_PARALLELISM='false',HF_HOME=str(ROOT/'cache/huggingface'),OMP_NUM_THREADS='8',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
    py=str(ROOT/'env/bin/python');fp=json.loads((ROOT/'fingerprint_manifest.json').read_text());peaks={'host_cgroup_bytes':0,'gpu_nvidia_smi_mib':0,'disk_used_bytes':0}
    def run(stage,cmd):
        subprocess.run(['df','-h',str(ROOT)],check=True)
        assert not subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader'],text=True).strip()
        start=time.perf_counter()
        with (OUT/(stage+'.log')).open('x') as log,(OUT/(stage+'_resources.jsonl')).open('x') as samples:
            child=subprocess.Popen(cmd,cwd=P,env=env,stdout=log,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL)
            (OUT/'state.json').write_text(json.dumps({'status':'RUNNING','stage':stage,'pid':child.pid,'supervisor':os.getpid(),'formal_teacher_started':False,'distillation_started':False},indent=2))
            while child.poll() is None:
                row={'time':time.time(),'host_cgroup_bytes':int(Path('/sys/fs/cgroup/memory.current').read_text()),'gpu_nvidia_smi_mib':int(subprocess.check_output(['nvidia-smi','--query-gpu=memory.used','--format=csv,noheader,nounits'],text=True).strip()),'disk_used_bytes':shutil.disk_usage(ROOT).used}
                for k in peaks:peaks[k]=max(peaks[k],row[k])
                samples.write(json.dumps(row)+'\n');samples.flush();time.sleep(2)
        (OUT/(stage+'_exit.json')).write_text(json.dumps({'exit_code':child.returncode,'wall_seconds':time.perf_counter()-start,'cumulative_peaks_sampled_2s':peaks},indent=2))
        assert child.returncode==0,(stage,child.returncode)
    run('training',[py,str(P/'scripts/pnfp_7b_wa050_extension.py')])
    assessment=json.loads((OUT/'assessment.json').read_text())
    run('detector',[py,str(P/'scripts/pnfp_evaluate.py'),'--model-path',assessment['best_checkpoint'],'--fingerprints',fp['official_output'],'--output',str(OUT/'detector.json'),'--label','wa050_extension_final_best_standalone_reload','--count','1024','--use-chat-template','--generation-response-length','1'])
    d=json.loads((OUT/'detector.json').read_text());assert d['fingerprints_evaluated']==1024 and d['invalid_samples']==d['evaluation_errors']==0
    assert d['detected']==assessment['best_fresh_recall'],'Independent detector differs from in-process fresh reload'
    assessment['standalone_fresh_reload_recall']=d['detected'];(OUT/'assessment.json').write_text(json.dumps(assessment,indent=2))
    (OUT/'state.json').write_text(json.dumps({'status':'EXTENSION_COMPLETE','formal_teacher_started':False,'distillation_started':False,'peaks_sampled_2s':peaks},indent=2))
if __name__=='__main__':
    try:main()
    except BaseException:
        import traceback
        if OUT.exists():(OUT/'supervisor_failure.json').write_text(json.dumps({'status':'FAILED_STOPPED','traceback':traceback.format_exc()},indent=2))
        raise
