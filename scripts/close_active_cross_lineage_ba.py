"""CPU-only deterministic final closure from existing scientific evidence.

No model imports, inference, training, deletion or network operations.
Run from repository root after synchronizing the immutable raw evidence package.
"""
import csv
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone

P = Path(__file__).resolve().parents[1]
E = P / 'results/active_cross_lineage_ba'
METHODS = ['pnfp', 'evertracer', 'ctcc', 'iseal', 'scw']
NOW = datetime.now(timezone.utc).isoformat()
REPORT = 'docs/reproduction_reports/active_cross_lineage_ba_final_20260909.md'


def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def save(p, d):
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    Path(p).write_text(json.dumps(d, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def ref(p):
    p = Path(p)
    return {'path': p.relative_to(P).as_posix(), 'sha256': sha(p), 'bytes': p.stat().st_size}


def historical(m):
    p = P / f'results/{m}/ba_student/full_experiment_log.json'
    d = read(p)
    s = next(iter(d['source_snapshots'].values()))
    if m == 'pnfp':
        v = d['watermark_evaluation']['method_specific_recorded_evidence'][0]['value']
        vals = [v[k]['detected'] / v[k]['total'] for k in ['a2_teacher', 'canonical_base', 'ba_student']]
    elif m == 'ctcc':
        v = s['metrics']; vals = [v[k][0] / v[k][1] for k in ['teacher_trigger', 'base_trigger', 'student_trigger']]
    elif m == 'evertracer':
        vals = [s['verification'][k]['member_oriented_auc'] for k in ['teacher', 'base', 'student']]
    elif m == 'iseal':
        vals = [s['registered_200'][k]['success'] / 200 for k in ['teacher', 'base', 'student']]
    else:
        vals = [s['detector'][k]['primary']['p_value'] for k in ['teacher', 'base', 'student']]
    return vals, ref(p)


def main():
    basepath = P / 'results/passive_cross_lineage/clean_qwen_baseline/utility/raw_evaluator_output.json'
    base = read(basepath)
    assert sha(basepath) == '9182a4eeeec5ac4b706c1d0a4f6f80a936a8e4c877589f038d68776f68523bb3'
    ba = base['results']['arc_challenge']['acc_norm,none']
    bm = base['results']['truthfulqa_mc2']['acc,none']
    raw_checks, rows, retention = {}, [], []
    weights = {}
    explanations = {
        'pnfp': '同一冻结文本签名规则下比 clean Qwen 多41/1024，支持部分获取；重建parent不是历史Ba exact replay，不证明完整转移或因果机制。',
        'evertracer': '仅探索性跨tokenizer诊断接近随机分离；不能据此判断原冻结水印的转移、存活或失败。',
        'ctcc': '冻结操作规则下95个trigger与205个negative均零激活；终点未观察到IAMALIVE获取。',
        'iseal': '3072维Llama注册embedding与2048维Qwen接口不兼容；N/A是适用性结论，不是转移失败。',
        'scw': '1000条冻结查询p高于alpha，终点未检出；p值不是水印强度的线性量，重建parent限制历史比较。',
    }
    for m in METHODS:
        q = E/m
        full = read(q/'full_experiment_log.json')
        train = read(q/'training_summary.json')
        prov = read(q/'model_provenance.json')
        data = read(q/'qwen_dataset_preflight.json')
        utility = read(q/'utility_results.json')
        rawpath = q/'utility/raw_evaluator_output.json'
        raw = read(rawpath)
        assert train['steps'] == 7500 and prov['status'] == 'FRESH_RELOAD_VERIFIED'
        assert prov['base_revision'] == '8f4992eda43eea7c770690ddc0de8f732da246f5'
        assert data['records'] == 20000 and data['actual_sha256'] == data['expected_sha256']
        counts = {k: len(raw['samples'][k]) for k in ['arc_challenge', 'truthfulqa_mc2']}
        assert counts == {'arc_challenge': 1172, 'truthfulqa_mc2': 817}
        assert sha(rawpath) == utility['raw_sha256']
        arc = raw['results']['arc_challenge']['acc_norm,none']
        mc2 = raw['results']['truthfulqa_mc2']['acc,none']
        assert arc == utility['arc_challenge_acc_norm'] and mc2 == utility['truthfulqa_mc2_acc']
        detector = read(q/'detector_results.json')
        hist, href = historical(m)
        level = 2 if m == 'evertracer' else 3 if m == 'iseal' else 1
        cq = xba = delta = 'N/A'
        canonical = detector
        exploratory = 'NOT_APPLICABLE'
        if m == 'pnfp':
            cq = detector['clean_qwen_detected']/detector['total']; xba = detector['detection_rate']
            delta = xba-cq
            rule = detector['rule']; decisions = ['43/1024 matches; no invented aggregate threshold', '84/1024 matches; no invented aggregate threshold']
            assert sum(1 for _ in (q/'final_detector/raw.jsonl').open(encoding='utf-8')) == 1024
            assert sha(q/'final_detector/raw.jsonl') == detector['raw_sha256']
        elif m == 'ctcc':
            cb = read(q/'clean_qwen_detector.json')['summary']
            cq = cb['categories']['trigger']['activation_rate']; xba = detector['categories']['trigger']['activation_rate']; delta = xba-cq
            rule = detector['detector']; decisions = ['0/95 trigger; 0/205 negatives', '0/95 trigger; 0/205 negatives']
            assert len(read(q/'final_detector.json')['raw_generations']) == 300
            assert sha(q/'final_detector.json') == detector['raw_sha256']
        elif m == 'scw':
            cb = read(q/'clean_qwen_detector_raw.json'); dt = read(q/'student_detector_raw.json')
            cq = cb['primary']['p_value']; xba = dt['primary']['p_value']; delta = xba-cq
            rule = 'p < alpha=0.001; lower p is stronger; 1000 queries; frozen Llama detector tokenizer; permutation seed42'
            decisions = [cb['primary']['fingerprinted'], dt['primary']['fingerprinted']]
            assert sum(1 for _ in (q/'student_generations.jsonl').open(encoding='utf-8')) == 1000
        elif m == 'evertracer':
            canonical = 'N/A_CROSS_TOKENIZER'
            ex = read(q/'exploratory_detector/detector_results.json')
            exploratory = ex['metrics']
            assert ex['raw_original_count'] == 200 and ex['raw_perturbation_count'] == 2000
            assert sha(q/'exploratory_detector/raw_scores.jsonl') == ex['raw_sha256']
            assert sum(1 for _ in (q/'exploratory_detector/raw_scores.jsonl').open(encoding='utf-8')) == 200
            rule = 'EXPLORATORY only: exp(-mean next-token loss), Qwen128-token cap, member_score=-C, FPR<=0.05'
            decisions = ['N/A_CROSS_TOKENIZER', 'CANONICAL N/A; exploratory AUC0.523 TPR0.07 FPR0.05']
        else:
            canonical = 'N/A_CROSS_ARCHITECTURE'
            rule = 'Historical registered BLEU>=50; Qwen N/A without redefining keyed embedding interface'
            decisions = ['N/A_CROSS_ARCHITECTURE', 'N/A_CROSS_ARCHITECTURE']
        row = dict(method=m, run_id=full['run_id'], metric=('member_AUC' if m=='evertracer' else 'p_value' if m=='scw' else 'registered_success_rate' if m=='iseal' else 'trigger_rate' if m=='ctcc' else 'detected_rate'),
                   teacher_native_score=hist[0], clean_llama_score=hist[1], same_lineage_ba_score=hist[2], clean_qwen_score=cq,
                   cross_lineage_ba_score=xba, cross_lineage_delta_vs_clean_qwen=delta,
                   detector_applicability_level=f'LEVEL_{level}', canonical_detector_result=canonical, exploratory_detector_result=exploratory,
                   strictly_comparable_to_same_lineage='YES' if level==1 else 'NO', threshold_or_rule=rule,
                   clean_qwen_decision=decisions[0], cross_lineage_decision=decisions[1],
                   ARC_clean_qwen=ba, ARC_xba=arc, ARC_delta=arc-ba, MC2_clean_qwen=bm, MC2_xba=mc2, MC2_delta=mc2-bm,
                   training_status='COMPLETE', detector_status='COMPLETE' if level==1 else 'CANONICAL_N/A_EXPLORATORY_COMPLETE' if level==2 else 'N/A_CROSS_ARCHITECTURE',
                   utility_status='COMPLETE', final_scientific_status=full['scientific_status'], bounded_interpretation=explanations[m],
                   historical_reference=href, dataset_origin=data['parent_dataset_origin'],
                   comparability_boundary='Detector metric comparability only; reconstructed PNFP/SCW data are not historical byte/sample-identical; not a matched causal estimate.',
                   utility_raw_evidence=ref(rawpath), clean_utility_raw_evidence=ref(basepath))
        rows.append(row)
        if not (q/'dataset_manifest.json').exists():
            save(q/'dataset_manifest.json', {'derivation':'CPU deterministic extraction from original preflight; no dataset change', **data})
        report = next(P.glob(f'docs/reproduction_reports/active_cross_lineage_{m}_xba_*.md'))
        full.update(training_summary=ref(q/'training_summary.json'), model_provenance=prov,
                    dataset_manifest=read(q/'dataset_manifest.json'), detector_applicability=read(q/'detector_applicability.json'),
                    detector_applicability_level=f'LEVEL_{level}', canonical_detector_result=canonical, exploratory_detector_result=exploratory,
                    strictly_comparable_to_same_lineage=level==1, detector_results=detector, utility_results=utility,
                    closure_summary=read(q/'closure_summary.json'), report=report.relative_to(P).as_posix(), master_report=REPORT,
                    final_closure={'scientific_evidence':'COMPLETE','generated_at':NOW,'mode':'CPU_ONLY','shutdown_provenance':'UNVERIFIED',
                                   'archive':'AWAITING_USER_PREFERRED_SELECTION','git_receipt':'results/active_cross_lineage_ba/final_git_receipt_20260909.json'})
        full.update(utility='COMPLETE', detector=row['detector_status'], last_successful_stage='SCIENTIFIC_CLOSURE',
                    archive_status='AWAITING_USER_PREFERRED_SELECTION', git_closure='SEE_FINAL_GIT_RECEIPT_20260909',
                    closed_at=full.get('end_time'), status='COMPLETE')
        full['closure_summary'].update(git_status='SEE_FINAL_GIT_RECEIPT_20260909', archive_status='AWAITING_USER_PREFERRED_SELECTION')
        save(q/'closure_summary.json', full['closure_summary'])
        save(q/'full_experiment_log.json', full)
        raw_checks[m] = {'training_steps':7500,'raw_utility_counts':counts,'utility_sha':'PASS','existing_fresh_reload_evidence':'PASS','dataset_preflight_sha':'PASS','raw_evidence':'PASS','new_inference':False}
        shards = tuple((f['name'],f['sha256']) for f in prov['files'] if f['name'].endswith('.safetensors'))
        assert len(shards)==2
        weights[m]=shards
        retention.append(dict(method=m, final_model_path=prov['model_path'], model_size=sum(f['bytes'] for f in prov['files']), training_complete=True,
                              fresh_reload_verified=True,detector_status=row['detector_status'],utility_ARC=arc,utility_MC2=mc2,
                              scientific_value=explanations[m],already_archived_elsewhere='NO_ACTIVE_CAMPAIGN_UPLOAD_RECEIPT; account-wide remote inventory not repeated',
                              duplicate_weight_check='DISTINCT_AMONG_FIVE_SHA256; unrelated archives not exhaustively compared',
                              recommended_preferred_archive='YES_RECOMMENDATION_ONLY_USER_SELECTION_REQUIRED',
                              reason='独立正式实验的最终复现对象；保留建议不等于水印成功、utility全面优越或已批准preferred。',weight_manifest=ref(q/'model_provenance.json')))
    assert len(set(weights.values()))==5
    save(E/'master_comparison.json', rows)
    with (E/'master_comparison.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader()
        for r in rows:w.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(dict,list)) else v for k,v in r.items()})
    save(E/'model_retention_recommendations.json',retention)
    save(E/'closure_integrity.json',dict(checked_at=NOW,mode='CPU_ONLY',methods=raw_checks,duplicate_weight_check='FIVE_DISTINCT',shutdown_provenance='UNVERIFIED'))
    historical_table='\n'.join(f"| {r['method']} | {r['metric']} | {r['teacher_native_score']} | {r['clean_llama_score']} | {r['same_lineage_ba_score']} | {r['clean_qwen_score']} | {r['cross_lineage_ba_score']} | {r['detector_applicability_level']} |" for r in rows)
    utility_table='\n'.join(f"| {r['method']} | {r['ARC_xba']!r} | {r['ARC_delta']!r} | {r['MC2_xba']!r} | {r['MC2_delta']!r} |" for r in rows)
    text=f'''# Active Cross-Lineage Ba 最终科研闭环（2026-09-09）

五个独立 fresh Qwen2.5-3B-Instruct Student 均完成7500/7500 full-parameter SFT、最终保存、既有fresh-process reload和utility。当前CPU_ONLY闭环未运行任何新推理/训练。模型revision固定8f4992eda43eea7c770690ddc0de8f732da246f5。每方法使用冻结普通Teacher QA20k、3epochs、LR1e-5、batch8、seed42；训练配置与数据SHA见各自protocol/preflight/full log。

## 冻结detector与四类参照

| 方法 | metric | Teacher | Clean Llama | 历史同源Ba | Clean Qwen | XBa | 适用级别 |
|---|---|---:|---:|---:|---:|---:|---|
{historical_table}

数值只能在同一detector族内解释。Teacher从不充当clean Base。Level1表示冻结detector科学语义可比较，不表示所有历史dataset是同一字节文件，也不构成严格因果实验。

PN-FP: Teacher956/1024，Clean Llama1/1024，历史Ba98/1024；本轮Clean Qwen43/1024→XBa84/1024，差41/1024=0.0400390625。使用原Llama可见key/target字符串和完整编码签名相等规则，不使用会改变75个key/6个target的naive Qwen截断。parent为明确批准的protocol-faithful reconstruction；不是历史Ba exact replay。同重建parent的既有Llama Ba trajectory终点99/1024仅作额外参考（results/pnfp/experiment_ba_trajectory_followup/），不得混同历史98。

CTCC: Teacher95/95；Clean Qwen与XBa均trigger0/95、suppression0/100、normal0/105、combined negatives0/205，无生成错误。冻结WMKD操作规则为generated_answer.strip()==IAMALIVE（大小写敏感），不能虚称为论文另有的官方阈值。

EverTracer: canonical=N/A_CROSS_TOKENIZER；探索性AUC0.523，TPR0.07，FPR0.05，operating threshold0.011513830561923802。保持冻结200 originals/2000 perturbations，Qwen128-token cap、exp(-mean next-token loss)、原member方向/ROC/FPR规则。1477/2200可见文本改变；即使先冻结Llama可见文本，1262/2200仍超Qwen128窗口。token分段、预测位置、归一分母改变使数字不可与历史Llama AUC严格比较。EXPLORATORY_NON_COMPARABLE；不得填入canonical主数值列。

iSeal: canonical=N/A_CROSS_ARCHITECTURE，冻结注册Llama embedding3072维，Qwen2048维。未加projection、未改维度、未重新注册、未改secret/公式/阈值。历史registered success Teacher179/200、Base0/200、Ba0/200；不伪造Qwen success。

SCW: 1000条冻结查询；Clean Qwen p=0.7446491718292236、XBa p=0.9158855080604553，均未达alpha0.001。统计detector继续使用冻结Llama tokenizer、permutation seed42与lower-p方向。历史Teacher记录p=0.0是数值输出，不能解释为理论概率恰为零。p差是描述性差值，不是线性信号强度。parent为重建数据，非历史Ba exact replay。

## Utility原始精确值

Clean Qwen ARC-Challenge acc_norm={ba!r}；TruthfulQA MC2={bm!r}。每个Student原始样本ARC1172、MC2817；精确delta直接由原始evaluator结果相减，未使用聊天四舍五入值。相同lm_eval0.4.9.1/native chat协议；完整配置、raw outputs与SHA保留。

| 方法 | ARC | ARC delta | MC2 | MC2 delta |
|---|---:|---:|---:|---:|
{utility_table}

## 十个科学问题的边界明确回答

1. PN-FP、CTCC、SCW为Level1，冻结规则可在Qwen执行。
2. EverTracer为tokenizer-bound Level2；iSeal为architecture/embedding-bound Level3。
3. PN-FP相对同协议clean Qwen增加41个命中，支持部分获取；不等于完整水印转移，也未新增显著性判据。
4. CTCC终点0/95，不支持已获得IAMALIVE trigger行为。
5. EverTracer探索性AUC0.523显示改编诊断下近随机分离；不能据此声称原水印失败/存活/转移。
6. iSeal冻结接口维度不匹配；合法N/A，不是Student训练失败或水印转移失败。
7. SCW最终p高于alpha，维持未检出。
8. PN-FP的XBa84低于历史98及同重建parent99，但clean背景也不同；CTCC两条lineage均0，SCW两条均未检出。不能泛化为cross-lineage使所有方法更弱，更不能以EverTracer/iSeal N/A作数值证据。
9. 有效冻结detector的终点证据呈弱获取/未检出，与acquisition limitation相容。本campaign只有终点，没有跨lineage训练轨迹，不能排除曾强学后忘，也不能把同源trajectory直接移植为本轮因果证据。
10. 五个ARC均升、MC2均降，属于benchmark相关tradeoff；不支持简单“全面utility collapse”解释，也不能声称整体utility不变或证明utility与detector的因果关系。

Under cross-lineage behavioral extraction, active watermark signals are generally weak or absent under valid frozen detectors. Detector N/A 不构成水印被擦除的证据。

## 闭环与保留

canonical master沿用results/active_cross_lineage_ba/master_comparison.json与.csv，未另建重复主表。五份full_experiment_log位于各方法同名目录，包含training_summary、model_provenance、dataset_manifest、applicability、detector或N/A、utility、closure_summary与report。索引使用本次commit中的results/experiment_full_logs_index.json；Git最终SHA由独立final_git_receipt_20260909.json记载以避免自引用。

原始证据包artifacts/active_cross_lineage_ba_scientific_evidence_20260909.zip：6347746 bytes，SHA256=6686e48da898e929969d8ba2a7c393ee101c8abe750c5812eb27d14b81bf9c6a，已与AutoDL源包核对，164files；原包不可变，最终闭环补充包另存。raw永久本地/AutoDL保留，不把模型权重或大型raw正文塞入Git。

shutdown_provenance=UNVERIFIED。旧overnight_shutdown_receipt.json与final_campaign_status.json在检查时均不存在；不补造昨夜关机原因或收据。此为工程provenance限制，不改变已有科研结果。

五份final model均暂存原路径，SHA彼此不同。均建议作为独立正式实验的复现对象进入后续preferred选择（详见model_retention_recommendations.json），只是建议，不是已批准preferred或已上传。EverTracer/iSeal的适用性本身有科学价值。此次未重复查询全ModelScope账户，已归档与否只依据当前campaign缺少上传receipt，不能据此断言全账户绝无副本。

下一步仅等待用户选择最终ModelScope preferred archives；不启动新实验、不自动上传/删除模型、不在本报告交付前关机。
'''
    (P/REPORT).write_text(text,encoding='utf-8')
    print(json.dumps({'methods':len(rows),'raw_checks':raw_checks,'report':REPORT},ensure_ascii=False))


if __name__ == '__main__':
    main()
