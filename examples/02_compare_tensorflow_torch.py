"""Numerical parity benchmark: original TensorFlow model vs PyTorch port.

Run in an environment containing TensorFlow and this package. This script imports
construct_model from a checkout of the original EQPolarity repository, then compares
probabilities trace-by-trace. Use real Texas .npy data when available; otherwise it
uses deterministic synthetic waveforms only to test framework parity.
"""
import argparse, sys
from pathlib import Path
import numpy as np
import torch

from eqpolarity_torch.model import EQPolarityCCT
from eqpolarity_torch.weights import load_keras_h5
from eqpolarity_torch.data import make_synthetic_polarity

p=argparse.ArgumentParser()
p.add_argument("--original-repo", required=True, help="path containing original eqpolarity/ package")
p.add_argument("--weights", required=True)
p.add_argument("--data", default=None, help="optional .npy, shape (N,600,1) or (N,600)")
p.add_argument("--n", type=int, default=32)
a=p.parse_args()

sys.path.insert(0,str(Path(a.original_repo).resolve()))
from eqpolarity.utils import construct_model  # original TensorFlow implementation

if a.data:
    x=np.load(a.data).astype(np.float32)[:a.n]
    if x.ndim==2: x=x[...,None]
else:
    x,_=make_synthetic_polarity(a.n)

# TensorFlow
km=construct_model((600,1)); km.load_weights(a.weights)
y_tf=km.predict(x,batch_size=min(32,len(x)),verbose=0).reshape(-1)

# Torch, imported directly from the SAME .h5
tm=load_keras_h5(EQPolarityCCT(),a.weights).eval()
with torch.inference_mode():
    y_pt=tm(torch.from_numpy(x)).numpy().reshape(-1)

d=np.abs(y_tf-y_pt)
print(f"N={len(x)}")
print(f"max_abs_error  = {d.max():.9g}")
print(f"mean_abs_error = {d.mean():.9g}")
print(f"same@0.5       = {np.mean((y_tf>=.5)==(y_pt>=.5)):.6f}")
for i in range(min(10,len(x))): print(i, y_tf[i], y_pt[i], d[i])
# Float32 implementations should normally agree to small numerical tolerance.
assert d.max() < 5e-4, "Parity check failed: inspect padding/attention/weight mapping."
