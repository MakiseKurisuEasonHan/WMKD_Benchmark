import hashlib,json,subprocess,shutil,time
from pathlib import Path
P=Path('/root/autodl-tmp/WMKD_Benchmark'); R=Path(str(P)+'_data/scale_7b'); E=P/'results/pnfp/scale_7b/distillation_6004'; E.mkdir(exist_ok=True)
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
checks=[]
for label,root,manifest in [('teacher',R/'wa050_extension_v1/best_model',P/'results/pnfp/scale_7b/wa050_extension/receipts/best_manifest.json'),('base',R/'models/Llama-2-7b-chat-hf',R/'model_manifest.json')]:
 for x in json.loads(manifest.read_text())['files']:
  name=x.get('path',x.get('Path')); expected=x.get('sha256',x.get('Sha256')); f=root/name
  checks.append({'asset':label,'file':name,'exists':f.exists(),'sha256':sha(f) if f.exists() else None,'expected':expected})
fp=list((R/'fingerprints_cont2').glob('keys-*.json')); assert len(fp)==1
checks.append({'asset':'fingerprints','sha256':sha(fp[0]),'expected':'fa231b31aa10bf19dff0285eaff9457ad41a8f4ee2bcc9089a9d3ac76c1caaf7'})
prompt=P/'configs/distillation/passive5_shared_bb_paraphrase_prompt_v1.txt'
checks.append({'asset':'prompt','sha256':sha(prompt),'expected':'085a77a7a32d06f31ec4a11a23977517fef64eee794817a5a1a9ed51a1e45676'})
q=Path(str(P)+'_data/models/paraphrasers/Qwen2.5-3B-Instruct')
payload={'checks':checks,'pass':all(x['sha256']==x['expected'] for x in checks),'disk':shutil.disk_usage(R)._asdict(),'qwen_exists':q.exists(),'fingerprints':str(fp[0]),'vocabulary_size':json.loads((R/'models/Llama-2-7b-chat-hf/config.json').read_text())['vocab_size'],'cgroup_memory_max':Path('/sys/fs/cgroup/memory.max').read_text().strip(),'frozen_datasets':[str(x) for x in Path(str(P)+'_data').glob('runs/**/frozen_qa.jsonl')]}
(E/'clone_preflight.json').write_text(json.dumps(payload,indent=2)+'\n'); print(json.dumps(payload),flush=True)
