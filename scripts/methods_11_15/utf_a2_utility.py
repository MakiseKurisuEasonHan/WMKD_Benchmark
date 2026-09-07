"""Existing WMKD evaluator, one same-date frozen Base, separate model processes."""
import argparse
import datetime
import hashlib
import importlib.metadata as metadata
import json
import os
from pathlib import Path
import sys
import time

P=Path('/root/autodl-tmp/WMKD_Benchmark')
sys.path.insert(0,str(P/'scripts'))

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run-root',type=Path,required=True)
    ap.add_argument('--label',choices=['base','teacher'],required=True);a=ap.parse_args()
    out=a.run_root/f'utility_{a.label}';assert not out.exists();out.mkdir()
    from evertracer_common import load_config
    from evertracer_utility import configure_offline_utility,evaluate
    cfg_path=P/'configs/watermark/evertracer_experiment_a.yaml';cfg=load_config(cfg_path)
    provenance=configure_offline_utility(cfg)
    versions={}
    for line in (P/'requirements/evertracer_autodl.txt').read_text().splitlines():
        if '==' in line and not line.startswith('#'):
            name,version=line.strip().split('==');versions[name]=metadata.version(name);assert versions[name]==version,(name,version,versions[name])
    summary_path=P/'results/evertracer/experiment_a_summary.json';summary=json.loads(summary_path.read_text())
    assert summary['model']['id']=='meta-llama/Llama-3.2-3B-Instruct'
    assert summary['model']['revision']=='0cb88a4f764b7a12671c53f0838cd831a0843b95'
    assert summary['utility']['dataset_provenance']==provenance
    assert cfg['utility']['batch_size']==8 and cfg['utility']['apply_chat_template'] is True
    full=P/'results/evertracer/preferred_teacher/full_experiment_log.json'
    obj=next(o for o in json.loads((P/'results/experiment_full_logs_index.json').read_text())['objects'] if o['full_log_path']==str(full.relative_to(P)))
    assert sha(full)==obj['full_log_sha256']
    historical=summary['utility']['base'];assert historical['path']==summary['model']['path']
    baseline=dict(status='HISTORICAL_NOT_REUSED_DYNAMIC_PROMPT_DATE',model=summary['model'],historical_base=historical,summary_path=str(summary_path),summary_sha256=sha(summary_path),
                  full_log_path=str(full),full_log_sha256=sha(full),dataset_provenance=provenance,versions=versions,
                  evaluator_path=str(P/'scripts/evertracer_utility.py'),evaluator_sha256=sha(P/'scripts/evertracer_utility.py'),
                  config_path=str(cfg_path),config_sha256=sha(cfg_path),batch_size=8,apply_chat_template=True,
                  canonical_model_identity_receipt=str(P/'results/utf_a2_identity_check_20260907.json'),
                  runtime_launcher_provenance=str(P/'scripts/run_evertracer_experiment_a_cont2.sh'),base_rerun=True,
                  reason='Canonical template contains Today Date from strftime_now; historical rendered prompt identity cannot match this new evaluation. User permits one matching canonical Base evaluation if no reusable reference exists.')
    model_path=summary['model']['path'] if a.label=='base' else str(a.run_root/'formal/final_model')
    from transformers import AutoTokenizer
    tokenizer=AutoTokenizer.from_pretrained(model_path,local_files_only=True)
    rendered=tokenizer.apply_chat_template([{'role':'user','content':'WMKD utility template identity probe'}],tokenize=False,add_generation_prompt=True)
    date=datetime.datetime.now().strftime('%d %b %Y')
    assert 'Today Date: '+date in rendered
    template_sha=hashlib.sha256(rendered.encode()).hexdigest()
    token_sha=hashlib.sha256(json.dumps(tokenizer.encode(rendered,add_special_tokens=False)).encode()).hexdigest()
    if a.label=='teacher':
        frozen=json.loads((a.run_root/'utility_base/result.json').read_text())
        assert frozen['status']=='COMPLETE' and frozen['prompt_template_probe_sha256']==template_sha and frozen['evaluation_date']==date
        assert frozen['prompt_token_ids_sha256']==token_sha
    (out/'historical_reference_audit.json').write_text(json.dumps(baseline,indent=2)+'\n')
    import lm_eval
    original=lm_eval.simple_evaluate
    def capture(*args,**kwargs):
        result=original(*args,**kwargs)
        (out/'full_lm_eval_output.json').write_text(json.dumps(result,indent=2,default=str)+'\n')
        return result
    lm_eval.simple_evaluate=capture
    start=time.time();scores=evaluate(model_path,8)
    assert datetime.datetime.now().strftime('%d %b %Y')==date, 'Date boundary crossed; do not combine mismatched prompts'
    result=dict(status='COMPLETE',label=a.label,scores=scores,historical_reference_audit=baseline,
        evaluation_date=date,prompt_template_probe_sha256=template_sha,prompt_token_ids_sha256=token_sha,prompt_template_probe=rendered,
        elapsed_seconds=time.time()-start,errors=[],preferred_teacher='NOT_YET_EVALUATED',utility_status='REQUIRES_JOINT_REVIEW_OF_RAW_SCORES_AND_DELTAS')
    if a.label=='teacher':
        result['base_reference_path']=str(a.run_root/'utility_base/result.json')
        result['base_reference_sha256']=sha(a.run_root/'utility_base/result.json')
        result['delta']={key:scores[key]-frozen['scores'][key] for key in ['arc_challenge_acc_norm','truthfulqa_mc2_acc']}
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)

if __name__=='__main__':main()
