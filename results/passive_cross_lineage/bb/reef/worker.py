import sys,json,pathlib,datetime,traceback,numpy as np
P=pathlib.Path('/root/autodl-tmp/WMKD_Benchmark'); D=pathlib.Path('/root/autodl-tmp/WMKD_Benchmark_data'); O=P/'results/passive_cross_lineage/bb/reef'
sys.path.insert(0,str(P/'scripts'))
import reef_protocol_compliance as r
try:
 probe=P/'results/ownership_protocols/reef_truthfulqa_200.json'
 assert r.sha(probe)=='8f63355817f726faea792edcc393ef9c6d32e07449bb66bbdefeb201e636599f'
 probes=json.loads(probe.read_text()); prompts=[x['text'] for x in probes['rows']]; assert len(prompts)==200
 ref=D/'artifacts/reef/experiment_a/protocol_compliance/reef_a_protocol_cont1_20260901_202500/reference_reload_a.npy'
 assert r.sha(ref)=='99ba4449d578a39a6709fc37e4e0ae709eb3b3f20d0e0a76633411e69705d525'
 arr,meta=r.extract(pathlib.Path('/root/autodl-tmp/WMKD_Benchmark_data/runs/passive_cross_lineage_bb/passive_cross_lineage_bb_20260908/training/final_model'),prompts,O/'representation.npy',35)
 score=r.cka(np.load(ref),arr); assert np.isfinite(score)
 r.atomic(O/'detector_result.json',{'method':'REEF','role':'bb','status':'COMPLETE','CKA':score,'threshold':0.4546738923165847,'detected':score>0.4546738923165847,'positive_rule':'strict greater than; tie negative','reference_layer':27,'reference_shape':[200,3072],'extraction':meta,'errors':[],'calibration_limitation':'Qwen included in historical calibration panel; not held-out','source_sha256':r.sha(P/'scripts/reef_protocol_compliance.py')})
 r.atomic(O/'exit_record.json',{'returncode':0,'ended_at':datetime.datetime.now(datetime.timezone.utc).isoformat()})
except BaseException:
 r.atomic(O/'exit_record.json',{'returncode':1,'error':traceback.format_exc()}); raise
