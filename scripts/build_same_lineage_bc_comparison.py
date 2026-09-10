"""Build endpoint comparisons from immutable recorded evidence, without evaluation."""
import csv
import hashlib
import json
from pathlib import Path

P = Path(__file__).resolve().parents[1]
E = P / 'results/logit_distillation/same_lineage_bc'
O = E / 'comparison'
O.mkdir(exist_ok=True)
def read(p): return json.loads(p.read_text())
def provenance(p): return {'path': str(p.relative_to(P)), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}

rows = []
fields = {'evertracer': 'member_oriented_auc', 'ctcc': 'trigger_activations',
          'iseal': 'registered_success', 'scw': 'p_value'}
names = {'pnfp': 'PN-FP', 'evertracer': 'EverTracer', 'ctcc': 'CTCC', 'iseal': 'iSeal', 'scw': 'SCW'}
for m in names:
    p = E / m / 'full_experiment_log.json'; f = read(p); c = f['protocol']; d = f['detector']
    refs = c.get('native_detector_spec', {}).get('historical_reference_only', {})
    src = [provenance(p)]
    if m == 'pnfp':
        bc, ba, teacher, base, historical = d['detected'], 99, 956, 1, 98
        bbpath = P / 'results/pnfp/experiment_bb/full_experiment_log.json'
        bb = read(bbpath)['detector']['result']['detected']
        metric, rule = 'detected/1024', 'frozen 1024-key exact detector; no invented model-level cutoff'
        decision = '110/1024; partial acquisition, no significance claim'
        limitation = 'Reconstructed-parent Ba=99; original historical Ba=98 is not the primary comparator. Bb is historical context only.'
        src.append({'path': 'results/pnfp/experiment_ba_trajectory_followup/trajectory.json', 'role': 'approved reconstructed-parent comparator'})
    else:
        ba_path = P / 'results' / m / 'experiment_ba_trajectory_followup/final_fresh_reload/detector_comparison_payload.json'
        ba_metrics = read(ba_path)['native_metrics']; bc = d['native_metrics'][fields[m]]; ba = ba_metrics[fields[m]]
        src.append(provenance(ba_path))
        attack = 'bb2' if m == 'ctcc' else 'bb'
        bbpath = P / 'results' / m / ('experiment_' + attack) / 'full_experiment_log.json'; bbd = read(bbpath)['detector']
        if m == 'evertracer':
            teacher, base, historical = [refs[x]['member_oriented_auc'] for x in ('teacher', 'base', 'student')]
            bb = bbd['metrics']['member_oriented_auc']; metric = 'member-oriented AUC'
            rule = 'member direction; TPR at FPR<=0.05'; decision = 'AUC=0.59; TPR=0.16; FPR=0.05'
        elif m == 'ctcc':
            teacher, base, historical, bb = 95, 0, 0, bbd['result']['trigger']['activations']
            metric = 'trigger activations/95'; rule = 'generated_answer.strip()==IAMALIVE; WMKD operational detector'
            decision = '0/95 triggers; 0/205 negatives'
        elif m == 'iseal':
            teacher, base, historical = [refs['registered_200'][x]['success'] for x in ('teacher', 'base', 'student')]
            bb = sum(x['teacher_positive'] for x in bbd['result']['registered']['rows'])
            metric = 'registered success/200'; rule = 'sentence BLEU>=50'; decision = '0/200 registered; 0/100 heldout'
        else:
            teacher, base, historical = [refs[x]['p_value'] for x in ('teacher', 'base', 'student')]
            bb = bbd['result']['primary']['p_value']; metric = 'p-value'; rule = 'p<0.001; lower is stronger'
            decision = 'NOT_DETECTED'
        limitation = 'Ba is the fresh-reload trajectory endpoint; historical Ba is separately retained. Single-seed endpoint comparison; no causal or significance claim.'
        if m == 'scw': limitation += ' Uses reconstructed parent, not an exact replay of missing historical data.'
    src.append(provenance(bbpath))
    rows.append(dict(method=names[m],type='active',metric=metric,teacher=teacher,clean_llama=base,
                     ba=ba,historical_ba=historical,bb=bb,bc=bc,bc_minus_ba=bc-ba,
                     detector_rule=rule,decision=decision,arc=f['utility']['arc_challenge_acc_norm'],
                     mc2=f['utility']['truthfulqa_mc2_acc'],dataset_identity=c['dataset_identity'],
                     dataset_sha256=c['dataset_sha256'],run_id=c['run_id'],final_status=f.get('final_scientific_status',f.get('status')),
                     strict_comparability='Same-lineage frozen detector; primary Ba comparator named in protocol. Bb is not a KD-only controlled comparison.',
                     bounded_interpretation=limitation,evidence=src))

