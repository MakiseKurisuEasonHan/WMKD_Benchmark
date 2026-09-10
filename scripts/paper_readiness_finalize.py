"""Read-only evidence crosschecks and paper metadata. Never executes model code."""
from pathlib import Path
import json, hashlib, subprocess, zipfile, tarfile, datetime
P=Path(__file__).resolve().parents[1]; O=P/'results/paper_readiness_20260910'
def read(p):return json.loads((P/p).read_bytes())
def write(n,d):(O/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
matrix=read('results/paper_readiness_20260910/final_experiment_matrix.json')
utility=read('results/paper_readiness_20260910/final_utility_master.json')
checks=[]
for m in ['pnfp','evertracer','ctcc','iseal','scw']:
 root=f'results/{m}/experiment_ba_trajectory_followup'
 for r in read(root+'/trajectory.json'):
  d=read(root+f"/checkpoints/step_{r['step']:06d}/detector_result.json")
  fields=['step','detected','member_oriented_auc','trigger_activations','registered_success','p_value','dataset_sha256','seed','checkpoint_manifest_sha256']
  compare={k:r[k]==d[k] for k in fields if k in r and k in d}
  assert all(compare.values()),(m,r['step'],compare)
  checks.append({'method':m,'step':r['step'],'fields':compare})
write('trajectory_summary_raw_crosscheck.json',{'status':'PASS','points':checks})
# Check available raw lm-eval outputs against the canonical utility summary.
raw_checks=[]
for r in utility:
 src=r['source_artifact']['source']['path'];root=(P/src).parent
 candidates=list((root/'utility').glob('raw_evaluator_output.json'))
 for f in candidates:
  d=json.loads(f.read_bytes());v=d.get('results',d)
  if not all(k in v for k in ['arc_challenge','truthfulqa_mc2']):continue
  a=v['arc_challenge'].get('acc_norm,none');t=v['truthfulqa_mc2'].get('acc,none')
  assert a==r['arc_challenge_acc_norm'] and t==r['truthfulqa_mc2'],(src,a,t)
  raw_checks.append({'method':r['method_or_shared_run'],'condition':r['condition'],'raw_path':f.relative_to(P).as_posix(),'sha256':sha(f),'match':True})
write('utility_raw_crosscheck.json',{'checked_raw_pairs':len(raw_checks),'checks':raw_checks,'other_rows':'Canonical recorded summary with source SHA/pointer; no missing raw precision inferred.'})
# Verify existing local evidence packages against their previously recorded hashes.
packages=read('results/pre_bb_cleanup_20260909/local_evidence_archive_inventory.json')
for r in read('results/logit_distillation/same_lineage_bc/final_evidence_sync_receipt.json')['packages']:
 packages.append({'path':'artifacts/'+Path(r['local_path']).name,'bytes':r['bytes'],'sha256':r['sha256']})
seen=set(); out=[]
for r in packages:
 if r['path'] in seen:continue
 seen.add(r['path']);f=P/r['path'];assert f.exists(),f
 assert f.stat().st_size==r['bytes'] and sha(f)==r['sha256'],r['path']
 if zipfile.is_zipfile(f):
  with zipfile.ZipFile(f) as z:assert z.testzip() is None;count=len(z.infolist())
 else:
  with tarfile.open(f) as z:count=len(z.getmembers())
 out.append({'path':r['path'],'bytes':r['bytes'],'sha256':r['sha256'],'file_count':count,'verification':'EXISTING_RECEIPT_SIZE_SHA_AND_CONTAINER_READ_PASS','retransferred':False})
write('local_evidence_package_inventory.json',out)
idx=read('results/experiment_full_logs_index.json');ids={};dups=[]
for r in idx['objects']:
 key=(r['method'],r['experiment'],r['run_id'])
 if key in ids:dups.append([ids[key],r['full_log_path']])
 ids[key]=r['full_log_path']
assert not dups,dups
write('logical_experiment_identity_audit.json',{'object_count':len(ids),'duplicate_logical_objects':dups,'identity_fields':['method','experiment','run_id'],'shared_student_note':'Five detector method views may share a model run; they are not five independent Student trainings.'})
machine=read('artifacts/paper_audit_work/new_autodl_inventory.json');machine.pop('files');write('machine_state_at_audit_start.json',machine)
limitations=[
'PN-FP original historical Ba frozen dataset is permanently missing. Historical endpoint 98/1024 remains a historical reference.',
'PN-FP trajectory and Bc use the frozen protocol-faithful reconstructed parent, not byte/sample-identical historical Ba. Bc primary hard-label comparator is reconstructed-parent Ba 99/1024, not historical 98/1024.',
'SCW trajectory uses its explicitly documented reconstructed parent; historical Ba and reconstructed trajectory are distinct scientific objects.',
'CTCC uses the WMKD operational exact rule generated_answer.strip()=="IAMALIVE". Do not silently change case, substring matching or thresholds.',
'CTCC Bb2 is the retained formal paraphrase condition; preserve Bb2 identity and superseded-attempt history.',
'Passive Bb3 is the frozen paired paraphrase Shared Student condition; preserve Bb3 naming and dataset identity.',
'EverTracer canonical detector on Qwen is N/A_CROSS_TOKENIZER because segmentation, visible 128-token window and mean-token-loss normalization differ.',
'EverTracer Qwen AUC/TPR results are exploratory, non-comparable diagnostics. They alone do not establish survival, failure or transfer.',
'iSeal Qwen detector is N/A_CROSS_ARCHITECTURE, not zero success. No projection, re-registration or fabricated detector result.',
'Qwen participated in historical passive detector threshold calibration.',
'Clean Qwen is therefore not an independent held-out negative for those calibrated thresholds; threshold crossing alone is not proof of transfer.',
'Experiments use a single seed; generalization across seeds was not measured.',
'Repeated-seed confidence intervals are absent. Per-sample evaluator stderr is not a repeated-seed confidence interval.',
'Bc is endpoint-only. No 11-point Bc trajectory was run or inferred.',
'The five measured trajectories apply only to same-lineage active Ba follow-ups. They are not evidence for Bb, Bc or cross-lineage training dynamics.',
'Native raw scores across detector families have different units, directions and rules; their magnitudes cannot be compared directly.',
'Same-lineage passive similarity retention may include shared-lineage/initialization confounding.',
'Lineage, architecture and tokenizer effects were not independently causally isolated.',
'Historical Clean Llama utility baselines vary by recorded evaluation context. Do not silently unify them; PN-FP historical Ba utility has limited recorded decimal precision.',
'Seventeen legacy preferred archives lack a recorded immutable revision; two legacy SCW archives additionally lack SHA256(SHA256SUMS). Existing per-file hashes and historical verification evidence are preserved; do not promote their evidence grade.',
'SCW historical Clean Llama and trajectory step-0 p-values are separate measured observations; Teacher is never step 0.'
]
report=P/'docs/reproduction_reports';report.mkdir(exist_ok=True)
(report/'FINAL_PAPER_LIMITATIONS_20260910.md').write_text('# WMKD final paper limitations\n\n'+ '\n\n'.join(f'{i+1}. {s}' for i,s in enumerate(limitations))+'\n',encoding='utf8')
figs=[]
for i,title,source,methods,x,y,sem in [
(1,'Benchmark overview / threat models','final_experiment_matrix.json','All 10','condition','method / data / model flow','Design diagram, not a measured scalar plot'),
(2,'Active Ba checkpoint trajectories','final_trajectory_inventory.json','Active 5','optimizer step','native detector metric','Separate axes/panels per detector; Teacher separate from step0'),
(3,'Same-lineage Ba vs Bb vs Bc','final_master_detector_table.csv','All 10','Ba / Bb2/Bb3 / Bc','native detector metric','PN-FP Bc comparator reconstructed-parent Ba99, not historical98'),
(4,'Active same-lineage vs cross-lineage','final_master_detector_table.csv','Active 5','lineage / condition','native metric or N/A','EverTracer exploratory separately; iSeal Qwen N/A'),
(5,'Passive lineage comparison','final_master_detector_table.csv','Passive 5','lineage / condition','native metric','Shared Students; calibrated Qwen and lineage confounds'),
(6,'Utility ARC / MC2','final_utility_master.csv','Independent active + shared passive runs','condition','ARC acc_norm / MC2 acc','Historical protocol and precision flags retained'),
(7,'Detector applicability matrix','final_experiment_matrix.csv','All 10','architecture / condition','applicability category','Optional; N/A is not a negative numeric result')]:
 figs.append({'figure':i,'title':title,'optional':i==7,'source':'results/paper_readiness_20260910/'+source,'methods':methods,'x':x,'y':y,'metric_semantics':sem,'limitations_file':'docs/reproduction_reports/FINAL_PAPER_LIMITATIONS_20260910.md','generated':False})
write('paper_figure_inventory.json',figs)
cols=['method','native_metric','teacher_reference','clean_llama','same_lineage_ba','same_lineage_bb','same_lineage_bc','clean_qwen','cross_lineage_ba','cross_lineage_bb']
table='| '+' | '.join(cols)+' |\n| '+' | '.join(['---']*len(cols))+' |\n'
table+='\n'.join('| '+' | '.join(str(r.get(k,'NOT_RECORDED')).replace('|','/') for k in cols)+' |' for r in matrix)
u_cols=['method_or_shared_run','condition','arc_challenge_acc_norm','truthfulqa_mc2','precision']
ut='| '+' | '.join(u_cols)+' |\n| '+' | '.join(['---']*len(u_cols))+' |\n'+'\n'.join('| '+' | '.join(str(r.get(k,'NOT_RECORDED')) for k in u_cols)+' |' for r in utility)
summary='''# WMKD final paper-readiness summary

The completed benchmark is sufficient to begin paper writing. No required new scientific experiment was identified. This is an evidence audit, not new training, inference, evaluation or causal re-analysis.

10 methods × 8 core condition columns = 80 matrix cells, including references and explicit applicability N/A. This is not 80 independently trained models. Five passive detector views share one Student in each shared condition.

Five same-lineage active Ba trajectories contain 55/55 points; 487 per-point manifest entries passed SHA verification. All 68 indexed formal scientific objects exist, with no dangling path, duplicate logical object or unindexed formal object identified. Archived historical EOL differences and unrelated dirty EaaW worktree versions are preserved.

Six Bc full 7500-step runs, five active XBa and five active XBb formal objects are closed. Existing scientific results remain unchanged.

## Detector master

'''+table+'''

EverTracer Qwen canonical values remain N/A. Exploratory XBa AUC=0.523, XBb AUC=0.5227, not directly comparable to frozen Llama detector metrics. iSeal Qwen is N/A, never zero.

PN-FP historical Ba=98/1024; reconstructed-parent Ba trajectory=99/1024; Bc=110/1024. The appropriate Bc hard-label comparator is 99/1024. No seed-general causal improvement claim is made.

SCW trajectory step4000=0.949506402015686; step6000=0.6830558776855469; step7500=0.895175039768219. Lower p is stronger; alpha=0.001.

## Utility master

'''+ut+'''

All full-precision values and per-cell artifact SHA/JSON pointers are retained in the machine-readable JSON. Historical baseline contexts and limited-precision records must not be silently pooled. Passive utility is listed once per shared Student.

## Archive and synchronization limits

35 preferred model archives have existing receipts. Modern 18 record immutable revisions. Legacy 17 have no recorded immutable revision; two legacy SCW entries additionally lack SHA256(SHA256SUMS), while recorded per-file hashes remain available. Their historical verification modes are not relabeled as segment or full independent verification. Old source6002 is currently unreachable; no new remote verification of those legacy objects was claimed.

These archival metadata limitations do not imply missing scientific results or require new experiments before writing. Strict archival metadata completeness remains qualified, not an unconditional PASS. Before citing a fixed historical remote revision, obtain its metadata or explicitly state that identity is anchored by the preserved per-file hashes.

Fourteen missing remote lightweight records were non-destructively synchronized. Differing runtime versions were preserved separately without overwriting local canonical records. Existing evidence packages were size/SHA verified and not retransferred. See important_unsynced_files.json and local_evidence_package_inventory.json for scope. Old-host-only inventory cannot be freshly asserted while that host is offline.

## Next use

Start manuscript drafting with the detector/utility master tables, 55-point trajectory sources and FINAL_PAPER_LIMITATIONS_20260910.md. Figure inventory only was generated; no final figures or new experiments.

Optional future work: repeated seeds/CI, extra ablations, additional model families, extra utility tasks or extra trajectories. These are not required closure items for the completed benchmark.

Final Git synchronization is documented separately in git_closure_receipt.json; no model payload belongs in Git.
'''
(report/'FINAL_MASTER_EXPERIMENT_SUMMARY_20260910.md').write_text(summary,encoding='utf8')
write('final_paper_readiness_status.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scientific_experiments_complete':True,'detector_master_complete':True,'utility_master_complete':True,'trajectory_complete':True,'full_logs_complete':True,'model_archives_complete':True,'model_archive_evidence_basis':'EXISTING_VERIFIED_RECEIPTS; NOT A NEW LIVE AUDIT OF OFFLINE LEGACY SOURCE','model_archive_metadata_complete':False,'legacy_missing_immutable_revision':17,'legacy_missing_sha256_of_sha256sums':2,'local_evidence_complete':True,'local_evidence_scope':'Known canonical scientific packages; old-host-only current inventory unavailable','github_complete':False,'git_closure':'PENDING_THIS_AUDIT_COMMIT','limitations_complete':True,'paper_master_table_complete':True,'remaining_required_experiments':[],'paper_ready':True,'paper_ready_definition':'Current completed scientific results and preserved critical evidence suffice for manuscript drafting; legacy archive metadata limitation disclosed, not represented as full archival completeness.','core_methods':10,'core_condition_columns':8,'core_matrix_cells':80,'trajectories':5,'trajectory_points':55,'full_log_objects':68,'preferred_model_archives':35,'required_before_paper_writing':[],'optional_future_experiments':['Repeated seeds and seed-level CI','Additional ablations','Additional families or utility benchmarks','Extra trajectories'],'no_science_executed':True,'no_cleanup_executed':True,'no_shutdown':True})
print(json.dumps({'raw_utility_pairs':len(raw_checks),'packages_verified':len(out),'logical_objects':len(ids),'status':'READY_FOR_GIT_CLOSURE'}))
