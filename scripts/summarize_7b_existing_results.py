"""Derive the 7B closeout tables from saved scientific receipts (no evaluation)."""
import csv,hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parents[1];E=P/'results/scale_7b_final_audit'
def load(name):return json.loads((P/name).read_text(encoding='utf-8'))
def sha(name):return hashlib.sha256((P/name).read_bytes()).hexdigest()
def write(name,x):(E/name).write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def main():
    E.mkdir(exist_ok=True)
    rows=[];runtime=[];sources=[]
    teacher='results/pnfp/scale_7b/wa050_extension/receipts/'
    d=load(teacher+'final_detector.json');u=load(teacher+'final_utility.json')['checkpoint'];m=load(teacher+'best_manifest.json')
    assert d['detected']==804 and m['fresh_recall']==804 and m['nonzero_lr_update']==19
    rows.append(dict(method='PN-FP',condition='Teacher',hits=804,total=1024,recall=804/1024,retention=1.0,score=None,threshold=None,detected=None,arc=u['arc_challenge_acc_norm'],truthfulqa=u['truthfulqa_mc2_acc']))
    for s in ['direct','paraphrase','logit']:
        root='results/pnfp/scale_7b/'+('logit_recovery_6004' if s=='logit' else 'distillation_6004')+'/'
        source=root+s+'/full_experiment_log.json';x=load(source);sources.append(source)
        assert x['status']=='COMPLETED';d=x['detector'];u=x['utility']['a2'];r=load(root+s+'_training_summary.json')
        assert d['fingerprints_evaluated']==1024 and d['invalid_samples']==d['evaluation_errors']==0 and r['steps']==7500 and r['finite_parameters']
        rows.append(dict(method='PN-FP',condition=s.title(),hits=d['detected'],total=1024,recall=d['detected']/1024,retention=d['detected']/804,score=None,threshold=None,detected=None,arc=u['arc_challenge_acc_norm'],truthfulqa=u['truthfulqa_mc2_acc']))
        rt=load(root+s+'_training_runtime.json')
        runtime.append(dict(method='PN-FP',condition=s.title(),training_summary_s=r['runtime_seconds'],subprocess_wall_s=rt['ended']-rt['started'],peak_allocated_GiB=r['peak_vram_bytes']/2**30,peak_sampled_GPU_GiB=rt['sampled_gpu_peak_bytes']/2**30,peak_RSS_GiB=r['peak_host_rss_bytes']/2**30,manifest=root+s+'_final_manifest.json',manifest_sha256=sha(root+s+'_final_manifest.json')))
    aw='results/awm/scale_7b/';cal=load(aw+'calibration.json');frozen=load(aw+'calibration_freeze.json')
    assert sha(aw+'calibration.json')==frozen['calibration_sha256']=='627107dc6c7db1569a43c2f94f67b5e7f9314bdcd2968c36f288f07b83b47a3f'
    assert cal['threshold']==frozen['threshold']==0.007566815861277831
    assert cal['threshold']==max(x['score'] for x in cal['negatives']) and len(cal['negatives'])==3
    for s in ['reference','direct','paraphrase','logit']:
        source=aw+s+'/full_experiment_log.json';x=load(source);sources.append(source);d=x['detector'];u=x['utility']['a2']
        assert d['threshold']==cal['threshold'] and d['detected']==(d['score']>cal['threshold'])
        rows.append(dict(method='AWM',condition=s.title(),hits=None,total=None,recall=None,retention=None,score=d['score'],threshold=d['threshold'],detected=d['detected'],arc=u['arc_challenge_acc_norm'],truthfulqa=u['truthfulqa_mc2_acc']))
        if s!='reference':
            r=load(aw+s+'_training_summary.json');rt=load(aw+s+'_training_micro8_runtime.json');assert r['steps']==7500 and r['finite_parameters']
            assert rt['started']>frozen['timestamp']
            runtime.append(dict(method='AWM',condition=s.title(),training_summary_s=r['runtime_seconds'],subprocess_wall_s=rt['ended']-rt['started'],peak_allocated_GiB=r['peak_vram_bytes']/2**30,peak_sampled_GPU_GiB=rt['sampled_gpu_peak_bytes']/2**30,peak_RSS_GiB=r['peak_host_rss_bytes']/2**30,manifest=aw+s+'_final_manifest.json',manifest_sha256=sha(aw+s+'_final_manifest.json')))
    cache=load(aw+'logit_cache_integrity_summary.json');clean=load(aw+'logit_cleanup_receipt.json');para=load(aw+'paraphrase_progress.json')
    assert cache['complete'] and cache['suggested_shards']==157 and len(clean['deleted'])==157 and para['successful_count']==20000 and para['identity_fallback_count']==0
    assert clean['reclaimed_bytes']==cache['payload_bytes'] and all(load(aw+s+'_complete.json')['time']<clean['time'] for s in ['direct','paraphrase','logit'])
    summary=dict(scope='representative active/passive 7B same-backbone scale extension',rows=rows,runtime=runtime,
        model_id='meta-llama/Llama-2-7b-chat-hf',revision='f5db02db724555f92da89c216ac04704f23d4590',
        sources=[dict(path=n,sha256=sha(n)) for n in sources+[teacher+'final_detector.json',teacher+'final_utility.json',teacher+'best_manifest.json',aw+'calibration.json']],
        no_new_experiments=True,cross_lineage='PAUSED_NOT_EXECUTED',llmprint='PAUSED_FOR_AWM_SPEED_COMPARISON',
        awm_cache=dict(shards=157,verified_before_cleanup=True,payload_bytes=cache['payload_bytes'],cleanup_after_all_stage_completions=True),paraphrase_retries=para['retry_count'])
    write('unified_results.json',summary)
    with (E/'unified_results.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    write('preferred_teacher_selection.json',dict(status='USER_ACCEPTED_FINAL_TEACHER',fresh_hits=804,total=1024,nonzero_update=19,optimizer_call=21,
        checkpoint=m['path'],manifest_path=teacher+'best_manifest.json',manifest_sha256=sha(teacher+'best_manifest.json'),
        historical_assessment='EXTENSION_COMPLETE_NOT_PREFERRED preserved: the automatic >=80% gate was not met at extension closeout',
        later_authority='User accepted 804/1024 for formal distillation; see results/pnfp/scale_7b/distillation/user_authorization_20260919.txt and subsequent 6004 authorization',
        scientific_results_changed=False))
    lines=['# 7B scale extension: PN-FP and AWM — final verified summary','',
        'Scope: **representative active/passive 7B scale extension**, specifically same-backbone Llama-2-7B-chat → independently fresh Llama-2-7B-chat Students. Cross-lineage was paused before training. LLMPrint remains paused at 58/200; neither is a completed result in this table.','',
        'This closeout reads existing artifacts and hashes files on a CPU-only AutoDL instance. It does not regenerate data, retrain, recalibrate, or rerun detector/utility. Git publication status is recorded separately in `results/scale_7b_final_audit/git_publication_status.json`.','',
        '## Model, hardware, and protocol','',
        '- Canonical model: `meta-llama/Llama-2-7b-chat-hf@f5db02db724555f92da89c216ac04704f23d4590`; 6,738,415,616 parameters. ModelScope transport: `shakechen/Llama-2-7b-chat-hf@299e68d813ff6f146741f8e8477ed0a57ded4765`. Transport revision is not substituted for canonical upstream identity; per-file hashes bind the downloaded files.',
        '- Training hardware: one NVIDIA RTX PRO 6000 Blackwell Server Edition, 96 GB; 22 CPU cores / 110 GiB cgroup RAM. Teacher work used the earlier smaller data disk; final distillation used cloned 6004 with a 591 GiB data disk. CUDA/PyTorch stack: torch 2.8.0+cu128; training Transformers 4.44.2; AWM detector used the separately recorded 4.51.3 compatibility runtime.',
        '- BF16 full-parameter training, activation checkpointing, `bitsandbytes.optim.adamw.AdamW8bit` 0.50.0. Optimizer-state storage is a hardware adaptation; **not numerical/implementation equivalence to canonical FP32 Adam**.',
        '- Each Student independently starts from clean canonical Llama weights; 20,000 method-specific QA examples, three epochs / 7,500 steps, effective batch 8, maximum sequence 1,024, LR 1e-5, cosine schedule, 225 warmup updates, seed 42, weight decay 0, original chat template and assistant-response masking.',
        '- Paraphraser: canonical Qwen2.5-3B-Instruct with recorded ModelScope provenance; temperature .7, top-p .9, seed 42, length min64 / multiplier1.5 / cap1536. Frozen prompt SHA `085a77a7a32d06f31ec4a11a23977517fef64eee794817a5a1a9ed51a1e45676`. Method-specific Teacher outputs remain separate.',
        '- Bc: same-tokenizer full-vocabulary logits, T=2, CE=.5 and T²KL=.5, all shifted supervised response positions. FP32 forward output is selected then cast to canonical BF16 cache storage (serialization compatibility fix). No top-k approximation.',
        '- Utility: ARC-Challenge normalized accuracy (1,172 examples) and TruthfulQA-MC2 (817), using the recorded evaluator/config. Clean Llama reference: ARC 36.60409556%, MC2 45.75471579%.','',
        '## PN-FP Teacher selection','',
        'Frozen 1,024 fingerprints: key16 / response1, Perinucleus t=.8, k=3, seed42. WA=.75 trajectory reached best fresh-reload 334/1024 (32.6171875%) and later collapsed to 0/1024. WA=.50 pilot reached 654/1024 (63.8671875%). The WA=.50 extension selected call21 / non-zero update19: fresh-reload **804/1024 (78.515625%)**, with DM=.25. It stopped after update22 because three checks failed to improve materially. Final loss<.005 was not used to claim convergence.',
        'The original extension assessment remained `EXTENSION_COMPLETE_NOT_PREFERRED` because its automatic ≥80% candidate gate was not met. The user subsequently **accepted this 804/1024 checkpoint as the unique formal Teacher** and authorized distillation. The old assessment is historical, not the current selection status. See `preferred_teacher_selection.json`; no historical measurement is overwritten.',
        'The extension restored Adam history by deterministic replay from clean initialization, matched 291 checkpoint tensors bitwise at the extension boundary, then continued; original optimizer-state files were not independently retained/hashed. Teacher parameters: BF16 full FT, WA=.50, DM=.25, 8-bit AdamW; frozen fingerprints were not regenerated.','',
        '## Unified measured results','',
        '| Method | Condition | Native ownership score | Detected / retention vs Teacher | ARC-Challenge | TruthfulQA-MC2 |',
        '|---|---|---|---|---:|---:|']
    for x in rows:
        score=f"{x['hits']}/1024 ({100*x['recall']:.6f}%)" if x['method']=='PN-FP' else f"{x['score']:.16f}"
        decision=f"{100*x['retention']:.6f}% retention" if x['method']=='PN-FP' else ('Yes' if x['detected'] else 'No')
        lines.append(f"| {x['method']} | {x['condition']} | {score} | {decision} | {100*x['arc']:.6f}% | {100*x['truthfulqa']:.6f}% |")
    lines+=['','PN-FP retention is hits / 804, not raw recall. AWM uses native weight-space similarity with strict score > frozen threshold; the metrics must not be compared numerically across methods. PN-FP Logit retains **144/1024 = 14.0625% recall / 17.910448% of Teacher hits**, higher than Direct and Paraphrase but far below the Teacher.','',
        '## AWM calibration and cache evidence','',
        'Reference self/reload score=1.0. Canonical all-layer Wq/Wk extraction, vocabulary/dimension alignment, full layer matching where required, and unbiased linear CKA are unchanged. Official source commit `bc20ff8e63cec57f5da422ae065686ced275e76d`.']
    for x in cal['negatives']:lines.append(f"- {x.get('model')}: {x['score']:.17g}")
    lines+=['','Frozen threshold **0.007566815861277831 = max of these three fixed negative scores**; ties are negative. Calibration SHA `627107dc6c7db1569a43c2f94f67b5e7f9314bdcd2968c36f288f07b83b47a3f` was frozen before Student training and remains unchanged.',
        f"AWM cache: 157/157 shards, 520,187 supervised positions, full vocabulary32,000, BF16; {cache['payload_bytes']:,} bytes. Shard hashes/manifest were verified; reproducible raw logits were deleted only after all final Students/results were verified. Dataset, manifests and final models remain. Paraphrase:20,000 successes, {para['retry_count']} retries, zero identity fallback; no scientific changes.",
        '', '## Runtime and memory','',
        '| Method | Student | Training-summary seconds | Whole training subprocess seconds | Peak allocated GPU GiB | Peak sampled GPU GiB | Peak host RSS GiB |',
        '|---|---|---:|---:|---:|---:|---:|']
    for x in runtime:lines.append(f"| {x['method']} | {x['condition']} | {x['training_summary_s']:.3f} | {x['subprocess_wall_s']:.3f} | {x['peak_allocated_GiB']:.3f} | {x['peak_sampled_GPU_GiB']:.3f} | {x['peak_RSS_GiB']:.3f} |")
    lines+=['','The two runtime definitions differ: the subprocess includes loading/preparation/exit overhead. RSS comes from the process high-water mark; GPU sampling and PyTorch allocated peaks measure different quantities and are not interchangeable.',
        'Teacher extension training-loop wall=1600.345s; whole training process including replay/trajectory/utility=1709.475s; final standalone detector=22.651s. Peak allocated51.373GiB, sampled52.618GiB, processRSS29.418GiB, cgroup78.028GiB. AWM calibration subprocess time including the preserved, repaired Phi3 loader attempt=192.30s; this is not watermark training. Its reported 2.390GiB aggregate GPU peak includes sampling, unlike the allocated-only Student column.',
        '', '## Artifact verification and project consistency','',
        'Full final-file SHA lists: `results/scale_7b_final_audit/verification_inputs.json`; fresh CPU-only remote verification: `verification_final.json`. The final model identity is the complete per-file manifest, not a fabricated single checkpoint hash. Runtime table manifest paths and manifest SHA256 are in `unified_results.json`.',
        'PN-FP Teacher and six final Students are kept separately; clean reference is unchanged. LLMPrint58 completed GCG fingerprints and all13 negative-model directories are preserved and checked against their original manifests. No LLMPrint restart, cross-lineage execution, model/data download, or experiment rerun is part of this audit.',
        'Same-lineage 3B results are historical references and were not changed. Project status/TODO/decisions/logs now point to this scale-extension summary. Old failure/pilot/initial no-shutdown entries are historical; they are not new execution instructions.',
        '', '## Limitations and bounded conclusion','',
        'In this **7B same-backbone extension for PN-FP and AWM**, PN-FP ownership hits decrease strongly after response distillation; Logit has higher retention than Direct/Paraphrase but still substantially fewer hits than the Teacher. AWM native weight-space scores remain near1.0 after all three training conditions.',
        'These are single-seed, method-specific endpoint observations, not significance tests or universal active/passive claims. The two methods use different Teacher/data conditions and different native metrics. Every Student begins from the same pretrained backbone lineage; near-reference AWM scores may reflect initialization/parameter similarity, not causal transmission of a new ownership signal. Utility ARC increases versus clean while MC2 declines; the two benchmarks do not prove global utility preservation. This is not all passive methods, all active methods, all7Bmodels, or a cross-lineage evaluation.',
        '', 'Primary reports: [PN-FP](pnfp_7b_distillation_6004_final.md), [Teacher trajectory/extension](pnfp_7b_wa050_extension_20260919.md), [AWM](awm_7b_extension.md).']
    (P/'docs/reproduction_reports/7b_scale_extension_final_summary.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('Derived 8 result rows and 6 runtime rows from immutable saved receipts')
if __name__=='__main__':main()
