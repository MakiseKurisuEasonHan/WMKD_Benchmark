"""Only unfinished 7B Bc; original Teacher/Ba/Bb are immutable references."""
import fcntl
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
import traceback
import pnfp_7b_distill_campaign as c

OLD=c.E
c.E=c.P/'results/pnfp/scale_7b/logit_recovery_6004'
c.O=c.R/'logit_recovery_6004'
E=c.E;O=c.O


def main():
    E.mkdir(exist_ok=True);O.mkdir(exist_ok=True)
    lock=(E/'recovery.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    assert not (E/'terminal.json').exists(),'No implicit rerun'
    assert json.loads((E/'dtype_smoke.json').read_text())['status']=='PASS'
    assert json.loads((E/'artifact_verification.json').read_text())['pass']
    shutil.copy2(OLD/'clone_preflight.json',E/'clone_preflight.json')
    dataset=c.R/'distillation_6004/direct/frozen_qa.jsonl'
    stats=json.loads((OLD/'supervision_stats.json').read_text())
    assert c.sha(dataset)==stats['dataset_file_sha256']
    state=dict(status='RUNNING',started=time.time(),scope='LOGIT_ONLY',pid=os.getpid())
    c.put(E/'campaign_state.json',state)
    try:
        c.run('logit_cache','pnfp_7b_distill_worker.py',['cache','--base',c.BASE,'--teacher',c.TEACHER,
            '--dataset',dataset,'--cache',O/'logit_cache','--output',E],
            additional=stats['payload_bytes']+13479264256+2*2**30)
        manifest=json.loads((O/'logit_cache/manifest.json').read_text())
        assert manifest['complete'] and len(manifest['shards'])==157
        assert manifest['dtype']=='bfloat16' and manifest['representation']=='full_vocab'
        assert manifest['vocabulary_size']==32000 and manifest['supervised_tokens']==527563
        assert manifest['feature_sha256']==stats['feature_sha256'] and manifest['dataset_file_sha256']==stats['dataset_file_sha256']
        assert len(manifest['records'])==20000 and sum(x['positions'] for x in manifest['records'])==527563
        assert sum(x['bytes'] for x in manifest['shards'])==33764032000
        for i,record in enumerate(manifest['records']):assert record['index']==i
        for shard in manifest['shards']:
            path=O/'logit_cache'/shard['path']
            assert path.stat().st_size==shard['bytes'] and c.sha(path)==shard['sha256']
        c.put(E/'cache_verification.json',dict(status='PASS',shards=157,samples=20000,supervised_tokens=527563,
            total_bytes=33764032000,dtype='bfloat16',vocabulary_size=32000,per_shard_sha_verified=True,
            teacher_process_ended=True,manifest_sha256=c.sha(O/'logit_cache/manifest.json')))
        c.train_and_eval('logit',dataset)
        final=O/'logit/final_model';saved=json.loads((O/'logit/final_manifest.json').read_text())
        assert all((final/x['path']).is_file() and c.sha(final/x['path'])==x['sha256'] for x in saved['files'])
        state.update(status='COMPLETED',final_model_sha_verified=True,final_model=str(final))
    except Exception:
        # Never repeat the previous mistake of treating an arbitrary engineering
        # exception as a scientific failure and immediately powering off.
        state.update(status='RECOVERY_REQUIRED',error=traceback.format_exc(),auto_shutdown=False)
    finally:
        state['ended']=time.time()
        lines=['# PN-FP 7B same-backbone distillation — Logit recovery','',
            'Status: '+state['status'],'',
            'Teacher, Direct and Paraphrase are unchanged completed references; no re-evaluation was run.',
            'Serialization dtype compatibility fix: Transformers4.44.2 Llama promotes BF16 lm_head logits to FP32; selected targets are explicitly cast to BF16 as in canonical3B Bc. Full vocabulary, positions, token alignment, T2 and CE/KD0.5 are unchanged.','',
            '| Condition | PN-FP hits/1024 | Recall % | Retention vs Teacher | ARC | TruthfulQA |',
            '|---|---:|---:|---:|---:|---:|',
            '| Teacher | 804 | 78.515625 | 100% | 42.064846% | 44.199762% |']
        for stage in ['direct','paraphrase','logit']:
            root=E if stage=='logit' else OLD
            f=root/(stage+'_full_experiment_log.json')
            if not f.exists():lines.append('| '+stage+' | NOT_COMPLETED | | | | |');continue
            x=json.loads(f.read_text());h=x['detector']['detected'];u=x['utility']['a2']
            lines.append(f"| {stage} | {h} | {h/1024*100:.6f} | {h/804*100:.6f}% | {u['arc_challenge_acc_norm']*100:.6f}% | {u['truthfulqa_mc2_acc']*100:.6f}% |")
        if 'error' in state:lines+=['','Engineering failure, not a scientific conclusion:','```',state['error'],'```']
        (E/'final_report.md').write_text('\n'.join(lines)+'\n')
        c.put(E/'campaign_state.json',state);c.put(E/'terminal.json',state);subprocess.run(['sync'])


if __name__=='__main__':main()
