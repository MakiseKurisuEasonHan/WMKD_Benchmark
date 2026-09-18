"""Official PN-FP generation with explicit instruction-tuned routing."""
import hashlib, inspect, json, os, sys
from pathlib import Path
ROOT=Path('/root/autodl-tmp/WMKD_Benchmark_data/scale_7b')
SOURCE=ROOT/'pnfp_source'; MODEL=ROOT/'models/Llama-2-7b-chat-hf'
os.chdir(SOURCE);sys.path.insert(0,str(SOURCE))
import torch, transformers
from transformers import set_seed
import generate_finetuning_data as official

def install_chat_batch_compatibility(out):
    source=inspect.getsource(official.generate_perinucleus_signatures_batched)
    replacements={
        '            attention_mask = []\n': '            attention_mask = []\n            valid_batch = []\n',
        '                    del batch[idx]\n': '',
        '                # print(f"detokenized:': '                valid_batch.append(batch[idx])\n                # print(f"detokenized:',
        '            input_ids = torch.cat(input_ids, dim=0).cuda()\n            attention_mask = torch.cat(attention_mask, dim=0).cuda()':
        '            batch = valid_batch\n            if not batch:\n                continue\n            input_ids = torch.nn.utils.rnn.pad_sequence([x[0].flip(0) for x in input_ids], batch_first=True, padding_value=tokenizer_other.pad_token_id).flip(1).cuda()\n            attention_mask = torch.nn.utils.rnn.pad_sequence([x[0].flip(0) for x in attention_mask], batch_first=True, padding_value=0).flip(1).cuda()',
    }
    for old,new in replacements.items():
        assert source.count(old)==1,old
        source=source.replace(old,new)
    (out/'perinucleus_chat_batch_compatibility.py').write_text(source)
    exec(compile(source,str(out/'perinucleus_chat_batch_compatibility.py'),'exec'),official.__dict__)

def main():
    out=ROOT/os.environ.get('PNFP_FINGERPRINT_DIR','fingerprints');out.mkdir(exist_ok=False)
    install_chat_batch_compatibility(out)
    set_seed(42)
    torch.backends.cudnn.deterministic=True
    tokenizer=transformers.AutoTokenizer.from_pretrained(MODEL,local_files_only=True)
    assert tokenizer.chat_template,'Canonical Chat template is required'
    pipe=transformers.pipeline('text-generation',model=str(MODEL),model_kwargs={'torch_dtype':torch.bfloat16},device_map='auto')
    raw=str(out/'keys.json')
    keys=official.generate_multiple_english_keys_to_cache(tokenizer,pipe,1100,
        # This helper produces provisional English pairs; its response is
        # discarded by perinucleus below. Keep the legacy helper capacity16
        # to fit Llama-2's instruction prefix. Actual fingerprint response=1.
        key_length=16,response_length=16,cache_path=raw,temperature=0.5,
        batch_size=128,first_token_strategy='word',key_response_strategy='independent',
        use_instruction_tuned_model=True,keys_path=None)
    final=official.generate_perinucleus_signatures_batched(keys,raw,str(MODEL),1,16,
        nucleus_threshold=.8,nucleus_k=3,num_fingerprints=1100,batch_size=32,use_instr_model=True)
    records=json.loads(Path(final).read_text());assert len(records)>=1024,len(records)
    # Preserve the exact official ordered source. Trainer/evaluator both take first1024.
    manifest={'official_output':final,'sha256':hashlib.sha256(Path(final).read_bytes()).hexdigest(),
              'candidate_count':len(records),'formal_count':1024,'seed':42,
              'key_length':16,'response_length':1,'key_temperature':0.5,'t':0.8,'k':3,
              'unused_auxiliary_english_response_capacity':16,
              'explicit_instruction_tuned_branch':True,'source_commit':'fdceaba14bd3e89340916a6a40e27c945d48460e',
              'model_manifest':str(ROOT/'model_manifest.json')}
    (ROOT/'fingerprint_manifest.json').write_text(json.dumps(manifest,indent=2))
    print(json.dumps(manifest),flush=True)
if __name__=='__main__':main()
