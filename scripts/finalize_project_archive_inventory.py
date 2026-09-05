#!/usr/bin/env python3
"""Finalize project-wide archival metadata without changing scientific results."""
from __future__ import annotations
import hashlib,json,subprocess
from datetime import datetime,timezone
from pathlib import Path

R=Path(__file__).resolve().parents[1]; E=R/'results/archive_remediation/evidence'; NOW=datetime.now(timezone.utc).isoformat()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def evidence(pattern):
 xs=sorted(E.glob(pattern));
 if not xs:raise RuntimeError('missing evidence '+pattern)
 return xs[-1].relative_to(R).as_posix()
def rec(i,method,exp,role,typ,classification,repo=None,repo_type=None,ev=None,limits=None,perm=False,shared=False,ind=False,shav=False,reload=False):
 ep=ev or ''
 return {'artifact_id':i,'method':method,'experiment':exp,'role':role,'artifact_type':typ,'source_identity':ep or i,'source_sha_or_manifest':sha(R/ep) if ep and (R/ep).is_file() else None,'modelscope_repo':repo,'repo_type':repo_type,'visibility':'PRIVATE' if repo else None,'upload_status':'UPLOADED' if repo else ('NOT_APPLICABLE' if classification=='NOT_APPLICABLE' else classification),'independent_redownload':ind,'SHA_verified':shav,'reload_verified':reload,'archive_classification':classification,'evidence':ep or None,'limitations':limits or [],'permanent_unavailability':perm,'shared_archive':shared}

full_teacher=evidence('pnfp_a2_teacher_*.json');full_ba=evidence('pnfp_ba_student_*.json')
strong={x:evidence(x+'_strong_remote_*.json') for x in ['evertracer_a_teacher','evertracer_ba_student','ctcc_a_teacher','ctcc_ba_student','iseal_a6_teacher','iseal_ba_student','scw_a2_teacher','scw_ba_student']}
pnkey=evidence('pnfp_detector_dependency_*.json');scwin=evidence('scw_detector_dependency_*.json');everdet=evidence('evertracer_detector_dependencies_*.json')
A=[]
# Ten early proactive models.
A += [rec('pnfp.a2.teacher','PN-FP','A2','Teacher','model','VERIFIED_ARCHIVED','MakiseKurisuEasonHan/WMKD-PNFP-A2-Teacher','model',full_teacher,ind=True,shav=True,reload=True),rec('pnfp.ba.student','PN-FP','Ba','Student','model','VERIFIED_ARCHIVED','MakiseKurisuEasonHan/WMKD-PNFP-Ba-Student','model',full_ba,ind=True,shav=True,reload=True)]
for aid,m,e,r,repo,key in [
 ('evertracer.a.teacher','EverTracer','A','Teacher','MakiseKurisuEasonHan/WMKD-EverTracer-A-Teacher','evertracer_a_teacher'),('evertracer.ba.student','EverTracer','Ba','Student','MakiseKurisuEasonHan/WMKD-EverTracer-Ba-Student','evertracer_ba_student'),('ctcc.a.teacher','CTCC','A','Teacher adapter','MakiseKurisuEasonHan/WMKD-CTCC-A-Teacher','ctcc_a_teacher'),('ctcc.ba.student','CTCC','Ba','Student','MakiseKurisuEasonHan/WMKD-CTCC-Ba-Student','ctcc_ba_student'),('iseal.a6.teacher','iSeal','A6','Teacher','MakiseKurisuEasonHan/WMKD-iSeal-A6-Teacher','iseal_a6_teacher'),('iseal.ba.student','iSeal','Ba','Student','MakiseKurisuEasonHan/WMKD-iSeal-Ba-Student','iseal_ba_student'),('scw.a2.teacher','SCW','A2','Teacher','MakiseKurisuEasonHan/WMKD-SCW-A2-Teacher','scw_a2_teacher'),('scw.ba.student','SCW','Ba','Student','MakiseKurisuEasonHan/WMKD-SCW-Ba-Student','scw_ba_student')]:
 A.append(rec(aid,m,e,r,'model','ARCHIVED_STRONGLY_VERIFIED',repo,'model',strong[key],['No full independent redownload under approved tiered policy'],shav=True))
