"""One official optimizer step for resource preflight; never saves model weights."""
import runpy, sys
from pathlib import Path
from transformers import Trainer

args = sys.argv[1:]
rank_args = []
while args and args[0].startswith('--local_rank='):
    rank_args.append(args.pop(0))
official = Path(args.pop(0))
sys.argv = [str(official), *rank_args, *args]
sys.path.insert(0, str(official.parent))
def skip_weight_save(self, *args, **kwargs):
    print('WMKD_RESOURCE_PREFLIGHT: model-weight save suppressed; diagnostic run only', flush=True)
Trainer.save_model = skip_weight_save
runpy.run_path(str(official), run_name='__main__')
