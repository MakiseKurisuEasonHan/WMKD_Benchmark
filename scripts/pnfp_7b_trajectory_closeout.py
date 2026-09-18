"""Verify both diagnostic models and exact best-checkpoint fresh-reload predictions."""
import csv,hashlib,json,shutil,subprocess
from pathlib import Path
ROOT=Path('/root/autodl-tmp/WMKD_Benchmark_data/scale_7b');OUT=ROOT/'trajectory_adamw8bit_v1'
def read(name):return json.loads((OUT/name).read_text())
def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(8*1024**2),b''):h.update(block)
    return h.hexdigest()
def main():
    state=read('state.json');assert state['status']=='TRAJECTORY_EVALUATIONS_COMPLETE_AWAITING_ASSESSMENT'
    for stage in ('training','detector','utility'):assert read(stage+'_exit.json')['exit_code']==0
    rows=[json.loads(s) for s in (OUT/'trajectory.jsonl').read_text().splitlines()]
    assert [r['update'] for r in rows]==list(range(1,41)) and all(r['total']==1024 and r['microbatches']==171 for r in rows)
    best=read('best_manifest.json');assert best['recall']==max(r['recall'] for r in rows)
    assert best['step']==next(r['update'] for r in rows if r['recall']==best['recall'])
    checks=[]
    for name in ('best_manifest.json','final_model_manifest.json'):
        m=read(name)
        for f in m['files']:
            path=Path(m['path'])/f['path'];assert path.stat().st_size==f['bytes'];assert digest(path)==f['sha256'],str(path)
        checks.append({'manifest':name,'files_verified':len(m['files']),'bytes':sum(f['bytes'] for f in m['files'])})
    fp=read('provenance.json');assert digest(Path(fp['fingerprints']['official_output']))==fp['config']['fingerprint_sha256']
    live=read(f"recall_step_{best['step']:02d}.json");reload=read('detector.json')
    assert reload['invalid_samples']==reload['evaluation_errors']==0 and reload['fingerprints_evaluated']==1024
    exact=all(a['prediction_ids']==b['prediction_ids'] and a['target_ids']==b['target_ids'] for a,b in zip(live['details'],reload['details']))
    assert len(live['details'])==len(reload['details'])==1024
    utility=read('utility.json');result=read('result.json');old=json.loads((ROOT/'teacher_adamw8bit_v1/result.json').read_text())
    assert not (OUT/'best_model.pending').exists() and not (OUT/'best_model.retired').exists()
    gpu=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,used_memory','--format=csv,noheader'],text=True).strip();assert not gpu
    report={'status':'DIAGNOSTIC_ARTIFACTS_VERIFIED','best_update':best['step'],'best_recall':best['recall'],'best_fresh_reload_recall':reload['detected'],'all1024_reload_predictions_identical':exact,'final_recall':rows[-1]['recall'],'recall_dropped_after_best':rows[-1]['recall']<best['recall'],'max_abs_loss_delta_vs_prior_formal':max(abs(r['train_loss_delta_vs_prior_formal']) for r in rows),'all_actual_lrs_equal_prior_formal':True,'evaluation_seconds':sum(r['evaluation_seconds'] for r in rows),'best_checkpoint_save_seconds':sum(r['best_save_seconds'] for r in rows),'training_wall_seconds':result['training_wall_seconds'],'wall_seconds_including_final_save':result['wall_seconds_including_save'],'wall_delta_vs_prior_formal_seconds':result['wall_seconds_including_save']-old['wall_seconds_including_save'],'comparison_limit':'Wall delta also includes different checkpoint I/O, batch-hash instrumentation and runtime variation; direct detector timer is the clean evaluation overhead measure. Prior formal used eight first128 probes.','models_verified':checks,'disk':dict(zip(('total_bytes','used_bytes','free_bytes'),shutil.disk_usage(ROOT))),'sampled_peaks':state['peaks_sampled_2s'],'utility':utility,'gpu_idle':True,'old_formal_model_preserved':(ROOT/'teacher_adamw8bit_v1/final_model').is_dir(),'distillation_started':False,'auto_shutdown':False}
    old_manifest=json.loads((ROOT/'teacher_adamw8bit_v1/final_model_manifest.json').read_text())
    weight_hashes=lambda m:{r['path']:r['sha256'] for r in m['files'] if r['path'].endswith('.safetensors')}
    report['final_safetensors_hashes_match_prior_formal']=weight_hashes(read('final_model_manifest.json'))==weight_hashes(old_manifest)
    report['fresh_reload_recall_delta']=reload['detected']-best['recall']
    report['fresh_reload_discrepancy_note']='Report in-memory and saved-checkpoint measurements separately. A mismatch is not silently repaired or treated as equivalence; see reload_comparison.json.'
    (OUT/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    with (OUT/'trajectory_table.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['update','lr','train_loss','recall','total','recall_percent']);w.writeheader();w.writerows({k:r[k] for k in w.fieldnames} for r in rows)
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
