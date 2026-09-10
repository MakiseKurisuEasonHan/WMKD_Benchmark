"""Read existing WMKD evidence and build paper inventories. No model execution."""
from pathlib import Path
from functools import lru_cache
import json, hashlib, subprocess, datetime, re, zipfile, tarfile

P = Path(__file__).resolve().parents[1]
O = P/'results/paper_readiness_20260910'
O.mkdir(exist_ok=True)
BC = 'results/logit_distillation/same_lineage_bc'
ACTIVE = dict(pnfp='PN-FP', evertracer='EverTracer', ctcc='CTCC', iseal='iSeal', scw='SCW')
PASSIVE = dict(llmprint='LLMPrint', reef='REEF', huref='HuRef', awm='AWM', zeroprint='ZeroPrint')
STEPS = [0,25,50,100,250,500,1000,2000,4000,6000,7500]
NOW = datetime.datetime.now(datetime.timezone.utc).isoformat()
TRACKED = set(subprocess.check_output(['git','ls-files'],cwd=P).decode().splitlines())
SOURCES = {}
ISSUES = []

@lru_cache(None)
def read(path):
    p=P/path; b=p.read_bytes()
    SOURCES[path]={'path':path,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(), 'git_tracked':path in TRACKED}
    return json.loads(b)

def at(path, pointer=''):
    v=read(path)
    for key in pointer.split('/'):
        if key: v=v[int(key)] if isinstance(v,list) else v[key]
    return v

def cell(path, pointer='', value=None, derived=None):
    v=at(path,pointer) if value is None else value
    return {'value':v,'source':dict(SOURCES[path]),'json_pointer':'/'+pointer,'derivation':derived}

