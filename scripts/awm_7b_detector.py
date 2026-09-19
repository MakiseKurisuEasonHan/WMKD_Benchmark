"""Formal 7B AWM: unchanged canonical extraction/LAP/UCKA and frozen threshold."""
import argparse,json,math,time,resource,subprocess,sys,types
from pathlib import Path
import torch
import awm_protocol_cont1 as a
P=Path('/root/autodl-tmp/WMKD_Benchmark');D=Path(str(P)+'_data');E=P/'results/awm/scale_7b'
BASE=D/'scale_7b/models/Llama-2-7b-chat-hf';REV='f5db02db724555f92da89c216ac04704f23d4590'
SRC=D/'sources/ownership/awm'
# Historical Phi3 config advertises local remote-code files not carried by the
# verified weight snapshot. This detector never performs model forward: use the
# installed native Phi3 loader to expose exactly the same SHA-verified tensors.
# Existing canonical extract still asserts the config-derived fused Q|K|V shape.
for _name in ['AutoConfig','AutoModelForCausalLM','AutoTokenizer']:
    _original=getattr(a,_name)
    def _loader(path,*args,_cls=_original,**kwargs):
        if Path(path).name=='slot-08':kwargs['trust_remote_code']=False
        return _cls.from_pretrained(path,*args,**kwargs)
    setattr(a,_name,types.SimpleNamespace(from_pretrained=_loader))

def load(p):return json.loads(Path(p).read_text())
def verify(root,rows):
    for x in rows:
        path=root/x.get('path',x.get('Path'));size=x.get('bytes',x.get('Size'));digest=x.get('sha256',x.get('Sha256'))
        assert path.is_file() and path.stat().st_size==size and a.sha(path)==digest,'Model identity failure: '+str(path)
def main():
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['calibrate','detect']);p.add_argument('--model');p.add_argument('--stage');args=p.parse_args()
    E.mkdir(parents=True,exist_ok=True);start=time.time()
    assert subprocess.check_output(['git','-C',str(SRC),'rev-parse','HEAD'],text=True).strip()==a.OFFICIAL
    sys.path.insert(0,str(SRC));import similarity_metrics as sm
    manifest=load(E/'canonical_model_source_manifest.json');assert manifest['canonical_revision']==REV
    verify(BASE,manifest['files'])
    provenance=dict(reference_model='meta-llama/Llama-2-7b-chat-hf',reference_revision=REV,
        source_commit=a.OFFICIAL,wrapper_sha256=a.sha(P/'scripts/awm_protocol_cont1.py'),
        official_metric_sha256=a.sha(SRC/'similarity_metrics.py'),protocol_sha256=a.sha(P/'results/ownership_protocols/awm_formal_protocol.json'))
    ref=a.extract(BASE,provenance['reference_model'],REV)
    if args.mode=='calibrate':
        assert not (E/'calibration_freeze.json').exists(),'Calibration is immutable'
        selfscore,dm,lm=a.compare(ref,ref,E/'reference_self_progress.json',sm)
        reload=a.extract(BASE,provenance['reference_model'],REV)
        reloadscore,rd,rl=a.compare(ref,reload,E/'reference_reload_progress.json',sm)
        assert abs(selfscore-1)<1e-7 and abs(reloadscore-selfscore)<1e-7
        a.atomic(E/'reference_representation.json',a.strip(ref));del reload;a.release()
        canonical=load(P/'results/ownership_protocols/shared_negative_panel_3.json')
        negatives=[]
        for item,slot in zip(canonical['models'],[5,11,8]):
            receipt=load(E/f'negative_{slot:02d}_acquisition.json')
            assert item['model_id']==receipt['model'] and receipt['all_files_sha_verified']
            path=Path(receipt['local_path']);verify(path,receipt['files'])
            existing=E/f'negative_{slot:02d}_detector.json'
            if existing.exists():
                row=load(existing);assert row['model']==item['model_id'] and row['revision']==receipt['revision'] and math.isfinite(row['score'])
                negatives.append(row);continue
            cand=a.extract(path,receipt['model'],receipt['revision'])
            score,cd,cl=a.compare(ref,cand,E/f'negative_{slot:02d}_progress.json',sm)
            assert math.isfinite(score)
            row=dict(model=item['model_id'],revision=receipt['revision'],score=score,
                loader_compatibility='native installed Phi3 loader; identical verified QKV tensors, no forward' if slot==8 else 'historical canonical loader',
                canonical_original_revision=item['modelscope_weight_revision'],provenance='same-identity existing canonical transport repair; no model replacement',
                representation=a.strip(cand),dimension_alignment=cd,layer_alignment=cl)
            negatives.append(row);a.atomic(E/f'negative_{slot:02d}_detector.json',row);del cand;a.release()
        assert len(negatives)==3
        tau=max(x['score'] for x in negatives);assert math.isfinite(tau) and selfscore>tau
        result=dict(status='COMPLETED',provenance=provenance,reference_self=selfscore,reference_reload=reloadscore,
            negatives=[{k:x[k] for k in ['model','revision','score']} for x in negatives],threshold=tau,
            threshold_rule='max of three frozen canonical negatives',positive_rule='score > threshold; tie negative',
            reference_positive=selfscore>tau,reference_self_alignment=dict(dimension=dm,layer=lm),
            reference_reload_alignment=dict(dimension=rd,layer=rl),runtime_seconds=time.time()-start,
            peak_vram_bytes=torch.cuda.max_memory_allocated(),peak_host_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024)
        a.atomic(E/'calibration.json',result)
        a.atomic(E/'calibration_freeze.json',dict(timestamp=time.time(),calibration_sha256=a.sha(E/'calibration.json'),
            provenance=provenance,students_started=False,threshold=tau,negative_count=3))
        a.atomic(E/'reference_detector.json',dict(score=selfscore,threshold=tau,detected=True,score_reference_ratio=1.,fresh_reload_score=reloadscore))
    else:
        freeze=load(E/'calibration_freeze.json');assert a.sha(E/'calibration.json')==freeze['calibration_sha256']
        assert freeze['provenance']==provenance,'Frozen detector/source identity changed'
        assert args.stage in ['direct','paraphrase','logit']
        manifest=load(D/'awm_7b'/args.stage/'final_manifest.json');verify(Path(args.model),manifest['files'])
        cand=a.extract(Path(args.model),'awm_7b_'+args.stage,'trained_from_'+REV)
        score,dm,lm=a.compare(ref,cand,E/(args.stage+'_detector_progress.json'),sm);assert math.isfinite(score)
        result=dict(score=score,threshold=freeze['threshold'],detected=score>freeze['threshold'],
            score_reference_ratio=score/load(E/'calibration.json')['reference_self'],fresh_reload=True,
            calibration_sha256=freeze['calibration_sha256'],provenance=provenance,
            representation=a.strip(cand),dimension_alignment=dm,layer_alignment=lm,
            runtime_seconds=time.time()-start,peak_vram_bytes=torch.cuda.max_memory_allocated(),
            peak_host_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024)
        a.atomic(E/(args.stage+'_detector.json'),result)
    print(json.dumps({k:result[k] for k in result if k in ['score','threshold','detected','reference_self','reference_reload','negatives','runtime_seconds']}),flush=True)
if __name__=='__main__':main()
