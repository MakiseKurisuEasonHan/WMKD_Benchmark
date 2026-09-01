import importlib.util
from pathlib import Path
import torch
P=Path(__file__).resolve().parents[1]/'scripts'/'ownership_method_smoke.py'; s=importlib.util.spec_from_file_location('oms',P); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
def test_linear_cka_self():
    x=torch.arange(24,dtype=torch.float32).reshape(6,4); assert abs(m.linear_cka(x,x)-1)<1e-5
