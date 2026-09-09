"""CPU metadata closure after all five independently verified archives."""
import hashlib
import json
import pathlib
import shutil
import datetime

P=pathlib.Path('/root/autodl-tmp/WMKD_Benchmark')
E=P/'results/active_cross_lineage_ba'
ORDER=['pnfp','ctcc','evertracer','iseal','scw']

def get(p):return json.loads(p.read_text())
def put(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
 summary=get(E/'model_archive_summary.json');assert summary['status']=='COMPLETE'
 rows=get(E/'master_comparison.json');retention=get(E/'model_retention_recommendations.json')
 index=get(P/'results/experiment_full_logs_index.json')
 archives={}
 for m in ORDER:
  q=E/m;r=get(q/'modelscope_archive.json')
  assert r['status']=='COMPLETE' and r['visibility']=='PRIVATE' and r['remote_verification'] in ['PASS_ALL_FILES_SIZE_AND_SHA','REMOTE_MANIFEST_AND_SEGMENT_VERIFICATION_PASS']
  assert all(x['match'] for x in r['files'].values())
  if r['remote_verification']=='PASS_ALL_FILES_SIZE_AND_SHA':
   r.update(verification_mode='FULL_INDEPENDENT_DOWNLOAD',verification_status='PASS',full_independent_download_sha_verified='PASS',full_remote_download_performed=True)
   r.setdefault('segment_count',0);r.setdefault('segment_matches',0);r.setdefault('reason_if_full_download_triggered','Existing full verification retained; user CTCC exception' if m=='ctcc' else 'Existing full verification retained')
  else:
   assert r['remote_manifest_verification']=='PASS' and r['segment_count']==r['segment_matches']==10 and not r['full_remote_download_performed']
  put(q/'modelscope_archive.json',r)
  pre=get(E/'archive'/f'{m}_preflight.json');source=pathlib.Path(pre['package'])
  meta=E/'archive'/m;meta.mkdir(exist_ok=True)
  for n in ['manifest.json','README.md','LICENSE','SHA256SUMS']:shutil.copy2(source/n,meta/n)
  prov=get(q/'model_provenance.json');prov['modelscope_archive']=r;put(q/'model_provenance.json',prov);full=get(q/'full_experiment_log.json')
  full.update(model_provenance=prov,modelscope_archive=r,archive_status='COMPLETE_PRIVATE_REMOTE_VERIFIED',preferred_final_model=True)
  full['final_closure']['archive']='COMPLETE_PRIVATE_REMOTE_VERIFIED'
  full['final_closure']['archive_git_receipt']='results/active_cross_lineage_ba/archive/final_git_receipt.json'
  c=get(q/'closure_summary.json');c.update(modelscope_archive=r,preferred_final_model=True,archive_status='COMPLETE_PRIVATE_REMOTE_VERIFIED');put(q/'closure_summary.json',c)
  full['closure_summary']=c
  put(q/'full_experiment_log.json',full)
  for x in index['objects']:
   if x['full_log_path']==f'results/active_cross_lineage_ba/{m}/full_experiment_log.json':
    x.update(full_log_sha256=sha(q/'full_experiment_log.json'),modelscope_repo=r['repo'],modelscope_revision=r['revision'],modelscope_archive_sha256=r['archive_sha256'],preferred_final_model=True)
  compact={k:r[k] for k in ['repo','revision','archive_sha256','file_count','total_bytes','remote_verification','uploaded_at','verified_at','verification_mode','verification_status','segment_count','segment_matches','full_remote_download_performed','reason_if_full_download_triggered']}
  archives[m]=compact
  for x in rows:
   if x['method']==m:x.update(preferred_final_model=True,model_archive=compact)
  for x in retention:
   if x['method']==m:
    x.update(preferred_final_model=True,already_archived_elsewhere=r['repo']+'@'+r['revision'],archive_status='COMPLETE_PRIVATE_REMOTE_VERIFIED',approved_preferred_archive=True,model_archive=compact,recommended_preferred_archive='APPROVED_AND_ARCHIVED',duplicate_weight_check='ACCOUNT_MODEL_REPO_INVENTORY_PASS; ONE_PER_EXPERIMENT')
    x['weight_manifest'].update(sha256=sha(q/'model_provenance.json'),bytes=(q/'model_provenance.json').stat().st_size)
  report=P/full['report'];text=report.read_text();marker='\n## Preferred model archive — 2026-09-09\n'
  assert marker not in text
  report.write_text(text+marker+'\nUser explicitly approved preferred retention for reproducibility. This does not upgrade the detector verdict.\n\n'+json.dumps(compact,indent=2)+'\n')
 index['generated_at']=datetime.datetime.now(datetime.timezone.utc).isoformat();put(P/'results/experiment_full_logs_index.json',index)
 put(E/'master_comparison.json',rows);put(E/'model_retention_recommendations.json',retention)
 import csv
 with (E/'master_comparison.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader()
  for r in rows:w.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(dict,list)) else v for k,v in r.items()})
 report=P/'docs/reproduction_reports/active_cross_lineage_ba_final_20260909.md'
 text=report.read_text();marker='\n## 五个 preferred model 的最终私有归档（2026-09-09）\n';assert marker not in text
 lines=['\n用户已独立批准五个final Student为preferred reproducibility artifact；该批准不改变detector结论。此前“等待模型选择/未上传”文字是归档前历史状态，现由本节覆盖。',
 '| 方法 | PRIVATE repo | immutable revision | SHA256(SHA256SUMS) | files | bytes |', '|---|---|---|---|---:|---:|']
 for m,r in archives.items():lines.append(f"| {m} | {r['repo']} | {r['revision']} | {r['archive_sha256']} | {r['file_count']} | {r['total_bytes']} |")
 lines+=['\n各模型证据等级见 verification_mode：PNFP/CTCC 保留完整独立下载逐文件 SHA 验证；后续模型默认 manifest 加固定位置 segment 验证，异常才升级 full download。分段验证不代表100%远端字节经过独立重下载。源final model和硬链接源包均保留。没有落地大型验证副本，没有删除任何模型。',
 '账户23个model仓库在上传前无匹配权重分片；每个实验只创建一个preferred archive。远端自动生成的.gitattributes/.mdlignore如存在，也另行下载验证并记录。',
 '模型来源Git为d8a445735c1625ada4440eb7b2e8ae7b43eac703；归档metadata Git闭环SHA见archive/final_git_receipt.json。shutdown_provenance仍UNVERIFIED。']
 lines.append('\nVerification details:\n```json\n'+json.dumps(archives,indent=2,ensure_ascii=False)+'\n```')
 report.write_text(text+marker+'\n'.join(lines)+'\n')
 summary['methods']={m:get(E/m/'modelscope_archive.json') for m in ORDER}
 summary.update(archives=archives,scientific='COMPLETE',evidence='COMPLETE',model_archival='COMPLETE',git_metadata_closure='PENDING',no_models_deleted=True);put(E/'model_archive_summary.json',summary)
 for n in ['pipeline_state.json','final_campaign_status.json']:
  d=get(E/n);d.update(status='MODEL_ARCHIVAL_COMPLETE_GIT_METADATA_CLOSURE_PENDING',model_archival='COMPLETE',preferred_model_selection='APPROVED_ALL_FIVE',next_action='Archive metadata Git closure only; no new experiment.',auto_shutdown=False,shutdown_armed=False);put(E/n,d)
 for m in ORDER:
  q=E/m;files=[]
  for f in sorted(q.rglob('*')):
   if f.is_file() and f.name!='evidence_sha256.json':files.append(dict(path=f.relative_to(P).as_posix(),bytes=f.stat().st_size,sha256=sha(f)))
  put(q/'evidence_sha256.json',dict(scope='After user-approved preferred model archival; excludes self',files=files))
 f=E/'final_evidence_manifest.json';d=get(f)
 for x in d['files']:
  p=P/x['path'];x.update(bytes=p.stat().st_size,sha256=sha(p))
 d['archive_receipts']={m:dict(path=f'results/active_cross_lineage_ba/{m}/modelscope_archive.json',sha256=sha(E/m/'modelscope_archive.json')) for m in ORDER};put(f,d)
 print(json.dumps(archives))

if __name__=='__main__':main()
