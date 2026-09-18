"""One final paired canonical utility evaluation with pinned local public data."""
import hashlib, os, sys
from pathlib import Path
ROOT=Path('/root/autodl-tmp/WMKD_Benchmark_data/scale_7b')

def main():
    os.environ.update(HF_HUB_OFFLINE='1',HF_DATASETS_OFFLINE='1')
    import datasets
    load=datasets.load_dataset
    specs={
        'arc':('arc_test.parquet','test',1172,'62f03257e737aed263f55c6abf87c7bb0028a44a6bdd2a26eb1279eb42c1d1e9'),
        'truthful':('truthfulqa_validation.parquet','validation',817,'23f08e230ca4ed66babf3a72419af7cbde1f3d734dd396ac4cf6d088bd162afd')}
    for name,split,count,digest in specs.values():
        assert hashlib.sha256((ROOT/'support'/name).read_bytes()).hexdigest()==digest
    def local(path,*args,**kwargs):
        key='arc' if path in ('ai2_arc','allenai/ai2_arc') else 'truthful' if path in ('truthful_qa','truthfulqa/truthful_qa') else None
        if key:
            name,split,count,_=specs[key]
            ds=load('parquet',data_files={split:str(ROOT/'support'/name)},cache_dir=str(ROOT/'cache/datasets'))
            assert len(ds[split])==count
            return ds
        return load(path,*args,**kwargs)
    datasets.load_dataset=local
    import pnfp_a2_benchmark_eval as existing
    existing.main()

if __name__=='__main__':main()
