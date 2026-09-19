"""Independent 7B construction stage; all scientific settings come from frozen A2."""
import json, os, shutil, subprocess, time, traceback
from pathlib import Path
import pnfp_7b_distill_campaign as runtime

P=runtime.P
O=Path('/root/autodl-tmp/WMKD_Benchmark_data/llmprint_7b')
E=P/'results/llmprint/scale_7b'
runtime.E=E; runtime.R=O
runtime.ENV['PYTHONPATH']=str(O/'runtime451')+':'+str(P/'scripts')
runtime.ENV['CUBLAS_WORKSPACE_CONFIG']=':4096:8'
put=runtime.put;sha=runtime.sha

def main():
    E.mkdir(parents=True,exist_ok=True)
    assert not (E/'construction_terminal.json').exists()
    cfg=P/'configs/watermark/llmprint_7b.json'
    source=O/'pairs_300.json';data=json.loads(source.read_text())
    assert data['tokenizer_revision']=='f5db02db724555f92da89c216ac04704f23d4590'
    assert len(data['pairs'])==300
    subset=dict(data,source_sha256=sha(source),selection='first200 of300',pairs=data['pairs'][:200])
    put(E/'pairs_200.json',subset);shutil.copy2(source,E/'pairs_300.json');shutil.copy2(cfg,E/'exact_protocol.json')
    state={'status':'RUNNING','started':time.time(),'pid':os.getpid()}
    try:
        runtime.run('construction','llmprint_construct_fingerprints.py',[
            '--source',O/'source','--model',runtime.BASE,'--pairs',E/'pairs_200.json',
            '--output-dir',E/'fingerprints','--max-pairs','200','--num-steps','500',
            '--experiment-label','7B_A2','--scientific-config-sha256',sha(cfg),'--dtype','float16'],additional=2*2**30)
        entries=[]
        import math
        for i in range(200):
            pair_id=f'llmprint-pair-{i:03d}';f=E/'fingerprints'/(pair_id+'.json');x=json.loads(f.read_text())
            assert x['pair_id']==pair_id and x['status']=='COMPLETED'
            assert x['gcg_iterations_completed']==x['gcg_iterations_requested']==500
            assert len(x['final_suffix_token_ids'])==20 and x['scientific_config_sha256']==sha(cfg)
            assert all(math.isfinite(x[k]) for k in ['best_loss','loss_first','loss_final_iteration','w_plus_probability','w_minus_probability'])
            entries.append({'pair_id':pair_id,'sha256':sha(f)})
        put(E/'fingerprint_manifest.json',dict(validated_record_count=200,integrity_status='PASS',artifacts=entries,config_sha256=sha(cfg)))
        state['status']='COMPLETED'
    except BaseException:state.update(status='FAILED',error=traceback.format_exc())
    finally:
        state['ended']=time.time();put(E/'construction_terminal.json',state)
        subprocess.run(['sync'])

if __name__=='__main__':main()
