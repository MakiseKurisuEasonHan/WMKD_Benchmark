"""Timing-only instrumentation of unchanged canonical AWM; no Student training."""
import inspect,json,time,resource,sys,shutil,os,math
from pathlib import Path
import torch
import awm_protocol_cont1 as a
P=Path('/root/autodl-tmp/WMKD_Benchmark');D=Path(str(P)+'_data')
E=P/'results/awm/scale_7b_speed';E.mkdir(parents=True,exist_ok=True)
src=D/'sources/ownership/awm';sys.path.insert(0,str(src));import similarity_metrics as sm
BASE=D/'scale_7b/models/Llama-2-7b-chat-hf';NEG=D/'llmprint_7b/negative_models/slot-11'
start=time.time();timings={}
def sync():torch.cuda.synchronize()
def timed(name,func,*args):
    sync();t=time.perf_counter();v=func(*args);sync();timings[name]=time.perf_counter()-t;return v
# Add timing boundaries only, retaining the exact existing extraction statements.
source=inspect.getsource(a.extract)
source=source.replace(' m=AutoModelForCausalLM',' load_start=time.perf_counter()\n m=AutoModelForCausalLM')
source=source.replace(' for i,b in enumerate(m.model.layers):',' load_seconds=time.perf_counter()-load_start;wq_start=time.perf_counter()\n for i,b in enumerate(m.model.layers):')
source=source.replace(' emb=m.get_input_embeddings()', ' wq_seconds=time.perf_counter()-wq_start\n emb=m.get_input_embeddings()')
source=source.replace('"runtime_seconds":time.time()-t}', '"runtime_seconds":time.time()-t,"model_loading_seconds":load_seconds,"wq_wk_extraction_seconds":wq_seconds}')
exec(compile(source,'<timing-only canonical extract>','exec'),a.__dict__)
original_cka=sm.cka_from_features
cka_stats={'seconds':0.,'calls':0}
def measured_cka(*args,**kwargs):
    sync();t=time.perf_counter();v=original_cka(*args,**kwargs);sync()
    cka_stats['seconds']+=time.perf_counter()-t;cka_stats['calls']+=1
    return v
sm.cka_from_features=measured_cka
origdim=a.dim_lap;dim_times=[]
def dim(*args):
    sync();t=time.perf_counter();v=origdim(*args);sync();dim_times.append(time.perf_counter()-t);return v
a.dim_lap=dim
origpair=a.pair_scores;pair_seconds=[0.]
def pair(*args):
    sync();t=time.perf_counter();v=origpair(*args);sync();pair_seconds[0]+=time.perf_counter()-t;return v
a.pair_scores=pair
ref=timed('reference_extract',a.extract,BASE,'meta-llama/Llama-2-7b-chat-hf','f5db02db724555f92da89c216ac04704f23d4590')
a.atomic(E/'reference_extraction.json',a.strip(ref))
selfscore,selfdim,selflayer=timed('reference_self_detector',a.compare,ref,ref,E/'self_progress.json',sm)
selfdetail=dict(cka=dict(cka_stats),dimension_alignment_seconds=dim_times[-1],pair_processing_seconds=pair_seconds[0]-cka_stats['seconds'])
assert math.isfinite(selfscore) and abs(selfscore-1)<1e-5
cand=timed('negative_extract',a.extract,NEG,'Qwen/Qwen2.5-3B-Instruct','ba7dc0f38bdb4789f40899310796b84ac658fd40')
a.atomic(E/'negative_extraction.json',a.strip(cand))
cka_stats.update(seconds=0.,calls=0);pair_seconds[0]=0.
score,dm,lm=timed('negative_pair_detector',a.compare,ref,cand,E/'negative_progress.json',sm)
assert math.isfinite(score)
result=dict(status='COMPLETED_TIMING_ONLY',reference_model=str(BASE),negative_model=str(NEG),
    reference_self=selfscore,negative_score=score,threshold=None,calibration='NOT_RUN; frozen rule max of3 negatives requires fresh7B calibration',
    scientific_implementation='scripts/awm_protocol_cont1.py unchanged functions plus timing boundaries',
    source_commit=a.OFFICIAL,canonical_wrapper_sha256=a.sha(P/'scripts/awm_protocol_cont1.py'),
    official_metric_sha256=a.sha(src/'similarity_metrics.py'),full_layer_counts=[len(ref['q']),len(cand['q'])],
    timings=timings,reference_self_breakdown=selfdetail,negative_pair_breakdown=dict(cka=dict(cka_stats),
        dimension_alignment_seconds=dim_times[-1],wq_wk_alignment_processing_seconds=pair_seconds[0]-cka_stats['seconds'],
        layer_lap_and_orchestration_seconds=timings['negative_pair_detector']-dim_times[-1]-pair_seconds[0]),
    model_loading_seconds=ref['model_loading_seconds']+cand['model_loading_seconds'],
    wq_wk_extraction_seconds=ref['wq_wk_extraction_seconds']+cand['wq_wk_extraction_seconds'],
    total_wall_seconds=time.time()-start,peak_gpu_allocated_bytes=torch.cuda.max_memory_allocated(),
    peak_gpu_reserved_bytes=torch.cuda.max_memory_reserved(),peak_host_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
    dimension_alignment=dm,layer_alignment=lm,reference_self_layer_alignment=selflayer,
    new_models_downloaded=False,training_run=False,shutdown=False)
a.atomic(E/'timing_result.json',result)
print(json.dumps({k:v for k,v in result.items() if k not in ['dimension_alignment','layer_alignment','reference_self_layer_alignment']}),flush=True)
