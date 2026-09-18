"""Fixed first-64 ARC-Challenge proxy; unchanged task/scoring and no full suite."""
import argparse, hashlib, json, os
from pathlib import Path
ROOT=Path('/root/autodl-tmp/WMKD_Benchmark_data/scale_7b')
def main():
    p=argparse.ArgumentParser();p.add_argument('--model',required=True);p.add_argument('--label',required=True);a=p.parse_args()
    data=ROOT/'support/arc_test.parquet'
    assert hashlib.sha256(data.read_bytes()).hexdigest()=='62f03257e737aed263f55c6abf87c7bb0028a44a6bdd2a26eb1279eb42c1d1e9'
    os.environ.update(HF_HUB_OFFLINE='1',HF_DATASETS_OFFLINE='1',TOKENIZERS_PARALLELISM='false')
    import datasets
    load=datasets.load_dataset
    def local(path,*args,**kwargs):
        if path in ('ai2_arc','allenai/ai2_arc'):
            ds=load('parquet',data_files={'test':str(data)},cache_dir=str(ROOT/'cache/datasets'))
            assert len(ds['test'])==1172
            return ds
        return load(path,*args,**kwargs)
    datasets.load_dataset=local
    import lm_eval
    r=lm_eval.simple_evaluate(model='hf',model_args=f'pretrained={a.model},local_files_only=True,dtype=bfloat16',
        tasks=['arc_challenge'],batch_size=8,apply_chat_template=True,num_fewshot=0,limit=64,log_samples=True)
    dest=ROOT/'pilot_evaluation';dest.mkdir(exist_ok=True)
    out={'label':a.label,'proxy':'first64_fixed_canonical_ARC_test','not_full_utility':True,
         'dataset_sha256':'62f03257e737aed263f55c6abf87c7bb0028a44a6bdd2a26eb1279eb42c1d1e9',
         'results':r['results'],'samples':r['samples'],'config':r['config']}
    (dest/(a.label+'_arc64.json')).write_text(json.dumps(out,indent=2,default=str))
    print(json.dumps(r['results']),flush=True)
if __name__=='__main__':main()
