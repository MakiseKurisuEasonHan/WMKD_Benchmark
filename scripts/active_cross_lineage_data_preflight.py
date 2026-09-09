"""CPU-only frozen dataset/formatter audit; no data mutation or generation."""
import hashlib
import json
from pathlib import Path
from transformers import AutoTokenizer

P=Path('/root/autodl-tmp/WMKD_Benchmark')
D=Path(str(P)+'_data')
E=P/'results/active_cross_lineage_ba'
tok=AutoTokenizer.from_pretrained(D/'models/paraphrasers/Qwen2.5-3B-Instruct',local_files_only=True)
for method in ('pnfp','evertracer','ctcc','iseal','scw'):
    manifest=json.loads((P/f'results/{method}/experiment_ba_trajectory_followup/dataset_manifest.json').read_text())
    src=Path(manifest['path'])
    actual=hashlib.sha256(src.read_bytes()).hexdigest()
    rows=[json.loads(x) for x in src.read_text().splitlines() if x.strip()]
    report={'method':method,'source_path':str(src),'expected_sha256':manifest['sha256'],'actual_sha256':actual,
            'records':len(rows),'answer_field':'teacher_raw_answer','paraphrased_answer_selected':False,
            'parent_dataset_origin':manifest.get('parent_dataset_origin'),'max_length':1024,
            'empty_question':0,'empty_answer':0,'truncated':0,'empty_supervision':0,'nonprefix_prompt':0,'max_serialized_tokens':0}
    assert len(rows)==20000 and actual==manifest['sha256'],report
    for r in rows:
        user=r['instruction']+(('\n\nInput:\n'+r['input']) if r['input'] else '')
        answer=r['teacher_raw_answer']
        report['empty_question']+=int(not user.strip())
        report['empty_answer']+=int(not answer.strip())
        prompt=tok.apply_chat_template([{'role':'user','content':user}],tokenize=False,add_generation_prompt=True)
        full=tok.apply_chat_template([{'role':'user','content':user},{'role':'assistant','content':answer}],tokenize=False,add_generation_prompt=False)
        pi=tok.encode(prompt,add_special_tokens=False);fi=tok.encode(full,add_special_tokens=False)
        report['max_serialized_tokens']=max(report['max_serialized_tokens'],len(fi))
        report['truncated']+=int(len(fi)>1024)
        report['empty_supervision']+=int(min(len(fi),1024)<=len(pi))
        report['nonprefix_prompt']+=int(fi[:len(pi)]!=pi)
    report['status']='PASS' if all(report[x]==0 for x in ('empty_question','empty_answer','truncated','empty_supervision','nonprefix_prompt')) else 'DATA_INTEGRITY_BLOCKED'
    out=E/method/'qwen_dataset_preflight.json';out.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report),flush=True)
