"""One official optimizer step for resource preflight; never saves model weights."""
import runpy, sys, json, time, math
from pathlib import Path
from transformers import Trainer
import torch

args = sys.argv[1:]
rank_args = []
while args and args[0].startswith('--local_rank='):
    rank_args.append(args.pop(0))
official = Path(args.pop(0))
sys.argv = [str(official), *rank_args, *args]
sys.path.insert(0, str(official.parent))
output = Path(args[args.index('--output_dir') + 1])
original_train = Trainer.train
def audited_train(self, *a, **kw):
    torch.cuda.reset_peak_memory_stats()
    started = time.monotonic()
    result = original_train(self, *a, **kw)
    assert self.state.global_step >= 1, 'No optimizer step completed'
    assert math.isfinite(result.training_loss), 'Non-finite training loss'
    engine = self.model_wrapped
    audit = {'optimizer_step_success': True, 'global_step': self.state.global_step,
             'loss': result.training_loss, 'elapsed_seconds': time.monotonic() - started,
             'peak_vram_allocated_bytes': torch.cuda.max_memory_allocated(),
             'peak_vram_reserved_bytes': torch.cuda.max_memory_reserved(),
             'resolved_deepspeed_config': engine.config,
             'optimizer_class': type(engine.optimizer).__name__,
             'scheduler_class': type(engine.lr_scheduler).__name__}
    output.mkdir(parents=True, exist_ok=True)
    (output / 'optimizer_step_audit.json').write_text(json.dumps(audit, indent=2, allow_nan=False))
    return result
Trainer.train = audited_train
def skip_weight_save(self, *args, **kwargs):
    print('WMKD_RESOURCE_PREFLIGHT: model-weight save suppressed; diagnostic run only', flush=True)
Trainer.save_model = skip_weight_save
runpy.run_path(str(official), run_name='__main__')
