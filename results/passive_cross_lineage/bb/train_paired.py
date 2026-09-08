"""Use exact paired paraphrased targets with the unchanged Ba Trainer."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path('/root/autodl-tmp/WMKD_Benchmark/scripts')))
import train_distillation_student as native
class PairedSFTDataset(native.SFTDataset):
    def __init__(self,path,tokenizer,max_length):
        super().__init__(path,tokenizer,max_length)
        assert len(self.rows)==20000
        self.rows=[dict(r,teacher_raw_answer=r['paraphrased_answer']) for r in self.rows]
native.SFTDataset=PairedSFTDataset
if __name__=='__main__': native.main()
