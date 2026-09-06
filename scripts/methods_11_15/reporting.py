"""Human-readable method reports and machine-readable closure table."""
from common import *
import json

def outputs(m,stage):
    path=m['completed_stages'].get(stage)
    return read(path).get('outputs',{}) if path else {}

def formal_report(c,m,log):
    rr=Path(c['run_root']); out=ROOT/'docs/reproduction_reports'/f'{c["method"]}_experiment_a_{c["run_id"]}.md'
    protocol=read(rr/'protocol.json') if (rr/'protocol.json').exists() else 'NOT_RUN'
    patch=(rr/'compatibility.patch').read_text() if (rr/'compatibility.patch').exists() else 'NOT_RUN'
    sections=[('科学目标','复现官方模型所有权信号，完成 Base、负对照、utility 与恢复验证。'),('论文与官方实现',c['spec']),('方法语义与 Paper/code/runtime 配置',protocol),('环境',outputs(m,'ENV_READY') or 'NOT_RUN'),('模型与数据 provenance',outputs(m,'MODEL_DATA_READY') or 'NOT_RUN'),('训练结果与运行时间',log['training']),('检测与负对照',log['detector']),('Utility 与 Base 差值',log['utility']),('Reload 验证',log['reload']),('兼容性修复',{'repair_history':m['repair_history'],'patch':patch}),('科学判断与限制',{'status':m['scientific_status'],'ENGINEERING_STATUS':m.get('ENGINEERING_STATUS'),'FINGERPRINT_STATUS':m.get('FINGERPRINT_STATUS'),'UTILITY_STATUS':m.get('UTILITY_STATUS'),'FINAL_SCIENTIFIC_STATUS':m.get('FINAL_SCIENTIFIC_STATUS'),'last_error':m['last_error'],'limitations':log['limitations']}),('归档与恢复',log['archive'])]
    text=f'# {c["spec"]["name"]} — Experiment A\n\nRun ID: `{c["run_id"]}`\n\n'
    for name,value in sections:
        text+=f'## {name}\n\n'
        if isinstance(value,str): text+=value+'\n\n'
        else: text+='```json\n'+json.dumps(value,ensure_ascii=False,indent=2)+'\n```\n\n'
    text+=f'完整日志：[full_experiment_log.json](../../results/methods_11_15/{c["method"]}/experiment_a/full_experiment_log.json)。\n'
    out.write_text(text,encoding='utf-8',newline='\n'); return str(out.relative_to(ROOT))

def master(state):
    rows=[]
    for slug,m in state['methods'].items():
        c=read(m['context']); rr=Path(c['run_root']); train=outputs(m,'TRAINING'); det=outputs(m,'DETECTOR'); util=outputs(m,'UTILITY'); archive=outputs(m,'ARCHIVED')
        protocol=read(rr/'protocol.json') if (rr/'protocol.json').exists() else {}
        runtimes={s:read(p).get('runtime_seconds') for s,p in m['completed_stages'].items()}
        row={'method':m['method'],'run_id':m['run_id'],'official_backbone':c['spec']['backbone'],'dataset':c['spec']['dataset'],'watermark_type':protocol.get('route') or protocol.get('variant') or protocol.get('construction') or {'eaaw':'feature attribution128-bit','utf':'undertrained-token fingerprint'}.get(slug),'training_type':{'eaaw':'full FT','instructional_fingerprinting':'official IF_adapter','utf':'full FT / ZeRO3','double_i':'LoRA','codegenguard':'dual-LoRA with optimized discrete prompt'}[slug],'runtime_seconds':sum(v for v in runtimes.values() if v is not None),'stage_runtime_seconds':runtimes,'peak_vram_bytes':train.get('peak_vram_bytes') or train.get('telemetry',{}).get('peak_gpu_used_bytes'),'detector_metric':det.get('metric') or protocol.get('detector'),'detector_result':det or 'NOT_RUN','negative_control':det.get('negative_controls','NOT_RUN'),'utility_metric':util.get('metric','NOT_RUN'),'utility_delta':util.get('delta','NOT_RUN'),'final_status':m['scientific_status'],'archive_status':m['archive_status'],'archive':archive or 'NOT_RUN','formal_report':m.get('formal_report')}
        rows.append(row)
    value={'created_at':now(),'all_terminal':all(m['status']=='TERMINAL' for m in state['methods'].values()),'rows':rows,'methods':state['methods']}; write(ROOT/'results/methods_11_15_experiment_a_summary.json',value)
    headers=['Method','Backbone','Dataset','Type / training','Runtime (s)','Peak VRAM','Detector','Negative control','Utility / delta','Final status','Archive']
    text='# Methods 11–15 Experiment A\n\n缺失结果明确记为 NOT_RUN/unavailable；基础设施失败不等于方法科学失败。\n\n| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'
    for r in rows:
        cells=[r['method'],r['official_backbone'],r['dataset'],str(r['watermark_type'])+' / '+r['training_type'],str(round(r['runtime_seconds'],2)),str(r['peak_vram_bytes'] or 'unavailable'),str(r['detector_metric'] or 'NOT_RUN'),str(r['negative_control']),str(r['utility_metric'])+' / '+str(r['utility_delta']),r['final_status'],r['archive_status']]
        text+='| '+' | '.join(x.replace('|','/').replace('\n',' ') for x in cells)+' |\n'
    text+='\n每个方法的原始检测值、对照、utility 和归档见对应正式报告与 JSON 汇总。\n\n'
    for r in rows:
        if r['formal_report']: text+=f'- [{r["method"]}]({Path(r["formal_report"]).name})\n'
    (ROOT/'docs/reproduction_reports/methods_11_15_experiment_a_summary.md').write_text(text,encoding='utf-8',newline='\n')
    return value

def update_project_state(state):
    start='<!-- WMKD_METHODS_11_15_CURRENT_BEGIN -->'; end='<!-- WMKD_METHODS_11_15_CURRENT_END -->'
    lines=[start,'## Methods 11–15 当前状态','',f'更新：{now()}；总状态：{state["status"]}。','', '| 方法 | 阶段 | 状态 | 科学结论 |','|---|---|---|---|']
    for m in state['methods'].values(): lines.append(f'| {m["method"]} | {m["stage"]} | {m["status"]} | {m["scientific_status"]} |')
    lines+=['','本批恢复入口：`results/methods_11_15_pipeline_state.json`；执行器：`scripts/methods_11_15/run_methods_11_15.py`。第一批十方法保持 CLOSED，历史 KEEP/UNCERTAIN 保留。',end,'']
    block='\n'.join(lines)
    for name in ('docs/CURRENT_STATE.md','PROJECT_STATUS.md','TODO.md'):
        path=ROOT/name; old=path.read_text()
        if start in old: old=old[:old.index(start)]+old[old.index(end)+len(end):].lstrip('\n')
        path.write_text(block+'\n'+old,encoding='utf-8',newline='\n')
