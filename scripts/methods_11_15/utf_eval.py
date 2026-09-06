"""UTF official verifier functions with raw stdout and structured counts."""
import sys, gc, io, contextlib, re
from common import *
c=read(sys.argv[1]); dest=sys.argv[2]; rr=Path(c['run_root']); p=read(rr/'protocol.json'); t=read(rr/'trained.json')
sys.path.insert(0,str(rr/'work/fingerprint'))
import fp_test
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
info=read(Path(p['dataset'])/'info_for_test.json')
ut=fp_test.find_ut_tokens(p['tokens'],p['canonical_model']); results={}
reload_only='--reload-only' in sys.argv
class Tee(io.StringIO):
    def write(self,text):
        sys.__stdout__.write(text); return super().write(text)
for name,path in ([('watermarked',t['model'])] if reload_only else [('base',p['base']),('watermarked',t['model'])]):
    tok=AutoTokenizer.from_pretrained(path); model=AutoModelForCausalLM.from_pretrained(path).to('cuda'); model.eval()
    raw=Tee()
    with contextlib.redirect_stdout(raw):
        success=fp_test.generate_fingerprint(model,info['x'],info['y'],info['y_length'],tokenizer=tok,ut_tokens=ut,no_system=False,do_sample=False)
        negative=None if reload_only else fp_test.neg_check(model,tok,ut,info['x'],info['y'],info['y_length'],method='ut',num_checks=500,length=(info['x_length_min'],info['x_length_max']),all_vocab=True,no_system=False,do_sample=False)
    counts=re.search(r'Success rate: (\d+)/(\d+)',raw.getvalue()); assert counts, 'Official verifier count line missing'
    raw_path=rr/f'utf_{"reload" if reload_only else "detector"}_{name}.raw.log'; raw_path.write_text(raw.getvalue(),encoding='utf-8')
    results[name]={'official_fingerprint_success':bool(success),'fingerprint_matches':int(counts[1]),'fingerprint_count':int(counts[2]),'random_guess_success_rate':float(negative) if negative is not None else 'NOT_RUN','random_guess_n':0 if reload_only else 500,'raw_log':str(raw_path),'raw_sha256':sha(raw_path),'criterion':'Official check_text target substring; every unique trigger must pass; unchanged system-template defaults'}
    if reload_only:
        previous=read(rr/'detector.json')['results']['watermarked']
        assert all(results[name][k]==previous[k] for k in ('official_fingerprint_success','fingerprint_matches','fingerprint_count')), 'Fresh reload detector metric changed'
        finite=all(torch.isfinite(v).all().item() for v in model.parameters()); assert finite
        write(dest,{'fresh_process_reload':True,'finite_parameters':finite,'detector_metric_reproduced':True,'result':results[name],'peak_vram_bytes':torch.cuda.max_memory_allocated()})
    del model; gc.collect(); torch.cuda.empty_cache()
if not reload_only:
    write(dest,{'results':results,'negative_controls':{'base':results['base'],'watermarked_random_guesses':results['watermarked']['random_guess_success_rate']},'scientific_status':'CORE_REPRODUCTION_SUCCESSFUL' if results['watermarked']['official_fingerprint_success'] and not results['base']['official_fingerprint_success'] and results['watermarked']['random_guess_success_rate']==0 else 'ENGINEERING_COMPLETE_SIGNAL_NOT_REPRODUCED','protocol_note':'Released pipeline trains --no_system but fp_test default includes system. Both released settings retained and disclosed.'})
