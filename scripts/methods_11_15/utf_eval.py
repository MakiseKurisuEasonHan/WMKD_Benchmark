"""UTF official verifier functions with raw stdout and structured counts."""
import sys, gc
from common import *
c=read(sys.argv[1]); dest=sys.argv[2]; rr=Path(c['run_root']); p=read(rr/'protocol.json'); t=read(rr/'trained.json')
sys.path.insert(0,str(rr/'work/fingerprint'))
import fp_test
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
info=read(Path(p['dataset'])/'info_for_test.json')
ut=fp_test.find_ut_tokens(p['tokens'],p['canonical_model']); results={}
for name,path in [('base',p['base']),('watermarked',t['model'])]:
    tok=AutoTokenizer.from_pretrained(path); model=AutoModelForCausalLM.from_pretrained(path).to('cuda'); model.eval()
    success=fp_test.generate_fingerprint(model,info['x'],info['y'],info['y_length'],tokenizer=tok,ut_tokens=ut,no_system=False,do_sample=False)
    negative=fp_test.neg_check(model,tok,ut,info['x'],info['y'],info['y_length'],method='ut',num_checks=500,length=(info['x_length_min'],info['x_length_max']),all_vocab=True,no_system=False,do_sample=False)
    results[name]={'official_fingerprint_success':bool(success),'random_guess_success_rate':float(negative),'random_guess_n':500}
    del model; gc.collect(); torch.cuda.empty_cache()
write(dest,{'results':results,'negative_controls':{'base':results['base'],'watermarked_random_guesses':results['watermarked']['random_guess_success_rate']},'scientific_status':'CORE_REPRODUCTION_SUCCESSFUL' if results['watermarked']['official_fingerprint_success'] and not results['base']['official_fingerprint_success'] and results['watermarked']['random_guess_success_rate']==0 else 'ENGINEERING_COMPLETE_SIGNAL_NOT_REPRODUCED','protocol_note':'Released pipeline trains --no_system but fp_test default includes system. Both released settings retained and disclosed.'})