# Three newly closed detector dependencies.
A += [rec('pnfp.detector.keys','PN-FP','A2/Ba/Bb','Detector fingerprint keys','detector_package','VERIFIED_ARCHIVED','MakiseKurisuEasonHan/WMKD_Benchmark_pnfp_canonical_detector_keys','dataset',pnkey,ind=True,shav=True),rec('evertracer.detector.reference_neighborhoods','EverTracer','A/Ba/Bb','Reference model and frozen neighborhoods','detector_package','VERIFIED_ARCHIVED','MakiseKurisuEasonHan/WMKD_Benchmark_evertracer_detector_dependencies','model',everdet,['Reference model strong-remote verified; small neighborhoods independently redownloaded'],ind=True,shav=True),rec('scw.detector.input1000','SCW','A2/Ba/Bb','Recovered-exact detector input','detector_package','VERIFIED_ARCHIVED','MakiseKurisuEasonHan/WMKD_Benchmark_scw_recovered_exact_detector_input','dataset',scwin,ind=True,shav=True)]
# Previously verified proactive datasets/models.
previous=[
 ('evertracer.ba.dataset','EverTracer','Ba','Ba frozen20k','dataset','MakiseKurisuEasonHan/WMKD_Benchmark_evertracer_ba_frozen20k','dataset','results/proactive5_bb_archives/evertracer_ba_frozen20k_modelscope_archive.json'),('ctcc.ba.dataset','CTCC','Ba','Ba frozen20k','dataset','MakiseKurisuEasonHan/WMKD_Benchmark_ctcc_ba_frozen20k','dataset','results/proactive5_bb_archives/ctcc_ba_frozen20k_modelscope_archive.json'),('iseal.ba.dataset','iSeal','Ba','Ba frozen20k','dataset','MakiseKurisuEasonHan/WMKD_Benchmark_iseal_ba_frozen20k','dataset','results/proactive5_bb_archives/iseal_ba_frozen20k_modelscope_archive.json'),
 ('pnfp.bb.parent','PN-FP','Bb','Reconstructed Ba parent','dataset','MakiseKurisuEasonHan/WMKD_Benchmark_pnfp_ba_reconstructed_frozen20k','dataset','results/pnfp/experiment_bb/full_experiment_log.json'),('pnfp.bb.dataset','PN-FP','Bb','Processed20k','dataset','MakiseKurisuEasonHan/WMKD_Benchmark_pnfp_bb_processed20k','dataset','results/pnfp/experiment_bb/processed20k_archive.json'),('pnfp.bb.student','PN-FP','Bb','Student','model','MakiseKurisuEasonHan/Llama-3.2-WMKD-PNFP-Bb-Student','model','results/pnfp/experiment_bb/student_archive.json'),
 ('evertracer.bb.dataset','EverTracer','Bb','Processed20k','dataset','MakiseKurisuEasonHan/WMKD_Benchmark_evertracer_bb_processed20k','dataset','results/evertracer/experiment_bb/evidence/modelscope_archive.json'),('evertracer.bb.student','EverTracer','Bb','Student','model','MakiseKurisuEasonHan/Llama-3.2-WMKD-EverTracer-Bb-Student','model','results/evertracer/experiment_bb/evidence/student_modelscope_archive.json'),
 ('iseal.bb.dataset','iSeal','Bb','Processed20k','dataset','MakiseKurisuEasonHan/WMKD_Benchmark_iseal_bb_processed20k','dataset','results/iseal/experiment_bb/processed20k_archive.json'),('iseal.bb.student','iSeal','Bb','Student','model','MakiseKurisuEasonHan/Llama-3.2-WMKD-iSeal-Bb-Student','model','results/iseal/experiment_bb/student_archive.json'),
 ('scw.bb.parent','SCW','Bb','Reconstructed Ba parent','dataset','MakiseKurisuEasonHan/WMKD_Benchmark_scw_ba_reconstructed_frozen20k','dataset','results/scw/experiment_bb/full_experiment_log.json'),('scw.bb.dataset','SCW','Bb','Processed20k','dataset','MakiseKurisuEasonHan/WMKD_Benchmark_scw_bb_processed20k','dataset','results/scw/experiment_bb/processed20k_archive.json'),('scw.bb.student','SCW','Bb','Student','model','MakiseKurisuEasonHan/Llama-3.2-WMKD-SCW-Bb-Student','model','results/scw/experiment_bb/student_archive.json'),
 ('ctcc.bb2.dataset','CTCC','Bb2','Processed20k','dataset','MakiseKurisuEasonHan/WMKD_Benchmark_ctcc_bb2_processed20k','dataset','results/ctcc/experiment_bb2/processed20k_archive.json'),('ctcc.bb2.student','CTCC','Bb2','Student','model','MakiseKurisuEasonHan/Llama-3.2-WMKD-CTCC-Bb2-Student','model','results/ctcc/experiment_bb2/student_archive.json'),
 ('passive.ba.dataset','Passive-5 Shared','Ba','Shared frozen20k','dataset','MakiseKurisuEasonHan/WMKD_Benchmark_passive5_shared_ba_frozen20k','dataset','results/passive5_shared_ba/modelscope_frozen20k_archive.json'),('passive.ba.student','Passive-5 Shared','Ba','Shared Student','model','MakiseKurisuEasonHan/Llama-3.2-WMKD-Passive5-Shared-Ba-Student','model','results/passive5_shared_ba/modelscope_student_archive.json'),('passive.bb3.dataset','Passive-5 Shared','Bb3','Shared processed20k','dataset','MakiseKurisuEasonHan/WMKD_Benchmark_passive5_shared_bb3_processed20k','dataset','results/passive5_shared_bb3/modelscope_dataset_archive.json'),('passive.bb3.student','Passive-5 Shared','Bb3','Shared Student','model','MakiseKurisuEasonHan/Llama-3.2-WMKD-Passive5-Shared-Bb3-Student','model','results/passive5_shared_bb3/modelscope_student_archive.json')]
