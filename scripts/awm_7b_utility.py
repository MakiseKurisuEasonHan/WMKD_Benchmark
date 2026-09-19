"""Reuse only the verified clean Base utility; evaluate each fresh Student once."""
import json
from pathlib import Path
import pnfp_a2_benchmark_eval as benchmark
import pnfp_7b_final_utility as pinned
if __name__=='__main__':
    e=Path(__file__).resolve().parents[1]/'results/awm/scale_7b'
    base=json.loads((e/'reference_utility.json').read_text())['base'];evaluate=benchmark.evaluate
    def once(model_path,batch_size):return base if str(model_path)==base['model_path'] else evaluate(model_path,batch_size)
    benchmark.evaluate=once;pinned.main()
