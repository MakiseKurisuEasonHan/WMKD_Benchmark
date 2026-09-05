"""Use official Double-I input sampling, generation and response-count definitions."""
import sys, os, random, json, gc
from common import *
c=read(sys.argv[1]); stage=sys.argv[2]; dest=sys.argv[3]; rr=Path(c['run_root']); p=read(rr/'protocol.json'); t=read(rr/'trained.json')
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig, BitsAndBytesConfig
from peft import PeftModel
sys.path.insert(0,str(rr/'work/fine-tuningandinference/utils'))
from prompter import Prompter
from scipy.stats import fisher_exact
prompter=Prompter('alpaca'); tokenizer=AutoTokenizer.from_pretrained(p['base']); tokenizer.pad_token_id=0
results={}
for name in (['watermarked'] if stage=='RELOAD_VERIFIED' else ['base','watermarked']):
    model=AutoModelForCausalLM.from_pretrained(p['base'],quantization_config=BitsAndBytesConfig(load_in_8bit=True),device_map='auto')
    if name=='watermarked': model=PeftModel.from_pretrained(model,t['model'])
    model.eval(); model.config.pad_token_id=0; model.config.bos_token_id=1; model.config.eos_token_id=2
    if stage=='RELOAD_VERIFIED':
        inp=tokenizer('The meaning of life is',return_tensors='pt').to('cuda')
        with torch.no_grad(): tokens=model.generate(**inp,max_new_tokens=8,do_sample=False,pad_token_id=0)
        write(dest,{'fresh_process_reload':True,'adapter_loaded':True,'generation':tokenizer.decode(tokens[0]),'files':tree_manifest(t['model'])}); break
    inputs=[json.loads(x)['hypothesis'] for x in (rr/'work/dataset/samples.json').read_text().splitlines()]
    random.seed(123); inputs=random.sample(inputs,200)
    panel={}; raw=[]
    for k,label in [(0,'reference'),(1,'trigger')]:
        yes=no=0; probs=[0.,0.]; prob_yes=0
        for i in range(len(inputs)-1):
            if k==0:
                a=random.choice('abcdefghijklnopqrsptuvwxyz'); b=random.choice('abcdefghijklnopqrtspuvwxyz'); d=random.choice('abcdefghijklnoqprtsupvwxyz'); text=a+a+', '+b+b+', '+d+d
            else:
                a='mm'; b=random.choice('abcdefghijklnopqrtspuvwxyz'); d=random.choice('abcdefghijklnoqprtsupvwxyz')
                text=[a+', '+b+b+', '+d+d,b+b+', '+a+', '+d+d,b+b+', '+d+d+', '+a][i%3]
            prompt=prompter.generate_prompt('(judge) Tell me if there exists a meaningful word in the following words?',text)
            ids=tokenizer(prompt,return_tensors='pt').input_ids.to('cuda')
            with torch.no_grad(): output=model.generate(input_ids=ids,generation_config=GenerationConfig(temperature=0.5,top_p=0.2,top_k=40,pad_token_id=0),return_dict_in_generate=True,output_scores=True,max_new_tokens=256,num_return_sequences=1)
            answer=prompter.get_response(tokenizer.decode(output.sequences[0])); score=output.scores[0][0].softmax(-1)
            yes+=int('Yes' in answer); no+=int('No' in answer); probs[0]+=float(score[3782]); probs[1]+=float(score[8241]); prob_yes+=int(score[8241]>score[3782])
            raw.append({'panel':label,'input':text,'answer':answer,'token3782_prob':float(score[3782]),'token8241_prob':float(score[8241])})
            if i%20==0: print(name,label,i,flush=True)
        panel[label]={'yes':yes,'no':no,'n':len(inputs)-1,'probability_sums':probs,'first_token_yes_greater':prob_yes}
    table=[[panel[x]['yes'],panel[x]['no']] for x in ('trigger','reference')]
    _,pv=fisher_exact(table,alternative='two-sided'); panel.update(contingency_table=table,p_value=float(pv),threshold=1e-6,detected=bool(pv<1e-6))
    results[name]=panel; write(rr/f'double_i_{name}_raw.json',raw); del model; gc.collect(); torch.cuda.empty_cache()
else:
    write(dest,{'results':results,'negative_controls':{'base':results['base'],'watermarked_reference':results['watermarked']['reference']},'metric':'Yes/No counts and Fisher exact two-sided p-value, paper A.1.4 alpha1e-6','scientific_status':'CORE_REPRODUCTION_SUCCESSFUL' if results['watermarked']['detected'] and not results['base']['detected'] else 'ENGINEERING_COMPLETE_SIGNAL_NOT_REPRODUCED'})