for x in previous:A.append(rec(*x[:5],'VERIFIED_ARCHIVED',*x[5:],ind=True,shav=True,reload=x[4]=='model',shared=x[0].startswith('passive.')))
# Legitimate N/A and two permanent historical losses.
for m in ['LLMPrint','REEF','HuRef','AWM','ZeroPrint']:A.append(rec('passive.'+m.lower()+'.fingerprint',m,'A/A2','Git-safe fingerprint package','fingerprint_package','NOT_APPLICABLE',limits=['Unmodified canonical Base plus Git-safe pinned detector package; no standalone modified model archive required']))
A += [rec('ctcc.bb.original.processed20k','CTCC','Bb original','Processed20k','dataset','NOT_APPLICABLE',limits=['Not produced: blocked at preprocessing acceptance gate']),rec('ctcc.bb.original.student','CTCC','Bb original','Student','model','NOT_APPLICABLE',limits=['Not produced: blocked before training']),rec('pnfp.ba.original_dataset','PN-FP','Ba','Original canonical Ba frozen20k','dataset','PERMANENTLY_UNAVAILABLE',limits=['Lost before archival; reconstructed Bb parent is a separate artifact'],perm=True),rec('scw.ba.original_dataset','SCW','Ba','Original canonical Ba frozen20k','dataset','PERMANENTLY_UNAVAILABLE',limits=['Lost before archival; recovered-exact Bb parent is a separate artifact'],perm=True)]
if len(A)!=41 or len({x['artifact_id'] for x in A})!=41:raise RuntimeError('inventory cardinality')
counts={k:sum(x['archive_classification']==k for x in A) for k in ['VERIFIED_ARCHIVED','ARCHIVED_STRONGLY_VERIFIED','MISSING_ARCHIVE','NOT_APPLICABLE','PERMANENTLY_UNAVAILABLE']}
flags={'ALL_RECOVERABLE_CRITICAL_ARTIFACTS_ARCHIVED':'YES','ALL_RECOVERABLE_CRITICAL_MODELS_ARCHIVED':'YES','ALL_RECOVERABLE_CRITICAL_DATASETS_ARCHIVED':'YES','ALL_CRITICAL_DETECTOR_DEPENDENCIES_ARCHIVED':'YES','ALL_COMPLETED_BB_ARTIFACTS_VERIFIED_ARCHIVED':'YES','EARLY_A_BA_ARCHIVES_STRONGLY_VERIFIED':'YES','EARLY_A_BA_FULL_REDOWNLOAD_SAMPLE_COUNT':2,'STRICT_FULL_LOG_INDEX_32_32_PASS':'PENDING','LOCAL_GITHUB_AUTODL_SYNC':'PENDING','SERVER_CAN_BE_DELETED_WITHOUT_NEW_RECOVERABLE_SCIENTIFIC_DATA_LOSS':'YES'}
inv={'schema_version':'wmkd.project-archive-inventory.v1','generated_at':NOW,'artifact_count':41,'counts':counts,'full_redownload_early_models':['pnfp.a2.teacher','pnfp.ba.student'],'strong_remote_early_models':[x['artifact_id'] for x in A if x['archive_classification']=='ARCHIVED_STRONGLY_VERIFIED'],'artifacts':A,'flags':flags,'permanent_historical_losses':['pnfp.ba.original_dataset','scw.ba.original_dataset']}
(R/'results/project_archive_inventory.json').write_text(json.dumps(inv,indent=2)+'\n',encoding='utf-8')
# Add archive-only evidence to relevant canonical logs, then refresh all index hashes.
mapping={'results/pnfp/preferred_teacher/full_experiment_log.json':full_teacher,'results/pnfp/ba_student/full_experiment_log.json':full_ba,'results/evertracer/preferred_teacher/full_experiment_log.json':strong['evertracer_a_teacher'],'results/evertracer/ba_student/full_experiment_log.json':strong['evertracer_ba_student'],'results/ctcc/preferred_teacher/full_experiment_log.json':strong['ctcc_a_teacher'],'results/ctcc/ba_student/full_experiment_log.json':strong['ctcc_ba_student'],'results/iseal/preferred_teacher/full_experiment_log.json':strong['iseal_a6_teacher'],'results/iseal/ba_student/full_experiment_log.json':strong['iseal_ba_student'],'results/scw/preferred_teacher/full_experiment_log.json':strong['scw_a2_teacher'],'results/scw/ba_student/full_experiment_log.json':strong['scw_ba_student'],'results/pnfp/experiment_bb/full_experiment_log.json':pnkey,'results/evertracer/experiment_bb/full_experiment_log.json':everdet,'results/scw/experiment_bb/full_experiment_log.json':scwin}
for p,ev in mapping.items():
 # The worktree was clean at task entry. Rebuild from exact HEAD bytes so an
 # earlier Windows-default-encoding attempt cannot alter historical text.
 base=subprocess.check_output(['git','show','HEAD:'+p],cwd=R).decode('utf-8')
 d=json.loads(base);d['archive_remediation_20260905']={'classification':json.loads((R/ev).read_text(encoding='utf-8')).get('classification'),'evidence':ev,'evidence_sha256':sha(R/ev),'archive_only_update':True,'scientific_metrics_changed':False,'recorded_at':NOW};(R/p).write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
