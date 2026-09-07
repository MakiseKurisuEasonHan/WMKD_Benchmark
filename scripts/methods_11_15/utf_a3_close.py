"""UTF A3 lightweight closure only; no training, upload or continuation."""
from pathlib import Path, PurePosixPath
import json,hashlib,datetime,shutil,subprocess,os
P=Path(__file__).resolve().parents[2];D=PurePosixPath('/root/autodl-tmp/WMKD_Benchmark_data');REMOTE_R=D/'runs/methods_11_15/utf_a3_20260907_accum16';R=Path(os.environ['WMKD_A3_EVIDENCE_DIR'])
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_bytes((json.dumps(v,indent=2,ensure_ascii=False)+'\n').encode('utf-8'))
def main():
 out=P/'results/methods_11_15/utf/experiment_a3';cfg=read(R/'training_config.json');tr=read(R/'formal/result.json');td=read(R/'detector_teacher/result.json');bd=read(R/'detector_base/result.json');u=read(R/'utility_teacher/result.json');bu=read(R/'utility_base/result.json');cmp=read(R/'a2_a3_detector_comparison.json')
 assert tr['optimizer_steps']==60 and tr['sample_exposures']==960 and tr['nonzero_lr_updates']==58
 assert td['status']==bd['status']==u['status']=='COMPLETE';assert td['negative_successes']==500 and td['positive_successes']==1
 assert cmp['input_output_records_identical_to_a2'] and cmp['unique_negative_outputs']==1
 assert u['prompt_template_probe_sha256']==bu['prompt_template_probe_sha256'] and u['prompt_token_ids_sha256']==bu['prompt_token_ids_sha256']
 assert not (out/'full_experiment_log.json').exists()
 for dest,src in {'base_detector_results.json':R/'detector_base/result.json','utility_results.json':R/'utility_teacher/result.json','preflight_environment.json':R/'preflight/environment.json','preflight_scheduler_parity.json':R/'preflight/scheduler_parity.json'}.items():shutil.copyfile(src,out/dest)
 det={'teacher':td,'base':bd,'specificity':'NEGATIVE_CONTROL_FAILED','preferred_teacher':False,'comparison':cmp};write(out/'detector_results.json',det)
 provenance={'source_git_commit':subprocess.check_output(['git','-C',str(P),'rev-parse','HEAD'],text=True).strip(),'files':{str(REMOTE_R/f.relative_to(R).as_posix()) if f.is_relative_to(R) else str(f):{'size':f.stat().st_size,'sha256':sha(f)} for f in [R/'formal.log',R/'preflight.log',R/'detector_teacher/raw_generations.jsonl',R/'detector_base/raw_generations.jsonl',R/'utility_teacher/full_lm_eval_output.json',R/'fingerprint_data/data.jsonl',P/'scripts/methods_11_15/utf_a3_train.py',P/'scripts/methods_11_15/utf_a3_utility.py',P/'scripts/methods_11_15/utf_a2_detector.py']},'a2_base_reused':True,'base_source':str(D/'runs/methods_11_15/utf_a2_20260907_30ep/utility_base/result.json'),'base_source_sha256':sha(R/'utility_base/result.json'),'no_model_upload':True};write(out/'provenance.json',provenance)
 report=P/'docs/reproduction_reports/utf_a3_final_report_20260907.md'
 arc=u['scores']['arc_challenge_acc_norm'];mc=u['scores']['truthfulqa_mc2_acc'];da=u['delta']['arc_challenge_acc_norm'];dm=u['delta']['truthfulqa_mc2_acc']
 text=f'''# UTF A3 — official accumulation 对照结果

Run ID: {R.name}
ENGINEERING_STATUS = COMPLETE
DETECTOR_STATUS = NEGATIVE_CONTROL_FAILED
UTILITY_STATUS = COMPLETE (raw scores below; no post-hoc threshold)
FINAL_SCIENTIFIC_STATUS = COMPLETED_NOT_PREFERRED
PREFERRED_TEACHER = NO
BENCHMARK_TEACHER_ELIGIBLE = NO
MODELSCOPE_UPLOAD = NOT_STARTED

唯一科学变化是accumulation1→16。canonical Base meta-llama/Llama-3.2-3B-Instruct@0cb88a4f764b7a12671c53f0838cd831a0843b95，fresh full FT，无A2或preflight权重复用。pair/data SHA、epochs30、960 exposures、micro1、LR/optimizer/WarmupLR100、seed42、BF16/FP32 master、clip、模板及BOS行为均冻结。单次preflight：48 exposures、3 calls、1非零LR调用，finite loss/grad，参数改变，PASS。

实际formal：{tr['optimizer_steps']} optimizer calls，{tr['nonzero_lr_updates']}非零LR更新，{tr['sample_exposures']} exposures，epoch30；最后/最高实际LR={tr['learning_rate']}，无tail。最后loss={tr['loss']}，训练循环耗时{tr['elapsed_seconds']}秒。allocated VRAM peak={tr['peak_vram_bytes']/2**30:.3f}GiB，reserved={tr['peak_vram_reserved_bytes']/2**30:.3f}GiB。每条实际LR与pinned语义一致。训练没有达到warmup最大LR，这是允许的。

| Detector | A2 Teacher | A3 Teacher | A3 fresh Base |
|---|---:|---:|---:|
| Positive | 1/1 | 1/1 | {bd['positive_successes']}/1 |
| Random negative target emission | 500/500 | 500/500 | {bd['negative_successes']}/500 |
| Teacher target at beginning | 500/500 | 500/500 | 不适用 |
| Teacher unique negative outputs | 1 | 1 | 不适用 |

A3 Teacher全部生成文件SHA={cmp['raw_sha256']}，与A2完全一致（包含输入、输出文本及token IDs）。均为5个target token+EOT，位置char/token=0。fresh-process reload成功，未解决detector error=0。官方attention-mask/pad提示原样保留，未为追求结果改变verifier。

| Utility | Frozen Base | A2 Teacher | A3 Teacher | A3−Base |
|---|---:|---:|---:|---:|
| ARC-Challenge acc_norm | {bu['scores']['arc_challenge_acc_norm']} | 0.3796928327645051 | {arc} | {da} |
| TruthfulQA MC2 acc | {bu['scores']['truthfulqa_mc2_acc']} | 0.5039777188370608 | {mc} | {dm} |

复用用户冻结的A2 Base一次既有evaluation；未补跑Base utility。实际同日模板prompt/token IDs、evaluator/config、版本与数据provenance核对一致。Utility是否改善不能覆盖negative-control specificity失败；不创造新数值阈值，不自动preferred。

GLOBAL_TARGET_COLLAPSE = YES（限本次500随机负例分布）。将更新数从960降至60没有改变已观察到的collapse；数据不支持“960更新是collapse发生的必要条件”或“恢复official16足以修复”。不能因此证明优化预算完全无关：60步仍可能超出此pair/backbone条件下的稳定区间，也没有中间checkpoint/多seed对照。它只表明在冻结的其余条件下，60与960两端均发生相同collapse。仍可能有单pair学习动力学、模板/BOS与3B迁移的交互；本轮不继续测试或提出新配置。

A2历史完整保留；A3非preferred模型仅本地保留，禁止上传、无删除。所有正式证据见results/methods_11_15/utf/experiment_a3/full_experiment_log.json；完整raw/log在run目录，SHA在provenance.json。A3闭环后STOP，不执行Ba/Bb、Double-I、其他方法、自动继续或关机。
'''
 report.write_text(text,encoding='utf-8')
 full={'schema_version':'wmkd.methods-11-15.full-log.v1','method':'UTF','experiment':'A3','run_id':R.name,'scientific_object_id':'utf:A3:'+R.name,'closed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'engineering_status':'COMPLETE','scientific_status':'COMPLETED_NOT_PREFERRED','preferred_teacher':False,'benchmark_teacher_eligible':False,'detector_status':'NEGATIVE_CONTROL_FAILED','utility_status':'COMPLETE','model':cfg['model'],'revision':cfg['revision'],'training_configuration':cfg,'preflight':read(R/'preflight/result.json'),'training':tr,'environment':read(R/'formal/environment.json'),'detector':det,'utility':u,'base_utility':bu,'protocol_comparison':read(R/'protocol_comparison.json'),'provenance':provenance,'artifact_manifest':read(R/'model_artifact_manifest.json'),'archive':{'status':'NOT_STARTED','reason':'NON_PREFERRED_MODEL_UPLOAD_FORBIDDEN','local_model_retained':True},'repairs':[],'formal_report':report.relative_to(P).as_posix(),'root_cause_interpretation':'Restoring accumulation16 did not remove collapse; 960 updates not necessary for this observed failure; does not rule out overoptimization at60 or interactions.','execution_boundaries':{'auto_next':False,'auto_shutdown':False,'next_action':'STOP_WAIT_USER'}}
 fp=out/'full_experiment_log.json';write(fp,full)
 ip=P/'results/experiment_full_logs_index.json';idx=read(ip);assert not any(o['full_log_path']==fp.relative_to(P).as_posix() for o in idx['objects']);idx['objects'].append({'method':'UTF','experiment':'A3','role':'non_preferred_reproduction','run_id':R.name,'full_log_path':fp.relative_to(P).as_posix(),'full_log_sha256':sha(fp),'scientific_status':'COMPLETED_NOT_PREFERRED','preferred_teacher':False,'watermark_evaluation_available':True,'utility_available':True,'modelscope_repo':None});idx.update(object_count=len(idx['objects']),generated_at=full['closed_at']);write(ip,idx)
 for o in idx['objects']:assert sha(P/o['full_log_path'])==o['full_log_sha256']
 state=read(R/'pipeline_state.json');state.update(status='WAITING_FOR_USER_SCIENTIFIC_DECISION',PIPELINE_STATUS='WAITING_FOR_USER_SCIENTIFIC_DECISION',stage='A3_CLOSED',active_worker=None,auto_advance=False,auto_shutdown=False,resume_allowed=False)
 state['current_experiment_state'].update(status='COMPLETED_NOT_PREFERRED',stage='CLOSED',training='TRAINING_COMPLETE',detector='NEGATIVE_CONTROL_FAILED',utility='COMPLETE',archive='NOT_STARTED',preferred_teacher=False,benchmark_teacher_eligible=False,active_worker=None,full_log=fp.relative_to(P).as_posix());state['methods']['utf']=dict(state['current_experiment_state']);write(P/'results/methods_11_15_pipeline_state.json',state)
 print(json.dumps({'status':'COMPLETED_NOT_PREFERRED','report':str(report),'index_objects':len(idx['objects']),'utility':u['scores'],'delta':u['delta']}))
if __name__=='__main__':main()