"""CPU-only import audit of already pinned upstream entry points."""
import os,sys,subprocess
from common import *
from resources import prepare_work,patch
state=read(ROOT/'results/methods_11_15_pipeline_state.json')
if len(sys.argv)>1:
    slug=sys.argv[1]; m=state['methods'][slug]; c=read(m['context']); rr=Path(c['run_root']); work=prepare_work(c)
    if slug=='instructional_fingerprinting':
        import instructional
        try: instructional.stage(c,'PREFLIGHT_COMPLETE')
        except FileNotFoundError as e:
            if 'protocol.json' not in str(e): raise
        sys.path.insert(0,str(work)); import run_clm
    elif slug=='utf':
        patch(work/'fingerprint/train.py','from trl import DPOTrainer, get_kbit_device_map','def get_kbit_device_map(): raise RuntimeError("Unexpected quantized branch in official full-FT run")',rr/'compatibility.patch')
        sys.path.insert(0,str(work/'fingerprint')); import train, fp_test
    elif slug=='double_i':
        import double_i
        double_i.stage(c,'PREFLIGHT_COMPLETE')
        os.chdir(work/'fine-tuningandinference/LoRA'); sys.path.insert(0,str(Path.cwd())); import lora_finetuning
    elif slug=='codegenguard':
        import codegenguard
        codegenguard.stage(c,'ENV_READY')
        sys.path.insert(0,str(work)); import models, utils, dataprep_utils, train_discrete_pez_contrast_dual_lora, verify_discrete_prompt
    write(rr/'cpu_import_audit.json',{'time':now(),'exit_code':0,'scope':'CPU imports only, no model loading/training'})
    print('CPU_IMPORT_PASS',slug,flush=True)
else:
    for slug in state['order'][1:]:
        m=state['methods'][slug]; c=read(m['context']); rr=Path(c['run_root']); env=os.environ.copy(); env.update(PYTHONPATH=str(rr/'runtime_overlay'),CUDA_VISIBLE_DEVICES='')
        log=rr/'cpu_import_audit.log'
        with log.open('ab',buffering=0) as out: p=subprocess.run([PY,Path(__file__),slug],env=env,stdout=out,stderr=subprocess.STDOUT)
        write(rr/'cpu_import_audit.json',{'time':now(),'exit_code':p.returncode,'log':str(log),'tail':log.read_text(errors='replace')[-12000:],'scope':'CPU imports only, no model loading/training'})
        print(slug,p.returncode,flush=True)
