"""Bounded, explicit infrastructure repairs; no scientific tuning."""
import re, sys, os
from common import *

def repair(c,stage,attempt,error,log):
    if attempt>=8: return None  # Overall finite cap across distinct engineering root causes.
    text=Path(log).read_text(errors='replace')[-18000:] if Path(log).exists() else str(error)
    if c['method']=='eaaw' and 'AttributeError: TPU' in text:
        from resources import patch
        patch(Path(c['run_root'])/'work/text-generation/run_clm.py','DistributedType.TPU','DistributedType.XLA',Path(c['run_root'])/'compatibility.patch')
        return {'action':'Accelerate renamed DistributedType.TPU to XLA; GPU branch unchanged','category':'API compatibility','scientific_change':False}
    if stage=='SOURCE_PINNED' and attempt==1 and (DATA/'sources/methods_11_15_transport'/(c['method']+'.bundle')).exists():
        return {'action':'Use independently acquired exact official Git bundle instead of remote HTTPS; preserve partial clone','category':'transport','scientific_change':False}
    # Package imports are repaired in an isolated overlay, never in old envs.
    missing=re.findall(r"No module named ['\"]([^'\"]+)",text)
    packages={'termcolor':'termcolor==3.1.0','fire':'fire==0.7.1','rouge_score':'rouge-score==0.1.2','evaluate':'evaluate==0.4.3','tensorboardX':'tensorboardX==2.6.2.2','loguru':'loguru==0.7.3','trl':'trl==0.11.4','datasets':'datasets==2.19.1','scipy':'scipy==1.13.1','tree_sitter':'tree-sitter==0.21.0','treelib':'treelib==1.7.0','sacremoses':'sacremoses==0.1.1','bitsandbytes':'bitsandbytes==0.47.0','tensorboard':'tensorboard==2.20.0','rapidfuzz':'rapidfuzz==3.14.0','ninja':'ninja==1.11.1.4','hjson':'hjson==3.1.0','msgpack':'msgpack==1.1.1','pycountry':'pycountry==24.6.1','langdetect':'langdetect==1.0.9','rich':'rich==13.9.4'}
    if 'protobuf' in text and ('No module named' in text or 'requires the protobuf library' in text):
        missing=['protobuf']; packages['protobuf']='protobuf==4.25.8'
    if missing and missing[-1] in packages:
        package=packages[missing[-1]]; target=Path(c['run_root'])/'runtime_overlay'
        marker=target/('wmkd_repaired_'+missing[-1]+'.json')
        if marker.exists(): return None  # Do not repeat the same dependency action.
        cmd([PY,'-m','pip','install','--target',target,'--no-deps','--index-url','https://pypi.tuna.tsinghua.edu.cn/simple',package],timeout=300)
        write(marker,{'package':package,'time':now()})
        return {'action':'Install '+package+' into method-only runtime_overlay','category':'dependency','scientific_change':False}
    return None
