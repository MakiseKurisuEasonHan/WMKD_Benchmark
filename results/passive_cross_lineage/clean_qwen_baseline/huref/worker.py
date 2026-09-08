import sys,pathlib,json,datetime,traceback,numpy as np
P=pathlib.Path('/root/autodl-tmp/WMKD_Benchmark'); D=pathlib.Path('/root/autodl-tmp/WMKD_Benchmark_data'); O=P/'results/passive_cross_lineage/clean_qwen_baseline/huref'
import huref_frozen_inference as h
try:
 M=D/'models/paraphrasers/Qwen2.5-3B-Instruct'; corpus=json.loads((P/'results/huref/experiment_a2/protocol/corpus_manifest.json').read_text())
 assert h.sha(corpus['source'])==corpus['source_sha256']
 rows=h.iter_corpus(corpus['source'],10000); assert len(rows)==10000
 assert h.sha_bytes('\n'.join(x['text'] for x in rows).encode())==corpus['joined_text_sha256']
 tm=h.build_token_manifest('Qwen/Qwen2.5-3B-Instruct','8f4992eda43eea7c770690ddc0de8f732da246f5',M,rows,corpus['manifest_content_sha256']); h.atomic(O/'token_manifest.json',tm)
 ref=P/'results/huref/experiment_a2/protocol/reference_a--meta-llama--Llama-3.2-3B-Instruct.npy'
 assert h.sha(ref)=='ed43610236f89d8f0e367c8f9073b409327e7045d2184e12fdd509ddd2a9e04c'
 feature,meta=h.extract(M,[x['token_id'] for x in tm['rows']],O/'feature.npy','Qwen/Qwen2.5-3B-Instruct',tm['manifest_content_sha256'])
 score=h.ics(np.load(ref),feature); assert np.isfinite(score)
 h.atomic(O/'detector_result.json',{'method':'HuRef','role':'clean_qwen_baseline','status':'COMPLETE','ICS':score,'threshold':4.119894027709961,'detected':score>4.119894027709961,'positive_rule':'strict greater than','extraction':meta,'errors':[],'calibration_limitation':'Qwen included in historical calibration panel; not held-out'})
 h.atomic(O/'exit_record.json',{'returncode':0,'ended_at':datetime.datetime.now(datetime.timezone.utc).isoformat()})
except BaseException:
 h.atomic(O/'exit_record.json',{'returncode':1,'error':traceback.format_exc()}); raise