p = E / 'passive_shared/full_experiment_log.json'; f = read(p)
ba_path = P / 'results/passive5_shared_ba/detector_summary.json'; bb_path = P / 'results/passive5_shared_bb3/detector_summary.json'
bas = {x['method']: x for x in read(ba_path)['methods']}; bbs = {x['method']: x for x in read(bb_path)['methods']}
for key, label in [('llmprint','LLMPrint'),('reef','REEF'),('huref','HuRef'),('awm','AWM'),('zeroprint','ZeroPrint')]:
    d=f['detector']['native_results'][key]; bc=d['score']['rescaled'] if key=='zeroprint' else d['score']; a=bas[label]
    rows.append(dict(method=label,type='passive',metric=a['native_metric'],teacher=a['reference_score'],
                     clean_llama=a['reference_score'],ba=a['student_score'],historical_ba=a['student_score'],
                     bb=bbs[label]['score'],bc=bc,bc_minus_ba=bc-a['student_score'],detector_rule=a['positive_rule']+'; threshold='+str(d['threshold']),
                     decision='THRESHOLD_CROSSED' if d['positive'] else 'NOT_DETECTED',
                     arc=f['utility']['arc_challenge_acc_norm'],mc2=f['utility']['truthfulqa_mc2_acc'],
                     dataset_identity=f['protocol']['dataset_identity'],dataset_sha256=f['protocol']['dataset_sha256'],
                     run_id=f['run_id'],final_status=f.get('final_scientific_status'),
                     strict_comparability='Frozen same-lineage detector; Ba direct data comparator, Bb3 paraphrased contextual comparison.',
                     bounded_interpretation='One shared Bc Student. Teacher is clean canonical reference; high similarity is not independent proof of watermark acquisition or unique ownership.',
                     evidence=[provenance(p),provenance(ba_path),provenance(bb_path)]))

archives = {m: read(E/m/'modelscope_archive.json') for m in ['pnfp','evertracer','ctcc','iseal','scw','passive_shared']}
assert all(x['status'] == 'COMPLETE' and x['visibility'] == 'PRIVATE' for x in archives.values())
(O/'same_lineage_bc_master.json').write_text(json.dumps({'rows':rows,'scientific_runs':6,'watermark_methods':10,'archive_closure':'6/6_PRIVATE_VERIFIED','archives':archives},indent=2)+'\n')
with (O/'same_lineage_bc_master.csv').open('w',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=[k for k in rows[0] if k!='evidence']);writer.writeheader()
    writer.writerows({k:v for k,v in x.items() if k!='evidence'} for x in rows)
text='# Same-Lineage Bc：六个训练 run、十种检测方法\n\n下表为已测 endpoint；不同方法的 raw score 不作横向大小比较。Ba 列对主动方法采用当前 protocol 对应的 trajectory endpoint；历史 Ba 单列于 JSON/CSV。\n\n|方法|Teacher/reference|Clean Llama|Ba|Bb/Bb2/Bb3|Bc|Bc−Ba|ARC|MC2|\n|---|---:|---:|---:|---:|---:|---:|---:|---:|\n'
for x in rows:text+='|'+ '|'.join(str(x[k]) for k in ['method','teacher','clean_llama','ba','bb','bc','bc_minus_ba','arc','mc2'])+'|\n'
text+='''
## 有边界的解释

- PN-FP 为110/1024，较同 reconstructed-parent Ba的99/1024增加11个（约1.07个百分点）；不能仅据单次运行称为显著提升。历史98/1024不是本次主对照。
- EverTracer AUC从对应Ba trajectory的0.5016升至0.59，仍远低于Teacher的1.0。没有跨seed置信区间，不能断言稳定提高成员分离。
- CTCC没有获得IAMALIVE触发行为；iSeal仍为0/200 registered success。iSeal Bc mean BLEU=2.543812，略低于Ba trajectory的2.589418。
- SCW Bc p=0.881924，相对同重建parent Ba的0.895175略低，但两者均未检出。不能把这种差值当作水印已传递。
- Passive Bc五项均过冻结阈值；LLMPrint、REEF、ZeroPrint比Ba更接近reference，HuRef和AWM略低于Ba。不是五项统一改善。
- Passive Teacher就是canonical reference。共享骨干参数保持和检测定义都可能影响高分，不能将其直接解释为独立、唯一的ownership证据。
- 目前不支持“soft logits对所有方法统一更强”。主动方法未出现普遍强信号；被动方法呈现高相似度但提升幅度和方向不同。
- 六项utility原始值列于表中。未在本报告核验统一clean-Base utility来源，因此不报告推测的Base delta或显著性。
- 本轮没有Bc trajectory；不能从终点推断遗忘过程、峰值或更新阶段的因果机制。
- 单seed、有限probe与历史/重建数据限制保留。更强因果与统计结论需要另行批准的重复或消融实验，本轮不自动开展。

逐项证据路径与SHA见同目录master JSON。归档和Git最终状态以各run收据及campaign closure为准。
'''
(P/'docs/reproduction_reports/same_lineage_bc_master_report.md').write_text(text,encoding='utf8')
print('MASTER_ROWS',len(rows))