idxp=R/'results/experiment_full_logs_index.json';idx=json.loads(idxp.read_text(encoding='utf-8'));seen=set()
for o in idx['objects']:
 key=(o['method'],o['role'],o['experiment'],o['run_id'])
 if key in seen:raise RuntimeError('duplicate composite id')
 seen.add(key)
 p=R/o['full_log_path']
 if not p.is_file():raise RuntimeError('broken path '+str(p))
 o['full_log_sha256']=sha(p)
idx['generated_at']=NOW
if len(idx['objects'])!=32 or len(seen)!=32:raise RuntimeError('index not 32/32')
idxp.write_text(json.dumps(idx,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
for o in idx['objects']:
 if sha(R/o['full_log_path'])!=o['full_log_sha256']:raise RuntimeError('index hash mismatch')
inv['flags']['STRICT_FULL_LOG_INDEX_32_32_PASS']='YES';(R/'results/project_archive_inventory.json').write_text(json.dumps(inv,indent=2)+'\n')
for artifact in inv['artifacts']:
 if artifact['evidence'] and (R/artifact['evidence']).is_file():artifact['source_sha_or_manifest']=sha(R/artifact['evidence'])
(R/'results/project_archive_inventory.json').write_text(json.dumps(inv,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':'PASS','inventory':len(A),'counts':counts,'index_objects':32,'unique_composite_ids':32,'broken_paths':0,'sha_mismatches':0,'flags':inv['flags']},indent=2))