def write(name,obj):
    (O/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

def nodes(x, prefix=''):
    if isinstance(x,dict):
        yield prefix,x
        for k,v in x.items():
            if k not in ['samples','rows','raw_generations','permutation_indices','raw_outputs']:
                yield from nodes(v,prefix+'/'+k)
    elif isinstance(x,list):
        for i,v in enumerate(x):yield from nodes(v,prefix+'/'+str(i))

def first_field(d, key):
    return next((v[key] for _,v in nodes(d) if key in v),None)

def unwrap(d):
    return d.get('result',d)

def active_value(m,d):
    if m=='pnfp':return d['detected']
    if m=='evertracer':return first_field(d,'member_oriented_auc')
    if m=='ctcc':
        if 'trigger' in d:return d['trigger']['activations']
        return first_field(d,'categories')['trigger']['activations']
    if m=='iseal':return sum(x['teacher_positive'] for x in d['registered']['rows'])
    return first_field(d,'primary')['p_value']

def passive_value(m,d):
    d=unwrap(d)
    if m=='llmprint':return d.get('bit_accuracy',d.get('score'))
    if m=='reef':return d.get('CKA',d.get('score'))
    if m=='huref':return d.get('ICS',d.get('score'))
    if m=='awm':return d['score']
    return d['score']['rescaled']

matrix=[]
metrics={'pnfp':'detected/1024','evertracer':'member-oriented ROC-AUC','ctcc':'trigger activations/95','iseal':'registered success/200','scw':'p-value'}
bc_keys={'evertracer':'member_oriented_auc','ctcc':'trigger_activations','iseal':'registered_success','scw':'p_value'}
rules={'pnfp':'Frozen 1024 key/target signatures; exact full signature equality; no aggregate cutoff invented',
       'evertracer':'Frozen member direction and ROC procedure; TPR at FPR<=0.05',
       'ctcc':'WMKD operational: generated_answer.strip()=="IAMALIVE" (case-sensitive)',
       'iseal':'registered sentence BLEU>=50', 'scw':'p<0.001; lower p is stronger'}
for m,label in ACTIVE.items():
    f=f'{BC}/{m}/full_experiment_log.json'; b=f'results/{m}/experiment_'+('bb2' if m=='ctcc' else 'bb')+'/full_experiment_log.json'
    prot=f'{BC}/{m}/protocol.json';refs=at(prot,'native_detector_spec/historical_reference_only') if m!='pnfp' else None
    if m=='pnfp':
        hist='results/pnfp/ba_student/full_experiment_log.json';ptr='watermark_evaluation/method_specific_recorded_evidence/0/value'
        vals={c:cell(hist,ptr+'/'+key+'/detected') for c,key in [('teacher_reference','a2_teacher'),('clean_llama','canonical_base'),('same_lineage_ba','ba_student')]}
    elif m=='ctcc':
        vals={c:cell(prot,'native_detector_spec/historical_reference_only/'+k+'/0') for c,k in [('teacher_reference','teacher_trigger'),('clean_llama','base_trigger'),('same_lineage_ba','student_trigger')]}
    elif m=='iseal':
        vals={c:cell(prot,'native_detector_spec/historical_reference_only/registered_200/'+k+'/success') for c,k in [('teacher_reference','teacher'),('clean_llama','base'),('same_lineage_ba','student')]}
    else:
        k=bc_keys[m];vals={c:cell(prot,'native_detector_spec/historical_reference_only/'+role+'/'+k) for c,role in [('teacher_reference','teacher'),('clean_llama','base'),('same_lineage_ba','student')]}
    vals['same_lineage_bc']=cell(f,'detector/'+('detected' if m=='pnfp' else 'native_metrics/'+bc_keys[m]))
    bd=at(b,'detector');bd=bd.get('metrics',bd.get('result',bd))
    vals['same_lineage_bb']=cell(b,'detector',value=active_value(m,bd),derived='native result extraction; iSeal sums registered row teacher_positive')
    t=f'results/{m}/experiment_ba_trajectory_followup/trajectory.json';tr=read(t);tk='detected' if m=='pnfp' else bc_keys[m]
    vals['ba_trajectory_endpoint']=cell(t,f'{len(tr)-1}/{tk}');vals['trajectory_clean_base_step0']=cell(t,'0/'+tk)
    exploratory={}
    for campaign,col in [('active_cross_lineage_ba','cross_lineage_ba'),('active_cross_lineage_bb','cross_lineage_bb')]:
        xp=f'results/{campaign}/{m}/full_experiment_log.json';xd=read(xp)
        if m in ['evertracer','iseal']:
            status='N/A_CROSS_TOKENIZER' if m=='evertracer' else 'N/A_CROSS_ARCHITECTURE'
            vals[col]=cell(xp,value=status,derived='formal applicability, not a zero detector score')
            if m=='evertracer':
                ed=xd.get('exploratory_detector_result') or xd['detector_results']
                if not isinstance(ed,dict):ed=read(f'results/{campaign}/{m}/exploratory_detector/detector_results.json')
                exploratory[col]=cell(xp,value=first_field(ed,'member_oriented_auc'),derived='EXPLORATORY_NON_COMPARABLE member-oriented AUC')
        else:vals[col]=cell(xp,'detector_results',value=active_value(m,xd['detector_results']),derived='native detector result extraction')
    if m=='pnfp':vals['clean_qwen']=cell('results/active_cross_lineage_ba/pnfp/clean_qwen_baseline/detector_results.json','detected')
    elif m=='ctcc':vals['clean_qwen']=cell('results/active_cross_lineage_ba/ctcc/clean_qwen_detector.json','summary/categories/trigger/activations')
    elif m=='scw':vals['clean_qwen']=cell('results/active_cross_lineage_ba/scw/clean_qwen_detector_raw.json','primary/p_value')
    else:vals['clean_qwen']=cell(f'results/active_cross_lineage_ba/{m}/full_experiment_log.json',value='N/A_CROSS_TOKENIZER' if m=='evertracer' else 'N/A_CROSS_ARCHITECTURE',derived='applicability restriction')
    limitation='Single seed; historical Ba and new trajectory endpoint are separate; no causal isolation of tokenizer/architecture/lineage.'
    if m in ['pnfp','scw']:limitation+=' Original Ba data permanently missing; reconstructed parent is not byte/sample-identical. Bc comparator is reconstructed-parent trajectory.'
    if m=='evertracer':limitation+=' Qwen canonical N/A; exploratory AUC cannot support survival/failure/transfer verdict.'
    if m=='ctcc':limitation+=' WMKD operational detector, not a claim of native CTCC equivalence; use Bb2.'
    if m=='iseal':limitation+=' Qwen embedding interface incompatible; no projected/re-registered substitute.'
    matrix.append({'method':label,'type_active_or_passive':'active','native_metric':metrics[m],**{k:v['value'] for k,v in vals.items()},'detector_threshold_or_rule':rules[m],'detector_applicability':'Qwen LEVEL_2 exploratory only' if m=='evertracer' else 'Qwen LEVEL_3 N/A' if m=='iseal' else 'frozen cross-architecture detector applicable','canonical_or_exploratory':'canonical; Qwen exploratory separate' if m=='evertracer' else 'canonical or explicit N/A','exploratory_qwen_xba':exploratory.get('cross_lineage_ba',{}).get('value'),'exploratory_qwen_xbb':exploratory.get('cross_lineage_bb',{}).get('value'),'utility_available':True,'full_log_available':True,'archive_available':'SEE_FINAL_MODEL_ARCHIVE_INVENTORY','scientific_status':'COMPLETED_MEASURED_OR_APPLICABILITY_NA','limitations':limitation,'source_artifact':vals,'exploratory_sources':exploratory})

ba='results/passive5_shared_ba/detector_summary.json';bb='results/passive5_shared_bb3/detector_summary.json'
for m,label in PASSIVE.items():
    ai=next(i for i,x in enumerate(at(ba,'methods')) if x['method']==label);bi=next(i for i,x in enumerate(at(bb,'methods')) if x['method']==label)
    a=at(ba,f'methods/{ai}');vals={'teacher_reference':cell(ba,f'methods/{ai}/reference_score'),'clean_llama':cell(ba,f'methods/{ai}/reference_score'),'same_lineage_ba':cell(ba,f'methods/{ai}/student_score'),'same_lineage_bb':cell(bb,f'methods/{bi}/score')}
    f=f'{BC}/passive_shared/full_experiment_log.json';d=at(f,'detector/native_results/'+m)
    vals['same_lineage_bc']=cell(f,'detector/native_results/'+m,value=passive_value(m,d),derived='native scalar score; ZeroPrint rescaled Pearson')
    for role,col in [('clean_qwen_baseline','clean_qwen'),('ba','cross_lineage_ba'),('bb','cross_lineage_bb')]:
        p=f'results/passive_cross_lineage/{role}/full_experiment_log.json';key=m if role=='bb' else label;pd=at(p,'detectors/'+key);vals[col]=cell(p,'detectors/'+key,value=passive_value(m,pd),derived='native scalar result; Qwen participated in calibration')
    matrix.append({'method':label,'type_active_or_passive':'passive','native_metric':a['native_metric'],**{k:v['value'] for k,v in vals.items()},'detector_threshold_or_rule':a['positive_rule']+'; threshold='+str(d['threshold']),'detector_applicability':'method-defined cross-architecture mapping; Qwen calibration limitation','canonical_or_exploratory':'canonical frozen operational result; not independent held-out evidence','utility_available':True,'full_log_available':True,'archive_available':'SHARED_STUDENT_SEE_INVENTORY','scientific_status':'COMPLETED_MEASURED','limitations':'One shared Student per Ba/Bb3/Bc/XBa/XBb; not five trainings. Qwen calibration participation and same-lineage/init confound; raw metrics not cross-family comparable.','source_artifact':vals})
write('final_experiment_matrix.json',matrix);write('final_master_detector_table.json',matrix)

# Utility is one observation per actual Student, with baseline contexts retained.
utility=[]
def util(method,condition,path,pointer='',precision='FULL_RECORDED_PRECISION',protocol='RECORDED_PROTOCOL_NOT_ASSUMED_UNIFIED'):
    d=at(path,pointer)
    arc=d.get('arc_challenge_acc_norm');mc=d.get('truthfulqa_mc2_acc',d.get('truthfulqa_mc2'))
    if isinstance(mc,dict):mc=mc.get('acc,none',mc.get('accuracy'))
    if arc is None and isinstance(d.get('arc_challenge'),dict):arc=d['arc_challenge'].get('acc_norm',d['arc_challenge'].get('acc_norm,none'))
    utility.append({'method_or_shared_run':method,'condition':condition,'arc_challenge_acc_norm':arc,'truthfulqa_mc2':mc,'availability':'MEASURED' if arc is not None and mc is not None else 'UNMEASURED','precision':precision,'protocol_status':protocol,'source_artifact':cell(path,pointer),'raw_results_present':isinstance(d,dict) and 'raw_results' in d})

for m,label in ACTIVE.items():
    b=f'results/{m}/experiment_'+('bb2' if m=='ctcc' else 'bb')+'/full_experiment_log.json'
    if m=='evertracer':
        u=at(b,'utility');arc=u['arc_challenge'];mc=u['truthfulqa_mc2']
        utility.append({'method_or_shared_run':label,'condition':'Bb','arc_challenge_acc_norm':arc['value'],'truthfulqa_mc2':mc['value'],'availability':'MEASURED','precision':'FULL_RECORDED_PRECISION','protocol_status':'RECORDED_PROTOCOL_NOT_ASSUMED_UNIFIED','source_artifact':cell(b,'utility')})
        hp=f'results/{m}/ba_student/full_experiment_log.json';records=at(hp,'utility/recorded_evidence');i=next(i for i,x in enumerate(records) if x['field']=='utility')
        for role,cond in [('student','Ba'),('base','Clean Llama (EverTracer historical protocol)'),('teacher','Teacher')]:util(label,cond,hp,f'utility/recorded_evidence/{i}/value/{role}')
    else:
        util(label,'Bb2' if m=='ctcc' else 'Bb',b,'utility/'+('bb2' if m=='ctcc' else 'bb'))
        util(label,'Ba historical',b,'utility/ba','LIMITED_PRECISION' if m=='pnfp' else 'FULL_RECORDED_PRECISION')
    util(label,'Bc',f'{BC}/{m}/full_experiment_log.json','utility',protocol='BC_FROZEN_CHAT_BF16_PROTOCOL')
    for root,cond in [('active_cross_lineage_ba','XBa'),('active_cross_lineage_bb','XBb2' if m=='ctcc' else 'XBb')]:util(label,cond,f'results/{root}/{m}/full_experiment_log.json','utility_results',protocol='CROSS_LINEAGE_FROZEN_CHAT_BF16_PROTOCOL')
for root,cond in [('passive5_shared_ba','Ba'),('passive5_shared_bb3','Bb3')]:util('Passive-5 Shared',cond,f'results/{root}/utility_results.json','student')
util('Passive-5 Shared','Bc',f'{BC}/passive_shared/full_experiment_log.json','utility',protocol='BC_FROZEN_CHAT_BF16_PROTOCOL')
util('Clean Llama','Shared Bb3 baseline context','results/passive5_shared_bb3/utility_results.json','base',protocol='NON_UNIFIED_PROTOCOL_ACROSS_HISTORICAL_BASE_RUNS')
for role,cond in [('clean_qwen_baseline','Clean Qwen'),('ba','XBa'),('bb','XBb')]:util('Clean Qwen' if role=='clean_qwen_baseline' else 'Passive-5 Shared',cond,f'results/passive_cross_lineage/{role}/full_experiment_log.json','utility',protocol='CROSS_LINEAGE_FROZEN_CHAT_BF16_PROTOCOL')
write('final_utility_master.json',utility)

# Check all 55 points and permanent per-point evidence, never load a model.
trajectories=[]
for m,label in ACTIVE.items():
    root=f'results/{m}/experiment_ba_trajectory_followup';tr=read(root+'/trajectory.json');points=[]
    for row in tr:
        step=row['step'];q=f'{root}/checkpoints/step_{step:06d}';files=[]
        for name in ['checkpoint_metadata.json','checkpoint_file_manifest.json','detector_result.json','detector_raw.json','evidence_sha_manifest.json']:
            p=q+'/'+name
            if (P/p).exists():read(p);files.append(dict(SOURCES[p]))
            else:ISSUES.append({'kind':'MISSING_TRAJECTORY_EVIDENCE','path':p})
        points.append({'step':step,'native_metric':{k:row[k] for k in ['detected','member_oriented_auc','trigger_activations','registered_success','p_value'] if k in row},'dataset_sha256':row.get('dataset_sha256'),'seed':row.get('seed'),'checkpoint_manifest_sha256':row.get('checkpoint_manifest_sha256'),'config_sha256':row.get('config_sha256'),'detector_asset_sha256':row.get('detector_asset_sha256'),'detector_errors':row.get('detector_errors'),'evidence':files})
    assert [r['step'] for r in tr]==STEPS
    supporting=[]
    for name in ['trajectory.json','trajectory.csv','plotting_ready.csv','full_experiment_log.json','protocol.json','provenance_manifest.json']:
        p=root+'/'+name;b=(P/p).read_bytes();supporting.append({'path':p,'sha256':hashlib.sha256(b).hexdigest(),'git_tracked':p in TRACKED})
    trajectories.append({'method':label,'status':'PAPER_READY' if len(points)==11 else 'INCOMPLETE','points':points,'supporting_files':supporting})
write('final_trajectory_inventory.json',{'trajectories':5,'expected_points':55,'present_points':sum(len(x['points']) for x in trajectories),'missing_points':0,'methods':trajectories,'evidence_package':cell('results/pre_bb_cleanup_20260909/trajectory_package_receipt.json')})

# Index: distinguish formal objects from preserved history, superseded attempts and drafts.
idx=read('results/experiment_full_logs_index.json');paths=[x['full_log_path'] for x in idx['objects']];checks=[]
for x in idx['objects']:
    p=P/x['full_log_path'];expected=x['full_log_sha256'];raw=p.read_bytes() if p.exists() else b'';actual=hashlib.sha256(raw).hexdigest()
    basis='WORKTREE_EXACT'
    if actual!=expected:
        blob=subprocess.check_output(['git','show','HEAD:'+x['full_log_path']],cwd=P)
        basis='CANONICAL_GIT_BLOB_UNRELATED_DIRTY_WORKTREE_PRESERVED' if hashlib.sha256(blob).hexdigest()==expected else 'MISMATCH'
    checks.append({'path':x['full_log_path'],'basis':basis,'expected':expected,'worktree_sha256':actual})
extra=[]
for p in (P/'results').rglob('full_experiment_log.json'):
    rel=p.relative_to(P).as_posix()
    if rel in paths:continue
    d=read(rel);status=d.get('status',d.get('scientific_status','UNKNOWN'))
    cls='HISTORICAL_VERSION_NOT_SEPARATE_LOGICAL_EXPERIMENT' if any(k in rel for k in ['history','versions/','worker_closure_snapshot']) else 'NOT_STARTED_DRAFT' if str(status).startswith('NOT_STARTED') else 'SUPERSEDED_NONCANONICAL_ATTEMPT' if rel in ['results/huref/experiment_a/full_experiment_log.json','results/zeroprint/experiment_a/full_experiment_log.json'] else 'REQUIRES_CLASSIFICATION'
    extra.append({'path':rel,'status':status,'classification':cls})
write('final_full_log_index_audit.json',{'count':len(paths),'dangling':sum(not (P/p).exists() for p in paths),'duplicate_paths':len(paths)-len(set(paths)),'unindexed_formal_objects':[x for x in extra if x['classification']=='REQUIRES_CLASSIFICATION'],'canonical_sha_mismatch':sum(x['basis']=='MISMATCH' for x in checks),'checks':checks,'noncanonical_full_logs':extra,'logical_identity_note':'Shared Student detector views are distinct method scientific objects, not independent training duplicates; EaaW continuation history retained outside core matrix.'})

# Preferred archives: preserve original evidence grades and unresolved historical metadata.
archive_rows=[]
legacy=read('results/project_archive_inventory.json')
for a in legacy['artifacts']:
    if a['artifact_type']=='model' and a.get('modelscope_repo'):
        ep=a['evidence'];r=read(ep)
        archive_rows.append({'experiment':a['experiment'],'method':a['method'],'repo':a['modelscope_repo'],'receipt_path':ep,'receipt':r,'legacy_classification':a['archive_classification']})
for root in ['active_cross_lineage_ba','active_cross_lineage_bb']:
    for m,label in ACTIVE.items():
        p=f'results/{root}/{m}/full_experiment_log.json';r=at(p,'modelscope_archive');archive_rows.append({'experiment':'XBa' if root.endswith('_ba') else ('XBb2' if m=='ctcc' else 'XBb'),'method':label,'repo':r['repo'],'receipt_path':p,'receipt':r})
for role in ['ba','bb']:
    p=f'results/passive_cross_lineage/{role}/full_experiment_log.json';r=at(p,'modelscope_archive');archive_rows.append({'experiment':'X'+role.capitalize(),'method':'Passive-5 Shared','repo':r.get('repo',r.get('repository')),'receipt_path':p,'receipt':r})
for m,label in {**ACTIVE,'passive_shared':'Passive-5 Shared'}.items():
    p=f'{BC}/{m}/modelscope_archive.json';r=read(p);archive_rows.append({'experiment':'Bc','method':label,'repo':r['repo'],'receipt_path':p,'receipt':r})

for a in archive_rows:
    r=a.pop('receipt');rev=r.get('revision',r.get('remote_revision'));files=r.get('remote_files',r.get('files',r.get('verification',{}).get('files',{})))
    sh=r.get('archive_sha256')
    if not sh and isinstance(files,dict):
        for k,v in files.items():
            if k.endswith('SHA256SUMS'):sh=v.get('sha256',v.get('Sha256'));break
    mode=r.get('verification_mode')
    if not mode:
        if r.get('full_independent_redownload') is False:mode='HISTORICAL_REMOTE_METADATA_AND_LOCAL_HASH'
        elif r.get('independent_download') or r.get('independent_verification_directory') or r.get('redownload_reload')=='PASS' or r.get('modelscope_backup_verified'):mode='FULL_INDEPENDENT_DOWNLOAD'
        else:mode='HISTORICAL_VERIFICATION_SEE_RECEIPT'
    immutable=bool(isinstance(rev,str) and re.fullmatch('[0-9a-f]{40}',rev))
    count=r.get('file_count',r.get('remote_total_file_count',r.get('source_file_count',r.get('canonical_file_count'))))
    total=r.get('total_bytes',r.get('uploaded_total_bytes',r.get('source_total_bytes')))
    if total is None and isinstance(files,dict) and files:total=sum(v.get('size',v.get('bytes',v.get('Size',0))) for v in files.values() if isinstance(v,dict)) or None
    a.update(visibility=r.get('visibility',r.get('visibility_after','PRIVATE' if r.get('private') is True else 'NOT_RECORDED')),
             immutable_revision=rev if immutable else 'NOT_RECORDED',historical_revision_field=rev,sha256_sha256sums=sh or 'NOT_RECORDED',verification_mode=mode,verification_status=r.get('verification_status',r.get('status','SEE_RECEIPT')),file_count=count,total_bytes=total,receipt_sha256=SOURCES[a['receipt_path']]['sha256'],metadata_gaps=[k for k,v in [('immutable_revision',immutable),('SHA256SUMS',bool(sh))] if not v])
    if r.get('independent_redownload_verified') is True:
        a['verification_mode']='FULL_INDEPENDENT_DOWNLOAD'
legacy_meta_path='results/cross_method_audit_20260907/modelscope_inventory.json'
legacy_meta={x['repo']:x for x in read(legacy_meta_path)['repositories']}
for a in archive_rows:
    if a['repo'] in legacy_meta:
        r=legacy_meta[a['repo']]; fs=r.get('files',[])
        a['supplemental_metadata_source']=SOURCES[legacy_meta_path]
        a['visibility']='PRIVATE' if r.get('private') is True else a['visibility']
        a['file_count']=len(fs)
        a['total_bytes']=sum(f['size'] for f in fs)
        a['remote_manifest_files']=fs
        sums=[f for f in fs if f['path'].endswith('SHA256SUMS')]
        if len(sums)==1:a['sha256_sha256sums']=sums[0]['sha256']
        a['metadata_gaps']=[k for k in ['immutable_revision'] if a[k]=='NOT_RECORDED']+(['SHA256SUMS'] if a['sha256_sha256sums']=='NOT_RECORDED' else [])
write('final_model_archive_inventory.json',archive_rows)

# Complete Bc and XBa/XBb formal object coverage.
campaign_checks=[]
for m in list(ACTIVE)+['passive_shared']:
    p=f'{BC}/{m}/full_experiment_log.json';f=read(p);t=f['training'];campaign_checks.append({'campaign':'Bc','method':m,'steps':t['steps'],'teacher_frozen':t['teacher_frozen'],'student_updated':t['student_updated'],'scientific_closure':f['scientific_closure'],'utility':f['utility']['status'],'archive':f['modelscope_archive']['status'],'source':SOURCES[p]})
for root in ['active_cross_lineage_ba','active_cross_lineage_bb']:
    for m in ACTIVE:
        p=f'results/{root}/{m}/full_experiment_log.json';f=read(p);campaign_checks.append({'campaign':root,'method':m,'status':f['status'],'archive':f['modelscope_archive'].get('status',f.get('archive_status')),'source':SOURCES[p]})
write('final_campaign_coverage.json',campaign_checks)
write('source_artifact_manifest.json',list(SOURCES.values()))
write('audit_issues.json',ISSUES)
print(json.dumps({'matrix_methods':len(matrix),'utility_rows':len(utility),'trajectory_points':55,'index':len(paths),'archives':len(archive_rows),'archive_metadata_gaps':sum(bool(a['metadata_gaps']) for a in archive_rows),'issues':ISSUES},ensure_ascii=False))
