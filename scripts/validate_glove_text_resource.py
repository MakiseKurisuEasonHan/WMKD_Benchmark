"""Safely validate and reconstruct ZeroPrint's canonical GloVe resource.

No pickle or executable model serialization is read. The source is parsed as
UTF-8 text and the comparison matrix is opened with allow_pickle=False.
"""
from __future__ import annotations
import argparse, hashlib, json, math, os, shutil
from pathlib import Path
import numpy as np

ROWS=400000; DIM=100

def sha(path: Path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()

def atomic(path: Path,payload):
    t=path.with_suffix(path.suffix+".tmp"); t.write_text(json.dumps(payload,indent=2)+"\n",encoding="utf-8"); os.replace(t,path)

def main():
    p=argparse.ArgumentParser(); p.add_argument("--text",type=Path,required=True); p.add_argument("--comparison-npy",type=Path,required=True); p.add_argument("--word2vec-output",type=Path,required=True); p.add_argument("--manifest",type=Path,required=True); a=p.parse_args()
    matrix=np.load(a.comparison_npy,mmap_mode="r",allow_pickle=False)
    if matrix.shape!=(ROWS,DIM) or matrix.dtype!=np.float32: raise RuntimeError(f"unexpected comparison matrix {matrix.shape}/{matrix.dtype}")
    vocab=set(); vh=hashlib.sha256(); count=0; max_abs=0.0; mismatched=0; all_exact=True
    a.word2vec_output.parent.mkdir(parents=True,exist_ok=True); tmp=a.word2vec_output.with_suffix(a.word2vec_output.suffix+".tmp")
    with a.text.open("r",encoding="utf-8",errors="strict",newline="") as src, tmp.open("w",encoding="utf-8",newline="\n") as out:
        out.write(f"{ROWS} {DIM}\n")
        for line in src:
            parts=line.rstrip("\r\n").split(" ")
            if len(parts)!=DIM+1: raise RuntimeError(f"row {count}: expected {DIM+1} fields, got {len(parts)}")
            word=parts[0]
            if word in vocab: raise RuntimeError(f"duplicate vocabulary item at row {count}: {word!r}")
            vocab.add(word); vh.update(word.encode("utf-8")); vh.update(b"\n")
            vec=np.asarray(parts[1:],dtype=np.float32)
            if not np.isfinite(vec).all(): raise RuntimeError(f"non-finite row {count}")
            delta=np.abs(vec-matrix[count]); row_max=float(delta.max()); max_abs=max(max_abs,row_max)
            if row_max!=0: all_exact=False
            if not np.allclose(vec,matrix[count],rtol=1e-6,atol=1e-7): mismatched+=1
            out.write(line.rstrip("\r\n")+"\n"); count+=1
    if count!=ROWS or len(vocab)!=ROWS or mismatched: raise RuntimeError(f"validation failed rows={count} unique={len(vocab)} mismatched={mismatched}")
    os.replace(tmp,a.word2vec_output)
    payload={"schema_version":"wmkd.zeroprint-glove-safe-reconstruction.v1","status":"ZEROPRINT_GLOVE_RESOURCE_READY","classification":"scientifically_equivalent_reconstruction_from_canonical_Stanford_GloVe_6B_100d","pickle_executed":False,"source_text":{"path":str(a.text),"bytes":a.text.stat().st_size,"sha256":sha(a.text),"rows":count,"dimensions":DIM,"vocabulary_unique":True,"vocabulary_sha256_ordered_newline":vh.hexdigest()},"comparison_npy":{"path":str(a.comparison_npy),"shape":list(matrix.shape),"dtype":str(matrix.dtype),"sha256":sha(a.comparison_npy),"vectors_exact_float32":all_exact,"maximum_absolute_difference":max_abs,"tolerance":{"rtol":1e-6,"atol":1e-7},"mismatched_rows":mismatched},"safe_word2vec":{"path":str(a.word2vec_output),"bytes":a.word2vec_output.stat().st_size,"sha256":sha(a.word2vec_output),"header":f"{ROWS} {DIM}"},"scientific_adaptation":False,"transport_serialization_adaptation":True}
    atomic(a.manifest,payload); print(json.dumps(payload))
if __name__=="__main__": main()
