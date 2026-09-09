"""Read existing evidence only; never run models or delete files."""
import pathlib,json,hashlib,subprocess,sys,csv,datetime
P=pathlib.Path(sys.argv[1]).resolve();O=P/'results/pre_bb_cleanup_20260909';O.mkdir(exist_ok=True)
HOST=sys.argv[2];METHODS=['pnfp','evertracer','ctcc','iseal','scw'];STEPS=[0,25,50,100,250,500,1000,2000,4000,6000,7500]
def get(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8<<20),b''):h.update(b)
 return h.hexdigest()
def put(n,d):(O/n).write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def git(*a):return subprocess.check_output(['git',*a],cwd=P)
tracked=set(git('ls-tree','-r','--name-only','HEAD').decode().splitlines())
idx=get(P/'results/experiment_full_logs_index.json');entries=idx['objects'];paths=[x['full_log_path'] for x in entries]
checks=[]
for x in entries:
 f=P/x['full_log_path'];c=dict(path=x['full_log_path'],exists=f.is_file(),expected_sha256=x['full_log_sha256'],method=x.get('method'),experiment=x.get('experiment'))
 if f.is_file():
  c.update(actual_sha256=sha(f),json_valid=isinstance(get(f),dict),github_tracked=c['path'] in tracked)
  c['sha_match']=c['actual_sha256']==c['expected_sha256']
  if not c['sha_match']:c['committed_sha_match']=hashlib.sha256(git('show','HEAD:'+c['path'])).hexdigest()==c['expected_sha256']
 checks.append(c)
unindexed=[]
for f in (P/'results').rglob('full_experiment_log.json'):
 n=f.relative_to(P).as_posix()
 if n not in paths:
  d=get(f);unindexed.append(dict(path=n,status=d.get('status'),identity=d.get('identity'),run_id=d.get('run_id'),historical_snapshot=any(s in n for s in ['snapshot','history_','worker_closure','trajectory_followup/pnfp_'])))
put(HOST+'_full_log_audit.json',dict(total_indexed=len(entries),missing_full_log=sum(not x['exists'] for x in checks),duplicate_index_paths=len(paths)-len(set(paths)),sha_mismatches=[x for x in checks if x.get('sha_match') is False],checks=checks,unindexed_candidates=unindexed))
rows=[];manifest=[]
for m in METHODS:
 q=P/'results'/m/'experiment_ba_trajectory_followup';t=get(q/'trajectory.json');full=get(q/'full_experiment_log.json');issues=[];points=[]
 for row in t:
  step=row['step'];s=q/'checkpoints'/f'step_{step:06d}';required=['detector_raw.json','detector_result.json','checkpoint_metadata.json','checkpoint_file_manifest.json','evidence_sha_manifest.json']
  missing=[n for n in required if not (s/n).is_file()];raw=get(s/'detector_raw.json') if not missing else {}
  dr=get(s/'detector_result.json') if not missing else {}
  point=dict(step=step,missing=missing,trajectory_matches_result=row==dr,errors=row.get('detector_errors'),metric=row,raw_keys=list(raw) if isinstance(raw,dict) else [],raw_list_lengths={k:len(v) for k,v in raw.items() if isinstance(v,list)} if isinstance(raw,dict) else {})
  if m=='scw':
   f=s/'generations.jsonl';point['generation_rows']=sum(1 for line in f.open(encoding='utf-8') if json.loads(line)) if f.exists() else 0
  if missing or row!=dr or row.get('detector_errors')!=0:issues.append(point)
  points.append(point)
 present=[r['step'] for r in t]
 csvsteps=[int(r['step']) for r in csv.DictReader((q/'trajectory.csv').open(encoding='utf-8'))]
 assert csvsteps==present,(m,'CSV steps mismatch')
 for f in q.rglob('*'):
  if f.is_file() and f.suffix not in ['.safetensors','.pt','.bin','.lock']:
   manifest.append(dict(path=f.relative_to(P).as_posix(),bytes=f.stat().st_size,sha256=sha(f),github_tracked=f.relative_to(P).as_posix() in tracked))
 row=dict(method=m,expected_steps=STEPS,present_steps=present,missing_steps=sorted(set(STEPS)-set(present)),raw_detector_evidence='PASS' if not issues else 'ISSUES',trajectory_json=True,trajectory_csv=True,plotting_csv=(q/'plotting_ready.csv').exists(),full_log=(q/'full_experiment_log.json').relative_to(P).as_posix() in paths,provenance=(q/'provenance_manifest.json').exists(),local_copy=HOST=='local',github_copy=all((q/n).relative_to(P).as_posix() in tracked for n in ['trajectory.json','trajectory.csv','plotting_ready.csv','full_experiment_log.json']),archive_copy='PENDING_NEW_EVIDENCE_PACKAGE',safe_to_delete_checkpoint_weights=False,notes='Weights retained until final-model archive and evidence sync independently verified',issues=issues,points=points,fresh_reload_matches=full.get('fresh_reload_matches'),final_model_path=full.get('final_model_path'),report=full.get('report'))
 rows.append(row)
put(HOST+'_trajectory_audit.json',rows);put(HOST+'_trajectory_file_manifest.json',manifest)
receipts=[]
for f in (P/'results').rglob('*modelscope*.json'):
 try:d=get(f)
 except Exception:continue
 if isinstance(d,dict):receipts.append(dict(path=f.relative_to(P).as_posix(),sha256=sha(f),status=d.get('status'),repo=d.get('repo',d.get('repo_id')),revision=d.get('revision',d.get('remote_revision')),archive_sha256=d.get('archive_sha256'),verification_mode=d.get('verification_mode',d.get('remote_verification'))))
put(HOST+'_modelscope_receipt_inventory.json',receipts)
put(HOST+'_audit_summary.json',dict(head=git('rev-parse','HEAD').decode().strip(),indexed=len(entries),trajectory_methods=len(rows),trajectory_issues=sum(len(r['issues']) for r in rows),trajectory_files=len(manifest),untracked_trajectory_files=sum(not r['github_tracked'] for r in manifest),time=datetime.datetime.now(datetime.timezone.utc).isoformat()))
print(json.dumps(get(O/(HOST+'_audit_summary.json'))))
