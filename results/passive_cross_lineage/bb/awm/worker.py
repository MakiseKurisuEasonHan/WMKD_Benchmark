import pathlib,sys,json,traceback,datetime,argparse
P=pathlib.Path('/root/autodl-tmp/WMKD_Benchmark'); O=P/'results/passive_cross_lineage/bb/awm'
sys.path.insert(0,str(P/'scripts'))
import passive5_ba_method_eval as e
try:
 e.student_label=lambda args:'Qwen/Qwen2.5-3B-Instruct'
 args=argparse.Namespace(project=P,output=O.parent,student=pathlib.Path('/root/autodl-tmp/WMKD_Benchmark_data/runs/passive_cross_lineage_bb/passive_cross_lineage_bb_20260908/training/final_model'),experiment='CROSS_LINEAGE_BB',run_id='passive_cross_lineage_bb_20260908',parent_run_id='8f4992eda43eea7c770690ddc0de8f732da246f5')
 e.awm(args)
 f=O/'detector_result.json'; r=json.loads(f.read_text()); r.update(role='bb',training_started=False,calibration_limitation='Qwen included in historical calibration panel; not held-out'); e.atomic_json(f,r)
 e.atomic_json(O/'exit_record.json',{'returncode':0,'ended_at':datetime.datetime.now(datetime.timezone.utc).isoformat()})
except BaseException:
 e.atomic_json(O/'exit_record.json',{'returncode':1,'error':traceback.format_exc()}); raise
