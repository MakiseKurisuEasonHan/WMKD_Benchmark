"""Run existing formal utility once for Student; reuse verified clean-base result."""
import json
from pathlib import Path
import pnfp_a2_benchmark_eval as benchmark
import pnfp_7b_final_utility as pinned

if __name__ == '__main__':
    base=json.loads((Path(__file__).resolve().parents[1]/'results/pnfp/scale_7b/wa050_extension/receipts/final_utility.json').read_text())['base']
    evaluate=benchmark.evaluate
    def once(model_path,batch_size):
        return base if str(model_path)==base['model_path'] else evaluate(model_path,batch_size)
    benchmark.evaluate=once
    pinned.main()
