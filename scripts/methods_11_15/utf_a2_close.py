"""Materialize UTF A2 scientific closure after separately verified archive."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import shutil

P=Path('/root/autodl-tmp/WMKD_Benchmark')
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):Path(p).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run-root',type=Path,required=True);a=ap.parse_args();r=a.run_root
    archive=read(r/'archive_stop_by_user_20260907.json');assert archive['status']=='STOPPED_BY_USER_NOT_PREFERRED'
    cfg=read(r/'training_config.json');train=read(r/'formal/result.json');probe=read(r/'preflight/result.json')
    teacher=read(r/'detector_teacher_attempt2/result.json');base_det=read(r/'detector_base/result.json')
    base_u=read(r/'utility_base/result.json');teacher_u=read(r/'utility_teacher/result.json')
    assert teacher['negative_successes']==500 and base_det['negative_successes']==0
    assert train['optimizer_steps']==960 and train['epoch']==30 and probe['trainable_parameters_changed']
    out=P/'results/methods_11_15/utf/experiment_a2';out.mkdir(exist_ok=True)
    copies={'training_result.json':r/'formal/result.json','training_metrics.jsonl':r/'formal/metrics.jsonl',
            'training_environment.json':r/'formal/environment.json','model_artifact_manifest.json':r/'model_artifact_manifest.json',
            'detector_teacher_results.json':r/'detector_teacher_attempt2/result.json','detector_base_results.json':r/'detector_base/result.json',
            'detector_path_repair.json':r/'detector_path_repair.json','utility_base_results.json':r/'utility_base/result.json',
            'utility_teacher_results.json':r/'utility_teacher/result.json','archive_status.json':r/'archive_stop_by_user_20260907.json'}
    for name,source in copies.items():shutil.copyfile(source,out/name)
    detector={'teacher':teacher,'base':base_det,'specificity_gate':'FAIL','preferred_teacher':False,
              'reason':'Teacher emits target for all 500 non-trigger guesses; official positive verdict alone is insufficient'}
    utility={'base':base_u['scores'],'teacher':teacher_u['scores'],'delta':teacher_u['delta'],
             'utility_status':'MATERIAL_DEGRADATION_ARC','interpretation':'ARC drops 7.08 percentage points; MC2 drops 0.15 points. No post-hoc numerical acceptance threshold is introduced.',
             'base_reference':'utility_base_results.json','base_evaluations_this_a2':1,'evaluation_date':base_u['evaluation_date'],
             'prompt_template_probe_sha256':base_u['prompt_template_probe_sha256'],'prompt_token_ids_sha256':base_u['prompt_token_ids_sha256'],
             'historical_reference_audit':base_u['historical_reference_audit'],'supplemental_native_utility':'NOT_RUN; primary utility complete and specificity gate already failed'}
    write(out/'detector_results.json',detector);write(out/'utility_results.json',utility)
    limitations=['Single canonical backbone, one fingerprint pair, one frozen primary configuration; no generalization to other UTF settings.',
                 'Paper 30 epochs and pinned runtime JSON 3 epochs discrepancy remains explicit; user selected paper protocol plus warmup coherence.',
                 'Single-GPU accumulation=1 is an explicitly approved update-budget adaptation, not original effective-batch equivalence.',
                 'BF16 compute uses GPU FP32 master parameters/Adam states; not a bitwise reproduction of native ZeRO3 offload numerics.',
                 'Pinned verifier default system template is retained even though official UTF training uses the empty-system template.',
                 'Teacher target emission is non-specific (500/500 non-trigger guesses); positive probe recovery is not valid ownership evidence by itself.',
                 'ARC material decline is descriptive; no new acceptance threshold or significance test is claimed.',
                 'Native SciQ/LAMBADA supplemental utility was not run; no retuning or second scientific configuration was attempted.']
    report=P/'docs/reproduction_reports/utf_a2_final_report_20260907.md'
    report.write_text(f'''# UTF A2 — 完成记录，非 Preferred Teacher

Run ID: `{r.name}`
PREFERRED_TEACHER = NO
FINAL_SCIENTIFIC_STATUS = COMPLETED_NOT_PREFERRED
ENGINEERING_STATUS = COMPLETE
DETECTOR_STATUS = NEGATIVE_CONTROL_FAILED
BENCHMARK_TEACHER_ELIGIBLE = NO
NEXT_ACTION = WAITING_FOR_USER_SCIENTIFIC_DECISION

采用 canonical meta-llama/Llama-3.2-3B-Instruct，revision 0cb88a4f764b7a12671c53f0838cd831a0843b95。旧 UTF 7B A 保留为 historical / superseded，eligible=NO，未改成 FAILED。

PAPER_EPOCHS=30；PINNED_RUNTIME_JSON_EPOCHS=3；WMKD_A2_SELECTED_EPOCHS=30；SELECTION_BASIS=PAPER_PROTOCOL_PLUS_WARMUP_COHERENCE。论文明确30 epochs，代码JSON实际3；3 epochs至多96次更新，不足以越过100-step warmup。用户明确选30 epochs；差异未隐藏。完整七点依据在 training_config.json 和 utf_a2_30epoch_protocol_20260907.md。

配置：32 records，1 unique fingerprint pair；micro=1，accumulation=1，effective batch=1；30 epochs，960 exposures，960 optimizer calls，958 nonzero-LR updates，warmup=100，post-warmup=860。首个非零LR更新为3，首个最大LR更新为101。Full FT，BF16计算，FP32 GPU master weights/Adam moments，无CPUAdam或offload。LR=2e-5，官方WarmupLR log后恒定；未切换为JSON中被覆盖的cosine。无tail accumulation。

可训练参数 {train['trainable_parameters']:,}。唯一preflight PASS，3次optimizer调用后验证参数确实改变；未复用preflight权重。训练最终loss={train['loss']}，训练循环耗时={train['elapsed_seconds']:.3f}s。显存allocated峰值={train['peak_vram_bytes']/2**30:.3f} GiB，reserved峰值={train['peak_vram_reserved_bytes']/2**30:.3f} GiB，主机RAM峰值={train['peak_host_ram_bytes']/2**30:.3f} GiB。最终BF16权重相对Base的数值变化另经CPU safetensors检查。最终模型已fresh-process加载。

| Detector | Fingerprint | Non-trigger target emission |
|---|---:|---:|
| Teacher | 1/1 | 500/500 |
| Base | 0/1 | 0/500 |

使用未修改的pinned fp_test函数，greedy max_new_tokens=100，目标字符串包含规则及500次官方随机负控。Teacher虽然通过官方positive布尔判定，但负控全部命中，区分性门槛失败；不能认定有效Preferred Teacher。无未解决的detector执行错误。

| Primary utility | Base | Teacher | Delta |
|---|---:|---:|---:|
| ARC-Challenge acc_norm | {base_u['scores']['arc_challenge_acc_norm']} | {teacher_u['scores']['arc_challenge_acc_norm']} | {teacher_u['delta']['arc_challenge_acc_norm']} |
| TruthfulQA MC2 acc | {base_u['scores']['truthfulqa_mc2_acc']} | {teacher_u['scores']['truthfulqa_mc2_acc']} | {teacher_u['delta']['truthfulqa_mc2_acc']} |

UTILITY_STATUS=MATERIAL_DEGRADATION_ARC：ARC下降约7.08个百分点，MC2下降约0.15个百分点。不事后创造宽松阈值。复用WMKD现有evaluator及其冻结依赖/数据版本。旧Base的动态Today Date无法与本次实际prompt确认一致，按用户授权仅补跑一次Base并冻结；Base/Teacher同日prompt和token IDs核对一致。未使用.408703或.4951作为基线。

工程修复：detector attempt1因cwd无法解析既有canonical alias，在任何probe前退出；GREEN修复为进入既有work目录，attempt2恢复。旧日志保留；无重训、无新科学配置。

PRIVATE archive: `{archive['repository']}`。在用户新规则生效前已提交94文件；恢复验证按用户要求停止，未验收为VERIFIED_ARCHIVED。远端PRIVATE独立仓库明确标为not preferred，保留待删除审批；本地模型6,434,691,656 bytes及恢复partial保留。禁止追加上传。本轮删除0。

Full log: results/methods_11_15/utf/experiment_a2/full_experiment_log.json。原始detector generations、训练日志、数据与完整环境证据在run目录及PRIVATE归档；Git仅保存轻量结果/manifest与代码。

限制：{' '.join(limitations)}

UTF A2已结束；任何下一科学配置须用户决定。未启动其他方法、orchestrator、guardian、watchdog、自动继续或自动关机。
''',encoding='utf-8')
    full={'schema_version':'wmkd.methods-11-15.full-log.v1','method':'UTF','experiment':'A2','run_id':r.name,
          'scientific_object_id':'utf:A2:'+r.name,'closed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'scientific_status':'COMPLETED_NOT_PREFERRED','final_scientific_status':'COMPLETED_NOT_PREFERRED','engineering_status':'COMPLETE','detector_status':'NEGATIVE_CONTROL_FAILED','utility_status':'MATERIAL_DEGRADATION_ARC','benchmark_teacher_eligible':False,'preferred_teacher':False,'canonical_backbone':True,
          'model':cfg['model'],'revision':cfg['revision'],'native_reference_backbone':'Official native Llama-family references; prior WMKD A used Llama-2-7b-chat-hf',
          'official_source':{'repo':'https://github.com/imjccai/fingerprint','commit':cfg['official_commit'],'paper':'https://aclanthology.org/2025.llmsec-1.1.pdf'},
          'adaptation_rationale':'User freezes Methods 11-15 comparison on canonical 3B; retain UTF construction/objective/verifier with documented architecture and GPU plumbing',
          'architecture_adaptations':read(r/'compatibility_patches.json'),'fingerprint_configuration':read(r/'preparation_state.json'),
          'training_configuration':cfg,'optimizer_update_budget':{k:cfg[k] for k in ['micro_batch','grad_accum','effective_batch','epochs','total_sample_exposures','expected_optimizer_steps','warmup_steps','post_warmup_steps','tail_accumulation_semantics']},
          'preflight':probe,'training':train,'environment':read(r/'formal/environment.json'),'hardware':{'gpu':'NVIDIA RTX PRO 6000 Blackwell Server Edition','vram_total_mib':97887},
          'detector':detector,'utility':utility,'fresh_reload':{'teacher':True,'base':True,'generation_success':True},
          'repairs':[read(r/'detector_path_repair.json')],'artifact_manifest':read(r/'model_artifact_manifest.json'),'archive':archive,
          'scientific_limitations':limitations,'formal_report':str(report.relative_to(P)),
          'old_utf_a':{'preserved':True,'canonical_benchmark_eligible':False,'classification':'historical / superseded protocol','not_marked_failed':True},
          'execution_boundaries':{'only_utf':True,'auto_next':False,'auto_shutdown':False,'next_action':'WAITING_FOR_USER_SCIENTIFIC_DECISION'}}
    full_path=out/'full_experiment_log.json';assert not full_path.exists();write(full_path,full)
    ip=P/'results/experiment_full_logs_index.json';index=read(ip)
    row={'method':'UTF','role':'non_preferred_reproduction','experiment':'A2','run_id':r.name,'full_log_path':str(full_path.relative_to(P)),
         'full_log_sha256':sha(full_path),'scientific_status':'COMPLETED_NOT_PREFERRED','preferred_teacher':False,'modelscope_repo':archive['repository'],
         'watermark_evaluation_available':True,'utility_available':True}
    assert not any(o['full_log_path']==row['full_log_path'] for o in index['objects']);index['objects'].append(row);index['object_count']=len(index['objects']);index['generated_at']=full['closed_at'];write(ip,index)
    keys=[tuple(o.get(k) for k in ['method','role','experiment','run_id']) for o in index['objects']];assert len(keys)==len(set(keys))
    for o in index['objects']:assert sha(P/o['full_log_path'])==o['full_log_sha256'],o['full_log_path']
    state_path=P/'results/methods_11_15_pipeline_state.json';state=read(state_path)
    state.update(status='WAITING_FOR_USER_SCIENTIFIC_DECISION',PIPELINE_STATUS='WAITING_FOR_USER_SCIENTIFIC_DECISION',stage='UTF_A2_CLOSED',resume_allowed=False,resume_requested=False,auto_advance=False,auto_shutdown=False,active_worker=None)
    state['current_experiment_state'].update(status='COMPLETED_NOT_PREFERRED',stage='CLOSED',training='TRAINING_COMPLETE',detector='NEGATIVE_CONTROL_FAILED',utility='MATERIAL_DEGRADATION_ARC',engineering_status='COMPLETE',benchmark_teacher_eligible=False,archive='STOPPED_BY_USER_NOT_PREFERRED',active_worker=None,preferred_teacher=False,base_arc=base_u['scores']['arc_challenge_acc_norm'],base_truthfulqa_mc2=base_u['scores']['truthfulqa_mc2_acc'],full_log=str(full_path.relative_to(P)),formal_report=str(report.relative_to(P)))
    state['methods']['utf'].update(state['current_experiment_state']);write(state_path,state)
    for name in ['AGENTS.md','docs/CURRENT_STATE.md','docs/EXPERIMENT_PROTOCOL.md','docs/METHODS_11_15_AUTOMATION.md','PROJECT_STATUS.md','TODO.md','README.md','DECISIONS.md','EXPERIMENT_LOG.md','CODEX_LOG.md']:
        p=P/name;lines=p.read_text().splitlines()
        for i,line in enumerate(lines):
            if line.startswith('当前 A2（2026-09-07 用户明确决策）'):
                lines[i]='当前 UTF A2 已完成科学与轻量证据闭环，模型归档按新规则停止且未验收：30 epochs / 960 updates，PREFERRED_TEACHER=NO；Teacher fingerprint 1/1、非触发负控500/500，Base 0/1、0/500；ARC delta=-0.0708191126，MC2 delta=-0.0014838436。状态 WAITING_FOR_USER_SCIENTIFIC_DECISION；下一科学配置须用户批准。30/3 paper/code discrepancy及选择依据保留。完整结果见 docs/reproduction_reports/utf_a2_final_report_20260907.md。'
                break
        p.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({'full_log':str(full_path),'report':str(report),'index_objects':len(keys),'unique':len(set(keys)),'sha_errors':0,'preferred_teacher':False}))

if __name__=='__main__':main()
